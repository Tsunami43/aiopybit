"""HTTP client for ByBit REST API."""

from __future__ import annotations

import asyncio
import base64
import hashlib
import hmac
import logging
import time
from collections.abc import Mapping

import aiohttp

from aiopybit.exceptions import ByBitAPIError, ByBitError, ByBitHTTPError
from aiopybit.protocols import ByBitResponse

logger = logging.getLogger('aiopybit')

# retCode returned when the request timestamp is outside recv_window.
_TIMESTAMP_RET_CODE = 10002
# retCodes returned when a rate limit is hit.
_RATE_LIMIT_RET_CODES = frozenset({10006, 10018})
_RATE_LIMIT_STATUSES = frozenset({403, 429})
_RATE_LIMIT_RESET_HEADER = 'X-Bapi-Limit-Reset-Timestamp'

# Sentinel returned by _interpret when the request should be retried.
_RETRY = object()


class ByBitHttpClient:
	"""Basic HTTP client for ByBit API."""

	def __init__(
		self,
		url: str,
		api_key: str,
		secret_key: str,
		max_retries: int = 3,
		retry_delay: float = 1.0,
		timeout: float = 10.0,
		recv_window: int = 5000,
		auto_time_sync: bool = True,
		rate_limit_max_wait: float = 5.0,
	):
		self.api_key = api_key
		self.secret_key = secret_key
		self.url = url
		self.recv_window = str(recv_window)
		self.max_retries = max_retries
		self.retry_delay = retry_delay
		self.timeout = aiohttp.ClientTimeout(total=timeout)
		self.auto_time_sync = auto_time_sync
		self.rate_limit_max_wait = rate_limit_max_wait
		self._session: aiohttp.ClientSession | None = None
		self._time_offset_ms = 0
		# RSA private keys are supplied in PEM form; HMAC secrets are not.
		self._is_rsa = '-----BEGIN' in secret_key

	def _get_session(self) -> aiohttp.ClientSession:
		"""Return the shared session, creating it lazily on first use.

		The session is created lazily so that it is bound to the running event
		loop rather than the loop that happened to be active at construction
		time.
		"""
		if self._session is None or self._session.closed:
			self._session = aiohttp.ClientSession(timeout=self.timeout)
		return self._session

	async def close(self) -> None:
		"""Close the underlying HTTP session, if it is open."""
		if self._session is not None and not self._session.closed:
			await self._session.close()
			self._session = None

	# -- Signing -----------------------------------------------------------

	def _timestamp(self) -> str:
		"""Current timestamp in milliseconds, adjusted by the synced offset."""
		return str(int(time.time() * 1000) + self._time_offset_ms)

	def _sign(self, param_str: str) -> str:
		"""Sign the pre-hash string with HMAC-SHA256 or RSA, per key type."""
		if self._is_rsa:
			return self._sign_rsa(param_str)
		return hmac.new(
			self.secret_key.encode('utf-8'),
			param_str.encode('utf-8'),
			hashlib.sha256,
		).hexdigest()

	def _sign_rsa(self, param_str: str) -> str:
		"""Sign with an RSA private key (PKCS#1 v1.5 + SHA256, base64)."""
		try:
			from cryptography.hazmat.primitives import hashes, serialization
			from cryptography.hazmat.primitives.asymmetric import padding
		except ImportError as exc:  # pragma: no cover - only without cryptography
			raise ByBitError(
				'RSA API keys require the cryptography package. '
				"Install it with: pip install 'aiopybit[rsa]'"
			) from exc

		private_key = serialization.load_pem_private_key(
			self.secret_key.encode('utf-8'), password=None
		)
		signature = private_key.sign(
			param_str.encode('utf-8'), padding.PKCS1v15(), hashes.SHA256()
		)
		return base64.b64encode(signature).decode('utf-8')

	def _generate_signature(self, timestamp: str, payload: str) -> str:
		"""Generate the request signature for the given timestamp.

		The same timestamp must be used both for the signature and for the
		``X-BAPI-TIMESTAMP`` header, otherwise ByBit rejects the request with
		an invalid-signature error.
		"""
		return self._sign(timestamp + self.api_key + self.recv_window + payload)

	def _get_headers(self, payload: str) -> dict:
		"""Build signed request headers using a single timestamp."""
		timestamp = self._timestamp()
		return {
			'X-BAPI-API-KEY': self.api_key,
			'X-BAPI-SIGN': self._generate_signature(timestamp, payload),
			'X-BAPI-SIGN-TYPE': '2',
			'X-BAPI-TIMESTAMP': timestamp,
			'X-BAPI-RECV-WINDOW': self.recv_window,
			'Content-Type': 'application/json',
		}

	# -- Time synchronisation ---------------------------------------------

	async def sync_time(self) -> int:
		"""Synchronise the local clock offset with the ByBit server.

		Returns the computed offset in milliseconds. Called automatically when
		a request fails with a timestamp error (retCode 10002) if
		``auto_time_sync`` is enabled.
		"""
		session = self._get_session()
		async with session.get(self.url + '/v5/market/time') as response:
			data = await response.json()

		server_ms = int(data.get('time') or 0)
		if not server_ms:
			result = data.get('result') or {}
			server_ms = int(float(result.get('timeSecond', 0)) * 1000)

		if server_ms:
			self._time_offset_ms = server_ms - int(time.time() * 1000)
			logger.info('Time synced with server; offset %d ms', self._time_offset_ms)
		return self._time_offset_ms

	# -- Rate limiting -----------------------------------------------------

	def _rate_limit_wait(
		self, reset_header: str | None, now_ms: int, attempt: int
	) -> float:
		"""Seconds to wait before retrying a rate-limited request.

		Prefers the ``X-Bapi-Limit-Reset-Timestamp`` header; falls back to
		exponential backoff. The result is clamped to ``rate_limit_max_wait``.
		"""
		if reset_header:
			try:
				wait = (int(reset_header) - now_ms) / 1000.0
			except ValueError:
				wait = self.retry_delay * (2**attempt)
		else:
			wait = self.retry_delay * (2**attempt)
		return max(0.0, min(wait, self.rate_limit_max_wait))

	# -- Requests ----------------------------------------------------------

	@staticmethod
	def _check_response(data: ByBitResponse) -> ByBitResponse:
		"""Validate a decoded ByBit response and raise on a non-zero retCode."""
		ret_code = data.get('retCode')
		if ret_code not in (0, None):
			raise ByBitAPIError(
				ret_code=ret_code,
				ret_msg=data.get('retMsg', ''),
				response=data,
			)
		return data

	async def _send(
		self,
		session: aiohttp.ClientSession,
		endpoint: str,
		method: str,
		payload: str,
	) -> tuple[int, dict, Mapping[str, str]]:
		"""Perform a single HTTP call and return (status, body, headers)."""
		if method == 'POST':
			async with session.post(
				self.url + endpoint,
				headers=self._get_headers(payload),
				data=payload,
			) as response:
				return response.status, await response.json(), response.headers
		url = self.url + endpoint
		if payload:
			url += '?' + payload
		async with session.get(url, headers=self._get_headers(payload)) as response:
			return response.status, await response.json(), response.headers

	async def _request(
		self,
		endpoint: str,
		method: str,
		payload: str = '',
		_resynced: bool = False,
	) -> ByBitResponse:
		"""Make an HTTP request with retries and resilience handling.

		- Transient connection/timeout errors are retried with exponential
		  backoff.
		- HTTP 429/403 and rate-limit retCodes wait for the reset window and
		  retry.
		- A timestamp error (retCode 10002) triggers a one-off clock resync and
		  a single retry when ``auto_time_sync`` is enabled.
		- Any other non-zero retCode raises :class:`ByBitAPIError`.
		"""
		last_exception: Exception | None = None
		session = self._get_session()

		for attempt in range(self.max_retries):
			try:
				status, data, headers = await self._send(
					session, endpoint, method, payload
				)
			except (aiohttp.ClientError, asyncio.TimeoutError) as e:
				last_exception = e
				await self._backoff(attempt, e)
				continue

			outcome = await self._interpret(
				status, data, headers, attempt, _resynced, endpoint, method, payload
			)
			if outcome is not _RETRY:
				return outcome

		if last_exception:
			raise last_exception
		raise RuntimeError('Request failed')

	async def _interpret(
		self, status, data, headers, attempt, resynced, endpoint, method, payload
	):
		"""Turn a raw response into a result, a retry signal, or an exception."""
		if status in _RATE_LIMIT_STATUSES:
			if attempt < self.max_retries - 1:
				await self._sleep_for_rate_limit(headers, attempt)
				return _RETRY
			raise ByBitHTTPError(status, str(data))

		if status >= 400:
			raise ByBitHTTPError(status, str(data))

		try:
			return self._check_response(data)
		except ByBitAPIError as exc:
			if (
				exc.ret_code == _TIMESTAMP_RET_CODE
				and self.auto_time_sync
				and not resynced
			):
				logger.warning('Timestamp rejected; resyncing clock')
				await self.sync_time()
				return await self._request(endpoint, method, payload, _resynced=True)
			if exc.ret_code in _RATE_LIMIT_RET_CODES and attempt < self.max_retries - 1:
				await self._sleep_for_rate_limit(headers, attempt)
				return _RETRY
			raise

	async def _backoff(self, attempt: int, error: Exception) -> None:
		"""Sleep with exponential backoff between transient-error retries."""
		if attempt < self.max_retries - 1:
			delay = self.retry_delay * (2**attempt)
			logger.warning(
				'Request failed (attempt %d/%d), retrying in %.2fs: %s',
				attempt + 1,
				self.max_retries,
				delay,
				str(error),
			)
			await asyncio.sleep(delay)
		else:
			logger.error('Request failed after %d attempts', self.max_retries)

	async def _sleep_for_rate_limit(self, headers, attempt: int) -> None:
		"""Sleep until the rate-limit window resets before retrying."""
		wait = self._rate_limit_wait(
			headers.get(_RATE_LIMIT_RESET_HEADER), int(time.time() * 1000), attempt
		)
		logger.warning('Rate limited; waiting %.2fs before retry', wait)
		await asyncio.sleep(wait)

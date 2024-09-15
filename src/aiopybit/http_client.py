"""HTTP client for ByBit REST API."""

import asyncio
import hashlib
import hmac
import logging
import time

import aiohttp

logger = logging.getLogger('aiopybit')


class ByBitHttpClient:
	"""Basic HTTP client for ByBit API."""

	def __init__(
		self,
		url: str,
		api_key: str,
		secret_key: str,
		max_retries: int = 3,
		retry_delay: float = 1.0,
	):
		self.api_key = api_key
		self.secret_key = secret_key
		self.url = url
		self.recv_window = '5000'
		self.max_retries = max_retries
		self.retry_delay = retry_delay

	@staticmethod
	def _timestamp() -> str:
		"""Get current timestamp in milliseconds."""
		return str(int(time.time() * 1000))

	def _generate_signature(self, timestamp: str, payload: str) -> str:
		"""Generate request signature for the given timestamp.

		The same timestamp must be used both for the signature and for the
		``X-BAPI-TIMESTAMP`` header, otherwise ByBit rejects the request with
		an invalid-signature error.
		"""
		param_str = timestamp + self.api_key + self.recv_window + payload
		hash_obj = hmac.new(
			bytes(self.secret_key, 'utf-8'),
			param_str.encode('utf-8'),
			hashlib.sha256,
		)
		return hash_obj.hexdigest()

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

	async def _request(self, endpoint: str, method: str, payload: str = '') -> dict:
		"""Make HTTP request with retry mechanism."""
		last_exception = None

		for attempt in range(self.max_retries):
			try:
				async with aiohttp.ClientSession() as session:
					if method == 'POST':
						async with session.post(
							self.url + endpoint,
							headers=self._get_headers(payload),
							data=payload,
						) as response:
							response.raise_for_status()
							return await response.json()
					else:
						url = self.url + endpoint
						if payload:
							url += '?' + payload

						async with session.get(url, headers=self._get_headers(payload)) as response:
							response.raise_for_status()
							return await response.json()

			except (aiohttp.ClientError, asyncio.TimeoutError) as e:
				last_exception = e
				if attempt < self.max_retries - 1:
					delay = self.retry_delay * (2**attempt)
					logger.warning(
						'Request failed (attempt %d/%d), retrying in %.2fs: %s',
						attempt + 1,
						self.max_retries,
						delay,
						str(e),
					)
					await asyncio.sleep(delay)
				else:
					logger.error('Request failed after %d attempts', self.max_retries)

		if last_exception:
			raise last_exception
		raise RuntimeError('Request failed')

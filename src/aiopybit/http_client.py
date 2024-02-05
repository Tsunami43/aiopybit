"""HTTP client for ByBit REST API."""

import hashlib
import hmac
import logging
import time

import aiohttp

logger = logging.getLogger('aiopybit')


class ByBitHttpClient:
	"""Basic HTTP client for ByBit API."""

	def __init__(self, url: str, api_key: str, secret_key: str):
		self.api_key = api_key
		self.secret_key = secret_key
		self.url = url
		self.recv_window = '5000'

	@property
	def time_stamp(self):
		"""Get current timestamp."""
		return str(int(time.time() * 1000))

	def _generate_signature(self, payload: str) -> str:
		"""Generate request signature."""
		param_str = self.time_stamp + self.api_key + self.recv_window + payload
		hash_obj = hmac.new(
			bytes(self.secret_key, 'utf-8'),
			param_str.encode('utf-8'),
			hashlib.sha256,
		)
		return hash_obj.hexdigest()

	def _get_headers(self, payload: str) -> dict:
		"""Build request headers."""
		return {
			'X-BAPI-API-KEY': self.api_key,
			'X-BAPI-SIGN': self._generate_signature(payload),
			'X-BAPI-SIGN-TYPE': '2',
			'X-BAPI-TIMESTAMP': self.time_stamp,
			'X-BAPI-RECV-WINDOW': self.recv_window,
			'Content-Type': 'application/json',
		}

	async def _request(self, endpoint: str, method: str, payload: str = '') -> dict:
		"""Make HTTP request."""
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

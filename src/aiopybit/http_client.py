import asyncio
import hashlib
import hmac
import logging
import time

import aiohttp

logger = logging.getLogger('aiopybit')


class ByBitHttpClient:
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

	@property
	def time_stamp(self):
		return str(int(time.time() * 1000))

	def __genSignature(self, payload: str):
		param_str = self.time_stamp + self.api_key + self.recv_window + payload
		hash = hmac.new(
			bytes(self.secret_key, 'utf-8'), param_str.encode('utf-8'), hashlib.sha256
		)
		signature = hash.hexdigest()
		return signature

	def headers(self, payload: str):
		return {
			'X-BAPI-API-KEY': self.api_key,
			'X-BAPI-SIGN': self.__genSignature(payload),
			'X-BAPI-SIGN-TYPE': '2',
			'X-BAPI-TIMESTAMP': self.time_stamp,
			'X-BAPI-RECV-WINDOW': self.recv_window,
			'Content-Type': 'application/json',
		}

	async def _request(self, endpoint: str, method: str, payload: str = '') -> dict:
		"""
		Make HTTP request with retry mechanism

		Args:
		    endpoint: API endpoint
		    method: HTTP method (GET, POST)
		    payload: Request payload

		Returns:
		    dict: Response JSON data

		Raises:
		    aiohttp.ClientError: After all retry attempts failed
		"""
		last_exception: Exception | None = None

		for attempt in range(self.max_retries + 1):
			try:
				async with aiohttp.ClientSession(
					timeout=aiohttp.ClientTimeout(total=30, connect=10)
				) as session:
					if method == 'POST':
						async with session.post(
							self.url + endpoint,
							headers=self.headers(payload),
							data=payload,
						) as response:
							response.raise_for_status()
							response_json = await response.json()
					else:
						# For GET requests, payload should be query parameters
						url = self.url + endpoint
						if payload:
							url += '?' + payload
						async with session.get(
							url, headers=self.headers(payload)
						) as response:
							response.raise_for_status()
							response_json = await response.json()

					logger.debug(
						'Response for endpoint(%s): %s', endpoint, response_json
					)
					return response_json

			except (
				aiohttp.ClientError,
				aiohttp.ServerTimeoutError,
				asyncio.TimeoutError,
			) as e:
				last_exception = e

				if attempt < self.max_retries:
					# Calculate exponential backoff delay
					delay = self.retry_delay * (2**attempt)
					logger.warning(
						'Request failed (attempt %d/%d), retrying in %.2f seconds: %s',
						attempt + 1,
						self.max_retries + 1,
						delay,
						str(e),
					)
					await asyncio.sleep(delay)
				else:
					logger.error(
						'Request failed after %d attempts: %s',
						self.max_retries + 1,
						str(e),
					)

			except Exception as e:
				# For non-retriable errors, fail immediately
				logger.error('Non-retriable error occurred: %s', str(e))
				raise

		# If we get here, all retries failed
		if last_exception:
			raise last_exception
		else:
			raise RuntimeError('Request failed for unknown reason')

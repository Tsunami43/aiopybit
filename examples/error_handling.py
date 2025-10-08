"""Example: Handling errors raised by the REST client."""

import asyncio

from aiopybit import (
	ByBitAPIError,
	ByBitClient,
	ByBitHTTPError,
)

API_KEY = ''
API_SECRET = ''
MODE = 'demo'


async def main():
	async with ByBitClient(API_KEY, API_SECRET, MODE) as client:
		try:
			# Intentionally use an invalid symbol to trigger an API error.
			await client.create_order(
				category='linear',
				symbol='NOTAREALPAIR',
				side='Buy',
				order_type='Market',
				qty=1,
			)
		except ByBitAPIError as exc:
			# Non-zero retCode: the request reached ByBit but was rejected.
			print(f'API rejected the request: [{exc.ret_code}] {exc.ret_msg}')
		except ByBitHTTPError as exc:
			# Transport-level failure (e.g. 4xx/5xx HTTP status).
			print(f'HTTP error: {exc.status}')


if __name__ == '__main__':
	asyncio.run(main())

"""Example: Stream real-time ticker data from ByBit."""

import asyncio

from aiopybit import ByBitClient

# Configuration
API_KEY = ''
API_SECRET = ''
MODE = 'demo'


async def handle_ticker(data):
	"""Handle ticker updates."""
	ticker = data.get('data', {})
	symbol = ticker.get('symbol', 'N/A')
	price = ticker.get('lastPrice', 'N/A')
	print(f'📊 {symbol}: ${price}')


async def main():
	"""Main function."""
	client = ByBitClient(API_KEY, API_SECRET, MODE)

	# Subscribe to tickers
	await client.ws.subscribe_to_ticker(
		category='spot', symbol='BTCUSDT', on_message=handle_ticker
	)
	await client.ws.subscribe_to_ticker(
		category='linear', symbol='ETHUSDT', on_message=handle_ticker
	)

	try:
		print('Streaming ticker data... Press Ctrl+C to stop')
		while True:
			await asyncio.sleep(1)
	except KeyboardInterrupt:
		print('\nStopping...')
	finally:
		await client.close()


if __name__ == '__main__':
	asyncio.run(main())

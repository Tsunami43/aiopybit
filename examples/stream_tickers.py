from aiopybit import ByBitClient

API_KEY = ''
API_SECRET = ''
MODE = 'demo'

client = ByBitClient(API_KEY, API_SECRET, MODE)


def on_ticker_liner(ticker):
	print('Ticker liner:', ticker)


def on_ticker_spot(ticker):
	print('Ticker spot:', ticker)


async def main():
	await client.ws.subscribe_to_ticker(
		category='spot', symbol='BTCUSDT', on_message=on_ticker_spot
	)
	await client.ws.subscribe_to_ticker(
		category='linear', symbol='ETHUSDT', on_message=on_ticker_liner
	)

	while True:
		await asyncio.sleep(1)


if __name__ == '__main__':
	import asyncio

	asyncio.run(main())

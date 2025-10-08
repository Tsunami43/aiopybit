"""Example: Stream private account data (orders, positions, wallet).

Requires API credentials with at least *Read* permission. Use the testnet or
demo environment while developing.
"""

import asyncio

from aiopybit import ByBitClient

API_KEY = ''
API_SECRET = ''
MODE = 'testnet'


async def handle_order(data):
	for order in data.get('data', []):
		print(f'📝 order {order.get("orderId")}: {order.get("orderStatus")}')


async def handle_position(data):
	for pos in data.get('data', []):
		print(
			f'📈 position {pos.get("symbol")}: size={pos.get("size")} pnl={pos.get("unrealisedPnl")}'
		)


async def handle_wallet(data):
	for wallet in data.get('data', []):
		print(f'💰 wallet equity: {wallet.get("totalEquity")}')


async def main():
	async with ByBitClient(API_KEY, API_SECRET, MODE) as client:
		await client.ws.subscribe_to_order(handle_order)
		await client.ws.subscribe_to_position(handle_position)
		await client.ws.subscribe_to_wallet(handle_wallet)

		print('Streaming private data... Press Ctrl+C to stop')
		try:
			while True:
				await asyncio.sleep(1)
		except KeyboardInterrupt:
			print('\nStopping...')


if __name__ == '__main__':
	asyncio.run(main())

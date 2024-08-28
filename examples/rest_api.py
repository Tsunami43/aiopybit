"""Example: Using ByBit REST API for trading operations."""

import asyncio

from aiopybit import ByBitClient

# Configuration
API_KEY = ''
API_SECRET = ''
MODE = 'demo'


async def main():
	"""Demonstrate various REST API operations."""
	client = ByBitClient(API_KEY, API_SECRET, MODE)

	try:
		# Get account balance
		print('\n📊 Getting account info...')
		balance = await client.get_wallet_balance('UNIFIED')
		print(f'Balance: {balance}')

		# Get market data
		print('\n📈 Getting ticker data...')
		ticker = await client.get_tickers('linear', 'BTCUSDT')
		print(f'Ticker: {ticker}')

		# Get orderbook
		print('\n📚 Getting orderbook...')
		orderbook = await client.get_orderbook('linear', 'BTCUSDT', limit=10)
		print(f'Orderbook: {orderbook}')

		# Get positions
		print('\n💼 Getting positions...')
		positions = await client.get_positions('linear', 'BTCUSDT')
		print(f'Positions: {positions}')

		# Set leverage
		print('\n⚙️ Setting leverage...')
		result = await client.set_leverage('linear', 'BTCUSDT', 10)
		print(f'Leverage set: {result}')

	finally:
		await client.close()
		print('\n✅ Done!')


if __name__ == '__main__':
	asyncio.run(main())

"""Example: Generate a shareable Bybit-style trading card.

Requires the optional ``cards`` extra:

    pip install "aiopybit[cards]"

You can also build the card straight from a live position fetched over REST.
"""

import asyncio

from aiopybit import ByBitClient
from aiopybit.cards import BybitCardGenerator

API_KEY = ''
API_SECRET = ''
MODE = 'demo'


def static_example() -> None:
	"""Render a card from explicit values."""
	generator = BybitCardGenerator()
	path = generator.save_card(
		symbol='BTCUSDT',
		direction='Long',
		leverage=100,
		entry_price=20000,
		market_price=41850.5,
		output_path='card_example.png',
	)
	print(f'Saved {path}')


async def from_live_position() -> None:
	"""Render a card from the first open position on the account."""
	generator = BybitCardGenerator()
	async with ByBitClient(API_KEY, API_SECRET, MODE) as client:
		ticker = await client.get_tickers('linear', 'BTCUSDT')
		market_price = float(ticker['result']['list'][0]['lastPrice'])

		positions = await client.get_positions('linear', 'BTCUSDT')
		pos = positions['result']['list'][0]

		image_bytes = generator.get_card_bytes(
			symbol=pos['symbol'],
			direction='Long' if pos['side'] == 'Buy' else 'Short',
			leverage=float(pos['leverage']),
			entry_price=float(pos['avgPrice']),
			market_price=market_price,
		)
		# image_bytes can be sent straight to a Telegram/Discord bot.
		print(f'Generated {len(image_bytes)} bytes')


if __name__ == '__main__':
	static_example()
	# Render from a live position instead when credentials are provided:
	if API_KEY and API_SECRET:
		asyncio.run(from_live_position())

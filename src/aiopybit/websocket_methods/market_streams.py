import logging
from collections.abc import Callable
from typing import Literal

from aiopybit.protocols import (
	ByBitSWebSocketManagerProtocol,
	ChannelCategories,
	KlineInterval,
	OrderbookDepth,
)

logger = logging.getLogger('aiopybit')


class ByBitPublicStreamsMixin:
	async def subscribe_to_ticker(
		self: ByBitSWebSocketManagerProtocol,
		category: ChannelCategories,
		symbol: str,
		on_message: Callable,
	) -> str:
		"""
		Subscribe to live ticker updates for the specified trading symbol.

		This method sends a subscription request to receive real-time updates
		about the ticker (such as price, volume, etc.) for the given symbol.

		Args:
		    symbol (str): Trading pair symbol (e.g., 'BTCUSDT').

		Example:
		    >>> await client.subscribe_to_ticker('BTCUSDT')
		"""
		websocket = await self.get_websocket('public.' + category)
		topic = f'tickers.{symbol}'
		websocket.topic_handlers[topic] = on_message
		try:
			await websocket.send(op='subscribe', args=[topic])
		except Exception:
			del websocket.topic_handlers[topic]
			raise

		return topic

	async def subscribe_to_orderbook(
		self: ByBitSWebSocketManagerProtocol,
		category: ChannelCategories,
		symbol: str,
		on_message: Callable,
		depth: OrderbookDepth,
	) -> str:
		"""
		Subscribe to live orderbook updates for the specified trading symbol.

		Depths
		Linear & inverse:
		Level 1 data, push frequency: 10ms
		Level 50 data, push frequency: 20ms
		Level 200 data, push frequency: 100ms
		Level 500 data, push frequency: 100ms (2025.09.11 offline)
		Level 1000 data, push frequency: 300ms (2025.08.14 online)

		Spot:
		Level 1 data, push frequency: 10ms
		Level 50 data, push frequency: 20ms
		Level 200 data, push frequency: 200ms
		Level 1000 data, push frequency: 300ms (2025.08.14 online)

		Option:
		Level 25 data, push frequency: 20ms
		Level 100 data, push frequency: 100ms

		Args:
		    symbol (str): Trading pair symbol (e.g., 'BTCUSDT').
		    on_message (Callable): Callback function to handle incoming data.

		Example:
		    >>> await client.subscribe_to_orderbook('BTCUSDT', my_handler)
		"""
		websocket = await self.get_websocket('public.' + category)
		topic = f'orderbook.{depth}.{symbol}'
		websocket.topic_handlers[topic] = on_message
		try:
			await websocket.send(op='subscribe', args=[topic])
		except Exception:
			del websocket.topic_handlers[topic]
			raise

		return topic

	async def subscribe_to_public_trades(
		self: ByBitSWebSocketManagerProtocol,
		category: ChannelCategories,
		symbol: str,
		on_message: Callable,
	) -> str:
		"""
		Subscribe to live public trade updates for the specified trading symbol.

		Args:
		    symbol (str): Trading pair symbol (e.g., 'BTCUSDT').
		    on_message (Callable): Callback function to handle incoming data.

		Example:
		    >>> await client.subscribe_to_public_trades('BTCUSDT', my_handler)
		"""
		websocket = await self.get_websocket('public.' + category)
		topic = f'publicTrade.{symbol}'
		websocket.topic_handlers[topic] = on_message
		try:
			await websocket.send(op='subscribe', args=[topic])
		except Exception:
			del websocket.topic_handlers[topic]
			raise

		return topic

	async def subscribe_to_kline(
		self: ByBitSWebSocketManagerProtocol,
		category: ChannelCategories,
		symbol: str,
		interval: KlineInterval,
		on_message: Callable,
	) -> str:
		"""
		Subscribe to live kline/candlestick updates for the specified trading symbol.

		Args:
		    symbol (str): Trading pair symbol (e.g., 'BTCUSDT').
		    interval (KlineInterval): Kline interval (e.g., '1', '5', '15', 'D').
		    on_message (Callable): Callback function to handle incoming data.

		Example:
		    >>> await client.subscribe_to_kline('BTCUSDT', '1', my_handler)
		"""
		websocket = await self.get_websocket('public.' + category)
		topic = f'kline.{interval}.{symbol}'
		websocket.topic_handlers[topic] = on_message
		try:
			await websocket.send(op='subscribe', args=[topic])
		except Exception:
			del websocket.topic_handlers[topic]
			raise

		return topic

	async def subscribe_to_liquidations(
		self: ByBitSWebSocketManagerProtocol,
		category: Literal['linear', 'inverse'],
		symbol: str,
		on_message: Callable,
	) -> str:
		"""
		Subscribe to liquidation updates for the specified trading symbol.

		Args:
		    symbol (str): Trading pair symbol (e.g., 'BTCUSDT').
		    on_message (Callable): Callback function to handle incoming data.

		Example:
		    >>> await client.subscribe_to_liquidations('BTCUSDT', my_handler)
		"""
		websocket = await self.get_websocket('public.' + category)
		topic = f'liquidation.{symbol}'
		websocket.topic_handlers[topic] = on_message
		try:
			await websocket.send(op='subscribe', args=[topic])
		except Exception:
			del websocket.topic_handlers[topic]
			raise

		return topic

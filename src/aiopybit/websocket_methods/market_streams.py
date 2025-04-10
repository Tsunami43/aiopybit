"""Public market data stream subscriptions."""

import logging

from aiopybit.protocols import (
	ByBitCategories,
	KlineInterval,
	OrderbookDepth,
	StreamHandler,
)

logger = logging.getLogger('aiopybit')


class ByBitPublicStreamsMixin:
	"""Mixin for public market data subscriptions."""

	async def subscribe_to_ticker(
		self,
		category: ByBitCategories,
		symbol: str,
		on_message: StreamHandler,
	) -> str:
		"""Subscribe to ticker updates."""
		websocket = await self.get_websocket('public.' + category)
		topic = f'tickers.{symbol}'
		websocket.topic_handlers[topic] = on_message

		try:
			await websocket.send(op='subscribe', args=[topic])
			logger.info('Subscribed to %s', topic)
		except Exception:
			del websocket.topic_handlers[topic]
			raise

		return topic

	async def subscribe_to_orderbook(
		self,
		category: ByBitCategories,
		symbol: str,
		on_message: StreamHandler,
		depth: OrderbookDepth = 50,
	) -> str:
		"""Subscribe to orderbook updates."""
		websocket = await self.get_websocket('public.' + category)
		topic = f'orderbook.{depth}.{symbol}'
		websocket.topic_handlers[topic] = on_message

		try:
			await websocket.send(op='subscribe', args=[topic])
			logger.info('Subscribed to %s', topic)
		except Exception:
			del websocket.topic_handlers[topic]
			raise

		return topic

	async def subscribe_to_public_trades(
		self,
		category: ByBitCategories,
		symbol: str,
		on_message: StreamHandler,
	) -> str:
		"""Subscribe to public trades."""
		websocket = await self.get_websocket('public.' + category)
		topic = f'publicTrade.{symbol}'
		websocket.topic_handlers[topic] = on_message

		try:
			await websocket.send(op='subscribe', args=[topic])
			logger.info('Subscribed to %s', topic)
		except Exception:
			del websocket.topic_handlers[topic]
			raise

		return topic

	async def subscribe_to_kline(
		self,
		category: ByBitCategories,
		symbol: str,
		interval: KlineInterval,
		on_message: StreamHandler,
	) -> str:
		"""Subscribe to kline/candlestick updates."""
		websocket = await self.get_websocket('public.' + category)
		topic = f'kline.{interval}.{symbol}'
		websocket.topic_handlers[topic] = on_message

		try:
			await websocket.send(op='subscribe', args=[topic])
			logger.info('Subscribed to %s', topic)
		except Exception:
			del websocket.topic_handlers[topic]
			raise

		return topic

	async def subscribe_to_liquidations(
		self,
		category: ByBitCategories,
		symbol: str,
		on_message: StreamHandler,
	) -> str:
		"""Subscribe to liquidation updates."""
		websocket = await self.get_websocket('public.' + category)
		topic = f'liquidation.{symbol}'
		websocket.topic_handlers[topic] = on_message

		try:
			await websocket.send(op='subscribe', args=[topic])
			logger.info('Subscribed to %s', topic)
		except Exception:
			del websocket.topic_handlers[topic]
			raise

		return topic

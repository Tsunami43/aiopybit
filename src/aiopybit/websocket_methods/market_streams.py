"""Public market data stream subscriptions."""

import logging
from collections.abc import Callable

logger = logging.getLogger('aiopybit')


class ByBitPublicStreamsMixin:
	"""Mixin for public market data subscriptions."""

	async def subscribe_to_ticker(
		self,
		category: str,
		symbol: str,
		on_message: Callable,
	) -> str:
		"""Subscribe to ticker updates."""
		websocket = await self.get_websocket('public.' + category)
		topic = f'tickers.{symbol}'
		websocket.topic_handlers[topic] = on_message

		await websocket.send(op='subscribe', args=[topic])
		logger.info('Subscribed to %s', topic)

		return topic

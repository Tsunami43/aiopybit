"""Private account data stream subscriptions."""

import logging
from collections.abc import Callable

logger = logging.getLogger('aiopybit')


class ByBitPrivateStreamsMixin:
	"""Mixin for private account data subscriptions."""

	async def subscribe_to_order(self, on_message: Callable) -> str:
		"""Subscribe to order updates."""
		websocket = await self.get_websocket('private')
		topic = 'order'
		websocket.topic_handlers[topic] = on_message

		await websocket.send(op='subscribe', args=[topic])
		logger.info('Subscribed to %s', topic)

		return topic

	async def subscribe_to_position(self, on_message: Callable) -> str:
		"""Subscribe to position updates."""
		websocket = await self.get_websocket('private')
		topic = 'position'
		websocket.topic_handlers[topic] = on_message

		await websocket.send(op='subscribe', args=[topic])
		logger.info('Subscribed to %s', topic)

		return topic

	async def subscribe_to_execution(self, on_message: Callable) -> str:
		"""Subscribe to execution updates."""
		websocket = await self.get_websocket('private')
		topic = 'execution'
		websocket.topic_handlers[topic] = on_message

		await websocket.send(op='subscribe', args=[topic])
		logger.info('Subscribed to %s', topic)

		return topic

	async def subscribe_to_wallet(self, on_message: Callable) -> str:
		"""Subscribe to wallet balance updates."""
		websocket = await self.get_websocket('private')
		topic = 'wallet'
		websocket.topic_handlers[topic] = on_message

		await websocket.send(op='subscribe', args=[topic])
		logger.info('Subscribed to %s', topic)

		return topic

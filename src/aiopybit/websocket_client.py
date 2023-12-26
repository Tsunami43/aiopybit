import asyncio
import json
import logging
from typing import Any, Callable

import websockets
from websockets.exceptions import ConnectionClosed

logger = logging.getLogger('aiopybit')


class ByBitWebSocketClient:
	"""Basic WebSocket client for ByBit API."""

	def __init__(self, url: str):
		self.url = url
		self.ws = None
		self.is_connected = False
		self.topic_handlers: dict[str, Callable] = {}

	async def connect(self) -> None:
		"""Establish WebSocket connection."""
		try:
			self.ws = await websockets.connect(self.url)
			self.is_connected = True
			logger.info('WebSocket connected to %s', self.url)
		except Exception as e:
			logger.error('Failed to connect: %s', e)
			raise

	async def send(self, **kwargs) -> None:
		"""Send message through WebSocket."""
		if not self.ws or not self.is_connected:
			raise ConnectionError('WebSocket not connected')

		message = json.dumps(kwargs)
		await self.ws.send(message)
		logger.debug('Sent message: %s', message)

	async def _message_listener(self) -> None:
		"""Listen for incoming messages."""
		while self.is_connected and self.ws:
			try:
				message = await self.ws.recv()
				data = json.loads(message)
				await self._handle_message(data)
			except ConnectionClosed:
				logger.warning('Connection closed')
				self.is_connected = False
				break
			except Exception as e:
				logger.error('Error in listener: %s', e)

	async def _handle_message(self, data: dict[str, Any]) -> None:
		"""Handle incoming WebSocket messages."""
		if 'topic' in data:
			topic = data.get('topic')
			if topic in self.topic_handlers:
				handler = self.topic_handlers[topic]
				try:
					if asyncio.iscoroutinefunction(handler):
						await handler(data)
					else:
						handler(data)
				except Exception as e:
					logger.error('Error in handler: %s', e)

	async def close(self) -> None:
		"""Close WebSocket connection."""
		self.is_connected = False
		if self.ws:
			await self.ws.close()
		logger.info('WebSocket closed')

import asyncio
import json
import logging
from typing import Any, Callable

import websockets
from websockets.exceptions import ConnectionClosed

logger = logging.getLogger('aiopybit')


class ByBitWebSocketClient:
	"""Basic WebSocket client for ByBit API."""

	def __init__(self, url: str, ping_interval: int = 20):
		self.url = url
		self.ws = None
		self.is_connected = False
		self.ping_interval = ping_interval
		self.topic_handlers: dict[str, Callable] = {}
		self.ping_task: asyncio.Task | None = None
		self.listen_task: asyncio.Task | None = None

	async def connect(self) -> None:
		"""Establish WebSocket connection."""
		try:
			self.ws = await websockets.connect(self.url)
			self.is_connected = True
			logger.info('WebSocket connected to %s', self.url)

			self.ping_task = asyncio.create_task(self._ping_handler())
			self.listen_task = asyncio.create_task(self._message_listener())
		except Exception as e:
			logger.error('Failed to connect: %s', e)
			raise

	async def _ping_handler(self) -> None:
		"""Handle periodic ping messages."""
		while self.is_connected:
			try:
				await self.send(op='ping')
				await asyncio.sleep(self.ping_interval)
			except ConnectionClosed:
				logger.warning('Connection closed during ping')
				self.is_connected = False
				break
			except Exception as e:
				logger.error('Error during ping: %s', e)
				break

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
		op = data.get('op')

		# Handle pong
		if op == 'pong':
			logger.debug('Received pong')
			return

		# Handle topic messages
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

		# Cancel tasks
		if self.ping_task and not self.ping_task.done():
			self.ping_task.cancel()
			try:
				await self.ping_task
			except asyncio.CancelledError:
				pass

		if self.listen_task and not self.listen_task.done():
			self.listen_task.cancel()
			try:
				await self.listen_task
			except asyncio.CancelledError:
				pass

		# Close connection
		if self.ws:
			await self.ws.close()

		logger.info('WebSocket closed')

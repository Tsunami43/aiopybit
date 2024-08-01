import asyncio
import hmac
import json
import logging
import time
from typing import Any, Callable

import websockets
from websockets.exceptions import ConnectionClosed

logger = logging.getLogger('aiopybit')


class ByBitWebSocketClient:
	"""Basic WebSocket client for ByBit API."""

	def __init__(
		self,
		url: str,
		api_key: str | None = None,
		api_secret: str | None = None,
		ping_interval: int = 20,
		auto_reconnect: bool = True,
	):
		self.url = url
		self.api_key = api_key
		self.api_secret = api_secret
		self.ws = None
		self.is_connected = False
		self.ping_interval = ping_interval
		self.auto_reconnect = auto_reconnect
		self.topic_handlers: dict[str, Callable] = {}
		self.ping_task: asyncio.Task | None = None
		self.listen_task: asyncio.Task | None = None
		self.reconnect_task: asyncio.Task | None = None
		self.is_reconnecting = False

	def _generate_signature(self, expires: int) -> str:
		"""Generate authentication signature."""
		if not self.api_secret:
			raise ValueError('API secret required')

		return hmac.new(
			bytes(self.api_secret, 'utf-8'),
			bytes(f'GET/realtime{expires}', 'utf-8'),
			digestmod='sha256',
		).hexdigest()

	async def _authenticate(self) -> None:
		"""Authenticate for private channels."""
		if not self.api_key or not self.api_secret:
			raise ValueError('API credentials required')

		expires = int((time.time() + 1) * 1000)
		signature = self._generate_signature(expires)

		await self.send(op='auth', args=[self.api_key, expires, signature])

		assert self.ws
		response = await self.ws.recv()
		auth_result = json.loads(response)

		if not auth_result.get('success'):
			raise ConnectionError('Authentication failed')

		logger.info('Authentication successful')

	async def connect(self) -> None:
		"""Establish WebSocket connection."""
		try:
			self.ws = await websockets.connect(self.url)
			self.is_connected = True
			logger.info('WebSocket connected to %s', self.url)

			# Authenticate if credentials provided
			if self.api_key and self.api_secret:
				await self._authenticate()

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
				if self.auto_reconnect and not self.is_reconnecting:
					self.reconnect_task = asyncio.create_task(self._reconnect())
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
				if self.auto_reconnect and not self.is_reconnecting:
					self.reconnect_task = asyncio.create_task(self._reconnect())
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

		# Handle subscription confirmation
		if op == 'subscribe':
			if data.get('success'):
				logger.info('Successfully subscribed')
			else:
				logger.error('Subscription failed: %s', data)
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

	async def _reconnect(self) -> None:
		"""Attempt to reconnect to WebSocket."""
		if self.is_reconnecting:
			return

		self.is_reconnecting = True
		logger.info('Attempting to reconnect...')

		try:
			# Wait before reconnecting
			await asyncio.sleep(2)

			# Clean up old connection
			if self.ws:
				try:
					await self.ws.close()
				except Exception:
					pass

			# Reconnect
			await self.connect()

			# Restore subscriptions
			if self.topic_handlers:
				topics = list(self.topic_handlers.keys())
				logger.info('Restoring subscriptions: %s', topics)
				await self.send(op='subscribe', args=topics)

			logger.info('Reconnection successful')
			self.is_reconnecting = False

		except Exception as e:
			logger.error('Reconnection failed: %s', e)
			self.is_reconnecting = False

	async def close(self) -> None:
		"""Close WebSocket connection."""
		self.is_connected = False
		self.is_reconnecting = False

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

		if self.reconnect_task and not self.reconnect_task.done():
			self.reconnect_task.cancel()
			try:
				await self.reconnect_task
			except asyncio.CancelledError:
				pass

		# Close connection
		if self.ws:
			await self.ws.close()

		logger.info('WebSocket closed')

	async def unsubscribe(self, topic: str) -> bool:
		"""Unsubscribe from a topic."""
		if topic not in self.topic_handlers:
			return False

		try:
			await self.send(op='unsubscribe', args=[topic])
			del self.topic_handlers[topic]
			logger.info('Unsubscribed from %s', topic)
			return True
		except Exception as e:
			logger.error('Failed to unsubscribe from %s: %s', topic, e)
			return False

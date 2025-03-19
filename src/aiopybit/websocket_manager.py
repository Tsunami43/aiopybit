"""WebSocket connection manager for ByBit API."""

import logging

from aiopybit.protocols import ByBitModes
from aiopybit.websocket_client import ByBitWebSocketClient
from aiopybit.websocket_methods.market_streams import ByBitPublicStreamsMixin
from aiopybit.websocket_methods.private_streams import ByBitPrivateStreamsMixin

logger = logging.getLogger('aiopybit')


class ByBitWebSocketManager(ByBitPublicStreamsMixin, ByBitPrivateStreamsMixin):
	"""Manager for WebSocket connections."""

	WSS_URLS = {
		'mainnet': {
			'public': {
				'linear': 'wss://stream.bybit.com/v5/public/linear',
				'inverse': 'wss://stream.bybit.com/v5/public/inverse',
				'spot': 'wss://stream.bybit.com/v5/public/spot',
				'option': 'wss://stream.bybit.com/v5/public/option',
			},
			'private': 'wss://stream.bybit.com/v5/private',
		},
		'testnet': {
			'public': {
				'linear': 'wss://stream-testnet.bybit.com/v5/public/linear',
				'inverse': 'wss://stream-testnet.bybit.com/v5/public/inverse',
				'spot': 'wss://stream-testnet.bybit.com/v5/public/spot',
				'option': 'wss://stream-testnet.bybit.com/v5/public/option',
			},
			'private': 'wss://stream-testnet.bybit.com/v5/private',
		},
		'demo': {
			'public': {
				'linear': 'wss://stream-demo.bybit.com/v5/public/linear',
				'spot': 'wss://stream-demo.bybit.com/v5/public/spot',
			},
			'private': 'wss://stream-demo.bybit.com/v5/private',
		},
	}

	def __init__(
		self,
		mode: ByBitModes,
		api_key: str = '',
		api_secret: str = '',
		ping_interval: int = 20,
	):
		self.mode = mode
		self.api_key = api_key
		self.api_secret = api_secret
		self.ping_interval = ping_interval
		self.connections: dict[str, ByBitWebSocketClient] = {}

	async def get_websocket(self, channel_type: str) -> ByBitWebSocketClient:
		"""Get or create WebSocket connection."""
		if channel_type in self.connections:
			return self.connections[channel_type]

		# Parse channel type
		if '.' in channel_type:
			channel, category = channel_type.split('.')
			url = self.WSS_URLS[self.mode][channel][category]
			websocket = ByBitWebSocketClient(url=url, ping_interval=self.ping_interval)
		else:
			# Private channel
			url = self.WSS_URLS[self.mode][channel_type]
			websocket = ByBitWebSocketClient(
				url=url,
				api_key=self.api_key,
				api_secret=self.api_secret,
				ping_interval=self.ping_interval,
			)

		await websocket.connect()
		self.connections[channel_type] = websocket
		return websocket

	async def unsubscribe(self, topic: str) -> bool:
		"""Unsubscribe from ``topic`` across all managed connections.

		Returns ``True`` if a connection was subscribed to the topic and the
		unsubscribe request was sent, ``False`` otherwise.
		"""
		for websocket in self.connections.values():
			if topic in websocket.topic_handlers:
				return await websocket.unsubscribe(topic)
		return False

	async def close_all(self):
		"""Close all WebSocket connections."""
		for websocket in self.connections.values():
			await websocket.close()
		self.connections.clear()

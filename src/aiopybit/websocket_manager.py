import logging

from aiopybit.protocols import (
	ByBitModes,
)
from aiopybit.websocket_client import ByBitWebSocketClient
from aiopybit.websocket_methods.market_streams import (
	ByBitPublicStreamsMixin,
)
from aiopybit.websocket_methods.private_streams import (
	ByBitPrivateStreamsMixin,
)

logger = logging.getLogger('aiopybit')


class ByBitWebSocketManager(ByBitPublicStreamsMixin, ByBitPrivateStreamsMixin):
	"""
	ByBit WebSocket client for real-time data streams

	Supports both public (market data) and private (account/order) streams.
	Features automatic reconnection, heartbeat, and subscription management.
	"""

	WSS_URLS = {
		'mainnet': {
			'public': {
				'linear': 'wss://stream.bybit.com/v5/public/linear',
				'spot': 'wss://stream.bybit.com/v5/public/spot',
				'option': 'wss://stream.bybit.com/v5/public/option',
			},
			'private': 'wss://stream.bybit.com/v5/private',
			'trade': 'wss://stream.bybit.com/v5/trade',
		},
		'demo': {
			'private': 'wss://stream-demo.bybit.com/v5/private',
		},
		'testnet': {
			'public': {
				'linear': 'wss://stream-testnet.bybit.com/v5/public/linear',
				'spot': 'wss://stream-testnet.bybit.com/v5/public/spot',
				'option': 'wss://stream-testnet.bybit.com/v5/public/option',
			},
			'private': 'wss://stream-testnet.bybit.com/v5/private',
			'trade': 'wss://stream-testnet.bybit.com/v5/trade',
		},
	}

	def __init__(
		self,
		mode: ByBitModes,
		api_key: str,
		api_secret: str,
		ping_interval: int = 20,
		ping_timeout: int = 10,
		auto_reconnect: bool = True,
	):
		self.mode = mode
		self.api_key = api_key
		self.api_secret = api_secret
		self.ping_interval = ping_interval
		self.ping_timeout = ping_timeout
		self.auto_reconnect = auto_reconnect
		self.connections: dict[str, ByBitWebSocketClient] = {}

	async def get_websocket(self, channel_type: str) -> ByBitWebSocketClient:
		websocket = self.connections.get(channel_type)
		if websocket is None:
			channel_type, category = channel_type.split('.')

			if channel_type == 'public':
				if category is None:
					raise ValueError(
						f'Invalid category for public channel: {channel_type}'
					)

				if self.mode == 'demo':
					url = self.WSS_URLS['mainnet']['public'][category]
				else:
					url = self.WSS_URLS[self.mode]['public'][category]

			else:
				if channel_type not in ['private', 'trade']:
					raise ValueError(f'Invalid channel type: {channel_type}')
				url = self.WSS_URLS[self.mode][channel_type]

			websocket = ByBitWebSocketClient(
				url=url,
				api_secret=self.api_secret,
				api_key=self.api_key,
				ping_interval=self.ping_interval,
				ping_timeout=self.ping_timeout,
				auto_reconnect=self.auto_reconnect,
			)
			self.connections[channel_type] = websocket

		if not websocket.is_connected:
			await websocket.connect()

		return websocket

	async def close_all(self):
		for websocket in self.connections.values():
			await websocket.close()

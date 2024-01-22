"""WebSocket connection manager for ByBit API."""

import logging

from aiopybit.protocols import ByBitModes
from aiopybit.websocket_client import ByBitWebSocketClient
from aiopybit.websocket_methods.market_streams import ByBitPublicStreamsMixin

logger = logging.getLogger('aiopybit')


class ByBitWebSocketManager(ByBitPublicStreamsMixin):
	"""Manager for WebSocket connections."""

	WSS_URLS = {
		'mainnet': {
			'public': {
				'linear': 'wss://stream.bybit.com/v5/public/linear',
				'spot': 'wss://stream.bybit.com/v5/public/spot',
			},
		},
		'testnet': {
			'public': {
				'linear': 'wss://stream-testnet.bybit.com/v5/public/linear',
				'spot': 'wss://stream-testnet.bybit.com/v5/public/spot',
			},
		},
	}

	def __init__(self, mode: ByBitModes, ping_interval: int = 20):
		self.mode = mode
		self.ping_interval = ping_interval
		self.connections: dict[str, ByBitWebSocketClient] = {}

	async def get_websocket(self, channel_type: str) -> ByBitWebSocketClient:
		"""Get or create WebSocket connection."""
		if channel_type in self.connections:
			return self.connections[channel_type]

		# Parse channel type
		channel, category = channel_type.split('.')
		url = self.WSS_URLS[self.mode][channel][category]

		websocket = ByBitWebSocketClient(url=url, ping_interval=self.ping_interval)
		await websocket.connect()

		self.connections[channel_type] = websocket
		return websocket

	async def close_all(self):
		"""Close all WebSocket connections."""
		for websocket in self.connections.values():
			await websocket.close()

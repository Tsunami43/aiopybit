"""Main ByBit client class."""

import logging

from aiopybit.http_client import ByBitHttpClient
from aiopybit.http_methods.account_methods import AccountMixin
from aiopybit.http_methods.market_methods import MarketMixin
from aiopybit.http_methods.order_methods import OrderMixin
from aiopybit.http_methods.position_methods import PositionMixin
from aiopybit.protocols import ByBitModes
from aiopybit.websocket_manager import ByBitWebSocketManager

logger = logging.getLogger('aiopybit')


class ByBitClient(
	ByBitHttpClient,
	AccountMixin,
	OrderMixin,
	MarketMixin,
	PositionMixin,
):
	"""ByBit Trading API Client."""

	BASE_URL = {
		'mainnet': 'https://api.bybit.com',
		'testnet': 'https://api-testnet.bybit.com',
		'demo': 'https://api-demo.bybit.com',
	}

	def __init__(
		self,
		api_key: str,
		secret_key: str,
		mode: ByBitModes,
	):
		self.mode = mode

		super().__init__(
			url=self.BASE_URL[mode], api_key=api_key, secret_key=secret_key
		)

		self.ws = ByBitWebSocketManager(
			mode=mode,
			api_key=api_key,
			api_secret=secret_key,
			ping_interval=20,
		)

	async def __aenter__(self) -> 'ByBitClient':
		return self

	async def __aexit__(self, exc_type, exc, tb) -> None:
		await self.close()

	async def close(self):
		"""Close all HTTP and WebSocket connections."""
		await self.ws.close_all()
		await super().close()

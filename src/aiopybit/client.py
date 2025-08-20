import logging

from aiopybit.http_client import ByBitHttpClient
from aiopybit.http_methods import (
	AccountMixin,
	MarketMixin,
	OrderMixin,
	PositionMixin,
)
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
	"""
	ByBit Trading API Client with Mixin Architecture

	A comprehensive client for interacting with ByBit's trading API.
	Supports futures, spot, and options trading across mainnet, demo, and testnet environments.

	This client uses a mixin-based architecture for better code organization:
	- AccountMixin: Account and wallet methods
	- OrderMixin: Order management methods
	- MarketMixin: Market data methods
	- PositionMixin: Position management methods

	Features:
	    - Account management and wallet balance queries
	    - Order creation, modification, cancellation
	    - Leverage and position management
	    - Market data retrieval (tickers, orderbook, klines)
	    - Trading stops and risk management
	    - Support for all ByBit product categories (linear, inverse, option, spot)

	Example:
	    # Create client
	    client = ByBitClient(
	        api_key='your_api_key',
	        secret_key='your_secret',
	        mode='demo'
	    )

	    # HTTP API usage
	    balance = await client.get_account_info(account_type='CONTRACT')
	    order = await client.create_order(
	        category='linear',
	        symbol='TONUSDT',
	        side='Buy',
	        order_type='Market',
	        qty=10
	    )
	"""

	BASE_URL = {
		'mainnet': 'https://api.bybit.com',
		'demo': 'https://api-demo.bybit.com',
		'testnet': 'https://api-testnet.bybit.com',
	}

	def __init__(
		self,
		api_key: str,
		secret_key: str,
		mode: ByBitModes,
		max_retries: int = 3,
		retry_delay: float = 1.0,
		websocket_auto_reconnect: bool = True,
		websocket_ping_interval: int = 20,
		websocket_ping_timeout: int = 10,
	):
		"""
		Initialize ByBit API client

		Args:
		    api_key: Your ByBit API key
		    secret_key: Your ByBit API secret
		    mode: Trading environment ('mainnet', 'demo', 'testnet')
		    max_retries: Maximum number of retry attempts for failed requests
		    retry_delay: Base delay between retries in seconds (uses exponential backoff)

		Example:
		    client = ByBitClient(
		        api_key='your_api_key',
		        secret_key='your_secret',
		        mode='demo',
		        max_retries=3,
		        retry_delay=1.0
		    )
		"""
		self.mode: ByBitModes = mode
		self.api_key = api_key
		self.secret_key = secret_key

		super().__init__(
			url=self.BASE_URL[mode],
			api_key=api_key,
			secret_key=secret_key,
			max_retries=max_retries,
			retry_delay=retry_delay,
		)
		logger.debug('%s', self.__repr__())

		self.ws = ByBitWebSocketManager(
			mode=mode,
			api_key=api_key,
			api_secret=secret_key,
			ping_interval=websocket_ping_interval,
			ping_timeout=websocket_ping_timeout,
			auto_reconnect=websocket_auto_reconnect,
		)

	def __repr__(self) -> str:
		return f"ByBitClient(mode='{self.mode}', url='{self.url}')"

	async def close(self):
		await self.ws.close_all()

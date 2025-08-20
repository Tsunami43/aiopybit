from collections.abc import Callable
from typing import Literal, Protocol


# HTTP
class ByBitHttpProtocol(Protocol):
	"""Protocol defining the interface for ByBit HTTP client methods"""

	async def _request(self, endpoint: str, method: str, payload: str = '') -> dict:
		"""Base HTTP request method"""
		...


ByBitModes = Literal['mainnet', 'demo', 'testnet']
ByBitCategories = Literal['linear', 'inverse', 'option', 'spot']
OrderSides = Literal['Buy', 'Sell']
OrderTypes = Literal['Market', 'Limit']
TimeInForce = Literal['GTC', 'IOC', 'FOK', 'PostOnly']
PositionIndex = Literal[0, 1, 2]
AccountTypes = Literal['UNIFIED', 'CONTRACT', 'SPOT', 'OPTION', 'FUND']
TriggerTypes = Literal['LastPrice', 'IndexPrice', 'MarkPrice']


ChannelType = Literal['public', 'private', 'trade']
KlineInterval = Literal[
	'1', '3', '5', '15', '30', '60', '120', '240', '360', '720', 'D', 'W', 'M'
]
OrderbookDepth = Literal[1, 25, 50, 100, 200, 500]
LongShortRatioPeriod = Literal['5min', '15min', '30min', '1h', '4h', '1d']
ChannelCategories = Literal['linear', 'inverse', 'option', 'spot']


class ByBitWebsocketClientProtocol(Protocol):
	"""Protocol defining the interface for ByBit WebSocket client methods"""

	topic_handlers: dict[str, Callable]

	async def send(self, **kwargs) -> None: ...


# WebSocket
class ByBitSWebSocketManagerProtocol(Protocol):
	"""WebSocket subscription configuration"""

	async def get_websocket(
		self, channel_type: str
	) -> ByBitWebsocketClientProtocol: ...

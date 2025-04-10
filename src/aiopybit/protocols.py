"""Type definitions and protocols for ByBit API."""

from collections.abc import Awaitable, Callable
from typing import Any, Literal

ByBitModes = Literal['mainnet', 'testnet', 'demo']
ByBitCategories = Literal['linear', 'spot', 'option', 'inverse']
ChannelType = Literal['public', 'private']
KlineInterval = Literal[
	'1', '3', '5', '15', '30', '60', '120', '240', '360', '720', 'D', 'W', 'M'
]
OrderbookDepth = Literal[1, 25, 50, 100, 200, 500]

OrderSide = Literal['Buy', 'Sell']
OrderType = Literal['Market', 'Limit']
TimeInForce = Literal['GTC', 'IOC', 'FOK', 'PostOnly']
AccountType = Literal['UNIFIED', 'CONTRACT', 'SPOT', 'FUND']

# A stream callback may be a plain or async function receiving the raw message.
StreamHandler = Callable[[dict[str, Any]], None | Awaitable[None]]

"""Type definitions and protocols for ByBit API."""

from typing import Literal

ByBitModes = Literal['mainnet', 'testnet', 'demo']
ByBitCategories = Literal['linear', 'spot', 'option', 'inverse']
ChannelType = Literal['public', 'private']
KlineInterval = Literal['1', '3', '5', '15', '30', '60', '120', '240', '360', '720', 'D', 'W', 'M']
OrderbookDepth = Literal[1, 25, 50, 100, 200, 500]

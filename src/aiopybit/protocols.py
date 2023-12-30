"""Type definitions and protocols for ByBit API."""

from typing import Literal

ByBitModes = Literal['mainnet', 'testnet', 'demo']
ByBitCategories = Literal['linear', 'spot', 'option']
ChannelType = Literal['public', 'private']

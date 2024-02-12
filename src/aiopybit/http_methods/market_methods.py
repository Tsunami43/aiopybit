"""Market data HTTP methods."""

import logging

logger = logging.getLogger('aiopybit')


class MarketMixin:
	"""Mixin for market data endpoints."""

	async def get_tickers(self, category: str, symbol: str = '') -> dict:
		"""Get ticker information."""
		payload = f'category={category}'
		if symbol:
			payload += f'&symbol={symbol}'
		return await self._request('/v5/market/tickers', 'GET', payload)

	async def get_orderbook(self, category: str, symbol: str, limit: int = 25) -> dict:
		"""Get orderbook data."""
		payload = f'category={category}&symbol={symbol}&limit={limit}'
		return await self._request('/v5/market/orderbook', 'GET', payload)

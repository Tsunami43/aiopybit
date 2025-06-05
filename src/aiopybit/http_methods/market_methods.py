"""Market data HTTP methods."""

import logging

logger = logging.getLogger('aiopybit')


class MarketMixin:
	"""Mixin for market data endpoints."""

	async def get_server_time(self) -> dict:
		"""Get ByBit server time."""
		return await self._request('/v5/market/time', 'GET')

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

	async def get_klines(
		self,
		category: str,
		symbol: str,
		interval: str,
		limit: int = 200,
		start: int | None = None,
		end: int | None = None,
	) -> dict:
		"""Get kline/candlestick data."""
		payload = (
			f'category={category}&symbol={symbol}&interval={interval}&limit={limit}'
		)
		if start is not None:
			payload += f'&start={start}'
		if end is not None:
			payload += f'&end={end}'
		return await self._request('/v5/market/kline', 'GET', payload)

	async def get_instruments_info(
		self,
		category: str,
		symbol: str = '',
		limit: int = 500,
	) -> dict:
		"""Get the specification of instruments (tick size, lot size, etc.)."""
		payload = f'category={category}&limit={limit}'
		if symbol:
			payload += f'&symbol={symbol}'
		return await self._request('/v5/market/instruments-info', 'GET', payload)

	async def get_recent_trades(
		self,
		category: str,
		symbol: str,
		limit: int = 60,
	) -> dict:
		"""Get recent public trades for a symbol."""
		payload = f'category={category}&symbol={symbol}&limit={limit}'
		return await self._request('/v5/market/recent-trade', 'GET', payload)

	async def get_funding_rate_history(
		self,
		category: str,
		symbol: str,
		limit: int = 200,
		start: int | None = None,
		end: int | None = None,
	) -> dict:
		"""Get historical funding rates for a perpetual/futures symbol."""
		payload = f'category={category}&symbol={symbol}&limit={limit}'
		if start is not None:
			payload += f'&startTime={start}'
		if end is not None:
			payload += f'&endTime={end}'
		return await self._request('/v5/market/funding/history', 'GET', payload)

	async def get_open_interest(
		self,
		category: str,
		symbol: str,
		interval_time: str,
		limit: int = 50,
	) -> dict:
		"""Get open interest of a contract over time.

		Args:
			interval_time: One of ``5min``, ``15min``, ``30min``, ``1h``,
				``4h``, ``1d``.
		"""
		payload = (
			f'category={category}&symbol={symbol}'
			f'&intervalTime={interval_time}&limit={limit}'
		)
		return await self._request('/v5/market/open-interest', 'GET', payload)

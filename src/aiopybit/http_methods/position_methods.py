"""Position management HTTP methods."""

import json
import logging

from aiopybit.protocols import (
	ByBitCategories,
	ByBitResponse,
	PositionMode,
	TradeMode,
)

logger = logging.getLogger('aiopybit')


class PositionMixin:
	"""Mixin for position endpoints."""

	async def get_positions(
		self, category: ByBitCategories, symbol: str = ''
	) -> ByBitResponse:
		"""Get position list."""
		payload = f'category={category}'
		if symbol:
			payload += f'&symbol={symbol}'
		return await self._request('/v5/position/list', 'GET', payload)

	async def set_leverage(
		self, category: ByBitCategories, symbol: str, leverage: float
	) -> ByBitResponse:
		"""Set leverage for trading pair."""
		payload = {
			'category': category,
			'symbol': symbol,
			'buyLeverage': str(leverage),
			'sellLeverage': str(leverage),
		}
		return await self._request(
			'/v5/position/set-leverage', 'POST', json.dumps(payload)
		)

	async def set_trading_stop(
		self,
		category: ByBitCategories,
		symbol: str,
		take_profit: float | None = None,
		stop_loss: float | None = None,
		trailing_stop: float | None = None,
		position_idx: int = 0,
		**extra: object,
	) -> ByBitResponse:
		"""Set take-profit, stop-loss or trailing-stop on an open position."""
		payload = {
			'category': category,
			'symbol': symbol,
			'positionIdx': position_idx,
		}
		if take_profit is not None:
			payload['takeProfit'] = str(take_profit)
		if stop_loss is not None:
			payload['stopLoss'] = str(stop_loss)
		if trailing_stop is not None:
			payload['trailingStop'] = str(trailing_stop)
		payload.update(extra)
		return await self._request(
			'/v5/position/trading-stop', 'POST', json.dumps(payload)
		)

	async def switch_margin_mode(
		self,
		category: ByBitCategories,
		symbol: str,
		trade_mode: TradeMode,
		leverage: float,
	) -> ByBitResponse:
		"""Switch between cross (0) and isolated (1) margin for a symbol."""
		payload = {
			'category': category,
			'symbol': symbol,
			'tradeMode': trade_mode,
			'buyLeverage': str(leverage),
			'sellLeverage': str(leverage),
		}
		return await self._request(
			'/v5/position/switch-isolated', 'POST', json.dumps(payload)
		)

	async def switch_position_mode(
		self,
		category: ByBitCategories,
		mode: PositionMode,
		symbol: str = '',
		coin: str = '',
	) -> ByBitResponse:
		"""Switch between one-way (0) and hedge (3) position mode."""
		payload = {'category': category, 'mode': mode}
		if symbol:
			payload['symbol'] = symbol
		if coin:
			payload['coin'] = coin
		return await self._request(
			'/v5/position/switch-mode', 'POST', json.dumps(payload)
		)

	async def get_closed_pnl(
		self,
		category: ByBitCategories,
		symbol: str = '',
		limit: int = 50,
	) -> ByBitResponse:
		"""Get closed profit and loss records."""
		payload = f'category={category}&limit={limit}'
		if symbol:
			payload += f'&symbol={symbol}'
		return await self._request('/v5/position/closed-pnl', 'GET', payload)

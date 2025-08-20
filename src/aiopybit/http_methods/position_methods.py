import json
from typing import Any

from aiopybit.protocols import ByBitCategories, ByBitHttpProtocol


class PositionMixin:
	"""Mixin containing position-related API methods"""

	async def get_positions(
		self: ByBitHttpProtocol,
		category: ByBitCategories,
		symbol: str | None = None,
		base_coin: str | None = None,
		settle_coin: str | None = None,
		limit: int = 200,
		cursor: str | None = None,
	) -> dict[str, Any]:
		"""
		Get position list

		Args:
		    category: Product type (linear, inverse, option)
		    symbol: Symbol name (optional)
		    base_coin: Base coin (optional, for option only)
		    settle_coin: Settle coin (optional)
		    limit: Limit for data size (max 200)
		    cursor: Pagination cursor (optional)

		Returns:
		    dict: Position information

		Example:
		    # Get all positions
		    positions = await client.get_positions('linear')

		    # Get specific symbol position
		    ton_position = await client.get_positions('linear', 'TONUSDT')
		"""
		payload = f'category={category}&limit={limit}'
		if symbol:
			payload += f'&symbol={symbol}'
		if base_coin:
			payload += f'&baseCoin={base_coin}'
		if settle_coin:
			payload += f'&settleCoin={settle_coin}'
		if cursor:
			payload += f'&cursor={cursor}'

		return await self._request(
			endpoint='/v5/position/list',
			method='GET',
			payload=payload,
		)

	async def set_leverage(
		self: ByBitHttpProtocol,
		category: ByBitCategories,
		symbol: str,
		leverage: float,
	) -> dict[str, Any]:
		"""
		    Set leverage for a trading pair

		    Args:
		        category: Product type (linear, inverse)
		        symbol: Symbol name (e.g., BTCUSDT, TONUSDT)
		leverage: Leverage value (1.0 to 100.0)

		    Returns:
		        dict: Leverage setting result

		    Example:
		        # Set leverage x50 for TON futures
		        result = await client.set_leverage(
		            category='linear',
		            symbol='TONUSDT',
		    leverage=50
		        )

		        # Different leverage for hedge mode
		        result = await client.set_leverage(
		            category='linear',
		            symbol='BTCUSDT',
		            leverage=50     l
		        )
		"""
		payload: dict[str, Any] = {
			'category': category,
			'symbol': symbol,
			'buyLeverage': str(leverage),
			'sellLeverage': str(leverage),
		}

		return await self._request(
			endpoint='/v5/position/set-leverage',
			method='POST',
			payload=json.dumps(payload),
		)

	async def switch_position_mode(
		self: ByBitHttpProtocol,
		category: ByBitCategories,
		symbol: str | None = None,
		coin: str | None = None,
		mode: int = 0,
	) -> dict[str, Any]:
		"""
		Switch position mode between One-Way and Hedge mode

		Args:
		    category: Product type (linear, inverse)
		    symbol: Symbol name (for linear only)
		    coin: Coin name (for inverse only)
		    mode: Position mode (0: one-way, 3: hedge)

		Returns:
		    dict: Position mode switch result

		Example:
		    # Switch to hedge mode for TONUSDT
		    result = await client.switch_position_mode(
		        category='linear',
		        symbol='TONUSDT',
		        mode=3
		    )
		"""
		payload: dict[str, Any] = {
			'category': category,
			'mode': mode,
		}

		if symbol:
			payload['symbol'] = symbol
		if coin:
			payload['coin'] = coin

		return await self._request(
			endpoint='/v5/position/switch-mode',
			method='POST',
			payload=json.dumps(payload),
		)

	async def set_trading_stop(
		self: ByBitHttpProtocol,
		category: ByBitCategories,
		symbol: str,
		position_idx: int = 0,
		take_profit: float | None = None,
		stop_loss: float | None = None,
		trailing_stop: str | None = None,
		tp_trigger_by: str | None = None,
		sl_trigger_by: str | None = None,
		active_price: str | None = None,
		tp_size: str | None = None,
		sl_size: str | None = None,
	) -> dict[str, Any]:
		"""
		Set trading stop (TP/SL) for an existing position

		Args:
		    category: Product type (linear, inverse)
		    symbol: Symbol name
		    position_idx: Position index (0: one-way, 1: hedge buy, 2: hedge sell)
		    take_profit: Take profit price
		    stop_loss: Stop loss price
		    trailing_stop: Trailing stop (percentage)
		    tp_trigger_by: TP trigger price type
		    sl_trigger_by: SL trigger price type
		    active_price: Trailing stop activation price
		    tp_size: Take profit size
		    sl_size: Stop loss size

		Returns:
		    dict: Trading stop setting result

		Example:
		    # Set TP/SL for position
		    result = await client.set_trading_stop(
		        category='linear',
		        symbol='TONUSDT',
		        take_profit='3.50',
		        stop_loss='2.00'
		    )
		"""
		payload: dict[str, Any] = {
			'category': category,
			'symbol': symbol,
			'positionIdx': position_idx,
		}

		if take_profit:
			payload['takeProfit'] = str(take_profit)
		if stop_loss:
			payload['stopLoss'] = str(stop_loss)
		if trailing_stop:
			payload['trailingStop'] = trailing_stop
		if tp_trigger_by:
			payload['tpTriggerBy'] = tp_trigger_by
		if sl_trigger_by:
			payload['slTriggerBy'] = sl_trigger_by
		if active_price:
			payload['activePrice'] = active_price
		if tp_size:
			payload['tpSize'] = tp_size
		if sl_size:
			payload['slSize'] = sl_size

		return await self._request(
			endpoint='/v5/position/trading-stop',
			method='POST',
			payload=json.dumps(payload),
		)

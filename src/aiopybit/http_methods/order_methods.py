"""Order management HTTP methods."""

import json
import logging

from aiopybit.protocols import (
	ByBitCategories,
	ByBitResponse,
	OrderSide,
	OrderType,
	TimeInForce,
)

logger = logging.getLogger('aiopybit')


class OrderMixin:
	"""Mixin for order endpoints."""

	async def create_order(
		self,
		category: ByBitCategories,
		symbol: str,
		side: OrderSide,
		order_type: OrderType,
		qty: float,
		price: float | None = None,
		time_in_force: TimeInForce | None = None,
		order_link_id: str | None = None,
		reduce_only: bool | None = None,
		**extra: object,
	) -> ByBitResponse:
		"""Create a new order.

		Args:
			time_in_force: One of ``GTC``, ``IOC``, ``FOK``, ``PostOnly``.
			order_link_id: Optional client-supplied order id.
			reduce_only: Whether the order may only reduce a position.
			**extra: Any additional ByBit order parameter (e.g. ``takeProfit``,
				``stopLoss``, ``triggerPrice``) passed through verbatim.
		"""
		payload = {
			'category': category,
			'symbol': symbol,
			'side': side,
			'orderType': order_type,
			'qty': str(qty),
		}

		if price is not None:
			payload['price'] = str(price)
		if time_in_force is not None:
			payload['timeInForce'] = time_in_force
		if order_link_id is not None:
			payload['orderLinkId'] = order_link_id
		if reduce_only is not None:
			payload['reduceOnly'] = reduce_only
		payload.update(extra)

		return await self._request('/v5/order/create', 'POST', json.dumps(payload))

	async def cancel_order(
		self,
		category: ByBitCategories,
		symbol: str,
		order_id: str | None = None,
		order_link_id: str | None = None,
	) -> ByBitResponse:
		"""Cancel an existing order."""
		if not order_id and not order_link_id:
			raise ValueError('Either order_id or order_link_id required')

		payload = {'category': category, 'symbol': symbol}

		if order_id:
			payload['orderId'] = order_id
		if order_link_id:
			payload['orderLinkId'] = order_link_id

		return await self._request('/v5/order/cancel', 'POST', json.dumps(payload))

	async def get_orders(
		self,
		category: ByBitCategories,
		symbol: str = '',
		limit: int = 20,
	) -> ByBitResponse:
		"""Get order list."""
		payload = f'category={category}&limit={limit}'
		if symbol:
			payload += f'&symbol={symbol}'
		return await self._request('/v5/order/realtime', 'GET', payload)

	async def amend_order(
		self,
		category: ByBitCategories,
		symbol: str,
		order_id: str | None = None,
		order_link_id: str | None = None,
		qty: float | None = None,
		price: float | None = None,
	) -> ByBitResponse:
		"""Modify an existing order."""
		if not order_id and not order_link_id:
			raise ValueError('Either order_id or order_link_id required')

		payload = {'category': category, 'symbol': symbol}

		if order_id:
			payload['orderId'] = order_id
		if order_link_id:
			payload['orderLinkId'] = order_link_id
		if qty is not None:
			payload['qty'] = str(qty)
		if price is not None:
			payload['price'] = str(price)

		return await self._request('/v5/order/amend', 'POST', json.dumps(payload))

	async def cancel_all_orders(
		self,
		category: ByBitCategories,
		symbol: str = '',
		settle_coin: str = '',
	) -> ByBitResponse:
		"""Cancel all open orders.

		Provide ``symbol`` or ``settle_coin`` to scope the cancellation for
		derivatives categories, as required by ByBit.
		"""
		payload = {'category': category}
		if symbol:
			payload['symbol'] = symbol
		if settle_coin:
			payload['settleCoin'] = settle_coin
		return await self._request('/v5/order/cancel-all', 'POST', json.dumps(payload))

	async def get_order_history(
		self,
		category: ByBitCategories,
		symbol: str = '',
		limit: int = 50,
	) -> ByBitResponse:
		"""Get historical (closed/cancelled/filled) orders."""
		payload = f'category={category}&limit={limit}'
		if symbol:
			payload += f'&symbol={symbol}'
		return await self._request('/v5/order/history', 'GET', payload)

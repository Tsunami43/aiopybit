"""Order management HTTP methods."""

import json
import logging

logger = logging.getLogger('aiopybit')


class OrderMixin:
	"""Mixin for order endpoints."""

	async def create_order(
		self,
		category: str,
		symbol: str,
		side: str,
		order_type: str,
		qty: float,
		price: float = None,
	) -> dict:
		"""Create a new order."""
		payload = {
			'category': category,
			'symbol': symbol,
			'side': side,
			'orderType': order_type,
			'qty': str(qty),
		}

		if price is not None:
			payload['price'] = str(price)

		return await self._request('/v5/order/create', 'POST', json.dumps(payload))

	async def cancel_order(
		self,
		category: str,
		symbol: str,
		order_id: str = None,
		order_link_id: str = None,
	) -> dict:
		"""Cancel an existing order."""
		if not order_id and not order_link_id:
			raise ValueError('Either order_id or order_link_id required')

		payload = {'category': category, 'symbol': symbol}

		if order_id:
			payload['orderId'] = order_id
		if order_link_id:
			payload['orderLinkId'] = order_link_id

		return await self._request('/v5/order/cancel', 'POST', json.dumps(payload))

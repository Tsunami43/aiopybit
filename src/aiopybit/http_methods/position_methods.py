"""Position management HTTP methods."""

import json
import logging

logger = logging.getLogger('aiopybit')


class PositionMixin:
	"""Mixin for position endpoints."""

	async def get_positions(self, category: str, symbol: str = '') -> dict:
		"""Get position list."""
		payload = f'category={category}'
		if symbol:
			payload += f'&symbol={symbol}'
		return await self._request('/v5/position/list', 'GET', payload)

	async def set_leverage(self, category: str, symbol: str, leverage: float) -> dict:
		"""Set leverage for trading pair."""
		payload = {
			'category': category,
			'symbol': symbol,
			'buyLeverage': str(leverage),
			'sellLeverage': str(leverage),
		}
		return await self._request('/v5/position/set-leverage', 'POST', json.dumps(payload))

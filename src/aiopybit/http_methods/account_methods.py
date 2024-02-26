"""Account management HTTP methods."""

import logging

logger = logging.getLogger('aiopybit')


class AccountMixin:
	"""Mixin for account endpoints."""

	async def get_wallet_balance(self, account_type: str, coin: str = '') -> dict:
		"""Get wallet balance."""
		payload = f'accountType={account_type}'
		if coin:
			payload += f'&coin={coin}'
		return await self._request('/v5/account/wallet-balance', 'GET', payload)

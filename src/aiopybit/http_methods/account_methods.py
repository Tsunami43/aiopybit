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

	async def get_account_info(self) -> dict:
		"""Get account configuration (margin mode, unified status, etc.)."""
		return await self._request('/v5/account/info', 'GET')

	async def get_fee_rates(self, category: str, symbol: str = '') -> dict:
		"""Get trading fee rates for a category (and optional symbol)."""
		payload = f'category={category}'
		if symbol:
			payload += f'&symbol={symbol}'
		return await self._request('/v5/account/fee-rate', 'GET', payload)

	async def get_transaction_log(
		self,
		account_type: str = 'UNIFIED',
		category: str = '',
		currency: str = '',
		limit: int = 50,
	) -> dict:
		"""Get the unified account transaction log."""
		payload = f'accountType={account_type}&limit={limit}'
		if category:
			payload += f'&category={category}'
		if currency:
			payload += f'&currency={currency}'
		return await self._request('/v5/account/transaction-log', 'GET', payload)

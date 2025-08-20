from typing import Any

from aiopybit.protocols import AccountTypes, ByBitHttpProtocol


class AccountMixin:
	"""Mixin containing account-related API methods"""

	async def get_account_info(
		self: ByBitHttpProtocol,
		account_type: AccountTypes = 'UNIFIED',
		coin: str | None = None,
	) -> dict[str, Any]:
		"""
		Get account wallet balance information

		Args:
		    account_type: Account type (UNIFIED, CONTRACT, SPOT, OPTION, FUND)
		    coin: Specific coin to query (optional, returns all if not specified)

		Returns:
		    dict: Account balance information

		Example:
		    # Get all balances for contracts account
		    balance = await client.get_account_info(account_type='CONTRACT')

		    # Get specific coin balance
		    usdt_balance = await client.get_account_info(
		        account_type='UNIFIED',
		        coin='USDT'
		    )
		"""
		payload = f'accountType={account_type}'
		if coin:
			payload += f'&coin={coin}'

		return await self._request(
			endpoint='/v5/account/wallet-balance',
			method='GET',
			payload=payload,
		)

	async def get_fee_rate(
		self: ByBitHttpProtocol,
		category: str,
		symbol: str | None = None,
		base_coin: str | None = None,
	) -> dict[str, Any]:
		"""
		Get trading fee rate

		Args:
		    category: Product type (linear, inverse, option, spot)
		    symbol: Symbol name (optional)
		    base_coin: Base coin (optional)

		Returns:
		    dict: Fee rate information

		Example:
		    # Get fee rate for specific symbol
		    fee = await client.get_fee_rate(
		        category='linear',
		        symbol='TONUSDT'
		    )
		"""
		payload = f'category={category}'
		if symbol:
			payload += f'&symbol={symbol}'
		if base_coin:
			payload += f'&baseCoin={base_coin}'

		return await self._request(
			endpoint='/v5/account/fee-rate',
			method='GET',
			payload=payload,
		)

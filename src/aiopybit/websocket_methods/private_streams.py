import logging
from collections.abc import Callable

from aiopybit.protocols import (
	ByBitSWebSocketManagerProtocol,
)

logger = logging.getLogger('aiopybit')


class ByBitPrivateStreamsMixin:
	async def subscribe_to_order(
		self: ByBitSWebSocketManagerProtocol, on_message: Callable
	) -> str:
		"""
		Subscribe to real-time order updates.

		Receives updates when orders are created, modified, filled, or cancelled.

		Args:
		    on_message (Callable): Callback function to handle incoming order data.

		Example:
		    >>> async def handle_order(data):
		    ...     order = data['data'][0]
		    ...     print(f'Order {order["orderId"]} status: {order["orderStatus"]}')
		    >>>
		    >>> await client.subscribe_to_order(handle_order)
		"""
		websocket = await self.get_websocket('private')
		topic = 'order'
		websocket.topic_handlers[topic] = on_message
		try:
			await websocket.send(op='subscribe', args=[topic])
		except Exception:
			del websocket.topic_handlers[topic]
			raise

		return topic

	async def subscribe_to_execution(
		self: ByBitSWebSocketManagerProtocol, on_message: Callable
	) -> str:
		"""
		Subscribe to real-time execution (trade) updates.

		Receives updates when your orders are executed (filled).

		Args:
		    on_message (Callable): Callback function to handle incoming execution data.

		Example:
		    >>> async def handle_execution(data):
		    ...     execution = data['data'][0]
		    ...     print(
		    ...         f'Executed {execution["execQty"]} at {execution["execPrice"]}'
		    ...     )
		    >>>
		    >>> await client.subscribe_to_execution(handle_execution)
		"""
		websocket = await self.get_websocket('private')
		topic = 'execution'
		websocket.topic_handlers[topic] = on_message
		try:
			await websocket.send(op='subscribe', args=[topic])
		except Exception:
			del websocket.topic_handlers[topic]
			raise

		return topic

	async def subscribe_to_position(
		self: ByBitSWebSocketManagerProtocol, on_message: Callable
	) -> str:
		"""
		Subscribe to real-time position updates.

		Receives updates when your positions change due to trades, funding, etc.

		Args:
		    on_message (Callable): Callback function to handle incoming position data.

		Example:
		    >>> async def handle_position(data):
		    ...     position = data['data'][0]
		    ...     print(
		    ...         f'Position {position["symbol"]}: {position["size"]} @ {position["avgPrice"]}'
		    ...     )
		    >>>
		    >>> await client.subscribe_to_position(handle_position)
		"""
		websocket = await self.get_websocket('private')
		topic = 'position'
		websocket.topic_handlers[topic] = on_message
		try:
			await websocket.send(op='subscribe', args=[topic])
		except Exception:
			del websocket.topic_handlers[topic]
			raise

		return topic

	async def subscribe_to_wallet(
		self: ByBitSWebSocketManagerProtocol, on_message: Callable
	) -> str:
		"""
		Subscribe to real-time wallet balance updates.

		Receives updates when your wallet balances change.

		Args:
		    on_message (Callable): Callback function to handle incoming wallet data.

		Example:
		    >>> async def handle_wallet(data):
		    ...     for account in data['data']:
		    ...         for coin in account['coin']:
		    ...             print(f'{coin["coin"]}: {coin["walletBalance"]}')
		    >>>
		    >>> await client.subscribe_to_wallet(handle_wallet)
		"""
		websocket = await self.get_websocket('private')
		topic = 'wallet'
		websocket.topic_handlers[topic] = on_message
		try:
			await websocket.send(op='subscribe', args=[topic])
		except Exception:
			del websocket.topic_handlers[topic]
			raise

		return topic

	async def subscribe_to_greeks(
		self: ByBitSWebSocketManagerProtocol, on_message: Callable
	) -> str:
		"""
		Subscribe to real-time option greeks updates.

		Receives updates on option portfolio greeks (delta, gamma, theta, vega).
		Available only for options trading accounts.

		Args:
		    on_message (Callable): Callback function to handle incoming greeks data.

		Example:
		    >>> async def handle_greeks(data):
		    ...     greeks = data['data'][0]
		    ...     print(f'Portfolio Delta: {greeks["totalDelta"]}')
		    >>>
		    >>> await client.subscribe_to_greeks(handle_greeks)
		"""
		websocket = await self.get_websocket('private')
		topic = 'greeks'
		websocket.topic_handlers[topic] = on_message
		try:
			await websocket.send(op='subscribe', args=[topic])
		except Exception:
			del websocket.topic_handlers[topic]
			raise

		return topic

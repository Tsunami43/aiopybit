import json
from typing import Any

from aiopybit.protocols import (
    ByBitCategories,
    ByBitHttpProtocol,
    OrderSides,
    OrderTypes,
    PositionIndex,
    TimeInForce,
    TriggerTypes,
)


class OrderMixin:
    """Mixin containing order-related API methods"""

    async def create_order(
        self: ByBitHttpProtocol,
        category: ByBitCategories,
        symbol: str,
        side: OrderSides,
        order_type: OrderTypes,
        qty: float,
        price: float | None = None,
        time_in_force: TimeInForce = 'GTC',
        position_idx: PositionIndex = 0,
        reduce_only: bool = False,
        close_on_trigger: bool = False,
        order_link_id: str | None = None,
        take_profit: float | None = None,
        stop_loss: float | None = None,
        tp_trigger_by: TriggerTypes | None = None,
        sl_trigger_by: TriggerTypes | None = None,
    ) -> dict[str, Any]:
        """
        Create a new order

        Args:
            category: Product type (linear, inverse, option, spot)
            symbol: Symbol name (e.g., BTCUSDT, TONUSDT)
            side: Order side (Buy or Sell)
            order_type: Order type (Market or Limit)
            qty: Order quantity
            price: Order price (required for Limit orders)
            time_in_force: Time in force (GTC, IOC, FOK, PostOnly)
            position_idx: Position index (0: one-way, 1: hedge Buy, 2: hedge Sell)
            reduce_only: Reduce only flag
            close_on_trigger: Close on trigger flag
            order_link_id: User customized order ID
            take_profit: Take profit price
            stop_loss: Stop loss price
            tp_trigger_by: Take profit trigger price type
            sl_trigger_by: Stop loss trigger price type

        Returns:
            dict: Order creation result

        Example:
            # Market order with stop loss
            order = await client.create_order(
                category='linear',
                symbol='TONUSDT',
                side='Buy',
                order_type='Market',
                qty=10,
                stop_loss=2.00,
                order_link_id='my_ton_trade'
            )

            # Limit order with TP/SL
            order = await client.create_order(
                category='linear',
                symbol='BTCUSDT',
                side='Buy',
                order_type='Limit',
                qty=0.1,
                price=40000,
                take_profit=45000,
                stop_loss=38000,
                time_in_force='GTC'
            )
        """
        payload: dict[str, Any] = {
            'category': category,
            'symbol': symbol,
            'side': side,
            'orderType': order_type,
            'qty': str(qty),
            'timeInForce': time_in_force,
            'positionIdx': position_idx,
        }

        if price is not None:
            payload['price'] = str(price)
        if reduce_only:
            payload['reduceOnly'] = True
        if close_on_trigger:
            payload['closeOnTrigger'] = True
        if order_link_id:
            payload['orderLinkId'] = order_link_id
        if take_profit:
            payload['takeProfit'] = str(take_profit)
        if stop_loss:
            payload['stopLoss'] = str(stop_loss)
        if tp_trigger_by:
            payload['tpTriggerBy'] = tp_trigger_by
        if sl_trigger_by:
            payload['slTriggerBy'] = sl_trigger_by

        return await self._request(
            endpoint='/v5/order/create',
            method='POST',
            payload=json.dumps(payload),
        )

    async def amend_order(
        self: ByBitHttpProtocol,
        category: ByBitCategories,
        symbol: str,
        order_id: str | None = None,
        order_link_id: str | None = None,
        qty: float | None = None,
        price: float | None = None,
        take_profit: float | None = None,
        stop_loss: float | None = None,
        tp_trigger_by: TriggerTypes | None = None,
        sl_trigger_by: TriggerTypes | None = None,
    ) -> dict[str, Any]:
        """
        Modify an existing order

        Args:
            category: Product type (linear, inverse, option, spot)
            symbol: Symbol name (e.g., BTCUSDT, TONUSDT)
            order_id: Order ID from Bybit
            order_link_id: User customized order ID
            qty: New order quantity
            price: New order price
            take_profit: New take profit price
            stop_loss: New stop loss price
            tp_trigger_by: Take profit trigger price type
            sl_trigger_by: Stop loss trigger price type

        Returns:
            dict: Order modification result

        Example:
            # Modify order by custom ID
            result = await client.amend_order(
                category='linear',
                symbol='TONUSDT',
                order_link_id='my_order_001',
                price=2.40,
                qty=10,
                stop_loss=1.90
            )

            # Modify order by Bybit order ID
            result = await client.amend_order(
                category='linear',
                symbol='BTCUSDT',
                order_id='1234567890',
                take_profit=45000
            )
        """
        if not order_id and not order_link_id:
            raise ValueError('Either order_id or order_link_id must be provided')

        payload: dict[str, Any] = {
            'category': category,
            'symbol': symbol,
        }

        if order_id:
            payload['orderId'] = order_id
        if order_link_id:
            payload['orderLinkId'] = order_link_id
        if qty is not None:
            payload['qty'] = str(qty)
        if price is not None:
            payload['price'] = str(price)
        if take_profit is not None:
            payload['takeProfit'] = str(take_profit)
        if stop_loss is not None:
            payload['stopLoss'] = str(stop_loss)
        if tp_trigger_by:
            payload['tpTriggerBy'] = tp_trigger_by
        if sl_trigger_by:
            payload['slTriggerBy'] = sl_trigger_by

        return await self._request(
            endpoint='/v5/order/amend',
            method='POST',
            payload=json.dumps(payload),
        )

    async def cancel_order(
        self: ByBitHttpProtocol,
        category: ByBitCategories,
        symbol: str,
        order_id: str | None = None,
        order_link_id: str | None = None,
        order_filter: str | None = None,
    ) -> dict[str, Any]:
        """
        Cancel an existing order

        Args:
            category: Product type (linear, inverse, option, spot)
            symbol: Symbol name (e.g., BTCUSDT, TONUSDT)
            order_id: Order ID from Bybit
            order_link_id: User customized order ID
            order_filter: Order filter (Order, StopOrder, tpslOrder)

        Returns:
            dict: Order cancellation result

        Example:
            # Cancel order by custom ID
            result = await client.cancel_order(
                category='linear',
                symbol='TONUSDT',
                order_link_id='my_order_001'
            )
        """
        if not order_id and not order_link_id:
            raise ValueError('Either order_id or order_link_id must be provided')

        payload: dict[str, Any] = {
            'category': category,
            'symbol': symbol,
        }

        if order_id:
            payload['orderId'] = order_id
        if order_link_id:
            payload['orderLinkId'] = order_link_id
        if order_filter:
            payload['orderFilter'] = order_filter

        return await self._request(
            endpoint='/v5/order/cancel',
            method='POST',
            payload=json.dumps(payload),
        )

    async def get_orders(
        self: ByBitHttpProtocol,
        category: ByBitCategories,
        symbol: str | None = None,
        order_id: str | None = None,
        order_link_id: str | None = None,
        order_status: str | None = None,
        order_filter: str | None = None,
        limit: int = 20,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        Get order list

        Args:
            category: Product type (linear, inverse, option, spot)
            symbol: Symbol name (optional)
            order_id: Order ID (optional)
            order_link_id: User customized order ID (optional)
            order_status: Order status (optional)
            order_filter: Order filter (optional)
            limit: Limit for data size per page (max 50)
            cursor: Pagination cursor (optional)

        Returns:
            dict: List of orders

        Example:
            # Get all active orders for TONUSDT
            orders = await client.get_orders(
                category='linear',
                symbol='TONUSDT',
                order_status='New'
            )
        """
        payload = f'category={category}'
        if symbol:
            payload += f'&symbol={symbol}'
        if order_id:
            payload += f'&orderId={order_id}'
        if order_link_id:
            payload += f'&orderLinkId={order_link_id}'
        if order_status:
            payload += f'&orderStatus={order_status}'
        if order_filter:
            payload += f'&orderFilter={order_filter}'
        if limit != 20:
            payload += f'&limit={limit}'
        if cursor:
            payload += f'&cursor={cursor}'

        return await self._request(
            endpoint='/v5/order/realtime',
            method='GET',
            payload=payload,
        )

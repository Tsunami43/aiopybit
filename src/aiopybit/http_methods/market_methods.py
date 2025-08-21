from typing import Any

from aiopybit.protocols import ByBitCategories, ByBitHttpProtocol, KlineInterval


class MarketMixin:
    """Mixin containing market data API methods"""

    async def get_ticker_price(
        self: ByBitHttpProtocol,
        category: ByBitCategories,
        symbol: str | None = None,
        base_coin: str | None = None,
        exp_date: str | None = None,
    ) -> dict[str, Any]:
        """
        Get latest price for symbols

        Args:
            category: Product type (linear, inverse, option, spot)
            symbol: Symbol name (e.g., BTCUSDT, TONUSDT) - optional
            base_coin: Base coin (for options) - optional
            exp_date: Expiry date (for options) - optional

        Returns:
            dict: Market ticker information including latest price, volume, etc.

        Example:
            # Get TON futures price
            ticker = await client.get_ticker_price('linear', 'TONUSDT')
            price = float(ticker['result']['list'][0]['lastPrice'])

            # Get all linear futures tickers
            tickers = await client.get_ticker_price('linear')

            # Get BTC spot price
            ticker = await client.get_ticker_price('spot', 'BTCUSDT')
            volume = float(ticker['result']['list'][0]['volume24h'])
        """
        payload = f'category={category}'
        if symbol:
            payload += f'&symbol={symbol}'
        if base_coin:
            payload += f'&baseCoin={base_coin}'
        if exp_date:
            payload += f'&expDate={exp_date}'

        return await self._request(
            endpoint='/v5/market/tickers',
            method='GET',
            payload=payload,
        )

    async def get_orderbook(
        self: ByBitHttpProtocol,
        category: ByBitCategories,
        symbol: str,
        limit: int = 25,
    ) -> dict[str, Any]:
        """
        Get order book data

        Args:
            category: Product type (linear, inverse, option, spot)
            symbol: Symbol name (e.g., BTCUSDT, TONUSDT)
            limit: Limit for data size (max 500, default 25)

        Returns:
            dict: Order book with bids and asks

        Example:
            # Get TON orderbook
            orderbook = await client.get_orderbook('linear', 'TONUSDT', limit=50)
            best_bid = float(orderbook['result']['b'][0][0])
            best_ask = float(orderbook['result']['a'][0][0])
        """
        payload = f'category={category}&symbol={symbol}&limit={limit}'

        return await self._request(
            endpoint='/v5/market/orderbook',
            method='GET',
            payload=payload,
        )

    async def get_klines(
        self: ByBitHttpProtocol,
        category: ByBitCategories,
        symbol: str,
        interval: KlineInterval,
        start: int | None = None,
        end: int | None = None,
        limit: int = 200,
    ) -> dict[str, Any]:
        """
        Get kline/candlestick data

        Args:
            category: Product type (linear, inverse, option, spot)
            symbol: Symbol name (e.g., BTCUSDT, TONUSDT)
            interval: Kline interval (1,3,5,15,30,60,120,240,360,720,D,M,W)
            start: Start timestamp (ms)
            end: End timestamp (ms)
            limit: Limit for data size (max 1000, default 200)

        Returns:
            dict: Kline data

        Example:
            # Get 1-hour candles for TON
            klines = await client.get_klines(
                category='linear',
                symbol='TONUSDT',
                interval='60',
                limit=100
            )
        """
        payload = (
            f'category={category}&symbol={symbol}&interval={interval}&limit={limit}'
        )
        if start:
            payload += f'&start={start}'
        if end:
            payload += f'&end={end}'

        return await self._request(
            endpoint='/v5/market/kline',
            method='GET',
            payload=payload,
        )

    async def get_instruments_info(
        self: ByBitHttpProtocol,
        category: ByBitCategories,
        symbol: str | None = None,
        base_coin: str | None = None,
        limit: int = 500,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """
        Get instruments info

        Args:
            category: Product type (linear, inverse, option, spot)
            symbol: Symbol name (optional)
            base_coin: Base coin (optional)
            limit: Limit for data size (max 1000, default 500)
            cursor: Pagination cursor (optional)

        Returns:
            dict: Instruments information

        Example:
            # Get TON instrument info
            info = await client.get_instruments_info('linear', 'TONUSDT')
            min_price = info['result']['list'][0]['priceFilter']['minPrice']
        """
        payload = f'category={category}&limit={limit}'
        if symbol:
            payload += f'&symbol={symbol}'
        if base_coin:
            payload += f'&baseCoin={base_coin}'
        if cursor:
            payload += f'&cursor={cursor}'

        return await self._request(
            endpoint='/v5/market/instruments-info',
            method='GET',
            payload=payload,
        )

# aiopybit

Asynchronous Python client for the [Bybit](https://www.bybit.com/invite?ref=D0B6GN) **v5** API — REST and WebSocket in a single, fully typed, `asyncio`-native package.

[![PyPI](https://img.shields.io/pypi/v/aiopybit.svg)](https://pypi.org/project/aiopybit/)
[![Python versions](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://pypi.org/project/aiopybit/)
[![CI](https://github.com/Tsunami43/aiopybit/actions/workflows/ci.yml/badge.svg)](https://github.com/Tsunami43/aiopybit/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

`aiopybit` gives you a small, predictable surface over the Bybit v5 API:

- **REST** — market data, orders, positions and account endpoints with request
  signing, automatic retries (exponential backoff) and a shared `aiohttp`
  session.
- **WebSocket** — public and private streams behind one connection manager with
  automatic reconnection and subscription restore.
- **Typed** — `Literal` types for categories, intervals, modes and more; ships a
  `py.typed` marker for full downstream type checking.
- **Ergonomic** — one `ByBitClient` entry point, `async with` support and a
  single `ByBitError` base exception.
- **Optional extras** — a trading-card image generator (`aiopybit[cards]`).

## Table of contents

- [Installation](#installation)
- [Quick start](#quick-start)
- [REST API](#rest-api)
- [WebSocket streams](#websocket-streams)
- [Error handling](#error-handling)
- [Trading cards](#trading-cards)
- [Environments and categories](#environments-and-categories)
- [Logging](#logging)
- [API reference](#api-reference)
- [Contributing](#contributing)
- [License](#license)

## Installation

Requires **Python 3.10+**.

```bash
pip install aiopybit
```

Optional trading-card generator (pulls in Pillow):

```bash
pip install "aiopybit[cards]"
```

From source:

```bash
git clone https://github.com/Tsunami43/aiopybit.git
cd aiopybit
pip install -e ".[cards]"
```

## Quick start

`ByBitClient` is the single entry point. It exposes REST methods directly and
WebSocket subscriptions through `client.ws`. Use it as an async context manager
so the HTTP session and every socket are closed for you:

```python
import asyncio

from aiopybit import ByBitClient


async def main():
    async with ByBitClient(api_key='...', secret_key='...', mode='testnet') as client:
        # REST
        tickers = await client.get_tickers('linear', 'BTCUSDT')
        print(tickers['result']['list'][0]['lastPrice'])

        # WebSocket
        async def on_ticker(message):
            data = message['data']
            print(data['symbol'], data['lastPrice'])

        await client.ws.subscribe_to_ticker('linear', 'BTCUSDT', on_ticker)
        await asyncio.sleep(30)


if __name__ == '__main__':
    asyncio.run(main())
```

`mode` is one of `mainnet`, `testnet` or `demo`. API credentials are only
required for private (account/trading) endpoints and streams.

## REST API

Every REST call returns the decoded Bybit JSON response (`{'retCode': 0,
'result': {...}, ...}`). A non-zero `retCode` raises `ByBitAPIError`, so you can
assume success once a call returns.

```python
async with ByBitClient(api_key, secret_key, 'mainnet') as client:
    # Market data (no auth required)
    await client.get_orderbook('linear', 'BTCUSDT', limit=50)
    await client.get_klines('linear', 'BTCUSDT', interval='15', limit=200)
    await client.get_instruments_info('linear', 'BTCUSDT')

    # Trading (auth required)
    await client.create_order(
        category='linear',
        symbol='BTCUSDT',
        side='Buy',
        order_type='Limit',
        qty=0.01,
        price=30000,
        time_in_force='PostOnly',
    )
    await client.cancel_all_orders('linear', symbol='BTCUSDT')

    # Account and positions
    await client.get_wallet_balance('UNIFIED')
    await client.get_positions('linear', 'BTCUSDT')
    await client.set_leverage('linear', 'BTCUSDT', 10)
```

See the [API reference](#api-reference) for the full list of methods.

## WebSocket streams

Subscriptions are managed for you: the manager opens (and reuses) one connection
per channel, authenticates private channels, keeps them alive with ping/pong and
restores subscriptions after a reconnect. Handlers may be plain or `async`
functions and receive the raw message dict.

```python
async def on_kline(message):
    for candle in message['data']:
        print(candle['start'], candle['close'])


async def on_order(message):
    for order in message['data']:
        print(order['orderId'], order['orderStatus'])


async with ByBitClient(api_key, secret_key, 'mainnet') as client:
    # Public — no credentials needed
    topic = await client.ws.subscribe_to_kline('linear', 'BTCUSDT', '1', on_kline)

    # Private — credentials required
    await client.ws.subscribe_to_order(on_order)

    # Later, unsubscribe by topic
    await client.ws.unsubscribe(topic)  # 'kline.1.BTCUSDT'
```

Each `subscribe_to_*` call returns the topic string, which you can pass to
`client.ws.unsubscribe(topic)`.

## Error handling

All errors derive from `ByBitError`, so a single `except` can catch everything,
or you can handle failures precisely:

```python
from aiopybit import ByBitError, ByBitAPIError, ByBitHTTPError

try:
    await client.create_order('linear', 'BTCUSDT', 'Buy', 'Market', 1)
except ByBitAPIError as exc:
    # Reached Bybit but was rejected (non-zero retCode).
    print(exc.ret_code, exc.ret_msg)
except ByBitHTTPError as exc:
    # Transport-level failure (non-2xx HTTP status).
    print(exc.status)
except ByBitError:
    # Anything else raised by the library.
    ...
```

| Exception | Raised when |
|-----------|-------------|
| `ByBitError` | Base class for every library error |
| `ByBitHTTPError` | Response has a non-successful HTTP status (`status`) |
| `ByBitAPIError` | Bybit returns a non-zero `retCode` (`ret_code`, `ret_msg`, `response`) |
| `ByBitAuthError` | WebSocket authentication fails or credentials are missing |

Transient connection/timeout errors are retried automatically with exponential
backoff before the exception is finally raised.

## Trading cards

The optional `aiopybit.cards` module renders shareable Bybit-style ROI/PnL cards
— handy for posting a position to a Telegram or Discord channel. Install the
extra with `pip install "aiopybit[cards]"`.

```python
from aiopybit.cards import BybitCardGenerator

generator = BybitCardGenerator()

# Save to a file...
generator.save_card(
    symbol='BTCUSDT',
    direction='Long',          # 'Long' or 'Short'
    leverage=100,
    entry_price=20000,
    market_price=41850.5,
    output_path='card.png',
)

# ...or get raw bytes to send straight to a bot.
image_bytes = generator.get_card_bytes('BTCUSDT', 'Long', 100, 20000, 41850.5)
```

ROI is computed automatically from the entry/market price, direction and
leverage; colours switch between green (profit) and red (loss). A background and
the IBM Plex Sans fonts are bundled, so no extra assets are required — you can
still pass your own `background_image_path` / `fonts_dir`.

![Example trading card](assets/card_example.png)

See [`examples/generate_card.py`](examples/generate_card.py) for building a card
directly from a live position.

## Environments and categories

| `mode` | Description | Base host |
|--------|-------------|-----------|
| `mainnet` | Production | `api.bybit.com` / `stream.bybit.com` |
| `testnet` | Testing | `api-testnet.bybit.com` / `stream-testnet.bybit.com` |
| `demo` | Demo trading | `api-demo.bybit.com` / `stream-demo.bybit.com` |

| `category` | Description |
|------------|-------------|
| `linear` | USDT/USDC perpetual & futures contracts |
| `inverse` | Inverse (coin-margined) contracts |
| `spot` | Spot trading pairs |
| `option` | Options contracts |

## Logging

The library logs under the `aiopybit` logger. Enable it to trace connections and
debug issues:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
)
logging.getLogger('aiopybit').setLevel(logging.DEBUG)  # verbose
```

## API reference

### `ByBitClient(api_key, secret_key, mode)`

REST methods (all coroutines):

**Market data**

| Method | Endpoint |
|--------|----------|
| `get_server_time()` | `/v5/market/time` |
| `get_tickers(category, symbol='')` | `/v5/market/tickers` |
| `get_orderbook(category, symbol, limit=25)` | `/v5/market/orderbook` |
| `get_klines(category, symbol, interval, limit=200, start=None, end=None)` | `/v5/market/kline` |
| `get_instruments_info(category, symbol='', limit=500)` | `/v5/market/instruments-info` |
| `get_recent_trades(category, symbol, limit=60)` | `/v5/market/recent-trade` |
| `get_funding_rate_history(category, symbol, limit=200, start=None, end=None)` | `/v5/market/funding/history` |
| `get_open_interest(category, symbol, interval_time, limit=50)` | `/v5/market/open-interest` |

**Orders**

| Method | Endpoint |
|--------|----------|
| `create_order(category, symbol, side, order_type, qty, price=None, time_in_force=None, order_link_id=None, reduce_only=None, **extra)` | `/v5/order/create` |
| `amend_order(category, symbol, order_id=None, order_link_id=None, qty=None, price=None)` | `/v5/order/amend` |
| `cancel_order(category, symbol, order_id=None, order_link_id=None)` | `/v5/order/cancel` |
| `cancel_all_orders(category, symbol='', settle_coin='')` | `/v5/order/cancel-all` |
| `get_orders(category, symbol='', limit=20)` | `/v5/order/realtime` |
| `get_order_history(category, symbol='', limit=50)` | `/v5/order/history` |

**Positions**

| Method | Endpoint |
|--------|----------|
| `get_positions(category, symbol='')` | `/v5/position/list` |
| `set_leverage(category, symbol, leverage)` | `/v5/position/set-leverage` |
| `set_trading_stop(category, symbol, take_profit=None, stop_loss=None, trailing_stop=None, position_idx=0, **extra)` | `/v5/position/trading-stop` |
| `switch_margin_mode(category, symbol, trade_mode, leverage)` | `/v5/position/switch-isolated` |
| `switch_position_mode(category, mode, symbol='', coin='')` | `/v5/position/switch-mode` |
| `get_closed_pnl(category, symbol='', limit=50)` | `/v5/position/closed-pnl` |

**Account**

| Method | Endpoint |
|--------|----------|
| `get_wallet_balance(account_type, coin='')` | `/v5/account/wallet-balance` |
| `get_account_info()` | `/v5/account/info` |
| `get_fee_rates(category, symbol='')` | `/v5/account/fee-rate` |
| `get_transaction_log(account_type='UNIFIED', category='', currency='', limit=50)` | `/v5/account/transaction-log` |

### `client.ws` — `ByBitWebSocketManager`

**Public streams:** `subscribe_to_ticker`, `subscribe_to_orderbook`,
`subscribe_to_public_trades`, `subscribe_to_kline`, `subscribe_to_liquidations`.

**Private streams:** `subscribe_to_order`, `subscribe_to_execution`,
`subscribe_to_position`, `subscribe_to_wallet`, `subscribe_to_greeks`.

**Management:** `unsubscribe(topic)`, `close_all()`.

Public subscriptions take `(category, symbol, on_message, ...)`; private ones
take `(on_message)`. Every subscribe method returns the topic string.

## Examples

The [`examples/`](examples) directory contains runnable scripts:

| File | What it shows |
|------|---------------|
| [`stream_tickers.py`](examples/stream_tickers.py) | Streaming public ticker data |
| [`stream_private.py`](examples/stream_private.py) | Private order/position/wallet streams |
| [`rest_api.py`](examples/rest_api.py) | REST trading and market-data calls |
| [`error_handling.py`](examples/error_handling.py) | Catching API and HTTP errors |
| [`generate_card.py`](examples/generate_card.py) | Rendering a trading card |

## Contributing

Contributions are welcome. The project uses [uv](https://docs.astral.sh/uv/) and
[ruff](https://docs.astral.sh/ruff/):

```bash
uv sync --all-extras --dev
uv run ruff check .
uv run ruff format --check .
uv run pytest -q
```

Please open an issue or pull request. CI runs lint, formatting and the test
suite on Python 3.10–3.13.

## License

Released under the [MIT License](LICENSE).

## Disclaimer

This software is provided for educational and development purposes and is not
affiliated with Bybit. Trading cryptocurrencies carries risk; use it at your own
risk. The authors accept no responsibility for any financial loss.

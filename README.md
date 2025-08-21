# AioPyBit - Python Client for ByBit API (v5)

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![ByBit API](https://img.shields.io/badge/ByBit%20API-v5-green.svg)](https://bybit-exchange.github.io/docs/v5/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

AioPyBit is a modern and convenient Python client for the [ByBit](https://www.bybit.com/invite?ref=D0B6GN) cryptocurrency exchange API (v5). The module provides real-time access to market data and private account information via efficient WebSocket connections, and also supports HTTP requests with advanced error handling and auto-retry mechanisms.

## 🚀 Features

- **🔗 Advanced WebSocket Manager**: Unified manager for multiple connections and subscriptions
- **📊 Real-time Market Data**: Access live ticker, orderbook, trades, and kline data
- **👤 Private Account Streams**: Monitor orders, executions, positions, and wallet balances
- **🌍 Multiple Environments**: Support for mainnet, testnet, and demo environments
- **💪 Robust Connection Management**: Automatic ping/pong, error handling, and reconnection
- **🔄 Enhanced Retry Mechanism**: HTTP requests with exponential backoff retry
- **⚡ Auto-Reconnection**: WebSocket automatic reconnection with subscription restoration
- **📝 Subscription Management**: Easy subscribe/unsubscribe with pattern matching
- **🛡️ Type-Safe**: Full type annotations with protocol definitions
- **🎯 Easy Integration**: Simple async/await interface with callback handlers
- **🧹 Connection Cleanup**: Graceful cleanup and resource management

## 📋 Requirements

- Python 3.10+
- `websockets` >= 10.0
- `aiohttp` >= 3.8.0
- `asyncio` (built-in)

## 🛠️ Installation

```bash
pip install aiopybit

# The module is ready to use - no separate installation needed
```

## 🏗️ Architecture

### Core Components

- **`ByBitWebSocketManager`**: High-level manager for multiple WebSocket connections
- **`ByBitWebSocketClient`**: Low-level WebSocket client with connection management
- **`ByBitPublicStreamsMixin`**: Methods for public market data streams
- **`ByBitPrivateStreamsMixin`**: Methods for private account data streams
- **Protocol Definitions**: Type-safe interfaces in `protocols.py`

### Supported Streams

#### Public Streams (No Authentication Required)
- **Tickers**: Real-time price and volume data
- **Orderbook**: Live order book updates with configurable depth
- **Public Trades**: Recent trade executions
- **Klines/Candlesticks**: OHLCV data with various intervals
- **Liquidations**: Liquidation events

#### Private Streams (API Credentials Required)
- **Orders**: Real-time order status updates
- **Executions**: Trade execution notifications
- **Positions**: Position changes and P&L updates
- **Wallet**: Account balance updates
- **Greeks**: Option portfolio greeks (for options accounts)

## 🔧 Quick Start

### Simple WebSocket Manager Usage

```python
import asyncio
from aiopybit import ByBitClient


client = ByBitClient(API_KEY, API_SECRET, MODE)


async def handle_ticker(data):
	ticker = data.get('data', {})
	symbol = ticker.get('symbol', 'N/A')
	price = ticker.get('lastPrice', 'N/A')
	print(f'📊 {symbol}: ${price}')


async def main():
	await client.ws.subscribe_to_ticker(
		category='spot', symbol='BTCUSDT', on_message=handle_ticker
	)
	try:
		while True:
			await asyncio.sleep(1)
	except KeyboardInterrupt:
		pass

	await client.close()


if __name__ == '__main__':
	asyncio.run(main())
```

The `examples/` directory contains comprehensive usage examples:


## 🔐 Authentication

For private streams, you need ByBit API credentials:

1. Create account at [ByBit](https://www.bybit.com/invite?ref=D0B6GN)
2. Go to [API Management](https://www.bybit.com/app/user/api-management)
3. Create new API key with appropriate permissions
4. Use testnet for development: [ByBit Testnet](https://testnet.bybit.com/)

### Required Permissions for Private Streams
- **Read**: For position, wallet, and order data
- **Trade**: For order and execution streams (if trading)

## 🌐 Supported Environments

| Environment | Description | WebSocket URLs |
|-------------|-------------|----------------|
| `mainnet` | Production environment | `wss://stream.bybit.com/v5/` |
| `testnet` | Testing environment | `wss://stream-testnet.bybit.com/v5/` |
| `demo` | Demo environment (limited features) | `wss://stream-demo.bybit.com/v5/` |

## 📊 Market Categories

| Category | Description | Supported Streams |
|----------|-------------|-------------------|
| `linear` | USDT/USDC perpetual contracts | All public streams |
| `spot` | Spot trading pairs | Tickers, orderbook, trades |
| `option` | Options contracts | All public + greeks |

## 🔄 Connection Management

The client includes robust connection management features:

- **Automatic Ping/Pong**: Maintains connection with 20-second intervals
- **Error Handling**: Graceful handling of connection errors
- **Resource Cleanup**: Proper cleanup of tasks and connections

## 📖 API Reference

### ByBitWebSocketManager

High-level WebSocket manager for multiple connections and subscriptions.

#### Constructor Parameters
- `mode`: Environment ('mainnet', 'testnet', 'demo')
- `api_key`: ByBit API key (required for private streams)
- `api_secret`: ByBit API secret (required for private streams)
- `ping_interval`: Ping interval in seconds (default: 20)
- `ping_timeout`: Ping timeout in seconds (default: 10)
- `auto_reconnect`: Enable auto-reconnection (default: True)

#### Connection Management Methods
- `get_websocket(channel_type)`: Get or create WebSocket for channel
- `close_all()`: Close all WebSocket connections

### Public Stream Methods
- `subscribe_to_ticker(category, symbol, on_message)`
- `subscribe_to_orderbook(category, symbol, on_message, depth)`
- `subscribe_to_public_trades(category, symbol, on_message)`
- `subscribe_to_kline(category, symbol, interval, on_message)`
- `subscribe_to_liquidations(category, symbol, on_message)`

### Private Stream Methods
- `subscribe_to_order(on_message)`
- `subscribe_to_execution(on_message)`
- `subscribe_to_position(on_message)`
- `subscribe_to_wallet(on_message)`
- `subscribe_to_greeks(on_message)`

### ByBitWebSocketClient

Low-level WebSocket client class with connection management.

#### Constructor Parameters
- `url`: WebSocket URL
- `api_key`: ByBit API key (optional for public streams)
- `api_secret`: ByBit API secret (optional for public streams)
- `ping_interval`: Ping interval in seconds (default: 20)
- `ping_timeout`: Ping timeout in seconds (default: 10)
- `auto_reconnect`: Enable auto-reconnection (default: True)

## 📝 Logging

Enable logging to monitor connection status and debug issues:

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)

# Set specific logger levels
logging.getLogger('aiopybit').setLevel(logging.INFO)

# For detailed debugging
logging.getLogger('aiopybit').setLevel(logging.DEBUG)
```

Log levels:
- `DEBUG`: Detailed connection and message information
- `INFO`: Connection status and important events  
- `WARNING`: Connection issues and recoverable errors
- `ERROR`: Critical errors and failures

Example log output:
```
2024-01-15 10:30:45 [INFO] aiopybit: WebSocket connection for wss://stream.bybit.com/v5/public/linear established
2024-01-15 10:30:45 [INFO] aiopybit: ✅ Subscribed to tickers.BTCUSDT
2024-01-15 10:30:46 [DEBUG] aiopybit: Sending ping for wss://stream.bybit.com/v5/public/linear
2024-01-15 10:31:05 [INFO] aiopybit: 📊 BTCUSDT: $45,123.45
```

## 🔗 Related Links

- [ByBit Official Website](https://www.bybit.com/)
- [ByBit API Documentation](https://bybit-exchange.github.io/docs/v5/intro)
- [ByBit WebSocket Documentation](https://bybit-exchange.github.io/docs/v5/ws/connect)
- [ByBit Testnet](https://testnet.bybit.com/)
- [ByBit API Management](https://www.bybit.com/app/user/api-management)
- [ByBit Referal Program](https://www.bybit.com/invite?ref=D0B6GN)

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## ⚠️ Disclaimer

This software is for educational and development purposes. Use at your own risk. The authors are not responsible for any financial losses incurred through the use of this software.

---

**Happy Trading! 🚀**

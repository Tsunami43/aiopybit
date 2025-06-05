"""Tests for WebSocket subscription topic construction."""

import pytest

from aiopybit.websocket_manager import ByBitWebSocketManager
from aiopybit.websocket_methods.market_streams import ByBitPublicStreamsMixin
from aiopybit.websocket_methods.private_streams import ByBitPrivateStreamsMixin


class FakeWebSocket:
	def __init__(self) -> None:
		self.topic_handlers: dict = {}
		self.sent: list[dict] = []

	async def send(self, **kwargs) -> None:
		self.sent.append(kwargs)

	async def unsubscribe(self, topic: str) -> bool:
		self.topic_handlers.pop(topic, None)
		return True


class FakeManager(ByBitPublicStreamsMixin, ByBitPrivateStreamsMixin):
	def __init__(self) -> None:
		self.ws = FakeWebSocket()
		self.requested_channels: list[str] = []

	async def get_websocket(self, channel_type: str):
		self.requested_channels.append(channel_type)
		return self.ws


@pytest.fixture
def manager() -> FakeManager:
	return FakeManager()


async def test_ticker_topic(manager):
	async def handler(_):
		pass

	topic = await manager.subscribe_to_ticker('spot', 'BTCUSDT', handler)
	assert topic == 'tickers.BTCUSDT'
	assert manager.requested_channels == ['public.spot']
	assert manager.ws.topic_handlers['tickers.BTCUSDT'] is handler
	assert manager.ws.sent[-1] == {'op': 'subscribe', 'args': ['tickers.BTCUSDT']}


async def test_orderbook_topic_includes_depth(manager):
	topic = await manager.subscribe_to_orderbook(
		'linear', 'BTCUSDT', lambda _: None, depth=50
	)
	assert topic == 'orderbook.50.BTCUSDT'


async def test_kline_topic(manager):
	topic = await manager.subscribe_to_kline('linear', 'ETHUSDT', '15', lambda _: None)
	assert topic == 'kline.15.ETHUSDT'


async def test_greeks_uses_private_channel(manager):
	topic = await manager.subscribe_to_greeks(lambda _: None)
	assert topic == 'greeks'
	assert manager.requested_channels == ['private']


def test_inverse_public_url_present():
	for env in ('mainnet', 'testnet'):
		assert 'inverse' in ByBitWebSocketManager.WSS_URLS[env]['public']

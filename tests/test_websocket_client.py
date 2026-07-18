"""Tests for the low-level WebSocket client reconnect backoff."""

from aiopybit.websocket_client import ByBitWebSocketClient


def _client(**kwargs) -> ByBitWebSocketClient:
	return ByBitWebSocketClient(url='wss://example.test/v5/public/linear', **kwargs)


def test_reconnect_delay_is_exponential():
	client = _client(reconnect_backoff_base=1.0, reconnect_backoff_max=60.0)
	assert client._reconnect_delay(0) == 1.0
	assert client._reconnect_delay(1) == 2.0
	assert client._reconnect_delay(2) == 4.0
	assert client._reconnect_delay(3) == 8.0


def test_reconnect_delay_is_capped():
	client = _client(reconnect_backoff_base=1.0, reconnect_backoff_max=10.0)
	assert client._reconnect_delay(20) == 10.0


def test_reconnect_defaults():
	client = _client()
	assert client.auto_reconnect is True
	assert client.max_reconnect_attempts == 0  # 0 == retry indefinitely
	assert client.reconnect_backoff_max == 60.0

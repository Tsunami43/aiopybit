"""Tests for REST method mixins: endpoint routing and payload building."""

import json

import pytest

from aiopybit.http_methods.account_methods import AccountMixin
from aiopybit.http_methods.market_methods import MarketMixin
from aiopybit.http_methods.order_methods import OrderMixin
from aiopybit.http_methods.position_methods import PositionMixin


class FakeClient(MarketMixin, OrderMixin, PositionMixin, AccountMixin):
	"""Combine every REST mixin over a recording _request."""

	def __init__(self) -> None:
		self.calls: list[tuple[str, str, str]] = []

	async def _request(self, endpoint, method, payload=''):
		self.calls.append((endpoint, method, payload))
		return {'retCode': 0, 'result': {}}

	@property
	def last(self):
		return self.calls[-1]


@pytest.fixture
def client() -> FakeClient:
	return FakeClient()


async def test_get_tickers_routing(client):
	await client.get_tickers('linear', 'BTCUSDT')
	endpoint, method, payload = client.last
	assert endpoint == '/v5/market/tickers'
	assert method == 'GET'
	assert payload == 'category=linear&symbol=BTCUSDT'


async def test_get_klines_optional_time_range(client):
	await client.get_klines('linear', 'BTCUSDT', '15', limit=10, start=1, end=2)
	_, _, payload = client.last
	assert 'interval=15' in payload
	assert 'start=1' in payload and 'end=2' in payload


async def test_instruments_info_added(client):
	await client.get_instruments_info('linear', 'BTCUSDT')
	assert client.last[0] == '/v5/market/instruments-info'


async def test_create_order_serialises_extra_params(client):
	await client.create_order(
		'linear', 'BTCUSDT', 'Buy', 'Limit', 0.1, price=100,
		time_in_force='PostOnly', takeProfit='120',
	)
	endpoint, method, payload = client.last
	assert endpoint == '/v5/order/create'
	assert method == 'POST'
	body = json.loads(payload)
	assert body['timeInForce'] == 'PostOnly'
	assert body['takeProfit'] == '120'
	assert body['qty'] == '0.1'


async def test_cancel_all_orders(client):
	await client.cancel_all_orders('linear', settle_coin='USDT')
	endpoint, _, payload = client.last
	assert endpoint == '/v5/order/cancel-all'
	assert json.loads(payload)['settleCoin'] == 'USDT'


async def test_cancel_order_requires_id(client):
	with pytest.raises(ValueError):
		await client.cancel_order('linear', 'BTCUSDT')


async def test_set_trading_stop(client):
	await client.set_trading_stop('linear', 'BTCUSDT', take_profit=100, stop_loss=90)
	endpoint, _, payload = client.last
	assert endpoint == '/v5/position/trading-stop'
	body = json.loads(payload)
	assert body['takeProfit'] == '100'
	assert body['stopLoss'] == '90'


async def test_get_fee_rates(client):
	await client.get_fee_rates('linear')
	assert client.last[0] == '/v5/account/fee-rate'

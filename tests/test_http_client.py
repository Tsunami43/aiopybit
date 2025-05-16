"""Tests for the low-level HTTP client: signing and response handling."""

import pytest

from aiopybit.exceptions import ByBitAPIError
from aiopybit.http_client import ByBitHttpClient


def test_signature_and_header_share_one_timestamp(http_client, monkeypatch):
	"""Regression: signature and X-BAPI-TIMESTAMP must use the same value."""
	timestamps = iter(['1700000000000', '1700000000999'])
	monkeypatch.setattr(
		ByBitHttpClient, '_timestamp', staticmethod(lambda: next(timestamps))
	)

	headers = http_client._get_headers('symbol=BTCUSDT')
	expected_sig = http_client._generate_signature(
		headers['X-BAPI-TIMESTAMP'], 'symbol=BTCUSDT'
	)

	assert headers['X-BAPI-TIMESTAMP'] == '1700000000000'
	assert headers['X-BAPI-SIGN'] == expected_sig


def test_signature_is_deterministic(http_client):
	sig1 = http_client._generate_signature('1700000000000', 'a=1')
	sig2 = http_client._generate_signature('1700000000000', 'a=1')
	assert sig1 == sig2
	assert sig1 != http_client._generate_signature('1700000000001', 'a=1')


def test_check_response_passes_on_zero_ret_code(http_client):
	payload = {'retCode': 0, 'result': {'ok': True}}
	assert http_client._check_response(payload) is payload


def test_check_response_raises_on_non_zero_ret_code(http_client):
	with pytest.raises(ByBitAPIError) as exc_info:
		http_client._check_response({'retCode': 10001, 'retMsg': 'params error'})

	assert exc_info.value.ret_code == 10001
	assert exc_info.value.ret_msg == 'params error'


def test_get_session_is_reused(http_client):
	# The session is created lazily; the same instance is returned each time.
	import asyncio

	async def _run():
		s1 = http_client._get_session()
		s2 = http_client._get_session()
		assert s1 is s2
		await http_client.close()
		assert http_client._session is None

	asyncio.run(_run())

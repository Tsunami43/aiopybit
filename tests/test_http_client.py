"""Tests for the low-level HTTP client: signing and response handling."""

import base64

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


# -- Time synchronisation --------------------------------------------------


def test_time_offset_applied_to_timestamp(http_client):
	http_client._time_offset_ms = 0
	base = int(http_client._timestamp())
	http_client._time_offset_ms = 60_000
	shifted = int(http_client._timestamp())
	assert 59_000 <= (shifted - base) <= 61_000


# -- Rate-limit backoff ----------------------------------------------------


def test_rate_limit_wait_uses_reset_header(http_client):
	now = 1_000_000
	assert http_client._rate_limit_wait(str(now + 2000), now, 0) == pytest.approx(2.0)


def test_rate_limit_wait_is_clamped(http_client):
	now = 1_000_000
	wait = http_client._rate_limit_wait(str(now + 999_999), now, 0)
	assert wait == http_client.rate_limit_max_wait


def test_rate_limit_wait_never_negative(http_client):
	now = 1_000_000
	assert http_client._rate_limit_wait(str(now - 5000), now, 0) == 0.0


def test_rate_limit_wait_falls_back_to_backoff(http_client):
	# No header -> retry_delay * 2**attempt = 1.0 * 2 = 2.0
	assert http_client._rate_limit_wait(None, 1_000_000, 1) == pytest.approx(2.0)


# -- Signing key type ------------------------------------------------------


def test_hmac_secret_not_detected_as_rsa(http_client):
	assert http_client._is_rsa is False


def test_rsa_key_detected_and_signature_verifies():
	pytest.importorskip('cryptography')
	from cryptography.hazmat.primitives import hashes, serialization
	from cryptography.hazmat.primitives.asymmetric import padding, rsa

	key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
	pem = key.private_bytes(
		serialization.Encoding.PEM,
		serialization.PrivateFormat.PKCS8,
		serialization.NoEncryption(),
	).decode()

	client = ByBitHttpClient(url='https://x', api_key='k', secret_key=pem)
	assert client._is_rsa is True

	signature = client._generate_signature('1700000000000', 'a=1')
	param_str = '1700000000000' + 'k' + client.recv_window + 'a=1'
	# Raises InvalidSignature if the signature does not match.
	key.public_key().verify(
		base64.b64decode(signature),
		param_str.encode(),
		padding.PKCS1v15(),
		hashes.SHA256(),
	)

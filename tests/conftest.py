"""Shared test fixtures and helpers."""

import pytest

from aiopybit.http_client import ByBitHttpClient


class RecordingHttpClient(ByBitHttpClient):
	"""HTTP client whose _request records calls instead of hitting the network."""

	def __init__(self) -> None:
		super().__init__(url='https://example.test', api_key='key', secret_key='secret')
		self.calls: list[tuple[str, str, str]] = []
		self.next_response: dict = {'retCode': 0, 'result': {}}

	async def _request(self, endpoint: str, method: str, payload: str = '') -> dict:
		self.calls.append((endpoint, method, payload))
		return self.next_response

	@property
	def last_call(self) -> tuple[str, str, str]:
		return self.calls[-1]


@pytest.fixture
def http_client() -> ByBitHttpClient:
	"""A real HTTP client with dummy credentials (no network calls made)."""
	return ByBitHttpClient(
		url='https://example.test', api_key='key', secret_key='secret'
	)

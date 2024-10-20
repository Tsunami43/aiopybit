"""Exception hierarchy for the AioPyBit client.

All errors raised by the library derive from :class:`ByBitError`, so callers
can catch that single base class to handle any failure originating from
AioPyBit.
"""

from __future__ import annotations


class ByBitError(Exception):
	"""Base class for every error raised by AioPyBit."""


class ByBitHTTPError(ByBitError):
	"""Raised when the transport layer returns a non-successful HTTP status."""

	def __init__(self, status: int, message: str = '') -> None:
		self.status = status
		self.message = message
		super().__init__(f'HTTP {status}: {message}' if message else f'HTTP {status}')


class ByBitAPIError(ByBitError):
	"""Raised when ByBit answers with a non-zero ``retCode``.

	Attributes:
		ret_code: The ``retCode`` returned by the API.
		ret_msg: The human-readable ``retMsg`` returned by the API.
		response: The full decoded JSON response, for further inspection.
	"""

	def __init__(self, ret_code: int, ret_msg: str, response: dict | None = None) -> None:
		self.ret_code = ret_code
		self.ret_msg = ret_msg
		self.response = response or {}
		super().__init__(f'[{ret_code}] {ret_msg}')


class ByBitAuthError(ByBitError):
	"""Raised when authentication fails (missing credentials or bad signature)."""

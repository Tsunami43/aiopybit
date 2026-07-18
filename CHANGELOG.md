# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.4.0] - 2026-07-18

### Added

- Optional trading card generator (`aiopybit.cards.BybitCardGenerator`) behind
  the `cards` extra, with bundled background and IBM Plex Sans fonts.
- `Literal`-typed REST signatures and a `ByBitResponse` TypedDict return type;
  the response/enum types are exported from the package root.
- HTTP resilience: automatic clock sync on timestamp errors (`sync_time()`),
  rate-limit-aware retries (HTTP 429/403 and retCodes 10006/10018), a
  configurable `recv_window`, and RSA API-key signing behind the `rsa` extra.
- WebSocket reconnection now uses exponential backoff with jitter and a
  configurable attempt cap.
- GitHub Actions workflow to publish to PyPI on `v*` tags.
- Trove classifiers (Python 3.10–3.13, typed, async) in the package metadata.

### Changed

- Rewrote the README with a professional, library-style layout.

## [0.3.0] - 2025-12-15

### Added

- Exception hierarchy (`ByBitError`, `ByBitHTTPError`, `ByBitAPIError`,
  `ByBitAuthError`) with automatic `retCode`/HTTP-status validation.
- Persistent, reusable `aiohttp` session with connection pooling and a
  configurable request timeout.
- `async with ByBitClient(...)` context manager that releases the HTTP session
  and all WebSocket connections on exit.
- REST endpoints: `get_server_time`, `get_instruments_info`,
  `get_recent_trades`, `get_funding_rate_history`, `get_open_interest`,
  `cancel_all_orders`, `get_order_history`, `get_account_info`,
  `get_fee_rates`, `get_transaction_log`, `set_trading_stop`,
  `switch_margin_mode`, `switch_position_mode`, `get_closed_pnl`.
- `create_order` now accepts `time_in_force`, `order_link_id`, `reduce_only`
  and arbitrary extra ByBit parameters (TP/SL, trigger price, ...).
- WebSocket: `subscribe_to_greeks`, the inverse public endpoint, and a
  manager-level `unsubscribe(topic)` helper.
- `py.typed` marker (PEP 561) and `Literal`-typed public stream methods.
- A hatchling build backend so the package can be built and installed.
- pytest test suite and a GitHub Actions CI pipeline (lint, format, tests).

### Fixed

- Signed requests failed authentication because the signature and the
  `X-BAPI-TIMESTAMP` header were computed from two different timestamps. A
  single timestamp is now reused for both.

## [0.1.2] - 2024-08-30

### Added

- Initial public release: WebSocket manager with public/private streams,
  auto-reconnection, and a REST client with retry/backoff.

[Unreleased]: https://github.com/Tsunami43/aiopybit/compare/v0.4.0...HEAD
[0.4.0]: https://github.com/Tsunami43/aiopybit/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/Tsunami43/aiopybit/compare/v0.1.2...v0.3.0
[0.1.2]: https://github.com/Tsunami43/aiopybit/releases/tag/v0.1.2

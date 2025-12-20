"""Tests for the trading card generator (skipped when Pillow is absent)."""

import pytest

pytest.importorskip('PIL')

from aiopybit.cards import BybitCardGenerator  # noqa: E402


@pytest.fixture
def generator() -> BybitCardGenerator:
	return BybitCardGenerator()


def test_roi_long_is_leveraged():
	# +10% move at 10x leverage -> +100% ROI.
	roi = BybitCardGenerator._calculate_roi(100.0, 110.0, 'Long', 10)
	assert roi == pytest.approx(100.0)


def test_roi_short_inverts_direction():
	# Price up 10% on a short at 10x -> -100% ROI.
	roi = BybitCardGenerator._calculate_roi(100.0, 110.0, 'Short', 10)
	assert roi == pytest.approx(-100.0)


def test_roi_zero_entry_is_safe():
	assert BybitCardGenerator._calculate_roi(0.0, 100.0, 'Long', 10) == 0.0


def test_generate_card_dimensions(generator):
	card = generator.generate_card('BTCUSDT', 'Long', 100, 20000, 41850.5)
	assert card.size == (generator.base_width, generator.base_height)


def test_get_card_bytes_returns_png(generator):
	data = generator.get_card_bytes('ETHUSDT', 'Short', 25, 3200, 2980)
	# PNG magic number.
	assert data[:8] == b'\x89PNG\r\n\x1a\n'


def test_unsupported_format_raises(generator):
	with pytest.raises(ValueError):
		generator.get_card_bytes('BTCUSDT', 'Long', 10, 100, 110, image_format='GIF')

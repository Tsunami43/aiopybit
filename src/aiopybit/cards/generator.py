"""Bybit-style trading card image generator.

Renders a compact PnL/ROI card (the kind Bybit lets you share for a position)
onto a background image. Requires the optional ``Pillow`` dependency:

    pip install "aiopybit[cards]"
"""

from __future__ import annotations

import io
from contextlib import contextmanager
from pathlib import Path
from typing import Literal

try:
	from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
except ImportError as exc:  # pragma: no cover - exercised only without Pillow
	raise ImportError(
		'The card generator requires Pillow. '
		"Install it with: pip install 'aiopybit[cards]'"
	) from exc

Side = Literal['Long', 'Short']

_ASSETS_DIR = Path(__file__).parent / 'assets'
_DEFAULT_BACKGROUND = _ASSETS_DIR / 'background.png'
_DEFAULT_FONTS_DIR = _ASSETS_DIR / 'fonts' / 'IBM Plex Sans'


class BybitCardGenerator:
	"""Generate shareable Bybit-style trading cards.

	The card shows the trading pair, direction/leverage badge, ROI (computed
	automatically from the prices, direction and leverage) and the entry and
	market prices.
	"""

	def __init__(
		self,
		background_image_path: str | Path = _DEFAULT_BACKGROUND,
		fonts_dir: str | Path = _DEFAULT_FONTS_DIR,
	) -> None:
		"""Initialise the generator.

		Args:
			background_image_path: Path to the background image. Defaults to the
				bundled Bybit-style background.
			fonts_dir: Directory containing the IBM Plex Sans ``.ttf`` files.
				Defaults to the bundled fonts.
		"""
		self.background_image_path = str(background_image_path)
		self.fonts_dir = str(fonts_dir)
		self.scale = 4  # Supersampling factor for crisp rendering.

		self.base_width = 400
		self.base_height = 240

		self.colors = {
			'white': (255, 255, 255),
			'gray_text': (173, 177, 184),
			'green_positive': (28, 158, 96),
			'red_negative': (255, 71, 87),
			'long_bg': (25, 145, 88, 40),
			'long_border': (25, 145, 88),
			'short_bg': (255, 71, 87, 40),
			'short_border': (255, 71, 87),
		}

	def _get_font(self, size: int, weight: str = 'Regular') -> ImageFont.FreeTypeFont:
		"""Load an IBM Plex Sans font at the (scaled) size."""
		font_mapping = {
			'Regular': 'IBMPlexSans-Regular.ttf',
			'Medium': 'IBMPlexSans-Medium.ttf',
			'SemiBold': 'IBMPlexSans-SemiBold.ttf',
			'Bold': 'IBMPlexSans-Bold.ttf',
		}
		font_file = font_mapping.get(weight, 'IBMPlexSans-Regular.ttf')
		font_path = Path(self.fonts_dir) / font_file
		scaled_size = int(size * self.scale)

		try:
			return ImageFont.truetype(str(font_path), scaled_size)
		except OSError:
			return ImageFont.load_default()

	def _scale_pos(self, x: int, y: int) -> tuple[int, int]:
		return (x * self.scale, y * self.scale)

	def _scale_value(self, value: int) -> int:
		return value * self.scale

	def _draw_rounded_rect(self, draw, coords, radius, fill) -> None:
		"""Draw a filled rectangle with rounded corners."""
		x1, y1, x2, y2 = coords
		draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill)
		draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill)
		draw.pieslice([x1, y1, x1 + 2 * radius, y1 + 2 * radius], 180, 270, fill=fill)
		draw.pieslice([x2 - 2 * radius, y1, x2, y1 + 2 * radius], 270, 360, fill=fill)
		draw.pieslice([x1, y2 - 2 * radius, x1 + 2 * radius, y2], 90, 180, fill=fill)
		draw.pieslice([x2 - 2 * radius, y2 - 2 * radius, x2, y2], 0, 90, fill=fill)

	@staticmethod
	def _format_price(price: float) -> str:
		if isinstance(price, (int, float)):
			return f'{price:,.2f}'.replace(',', ' ')
		return str(price)

	@staticmethod
	def _format_roi(roi: float) -> str:
		sign = '+' if roi >= 0 else ''
		return f'{sign}{roi:.2f}%'

	@staticmethod
	def _calculate_roi(
		entry_price: float, market_price: float, direction: Side, leverage: float
	) -> float:
		"""Compute ROI from prices, direction and leverage."""
		if entry_price <= 0:
			return 0.0

		price_change_pct = (market_price - entry_price) / entry_price
		if direction.lower() == 'short':
			price_change_pct = -price_change_pct
		return price_change_pct * leverage * 100

	def generate_card(
		self,
		symbol: str,
		direction: Side,
		leverage: float,
		entry_price: float,
		market_price: float,
	) -> Image.Image:
		"""Render the card and return it as a PIL image.

		Args:
			symbol: Trading pair, e.g. ``'BTCUSDT'``.
			direction: ``'Long'`` or ``'Short'``.
			leverage: Position leverage, e.g. ``100``.
			entry_price: Position entry price.
			market_price: Current market price.

		Returns:
			The rendered card as a :class:`PIL.Image.Image`.
		"""
		roi = self._calculate_roi(entry_price, market_price, direction, leverage)

		width = self.base_width * self.scale
		height = self.base_height * self.scale
		img = Image.new('RGB', (width, height), color=(0, 0, 0))

		bg_img = Image.open(self.background_image_path)
		if bg_img.mode != 'RGB':
			# Route palette/transparency images through RGBA (Pillow's
			# recommended path) before flattening to RGB.
			bg_img = bg_img.convert('RGBA').convert('RGB')
		bg_img = bg_img.resize((width, height), Image.Resampling.LANCZOS)
		bg_img = ImageEnhance.Sharpness(bg_img).enhance(1.1)
		bg_img = ImageEnhance.Contrast(bg_img).enhance(1.05)
		img.paste(bg_img, (0, 0))

		draw = ImageDraw.Draw(img)

		font_symbol = self._get_font(20, 'SemiBold')
		font_side = self._get_font(10, 'Bold')
		font_roi_label = self._get_font(12, 'Regular')
		font_roi_value = self._get_font(34, 'Bold')
		font_price_label = self._get_font(12, 'Regular')
		font_price_value = self._get_font(16, 'SemiBold')

		is_long = direction.lower() == 'long'
		is_positive = roi >= 0

		badge_bg = self.colors['long_bg'] if is_long else self.colors['short_bg']
		badge_border = (
			self.colors['long_border'] if is_long else self.colors['short_border']
		)
		roi_color = (
			self.colors['green_positive']
			if is_positive
			else self.colors['red_negative']
		)

		# 1. Trading pair symbol with drop shadow.
		symbol_x, symbol_y = self._scale_pos(20, 59)
		shadow_offset = self._scale_value(2)
		for dx in range(-shadow_offset, shadow_offset + 1):
			for dy in range(-shadow_offset, shadow_offset + 1):
				if dx or dy:
					draw.text(
						(symbol_x + dx, symbol_y + dy),
						symbol,
						fill=(0, 0, 0),
						font=font_symbol,
					)
		draw.text(
			(symbol_x, symbol_y), symbol, fill=self.colors['white'], font=font_symbol
		)

		# 2. Direction / leverage badge.
		side_text = f'{direction} {leverage:g}x'
		symbol_bbox = draw.textbbox((0, 0), symbol, font=font_symbol)
		symbol_width = symbol_bbox[2] - symbol_bbox[0]
		side_x = symbol_x + symbol_width + self._scale_value(10)
		side_y = symbol_y + self._scale_value(6)

		side_bbox = draw.textbbox((0, 0), side_text, font=font_side)
		side_width = side_bbox[2] - side_bbox[0]
		side_height = self._scale_value(20)
		badge_coords = (
			side_x - self._scale_value(4),
			side_y - self._scale_value(3),
			side_x + side_width + self._scale_value(8),
			side_y + side_height - self._scale_value(3),
		)

		bg_alpha = badge_bg[3] / 255.0
		badge_bg_rgb = (
			int(bg_alpha * badge_bg[0]),
			int(bg_alpha * badge_bg[1]),
			int(bg_alpha * badge_bg[2]),
		)
		self._draw_rounded_rect(draw, badge_coords, self._scale_value(4), badge_bg_rgb)
		draw.text((side_x, side_y), side_text, fill=badge_border, font=font_side)

		# 3-4. ROI label and value.
		roi_x, roi_y = self._scale_pos(20, 95)
		draw.text(
			(roi_x, roi_y), 'ROI', fill=self.colors['gray_text'], font=font_roi_label
		)
		roi_value_x, roi_value_y = self._scale_pos(20, 111)
		draw.text(
			(roi_value_x, roi_value_y),
			self._format_roi(roi),
			fill=roi_color,
			font=font_roi_value,
		)

		# 5. Entry / market prices.
		entry_x, entry_y = self._scale_pos(20, 163)
		draw.text(
			(entry_x, entry_y),
			'Entry Price',
			fill=self.colors['gray_text'],
			font=font_price_label,
		)
		draw.text(
			(entry_x, entry_y + self._scale_value(16)),
			self._format_price(entry_price),
			fill=self.colors['white'],
			font=font_price_value,
		)

		market_x = entry_x + self._scale_value(126)
		draw.text(
			(market_x, entry_y),
			'Market Price',
			fill=self.colors['gray_text'],
			font=font_price_label,
		)
		draw.text(
			(market_x, entry_y + self._scale_value(16)),
			self._format_price(market_price),
			fill=self.colors['white'],
			font=font_price_value,
		)

		# Downscale for anti-aliasing, then sharpen.
		img = img.resize((self.base_width, self.base_height), Image.Resampling.LANCZOS)
		return img.filter(ImageFilter.UnsharpMask(radius=1, percent=110, threshold=2))

	def save_card(
		self,
		symbol: str,
		direction: Side,
		leverage: float,
		entry_price: float,
		market_price: float,
		output_path: str | Path,
	) -> str:
		"""Generate a card and write it to ``output_path`` as PNG."""
		card = self.generate_card(
			symbol, direction, leverage, entry_price, market_price
		)
		card.save(str(output_path), 'PNG', optimize=False, compress_level=1)
		return str(output_path)

	def get_card_buffer(
		self,
		symbol: str,
		direction: Side,
		leverage: float,
		entry_price: float,
		market_price: float,
		image_format: str = 'PNG',
	) -> io.BytesIO:
		"""Generate a card and return it as an in-memory buffer."""
		card = self.generate_card(
			symbol, direction, leverage, entry_price, market_price
		)
		buffer = io.BytesIO()
		fmt = image_format.upper()
		if fmt == 'PNG':
			card.save(buffer, format='PNG', optimize=False, compress_level=1)
		elif fmt == 'JPEG':
			card.save(buffer, format='JPEG', quality=95, optimize=True)
		elif fmt == 'WEBP':
			card.save(buffer, format='WEBP', quality=95, method=6)
		else:
			raise ValueError(f'Unsupported format: {image_format}')
		buffer.seek(0)
		return buffer

	def get_card_bytes(
		self,
		symbol: str,
		direction: Side,
		leverage: float,
		entry_price: float,
		market_price: float,
		image_format: str = 'PNG',
	) -> bytes:
		"""Generate a card and return the raw image bytes.

		Handy for sending directly to a Telegram/Discord bot.
		"""
		with self.get_card_buffer(
			symbol, direction, leverage, entry_price, market_price, image_format
		) as buffer:
			return buffer.getvalue()

	@contextmanager
	def card_buffer(
		self,
		symbol: str,
		direction: Side,
		leverage: float,
		entry_price: float,
		market_price: float,
		image_format: str = 'PNG',
	):
		"""Context manager yielding an image buffer that is closed on exit."""
		buffer = self.get_card_buffer(
			symbol, direction, leverage, entry_price, market_price, image_format
		)
		try:
			yield buffer
		finally:
			buffer.close()

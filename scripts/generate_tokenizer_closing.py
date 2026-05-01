"""Closing-slide background: faded token fragments.

Renders at low opacity so it sits quietly behind the closing quote. Target
placement is on a dark slide, so fragments are rendered in warm tones that
read on `#1A1814`.
"""
from __future__ import annotations

import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 640, 480
SCALE = 3
SW, SH = W * SCALE, H * SCALE

BG = (0, 0, 0, 0)
AMBER = (217, 119, 6)
AMBER_SOFT = (245, 158, 11)
STONE = (120, 113, 108)


def _s(v: float) -> int:
    return int(round(v * SCALE))


def _font(paths: list[str], size: int) -> ImageFont.ImageFont:
    for p in paths:
        try:
            return ImageFont.truetype(p, _s(size))
        except Exception:
            continue
    return ImageFont.load_default()


MONO_PATHS = [
    "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
]


def draw_chip(draw, x, y, text, font, color_rgb, alpha: int = 120, pad_x: float = 8, pad_y: float = 5):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = font.getbbox("A")[3] - font.getbbox("A")[1]
    chip_w = tw / SCALE + pad_x * 2
    chip_h = th / SCALE + pad_y * 2
    fill = (*color_rgb, max(0, alpha - 40))
    outline = (*color_rgb, alpha)
    draw.rounded_rectangle(
        [_s(x), _s(y), _s(x + chip_w), _s(y + chip_h)],
        radius=_s(5),
        fill=fill,
        outline=outline,
        width=_s(1.4),
    )
    # text in same color, slightly brighter
    text_alpha = min(255, alpha + 40)
    draw.text(
        (_s(x + pad_x) - bbox[0], _s(y + pad_y) - font.getbbox("A")[1]),
        text,
        fill=(*color_rgb, text_alpha),
        font=font,
    )
    return chip_w, chip_h


def generate(out_path: Path) -> None:
    img = Image.new("RGBA", (SW, SH), BG)
    draw = ImageDraw.Draw(img)

    random.seed(42)
    font = _font(MONO_PATHS, 13)

    # Scatter chips across the canvas in loose rows
    fragments = [
        "fetch", "User", "Data", "const", "=", "async",
        "()", "await", "load", "tokens", "ize", "api",
        "_key", "cache", "hit", " /", "json", "CLAUDE",
        ".md", "stack", "trace", "prompt", " v4.7", "split",
        "merge", "BPE", "pair", "count", "cost", "usd",
    ]
    # Two bands: top and bottom, leaving the middle clear for the quote
    bands = [(20, 150), (340, 440)]
    colors = [AMBER, AMBER_SOFT, STONE]

    for band_top, band_bottom in bands:
        y = band_top
        while y < band_bottom:
            x = 30 + random.uniform(-10, 10)
            while x < W - 30:
                text = random.choice(fragments)
                color = random.choice(colors)
                alpha = random.randint(90, 160)
                cw, ch = draw_chip(draw, x, y, text, font, color, alpha=alpha)
                x += cw + random.uniform(8, 20)
            y += 30 + random.uniform(-4, 4)

    final = img.resize((W, H), Image.LANCZOS)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    final.save(out_path, "PNG")
    print(f"Wrote {out_path} ({W}x{H})")


if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("assets/tokenizer-tax/closing.png")
    generate(out)

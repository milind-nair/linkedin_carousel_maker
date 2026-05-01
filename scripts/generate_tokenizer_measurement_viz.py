"""Horizontal bar chart of token-expansion ratios by content type.

For the light-background content slide (slide 2). Shows each content type's
measured expansion ratio, color-coded by severity. Target placement is
slot-style (roughly 460x220 in the slide).
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 640, 420
SCALE = 3
SW, SH = W * SCALE, H * SCALE

BG = (0, 0, 0, 0)
TEXT = (41, 37, 36, 255)
MUTED = (120, 113, 108, 255)
TRACK = (231, 229, 228, 255)
BASELINE = (168, 162, 158, 255)
RED = (220, 38, 38, 255)
AMBER = (217, 119, 6, 255)
GREEN = (5, 150, 105, 255)


def _s(v: float) -> int:
    return int(round(v * SCALE))


def _font(paths: list[str], size: int) -> ImageFont.ImageFont:
    for p in paths:
        try:
            return ImageFont.truetype(p, _s(size))
        except Exception:
            continue
    return ImageFont.load_default()


SANS_PATHS = [
    "/usr/share/fonts/truetype/google-fonts/Poppins-Light.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]
SANS_BOLD_PATHS = [
    "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]


def color_for(ratio: float) -> tuple[int, int, int, int]:
    if ratio >= 1.40:
        return RED
    if ratio >= 1.20:
        return AMBER
    return GREEN


def draw_text_at(draw, text, x, y, font, fill, anchor="lt") -> None:
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    if anchor == "rt":
        x_draw = _s(x) - tw
    elif anchor == "mt":
        x_draw = _s(x) - tw // 2
    else:
        x_draw = _s(x)
    y_draw = _s(y) - font.getbbox("A")[1]
    draw.text((x_draw - bbox[0] if anchor != "rt" else x_draw, y_draw), text, fill=fill, font=font)


def generate(out_path: Path) -> None:
    img = Image.new("RGBA", (SW, SH), BG)
    draw = ImageDraw.Draw(img)

    # Title
    title_font = _font(SANS_BOLD_PATHS, 14)
    draw_text_at(draw, "TOKEN EXPANSION BY CONTENT TYPE", W / 2, 16, title_font, MUTED, anchor="mt")

    # Data rows
    rows = [
        ("Technical docs", 1.47),
        ("CLAUDE.md", 1.445),
        ("User prompts", 1.373),
        ("Stack traces", 1.25),
        ("JSON / CJK", 1.05),
    ]

    # Layout
    label_col_w = 140
    label_x_right = label_col_w + 10
    bar_x0 = label_col_w + 20
    bar_x1 = W - 60
    bar_track_w = bar_x1 - bar_x0
    # Scale: 1.0 → 0, 1.5 → bar_track_w
    scale_min, scale_max = 1.0, 1.5

    def ratio_to_x(r: float) -> float:
        return bar_x0 + (r - scale_min) / (scale_max - scale_min) * bar_track_w

    row_top = 76
    row_h = 46
    bar_h = 22

    label_font = _font(SANS_BOLD_PATHS, 13)
    value_font = _font(SANS_BOLD_PATHS, 13)

    for i, (label, ratio) in enumerate(rows):
        y = row_top + i * row_h
        color = color_for(ratio)

        # Label (right-aligned to label_x_right)
        bbox = draw.textbbox((0, 0), label, font=label_font)
        tw = bbox[2] - bbox[0]
        draw.text(
            (_s(label_x_right) - tw - bbox[0], _s(y + bar_h / 2 - 6) - label_font.getbbox("A")[1]),
            label,
            fill=TEXT,
            font=label_font,
        )

        # Track
        draw.rounded_rectangle(
            [_s(bar_x0), _s(y), _s(bar_x1), _s(y + bar_h)],
            radius=_s(3),
            fill=TRACK,
        )
        # Filled bar
        fill_end = ratio_to_x(ratio)
        draw.rounded_rectangle(
            [_s(bar_x0), _s(y), _s(fill_end), _s(y + bar_h)],
            radius=_s(3),
            fill=color,
        )
        # Value label to the right of the bar
        val_text = f"{ratio:.2f}x"
        vb = draw.textbbox((0, 0), val_text, font=value_font)
        vw = vb[2] - vb[0]
        draw.text(
            (_s(fill_end + 6) - vb[0], _s(y + bar_h / 2 - 6) - value_font.getbbox("A")[1]),
            val_text,
            fill=color,
            font=value_font,
        )

    # Baseline tick at 1.0x
    base_x = ratio_to_x(1.0)
    draw.line(
        [(_s(base_x), _s(row_top - 8)), (_s(base_x), _s(row_top + len(rows) * row_h - 10))],
        fill=BASELINE,
        width=_s(1),
    )
    tick_font = _font(SANS_PATHS, 9)
    draw_text_at(draw, "1.0x", base_x, row_top - 18, tick_font, MUTED, anchor="mt")

    # Weighted average callout
    avg_x = ratio_to_x(1.325)
    avg_top = row_top + len(rows) * row_h + 8
    draw.line(
        [(_s(avg_x), _s(row_top - 4)), (_s(avg_x), _s(avg_top))],
        fill=AMBER,
        width=_s(1.6),
    )
    avg_label_font = _font(SANS_BOLD_PATHS, 11)
    draw_text_at(draw, "weighted avg  1.325x", avg_x, avg_top + 6, avg_label_font, AMBER, anchor="mt")

    # Footer caption
    cap_font = _font(SANS_PATHS, 10)
    draw_text_at(
        draw,
        "Measured on authentic Claude Code workloads",
        W / 2,
        H - 20,
        cap_font,
        MUTED,
        anchor="mt",
    )

    final = img.resize((W, H), Image.LANCZOS)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    final.save(out_path, "PNG")
    print(f"Wrote {out_path} ({W}x{H})")


if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("assets/tokenizer-tax/measurement-viz.png")
    generate(out)

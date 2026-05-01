"""Cost comparison bars: an 80-turn Claude Code session on 4.6 vs 4.7.

Two grouped bars with dollar-labels. Supports the comparison table on slide 3,
does not duplicate it. Light background (transparent PNG).
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 640, 440
SCALE = 3
SW, SH = W * SCALE, H * SCALE

BG = (0, 0, 0, 0)
TEXT = (41, 37, 36, 255)
MUTED = (120, 113, 108, 255)
TRACK = (231, 229, 228, 255)
AMBER = (217, 119, 6, 255)
AMBER_SOFT = (245, 158, 11, 255)
RED = (220, 38, 38, 255)
STONE = (120, 113, 108, 255)


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


def draw_text_anchored(draw, text, x, y, font, fill, anchor="lt") -> None:
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    if anchor == "rt":
        x_draw = _s(x) - tw
    elif anchor == "mt":
        x_draw = _s(x) - tw // 2
    else:
        x_draw = _s(x)
    y_draw = _s(y) - font.getbbox("A")[1]
    draw.text(
        (x_draw - (bbox[0] if anchor != "rt" else 0), y_draw),
        text,
        fill=fill,
        font=font,
    )


def generate(out_path: Path) -> None:
    img = Image.new("RGBA", (SW, SH), BG)
    draw = ImageDraw.Draw(img)

    # Title
    title_font = _font(SANS_BOLD_PATHS, 14)
    draw_text_anchored(
        draw,
        "80-TURN CLAUDE CODE SESSION",
        W / 2,
        16,
        title_font,
        MUTED,
        anchor="mt",
    )
    sub_font = _font(SANS_PATHS, 11)
    draw_text_anchored(
        draw,
        "identical workload, same per-token price",
        W / 2,
        38,
        sub_font,
        MUTED,
        anchor="mt",
    )

    # Chart area
    chart_top = 80
    chart_bottom = H - 70
    chart_h = chart_bottom - chart_top

    # Scale: y=chart_bottom is $0, y=chart_top is $10
    y_max = 10.0

    def cost_to_y(c: float) -> float:
        return chart_bottom - (c / y_max) * chart_h

    # Baseline
    draw.line(
        [(_s(80), _s(chart_bottom)), (_s(W - 60), _s(chart_bottom))],
        fill=STONE,
        width=_s(1),
    )

    # Two bars: 4.6 (single) and 4.7 (range low-high as stacked)
    bar_w = 80
    col_centers = [W * 0.33, W * 0.67]

    # --- 4.6 bar ---
    c46 = 6.65
    y46 = cost_to_y(c46)
    bx = col_centers[0] - bar_w / 2
    draw.rounded_rectangle(
        [_s(bx), _s(y46), _s(bx + bar_w), _s(chart_bottom)],
        radius=_s(6),
        fill=AMBER_SOFT,
    )
    # Column label
    label_font = _font(SANS_BOLD_PATHS, 13)
    draw_text_anchored(draw, "CLAUDE 4.6", col_centers[0], chart_bottom + 14, label_font, TEXT, anchor="mt")
    # Cost label above bar
    cost_font = _font(SANS_BOLD_PATHS, 18)
    draw_text_anchored(draw, "$6.65", col_centers[0], y46 - 26, cost_font, AMBER, anchor="mt")

    # --- 4.7 bar: range $7.86 low – $8.76 high ---
    c47_low = 7.86
    c47_high = 8.76
    y47_low = cost_to_y(c47_low)
    y47_high = cost_to_y(c47_high)
    bx2 = col_centers[1] - bar_w / 2

    # Solid bar up to low value
    draw.rounded_rectangle(
        [_s(bx2), _s(y47_low), _s(bx2 + bar_w), _s(chart_bottom)],
        radius=_s(6),
        fill=RED,
    )
    # Translucent bar from low to high
    translucent_red = (220, 38, 38, 110)
    draw.rectangle(
        [_s(bx2), _s(y47_high), _s(bx2 + bar_w), _s(y47_low)],
        fill=translucent_red,
    )
    # Top edge of range
    draw.line(
        [(_s(bx2), _s(y47_high)), (_s(bx2 + bar_w), _s(y47_high))],
        fill=RED,
        width=_s(2),
    )
    # Column label
    draw_text_anchored(draw, "CLAUDE 4.7", col_centers[1], chart_bottom + 14, label_font, TEXT, anchor="mt")
    # Cost label above bar
    draw_text_anchored(draw, "$7.86 – $8.76", col_centers[1], y47_high - 26, cost_font, RED, anchor="mt")

    # Uplift arrow and label between bars
    arrow_y = (y46 + y47_low) / 2 - 14
    from_x = col_centers[0] + bar_w / 2 + 14
    to_x = col_centers[1] - bar_w / 2 - 14
    draw.line(
        [(_s(from_x), _s(arrow_y)), (_s(to_x), _s(arrow_y))],
        fill=MUTED,
        width=_s(1.5),
    )
    # Arrowhead
    import math
    ang = math.atan2(0, to_x - from_x)
    head = 8
    for wing in (math.radians(150), math.radians(-150)):
        wx = to_x + head * math.cos(ang + wing)
        wy = arrow_y + head * math.sin(ang + wing)
        draw.line(
            [(_s(to_x), _s(arrow_y)), (_s(wx), _s(wy))],
            fill=MUTED,
            width=_s(1.5),
        )
    uplift_font = _font(SANS_BOLD_PATHS, 13)
    draw_text_anchored(
        draw,
        "+20–30%",
        (from_x + to_x) / 2,
        arrow_y - 18,
        uplift_font,
        AMBER,
        anchor="mt",
    )

    # Column captions
    turn_font = _font(SANS_PATHS, 11)
    draw_text_anchored(draw, "baseline", col_centers[0], chart_bottom + 32, turn_font, MUTED, anchor="mt")
    draw_text_anchored(draw, "new tokenizer", col_centers[1], chart_bottom + 32, turn_font, MUTED, anchor="mt")

    final = img.resize((W, H), Image.LANCZOS)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    final.save(out_path, "PNG")
    print(f"Wrote {out_path} ({W}x{H})")


if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("assets/tokenizer-tax/cost-bars.png")
    generate(out)

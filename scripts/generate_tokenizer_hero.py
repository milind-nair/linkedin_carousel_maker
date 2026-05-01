"""Generate hero PNG for the Claude 4.7 tokenizer-tax carousel.

Renders the same short text tokenized two ways: left (4.6 tokenizer, fewer/larger
chunks), right (4.7 tokenizer, more/smaller chunks). Designed for the dark
title slide, so uses light text on a transparent background.

Usage:
    python scripts/generate_tokenizer_hero.py [output_path]
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 600, 320
SCALE = 3
SW, SH = W * SCALE, H * SCALE

BG = (0, 0, 0, 0)
TEXT = (245, 245, 244, 255)
MUTED = (168, 162, 158, 255)
AMBER = (217, 119, 6, 255)
AMBER_SOFT = (245, 158, 11, 255)
RED = (220, 38, 38, 255)
CARD_FILL = (40, 36, 32, 255)
BORDER = (87, 83, 78, 255)


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
    "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
]
MONO_BOLD_PATHS = [
    "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
]
SANS_BOLD_PATHS = [
    "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]
SANS_PATHS = [
    "/usr/share/fonts/truetype/google-fonts/Poppins-Light.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]


def draw_token_row(
    draw: ImageDraw.ImageDraw,
    pieces: list[str],
    cx: float,
    y: float,
    color: tuple[int, int, int, int],
    font: ImageFont.ImageFont,
    gap: float = 5,
    pad_x: float = 7,
    pad_y: float = 6,
) -> None:
    """Draw a row of token chips, horizontally centered at cx."""
    widths = []
    for p in pieces:
        bbox = draw.textbbox((0, 0), p, font=font)
        widths.append(bbox[2] - bbox[0])
    ascent, descent = font.getmetrics()
    text_h = ascent
    chip_h = text_h / SCALE + pad_y * 2
    total_w = sum(w / SCALE for w in widths) + pad_x * 2 * len(pieces) + gap * (len(pieces) - 1)
    x = cx - total_w / 2
    for i, p in enumerate(pieces):
        w_pt = widths[i] / SCALE + pad_x * 2
        draw.rounded_rectangle(
            [_s(x), _s(y), _s(x + w_pt), _s(y + chip_h)],
            radius=_s(6),
            fill=CARD_FILL,
            outline=color,
            width=_s(1.6),
        )
        text_x = _s(x + pad_x)
        text_y = _s(y + pad_y) - font.getbbox("A")[1] + 1
        draw.text((text_x, text_y), p, fill=color, font=font)
        x += w_pt + gap


def draw_panel(
    draw: ImageDraw.ImageDraw,
    cx: float,
    top_y: float,
    label: str,
    label_color: tuple[int, int, int, int],
    token_color: tuple[int, int, int, int],
    pieces: list[str],
    count_text: str,
) -> None:
    label_font = _font(SANS_BOLD_PATHS, 13)
    bbox = draw.textbbox((0, 0), label, font=label_font)
    lw = bbox[2] - bbox[0]
    draw.text(
        (_s(cx) - lw // 2 - bbox[0], _s(top_y) - label_font.getbbox("A")[1]),
        label,
        fill=label_color,
        font=label_font,
    )

    mono = _font(MONO_BOLD_PATHS, 14)
    draw_token_row(draw, pieces, cx, top_y + 30, token_color, mono)

    count_font = _font(SANS_BOLD_PATHS, 14)
    cb = draw.textbbox((0, 0), count_text, font=count_font)
    cw = cb[2] - cb[0]
    draw.text(
        (_s(cx) - cw // 2 - cb[0], _s(top_y + 70) - count_font.getbbox("A")[1]),
        count_text,
        fill=token_color,
        font=count_font,
    )


def generate(out_path: Path) -> None:
    img = Image.new("RGBA", (SW, SH), BG)
    draw = ImageDraw.Draw(img)

    # Top label
    top_font = _font(SANS_BOLD_PATHS, 12)
    top_text = "SAME TEXT. DIFFERENT COUNTS."
    tb = draw.textbbox((0, 0), top_text, font=top_font)
    tw = tb[2] - tb[0]
    draw.text(
        (_s(W / 2) - tw // 2 - tb[0], _s(22) - top_font.getbbox("A")[1]),
        top_text,
        fill=MUTED,
        font=top_font,
    )

    # Sub-label: source text
    src_font = _font(MONO_PATHS, 12)
    src_text = 'fetchUserData'
    sb = draw.textbbox((0, 0), src_text, font=src_font)
    sw = sb[2] - sb[0]
    draw.text(
        (_s(W / 2) - sw // 2 - sb[0], _s(46) - src_font.getbbox("A")[1]),
        src_text,
        fill=TEXT,
        font=src_font,
    )

    # Left panel: 4.6 tokenizer (3 tokens)
    draw_panel(
        draw,
        cx=W * 0.28,
        top_y=90,
        label="CLAUDE 4.6",
        label_color=MUTED,
        token_color=AMBER_SOFT,
        pieces=["fetch", "User", "Data"],
        count_text="3 tokens",
    )

    # Right panel: 4.7 tokenizer (5 tokens)
    draw_panel(
        draw,
        cx=W * 0.72,
        top_y=90,
        label="CLAUDE 4.7",
        label_color=AMBER,
        token_color=RED,
        pieces=["fet", "ch", "Use", "r", "Data"],
        count_text="5 tokens",
    )

    # Divider between panels
    draw.line(
        [(_s(W / 2), _s(78)), (_s(W / 2), _s(210))],
        fill=BORDER,
        width=_s(1.2),
    )

    # Bottom result strip
    pill_w, pill_h = 260, 44
    px = W / 2 - pill_w / 2
    py = 230
    draw.rounded_rectangle(
        [_s(px), _s(py), _s(px + pill_w), _s(py + pill_h)],
        radius=_s(10),
        fill=(35, 31, 27, 255),
        outline=AMBER,
        width=_s(2),
    )
    result_font = _font(SANS_BOLD_PATHS, 16)
    rt = "1.325x on real workloads"
    rb = draw.textbbox((0, 0), rt, font=result_font)
    rw = rb[2] - rb[0]
    draw.text(
        (_s(W / 2) - rw // 2 - rb[0], _s(py + pill_h / 2 - 9) - result_font.getbbox("A")[1]),
        rt,
        fill=TEXT,
        font=result_font,
    )

    sub_font = _font(SANS_PATHS, 11)
    st = "weighted average on authentic Claude Code traffic"
    sb = draw.textbbox((0, 0), st, font=sub_font)
    sw = sb[2] - sb[0]
    draw.text(
        (_s(W / 2) - sw // 2 - sb[0], _s(288) - sub_font.getbbox("A")[1]),
        st,
        fill=MUTED,
        font=sub_font,
    )

    final = img.resize((W, H), Image.LANCZOS)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    final.save(out_path, "PNG")
    print(f"Wrote {out_path} ({W}x{H})")


if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("assets/tokenizer-tax/hero.png")
    generate(out)

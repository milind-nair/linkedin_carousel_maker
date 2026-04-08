"""Generate flow diagram PNG for the S3 Files carousel.

Shows the stage-and-commit write cycle:
Write to NFS → Accumulate in EFS → Sync to S3 → S3 source of truth

Usage:
    python scripts/generate_s3_files_flow.py [output_path]
"""

from __future__ import annotations
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 580, 440
SCALE = 3
SW, SH = W * SCALE, H * SCALE

AMBER = (217, 119, 6, 255)
GREEN = (5, 150, 105, 255)
BLUE = (37, 99, 235, 255)
PURPLE = (124, 58, 237, 255)
CREAM = (255, 253, 245, 255)
DARK = (26, 24, 20, 255)
MUTED = (100, 95, 90, 255)
CARD_BG = (255, 255, 255, 240)


def s(val):
    return int(round(val * SCALE))


def draw_step_box(draw, x, y, w, h, color, font, font_sm, number, title, subtitle):
    """Draw a numbered step box."""
    # Background
    draw.rounded_rectangle(
        [s(x), s(y), s(x + w), s(y + h)],
        radius=s(10), fill=CARD_BG, outline=color, width=s(2),
    )

    # Number circle
    circle_r = 14
    ccx = x + 28
    ccy = y + h / 2
    draw.ellipse(
        [s(ccx - circle_r), s(ccy - circle_r), s(ccx + circle_r), s(ccy + circle_r)],
        fill=color,
    )
    # Number text
    num_str = str(number)
    ntw = font.getlength(num_str)
    draw.text((s(ccx) - ntw / 2, s(ccy) - font.size / 2), num_str, fill=(255, 255, 255, 255), font=font)

    # Title
    tx = x + 56
    draw.text((s(tx), s(y + h / 2 - 16)), title, fill=DARK, font=font)

    # Subtitle
    draw.text((s(tx), s(y + h / 2 + 4)), subtitle, fill=MUTED, font=font_sm)


def draw_arrow_down(draw, cx, y1, y2, color):
    """Downward arrow between steps."""
    draw.line([s(cx), s(y1), s(cx), s(y2)], fill=color, width=s(2))
    head = 7
    draw.polygon([
        (s(cx), s(y2)),
        (s(cx - head * 0.6), s(y2 - head)),
        (s(cx + head * 0.6), s(y2 - head)),
    ], fill=color)


def generate(output_path: Path):
    img = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Load fonts
    font_paths = [
        "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    font_sm_paths = [
        "/usr/share/fonts/truetype/google-fonts/Poppins-Light.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]

    font = None
    for p in font_paths:
        try:
            font = ImageFont.truetype(p, s(11))
            break
        except OSError:
            continue
    if not font:
        font = ImageFont.load_default()

    font_sm = None
    for p in font_sm_paths:
        try:
            font_sm = ImageFont.truetype(p, s(9))
            break
        except OSError:
            continue
    if not font_sm:
        font_sm = font

    # Steps
    steps = [
        (BLUE, "1", "Write via NFS", "App writes files normally"),
        (AMBER, "2", "Stage in EFS", "Mutations accumulate locally"),
        (GREEN, "3", "Commit to S3", "Atomic PUTs every ~60 seconds"),
        (PURPLE, "4", "S3 = Source of Truth", "Conflicts go to lost+found"),
    ]

    box_w = 380
    box_h = 60
    gap = 22
    total_h = len(steps) * box_h + (len(steps) - 1) * gap
    start_y = (H - total_h) / 2
    start_x = (W - box_w) / 2

    for i, (color, num, title, subtitle) in enumerate(steps):
        y = start_y + i * (box_h + gap)
        draw_step_box(draw, start_x, y, box_w, box_h, color, font, font_sm, num, title, subtitle)

        # Arrow between steps
        if i < len(steps) - 1:
            arrow_y1 = y + box_h + 2
            arrow_y2 = y + box_h + gap - 2
            draw_arrow_down(draw, W / 2, arrow_y1, arrow_y2, MUTED)

    # Downsample
    final = img.resize((W, H), Image.LANCZOS)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    final.save(output_path, "PNG")
    print(f"Wrote {output_path} ({W}x{H})")


if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("assets/s3-files/flow.png")
    generate(out)

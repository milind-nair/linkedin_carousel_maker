"""Generate hero PNG for the S3 Files carousel.

Shows an S3 bucket icon connected to a filesystem/folder icon,
representing the bridge between object storage and file systems.

Usage:
    python scripts/generate_s3_files_hero.py [output_path]
"""

from __future__ import annotations
import math
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 580, 440
SCALE = 3
SW, SH = W * SCALE, H * SCALE

# Palette (dark theme for title_dark slide)
AMBER = (217, 119, 6, 255)        # #D97706
AMBER_DIM = (217, 119, 6, 120)
GREEN = (5, 150, 105, 255)        # #059669
CREAM = (255, 253, 245, 255)      # #FFFDF5
DARK = (26, 24, 20, 255)          # #1A1814
MUTED = (168, 162, 158, 200)      # muted


def s(val):
    return int(round(val * SCALE))


def draw_bucket(draw, cx, cy, w, h, color):
    """S3-style bucket: cylinder shape."""
    # Body
    x1, y1 = s(cx - w / 2), s(cy - h / 2 + h * 0.15)
    x2, y2 = s(cx + w / 2), s(cy + h / 2 - h * 0.15)
    draw.rectangle([x1, y1, x2, y2], fill=color)

    # Top ellipse
    top_cy = cy - h / 2 + h * 0.15
    ew, eh = w / 2, h * 0.15
    draw.ellipse([s(cx - ew), s(top_cy - eh), s(cx + ew), s(top_cy + eh)], fill=color)

    # Bottom ellipse
    bot_cy = cy + h / 2 - h * 0.15
    draw.ellipse([s(cx - ew), s(bot_cy - eh), s(cx + ew), s(bot_cy + eh)], fill=color)

    # Inner rim on top ellipse for depth
    rim_color = (255, 255, 255, 60)
    draw.ellipse(
        [s(cx - ew + 6), s(top_cy - eh + 4), s(cx + ew - 6), s(top_cy + eh - 4)],
        fill=rim_color,
    )

    # "S3" label lines (abstract)
    lw = w * 0.35
    for offset in (-h * 0.08, h * 0.08):
        draw.rounded_rectangle(
            [s(cx - lw / 2), s(cy + offset - 2), s(cx + lw / 2), s(cy + offset + 2)],
            radius=s(2), fill=(255, 255, 255, 100),
        )


def draw_folder(draw, cx, cy, w, h, color):
    """Filesystem folder icon."""
    x = cx - w / 2
    y = cy - h / 2

    # Tab
    tab_w = w * 0.35
    tab_h = h * 0.18
    draw.rounded_rectangle(
        [s(x), s(y), s(x + tab_w), s(y + tab_h + 4)],
        radius=s(4), fill=color,
    )

    # Main body
    body_y = y + tab_h
    draw.rounded_rectangle(
        [s(x), s(body_y), s(x + w), s(y + h)],
        radius=s(6), fill=color,
    )

    # Inner detail lines (file rows)
    line_color = (255, 255, 255, 80)
    lx1, lx2 = x + w * 0.15, x + w * 0.85
    for i in range(3):
        ly = body_y + h * 0.22 + i * h * 0.18
        draw.rounded_rectangle(
            [s(lx1), s(ly - 2), s(lx2), s(ly + 2)],
            radius=s(2), fill=line_color,
        )


def draw_arrow_connector(draw, x1, y, x2, color, width=3):
    """Bidirectional arrow between two points."""
    mid = (x1 + x2) / 2
    head = 10

    # Top arrow (left to right)
    ay = y - 8
    draw.line([s(x1), s(ay), s(x2), s(ay)], fill=color, width=s(width))
    draw.polygon([
        (s(x2), s(ay)),
        (s(x2 - head), s(ay - head * 0.6)),
        (s(x2 - head), s(ay + head * 0.6)),
    ], fill=color)

    # Bottom arrow (right to left)
    by = y + 8
    draw.line([s(x1), s(by), s(x2), s(by)], fill=color, width=s(width))
    draw.polygon([
        (s(x1), s(by)),
        (s(x1 + head), s(by - head * 0.6)),
        (s(x1 + head), s(by + head * 0.6)),
    ], fill=color)


def draw_nfs_label(draw, cx, cy):
    """NFS v4.2 label between the icons."""
    bw, bh = 80, 28
    draw.rounded_rectangle(
        [s(cx - bw / 2), s(cy - bh / 2), s(cx + bw / 2), s(cy + bh / 2)],
        radius=s(6), fill=AMBER_DIM,
    )
    # Small inner mark
    draw.rounded_rectangle(
        [s(cx - 22), s(cy - 3), s(cx + 22), s(cy + 3)],
        radius=s(2), fill=(255, 255, 255, 140),
    )


def generate(output_path: Path):
    img = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    cy = H * 0.48

    # S3 bucket on the left
    bucket_cx = W * 0.22
    draw_bucket(draw, bucket_cx, cy, 110, 130, AMBER)

    # Folder on the right
    folder_cx = W * 0.78
    draw_folder(draw, folder_cx, cy, 120, 110, GREEN)

    # Connector arrows
    arrow_x1 = bucket_cx + 70
    arrow_x2 = folder_cx - 74
    draw_arrow_connector(draw, arrow_x1, cy, arrow_x2, CREAM, width=2)

    # NFS label in the middle
    mid_x = (bucket_cx + folder_cx) / 2
    draw_nfs_label(draw, mid_x, cy)

    # Subtle decorative dots in background
    for dx, dy, r, alpha in [
        (W * 0.1, H * 0.15, 4, 40),
        (W * 0.9, H * 0.2, 3, 30),
        (W * 0.5, H * 0.85, 5, 35),
        (W * 0.15, H * 0.8, 3, 25),
        (W * 0.85, H * 0.82, 4, 30),
    ]:
        draw.ellipse(
            [s(dx - r), s(dy - r), s(dx + r), s(dy + r)],
            fill=(217, 119, 6, alpha),
        )

    # Downsample
    final = img.resize((W, H), Image.LANCZOS)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    final.save(output_path, "PNG")
    print(f"Wrote {output_path} ({W}x{H})")


if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("assets/s3-files/hero.png")
    generate(out)

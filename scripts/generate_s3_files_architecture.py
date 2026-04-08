"""Generate architecture diagram PNG for the S3 Files carousel.

Shows: NFS Clients → EFS Cache → S3 (source of truth)
with labeled details about thresholds and performance.
Large, clear elements with strong visual hierarchy.

Usage:
    python scripts/generate_s3_files_architecture.py [output_path]
"""

from __future__ import annotations
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 580, 440
SCALE = 3
SW, SH = W * SCALE, H * SCALE

AMBER = (217, 119, 6, 255)
AMBER_LIGHT = (254, 243, 199, 255)
GREEN = (5, 150, 105, 255)
GREEN_LIGHT = (236, 253, 245, 255)
BLUE = (37, 99, 235, 255)
BLUE_LIGHT = (219, 234, 254, 255)
CREAM = (255, 253, 245, 255)
DARK = (41, 37, 36, 255)
MUTED = (120, 113, 108, 255)
WHITE = (255, 255, 255, 255)


def s(val):
    return int(round(val * SCALE))


def load_font(paths, size):
    for p in paths:
        try:
            return ImageFont.truetype(p, s(size))
        except OSError:
            continue
    return ImageFont.load_default()


def draw_box(draw, x, y, w, h, fill, outline, radius=12, outline_width=3):
    draw.rounded_rectangle(
        [s(x), s(y), s(x + w), s(y + h)],
        radius=s(radius), fill=fill, outline=outline, width=s(outline_width),
    )


def draw_arrow_right(draw, x1, y, x2, color, width=3, head=10):
    draw.line([s(x1), s(y), s(x2 - head), s(y)], fill=color, width=s(width))
    draw.polygon([
        (s(x2), s(y)),
        (s(x2 - head), s(y - head * 0.65)),
        (s(x2 - head), s(y + head * 0.65)),
    ], fill=color)


def draw_arrow_left(draw, x1, y, x2, color, width=3, head=10):
    """Arrow from x1 to x2 where x2 < x1 (points left)."""
    draw.line([s(x1), s(y), s(x2 + head), s(y)], fill=color, width=s(width))
    draw.polygon([
        (s(x2), s(y)),
        (s(x2 + head), s(y - head * 0.65)),
        (s(x2 + head), s(y + head * 0.65)),
    ], fill=color)


def centered_text(draw, cx, y, text, font, fill):
    tw = font.getlength(text)
    draw.text((s(cx) - tw / 2, s(y)), text, fill=fill, font=font)


def generate(output_path: Path):
    img = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    regular = [
        "/usr/share/fonts/truetype/google-fonts/Poppins-Light.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    bold = [
        "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]

    font_title = load_font(bold, 14)
    font_label = load_font(bold, 11)
    font_sub = load_font(regular, 10)
    font_sm = load_font(regular, 9)

    # ── Layout: 3 boxes with wide gaps for labels ──
    box_w, box_h = 120, 160
    gap = 80
    total_w = 3 * box_w + 2 * gap
    start_x = (W - total_w) / 2
    box_y = 70

    # ── Box 1: NFS Clients ──
    x1 = start_x
    draw_box(draw, x1, box_y, box_w, box_h, BLUE_LIGHT, BLUE)

    # Icon: three stacked server bars
    for i in range(3):
        iy = box_y + 30 + i * 36
        draw.rounded_rectangle(
            [s(x1 + 16), s(iy), s(x1 + box_w - 16), s(iy + 26)],
            radius=s(6), fill=WHITE, outline=BLUE, width=s(2),
        )
        # Dot indicator on each bar
        draw.ellipse(
            [s(x1 + 24), s(iy + 9), s(x1 + 32), s(iy + 17)],
            fill=BLUE,
        )
        # Line on each bar
        draw.rounded_rectangle(
            [s(x1 + 40), s(iy + 10), s(x1 + box_w - 28), s(iy + 16)],
            radius=s(2), fill=(37, 99, 235, 80),
        )

    centered_text(draw, x1 + box_w / 2, box_y + box_h + 10, "NFS Clients", font_title, BLUE)
    centered_text(draw, x1 + box_w / 2, box_y + box_h + 30, "EC2 / EKS / Lambda", font_sm, MUTED)

    # ── Box 2: EFS Cache ──
    x2 = start_x + box_w + gap
    draw_box(draw, x2, box_y, box_w, box_h, AMBER_LIGHT, AMBER)

    # Icon: layered cache with gradient opacity
    for i in range(4):
        iy = box_y + 24 + i * 32
        alpha = 255 - i * 45
        draw.rounded_rectangle(
            [s(x2 + 14), s(iy), s(x2 + box_w - 14), s(iy + 24)],
            radius=s(6), fill=(217, 119, 6, alpha),
        )
        # Inner highlight
        draw.rounded_rectangle(
            [s(x2 + 22), s(iy + 8), s(x2 + box_w - 22), s(iy + 14)],
            radius=s(2), fill=(255, 255, 255, 100),
        )

    centered_text(draw, x2 + box_w / 2, box_y + box_h + 10, "EFS Cache", font_title, AMBER)
    centered_text(draw, x2 + box_w / 2, box_y + box_h + 30, "~1ms latency", font_sm, MUTED)

    # ── Box 3: S3 Bucket ──
    x3 = start_x + 2 * (box_w + gap)
    draw_box(draw, x3, box_y, box_w, box_h, GREEN_LIGHT, GREEN)

    # Icon: large bucket/cylinder
    bcx = x3 + box_w / 2
    bcy = box_y + box_h / 2
    bw, bh = 60, 90
    # Cylinder body
    draw.rounded_rectangle(
        [s(bcx - bw / 2), s(bcy - bh / 2 + 14), s(bcx + bw / 2), s(bcy + bh / 2)],
        radius=s(4), fill=(5, 150, 105, 100),
    )
    # Top ellipse
    draw.ellipse(
        [s(bcx - bw / 2), s(bcy - bh / 2), s(bcx + bw / 2), s(bcy - bh / 2 + 28)],
        fill=GREEN,
    )
    # Inner ellipse highlight
    draw.ellipse(
        [s(bcx - bw / 2 + 8), s(bcy - bh / 2 + 4), s(bcx + bw / 2 - 8), s(bcy - bh / 2 + 24)],
        fill=(255, 255, 255, 60),
    )
    # Bottom ellipse
    draw.ellipse(
        [s(bcx - bw / 2), s(bcy + bh / 2 - 14), s(bcx + bw / 2), s(bcy + bh / 2)],
        fill=GREEN,
    )

    centered_text(draw, x3 + box_w / 2, box_y + box_h + 10, "S3 Bucket", font_title, GREEN)
    centered_text(draw, x3 + box_w / 2, box_y + box_h + 30, "Source of truth", font_sm, MUTED)

    # ── Arrows between boxes ──
    arrow_y_top = box_y + box_h / 2 - 8
    arrow_y_bot = box_y + box_h / 2 + 8

    # Clients → EFS (top arrow, rightward)
    draw_arrow_right(draw, x1 + box_w + 4, arrow_y_top, x2 - 4, BLUE)
    # EFS → Clients (bottom arrow, leftward)
    draw_arrow_left(draw, x2 - 4, arrow_y_bot, x1 + box_w + 4, AMBER)

    # EFS → S3 (top arrow, rightward)
    draw_arrow_right(draw, x2 + box_w + 4, arrow_y_top, x3 - 4, AMBER)
    # S3 → EFS (bottom arrow, leftward)
    draw_arrow_left(draw, x3 - 4, arrow_y_bot, x2 + box_w + 4, GREEN)

    # ── Arrow labels ──
    mid1 = (x1 + box_w + x2) / 2
    centered_text(draw, mid1, arrow_y_top - 22, "NFS v4.2", font_label, BLUE)

    mid2 = (x2 + box_w + x3) / 2
    centered_text(draw, mid2, arrow_y_top - 22, "~60s sync", font_label, AMBER)

    # ── Threshold label above EFS ──
    centered_text(draw, x2 + box_w / 2, box_y - 22, "< 128KB: fully cached", font_label, AMBER)

    # ── Read bypass: curved path at bottom ──
    bypass_y = box_y + box_h + 66

    # Horizontal line from S3 to Clients at bypass_y
    draw.line(
        [s(x1 + box_w / 2), s(bypass_y), s(x3 + box_w / 2), s(bypass_y)],
        fill=GREEN, width=s(2),
    )
    # Vertical connectors
    draw.line(
        [s(x3 + box_w / 2), s(box_y + box_h + 48), s(x3 + box_w / 2), s(bypass_y)],
        fill=GREEN, width=s(2),
    )
    draw.line(
        [s(x1 + box_w / 2), s(bypass_y), s(x1 + box_w / 2), s(box_y + box_h + 48)],
        fill=GREEN, width=s(2),
    )
    # Arrowhead pointing up at clients
    head = 8
    draw.polygon([
        (s(x1 + box_w / 2), s(box_y + box_h + 48)),
        (s(x1 + box_w / 2 - head * 0.65), s(box_y + box_h + 48 + head)),
        (s(x1 + box_w / 2 + head * 0.65), s(box_y + box_h + 48 + head)),
    ], fill=GREEN)

    # Bypass label
    mid_bp = (x1 + box_w / 2 + x3 + box_w / 2) / 2
    centered_text(draw, mid_bp, bypass_y + 8, "Read bypass: 3 GB/s (files >= 128KB)", font_label, GREEN)

    # ── Downsample ──
    final = img.resize((W, H), Image.LANCZOS)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    final.save(output_path, "PNG")
    print(f"Wrote {output_path} ({W}x{H})")


if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("assets/s3-files/architecture.png")
    generate(out)

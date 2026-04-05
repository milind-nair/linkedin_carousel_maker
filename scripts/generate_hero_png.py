"""Generate a custom hero PNG for the CLI vs SDK carousel.

Renders at 3x scale and downsamples for crisp edges. Output is a
transparent-background PNG suitable for use with the `illustration.source`
or `image.source` fields in a carousel JSON payload.

Usage:
    python scripts/generate_hero_png.py [output_path]
"""

from __future__ import annotations
import math
import sys
from pathlib import Path
from PIL import Image, ImageDraw

# Base dimensions (points). Rendered at SCALE× then downsampled.
W, H = 600, 320
SCALE = 3

# Palette
ORANGE = (217, 119, 6, 255)       # #D97706 — CLI
BLUE = (37, 99, 235, 255)         # #2563EB — SDK
GREEN = (5, 150, 105, 255)        # #059669 — shared runtime
DARK = (41, 37, 36, 255)          # text
MUTED = (120, 113, 108, 255)


def _scale(val: float) -> int:
    return int(round(val * SCALE))


def _line(draw, x1, y1, x2, y2, color, width):
    draw.line(
        [(_scale(x1), _scale(y1)), (_scale(x2), _scale(y2))],
        fill=color, width=_scale(width),
    )


def _circle(draw, cx, cy, r, fill=None, outline=None, width=0):
    bbox = [
        _scale(cx - r), _scale(cy - r),
        _scale(cx + r), _scale(cy + r),
    ]
    draw.ellipse(bbox, fill=fill, outline=outline, width=_scale(width) if width else 0)


def _rect(draw, x, y, w, h, fill=None, outline=None, width=0, radius=0):
    bbox = [_scale(x), _scale(y), _scale(x + w), _scale(y + h)]
    if radius > 0:
        draw.rounded_rectangle(
            bbox, radius=_scale(radius), fill=fill, outline=outline,
            width=_scale(width) if width else 0,
        )
    else:
        draw.rectangle(bbox, fill=fill, outline=outline,
                       width=_scale(width) if width else 0)


def draw_terminal(draw, x, y, w, h, color):
    """Terminal window with prompt and cursor. (x, y) = top-left."""
    # Outer frame (stroked)
    _rect(draw, x, y, w, h, outline=color, width=3, radius=6)
    # Title bar line
    bar_y = y + 14
    _line(draw, x, bar_y, x + w, bar_y, color, 2)
    # Three dots
    for i, dx in enumerate([8, 18, 28]):
        _circle(draw, x + dx, y + 7, 2.2, fill=color)
    # Prompt chevron
    cx, cy = x + 16, y + h * 0.6
    arm = 7
    _line(draw, cx - arm, cy - arm, cx, cy, color, 3)
    _line(draw, cx, cy, cx - arm, cy + arm, color, 3)
    # Cursor block
    _rect(draw, cx + 8, cy - 2, 18, 4, fill=color)


def draw_code(draw, x, y, w, h, color):
    """</> code brackets. (x, y) = top-left of bounding box."""
    cy = y + h / 2
    arm = h * 0.32
    # Left bracket
    lx = x + w * 0.22
    _line(draw, lx, cy - arm, lx - arm * 0.9, cy, color, 4)
    _line(draw, lx - arm * 0.9, cy, lx, cy + arm, color, 4)
    # Right bracket
    rx = x + w * 0.78
    _line(draw, rx, cy - arm, rx + arm * 0.9, cy, color, 4)
    _line(draw, rx + arm * 0.9, cy, rx, cy + arm, color, 4)
    # Slash
    _line(draw, x + w * 0.5 - 5, cy + arm - 2, x + w * 0.5 + 5, cy - arm + 2,
          color, 4)


def draw_runtime_core(draw, cx, cy, r, color):
    """Hexagonal runtime core at center."""
    points = []
    for i in range(6):
        a = math.radians(60 * i - 30)
        points.append((_scale(cx + r * math.cos(a)), _scale(cy + r * math.sin(a))))
    # Fill
    draw.polygon(points, fill=color)
    # Inner label mark
    inner_r = r * 0.42
    inner_pts = []
    for i in range(6):
        a = math.radians(60 * i - 30)
        inner_pts.append((
            _scale(cx + inner_r * math.cos(a)),
            _scale(cy + inner_r * math.sin(a)),
        ))
    draw.polygon(inner_pts, fill=(255, 253, 245, 255))


def _arrow(draw, x1, y1, x2, y2, color, width, head_size=8):
    _line(draw, x1, y1, x2, y2, color, width)
    # Arrowhead
    ang = math.atan2(y2 - y1, x2 - x1)
    for wing_offset in (math.radians(150), math.radians(-150)):
        wx = x2 + head_size * math.cos(ang + wing_offset)
        wy = y2 + head_size * math.sin(ang + wing_offset)
        _line(draw, x2, y2, wx, wy, color, width)


def generate(output_path: Path):
    img = Image.new("RGBA", (W * SCALE, H * SCALE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Runtime core at center
    cx, cy = W / 2, H / 2
    core_r = 44
    draw_runtime_core(draw, cx, cy, core_r, GREEN)

    # CLI: terminal on the left
    cli_w, cli_h = 148, 96
    cli_x, cli_y = 40, cy - cli_h / 2
    draw_terminal(draw, cli_x, cli_y, cli_w, cli_h, ORANGE)

    # SDK: code brackets on the right
    sdk_w, sdk_h = 148, 96
    sdk_x, sdk_y = W - 40 - sdk_w, cy - sdk_h / 2
    draw_code(draw, sdk_x, sdk_y, sdk_w, sdk_h, BLUE)

    # Connector lines from interfaces to core
    _arrow(draw, cli_x + cli_w + 8, cy, cx - core_r - 4, cy, ORANGE, 3, head_size=10)
    _arrow(draw, sdk_x - 8, cy, cx + core_r + 4, cy, BLUE, 3, head_size=10)

    # Labels under each interface
    label_y = cli_y + cli_h + 18
    _rect(draw, cli_x + cli_w / 2 - 18, label_y, 36, 4, fill=ORANGE, radius=2)
    _rect(draw, sdk_x + sdk_w / 2 - 18, label_y, 36, 4, fill=BLUE, radius=2)

    # Downsample for crispness
    final = img.resize((W, H), Image.LANCZOS)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    final.save(output_path, "PNG")
    print(f"Wrote {output_path} ({W}x{H})")


if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("assets/cli-vs-sdk-hero.png")
    generate(out)

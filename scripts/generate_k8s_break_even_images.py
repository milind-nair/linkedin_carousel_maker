"""Generate the two illustration PNGs for the kubernetes-break-even carousel.

Slide 2 — scheduler placing pods across a fleet of nodes (amber).
Slide 3 — control plane + node components cluster showing operational surface (red/stone).

Rendered at 3x and downsampled with LANCZOS for crisp edges.
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 560, 400
SCALE = 3

AMBER = (217, 119, 6, 255)        # #D97706
AMBER_LIGHT = (254, 243, 199, 255)
RED = (220, 38, 38, 255)          # #DC2626
RED_LIGHT = (254, 242, 242, 255)
STONE = (120, 113, 108, 255)      # #78716C
DARK = (41, 37, 36, 255)
BG_CARD = (255, 255, 255, 255)
GRID = (231, 229, 228, 255)


def _s(v: float) -> int:
    return int(round(v * SCALE))


def _font(size: int) -> ImageFont.FreeTypeFont:
    candidates = [
        "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    for c in candidates:
        if Path(c).exists():
            return ImageFont.truetype(c, _s(size))
    return ImageFont.load_default()


def _rect(d, x, y, w, h, fill=None, outline=None, width=0, radius=0):
    bbox = [_s(x), _s(y), _s(x + w), _s(y + h)]
    if radius > 0:
        d.rounded_rectangle(
            bbox, radius=_s(radius), fill=fill, outline=outline,
            width=_s(width) if width else 0,
        )
    else:
        d.rectangle(bbox, fill=fill, outline=outline,
                    width=_s(width) if width else 0)


def _line(d, x1, y1, x2, y2, color, width):
    d.line([(_s(x1), _s(y1)), (_s(x2), _s(y2))],
           fill=color, width=_s(width))


def _circle(d, cx, cy, r, fill=None, outline=None, width=0):
    bbox = [_s(cx - r), _s(cy - r), _s(cx + r), _s(cy + r)]
    d.ellipse(bbox, fill=fill, outline=outline,
              width=_s(width) if width else 0)


def _text(d, x, y, text, size, color, anchor="lt", bold=True):
    d.text((_s(x), _s(y)), text, fill=color, font=_font(size), anchor=anchor)


def generate_scheduler(output: Path):
    img = Image.new("RGBA", (W * SCALE, H * SCALE), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Scheduler hub at top
    hub_cx, hub_cy, hub_r = W / 2, 52, 34
    _circle(d, hub_cx, hub_cy, hub_r, fill=AMBER)
    _circle(d, hub_cx, hub_cy, hub_r - 6, fill=AMBER_LIGHT)
    _text(d, hub_cx, hub_cy, "SCHED", 10, AMBER, anchor="mm")

    # Three nodes arranged horizontally
    node_w, node_h = 140, 200
    node_y = 150
    gap = 28
    total_w = 3 * node_w + 2 * gap
    start_x = (W - total_w) / 2

    pod_layouts = [
        [("api", AMBER), ("web", AMBER), ("db", STONE)],
        [("web", AMBER), ("jobs", STONE), ("cache", AMBER)],
        [("api", AMBER), ("auth", AMBER), ("db", STONE)],
    ]

    for i in range(3):
        nx = start_x + i * (node_w + gap)
        # Connector from scheduler to node top
        _line(d, hub_cx, hub_cy + hub_r, nx + node_w / 2, node_y, AMBER, 2)

        # Node body
        _rect(d, nx, node_y, node_w, node_h, fill=BG_CARD,
              outline=GRID, width=1, radius=8)
        # Top accent
        _rect(d, nx, node_y, node_w, 4, fill=AMBER, radius=0)
        _text(d, nx + 14, node_y + 14, f"NODE {i + 1}", 10, STONE)

        # Pods grid inside node (3 pods stacked)
        pods = pod_layouts[i]
        pod_w = node_w - 28
        pod_h = 38
        pod_gap = 8
        pod_start_y = node_y + 40
        for j, (label, color) in enumerate(pods):
            py = pod_start_y + j * (pod_h + pod_gap)
            _rect(d, nx + 14, py, pod_w, pod_h,
                  fill=AMBER_LIGHT, outline=color, width=1, radius=4)
            # Pod dot
            _circle(d, nx + 28, py + pod_h / 2, 5, fill=color)
            _text(d, nx + 42, py + pod_h / 2 - 7, label, 11, DARK, anchor="lt")

    final = img.resize((W, H), Image.LANCZOS)
    output.parent.mkdir(parents=True, exist_ok=True)
    final.save(output, "PNG")
    print(f"Wrote {output} ({W}x{H})")


def generate_complexity(output: Path):
    img = Image.new("RGBA", (W * SCALE, H * SCALE), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Title band
    _text(d, W / 2, 14, "CONTROL PLANE", 11, RED, anchor="mt")

    # Control plane row — 4 components
    cp_y = 40
    cp_h = 70
    cp_labels = ["api-server", "etcd", "scheduler", "controller"]
    comp_w = 120
    gap = 12
    total_w = 4 * comp_w + 3 * gap
    start_x = (W - total_w) / 2

    for i, label in enumerate(cp_labels):
        x = start_x + i * (comp_w + gap)
        _rect(d, x, cp_y, comp_w, cp_h, fill=BG_CARD,
              outline=RED, width=2, radius=6)
        _rect(d, x, cp_y, comp_w, 4, fill=RED, radius=0)
        _text(d, x + comp_w / 2, cp_y + cp_h / 2 - 6, label, 12, DARK, anchor="mm")

    # Divider label
    _text(d, W / 2, 140, "NODE", 11, STONE, anchor="mt")

    # Node row — 3 components + kubelet on the side
    node_y = 166
    node_h = 70
    node_labels = ["kubelet", "CNI", "CSI"]
    n_comp_w = 130
    n_total = 3 * n_comp_w + 2 * gap
    n_start = (W - n_total) / 2

    for i, label in enumerate(node_labels):
        x = n_start + i * (n_comp_w + gap)
        _rect(d, x, node_y, n_comp_w, node_h, fill=BG_CARD,
              outline=STONE, width=2, radius=6)
        _rect(d, x, node_y, n_comp_w, 4, fill=STONE, radius=0)
        _text(d, x + n_comp_w / 2, node_y + node_h / 2 - 6, label, 12, DARK, anchor="mm")

    # Ingress box centered below
    ing_y = 272
    ing_w, ing_h = 160, 60
    ing_x = (W - ing_w) / 2
    _rect(d, ing_x, ing_y, ing_w, ing_h, fill=BG_CARD,
          outline=RED, width=2, radius=6)
    _rect(d, ing_x, ing_y, ing_w, 4, fill=RED, radius=0)
    _text(d, ing_x + ing_w / 2, ing_y + ing_h / 2 - 6, "ingress", 12, DARK, anchor="mm")
    _text(d, W / 2, 350, "each fails in its own way", 11, STONE, anchor="mt")

    # Connectors — thin lines between layers to convey coupling
    # Control plane to node
    for i in range(4):
        cx = start_x + i * (comp_w + gap) + comp_w / 2
        _line(d, cx, cp_y + cp_h, cx, node_y, RED, 1)
    # Node to ingress
    for i in range(3):
        nx = n_start + i * (n_comp_w + gap) + n_comp_w / 2
        _line(d, nx, node_y + node_h, ing_x + ing_w / 2, ing_y, RED, 1)

    final = img.resize((W, H), Image.LANCZOS)
    output.parent.mkdir(parents=True, exist_ok=True)
    final.save(output, "PNG")
    print(f"Wrote {output} ({W}x{H})")


if __name__ == "__main__":
    base = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("assets/kubernetes-break-even")
    generate_scheduler(base / "slide2-scheduler.png")
    generate_complexity(base / "slide3-complexity.png")

"""Hand-drawn primitives for the lab notebook aesthetic.

All functions are deterministic given a seed, so a given carousel renders
identically on every run. All output is rendered in red ink (red_pen) by
default. The wobble technique is inspired by rough.js: sample a path,
perturb interior points with Gaussian noise, draw the path twice with a
small offset to simulate "pen passed twice".
"""

from __future__ import annotations
import hashlib
import math
import random
from typing import Iterable, Tuple

Point = Tuple[float, float]

# Default wobble parameters — tuned in the visual gate (Task 17).
DEFAULT_JITTER = 1.5      # std-dev of point perturbation, in points
DEFAULT_SAMPLES = 32      # points sampled along a curve
DEFAULT_LINE_WIDTH = 1.2  # stroke weight for hand-drawn lines


def make_seed(text: str, slide_index: int) -> int:
    """Deterministic 32-bit seed from slide identity. Same identity = same wobble."""
    h = hashlib.sha256(f"{text}|{slide_index}".encode("utf-8")).digest()
    return int.from_bytes(h[:4], "big")


def _wobbled_polyline(
    anchor_points: list[Point],
    seed: int,
    samples: int = DEFAULT_SAMPLES,
    jitter: float = DEFAULT_JITTER,
) -> list[Point]:
    """Sample a polyline interpolated through anchor_points, with Gaussian
    perturbation on each interior sample. Endpoints are pinned (so arrows
    connect cleanly to the anchors they're aiming at)."""
    if len(anchor_points) < 2:
        raise ValueError("anchor_points must have at least 2 points")
    if samples < 2:
        raise ValueError("samples must be >= 2")

    rng = random.Random(seed)
    # Build a piecewise-linear length parameterization
    seg_lengths = [
        math.hypot(b[0] - a[0], b[1] - a[1])
        for a, b in zip(anchor_points, anchor_points[1:])
    ]
    total = sum(seg_lengths) or 1.0
    cum = [0.0]
    for s in seg_lengths:
        cum.append(cum[-1] + s)

    out: list[Point] = []
    for i in range(samples):
        t = i / (samples - 1)
        target = t * total
        # Find segment
        for j in range(len(seg_lengths)):
            if target <= cum[j + 1] or j == len(seg_lengths) - 1:
                seg_t = (target - cum[j]) / max(seg_lengths[j], 1e-9)
                a, b = anchor_points[j], anchor_points[j + 1]
                x = a[0] + seg_t * (b[0] - a[0])
                y = a[1] + seg_t * (b[1] - a[1])
                break
        # Pin endpoints
        if i == 0 or i == samples - 1:
            out.append((x, y))
        else:
            out.append((x + rng.gauss(0, jitter), y + rng.gauss(0, jitter)))
    return out


from reportlab.lib.colors import HexColor

RED_PEN = HexColor("#B22222")


def _arrow_anchor_points(start: Point, end: Point, style: str) -> list[Point]:
    """Return the anchor points that the arrow path interpolates through.
    These are the 'idealized' points before wobble is applied."""
    sx, sy = start
    ex, ey = end
    if style == "sweep":
        # One off-axis control point ~30% along, perpendicular offset
        mx, my = (sx + ex) / 2, (sy + ey) / 2
        dx, dy = ex - sx, ey - sy
        length = math.hypot(dx, dy) or 1.0
        # Perpendicular unit vector
        px, py = -dy / length, dx / length
        # Offset magnitude: a quarter of the run, capped
        offset = min(length * 0.18, 28)
        ctrl = (mx + px * offset, my + py * offset)
        return [start, ctrl, end]
    if style == "pointer":
        return [start, end]
    if style == "branch":
        # Move horizontally first, then turn 90° to the endpoint
        elbow = (ex, sy)
        return [start, elbow, end]
    raise ValueError(f"unknown arrow style: {style!r}")


def _draw_polyline(canvas, points: list[Point], line_width: float):
    p = canvas.beginPath()
    p.moveTo(*points[0])
    for x, y in points[1:]:
        p.lineTo(x, y)
    canvas.setLineWidth(line_width)
    canvas.drawPath(p, stroke=1, fill=0)


def _draw_arrowhead(canvas, tip: Point, direction: Point, seed: int, color):
    """Small triangle at `tip`, pointing along `direction` (a unit-ish vector)."""
    rng = random.Random(seed ^ 0xA17A1)
    dx, dy = direction
    length = math.hypot(dx, dy) or 1.0
    ux, uy = dx / length, dy / length
    # Perpendicular
    px, py = -uy, ux
    head_len = 7.0
    head_wide = 3.5
    # ±5° rotation jitter
    angle_jitter = math.radians(rng.uniform(-5, 5))
    cos_a, sin_a = math.cos(angle_jitter), math.sin(angle_jitter)
    rux = ux * cos_a - uy * sin_a
    ruy = ux * sin_a + uy * cos_a
    rpx = -ruy
    rpy = rux
    base = (tip[0] - rux * head_len, tip[1] - ruy * head_len)
    left = (base[0] + rpx * head_wide, base[1] + rpy * head_wide)
    right = (base[0] - rpx * head_wide, base[1] - rpy * head_wide)
    p = canvas.beginPath()
    p.moveTo(*tip)
    p.lineTo(*left)
    p.lineTo(*right)
    p.close()
    canvas.setFillColor(color)
    canvas.drawPath(p, stroke=1, fill=1)


def draw_arrow(
    canvas,
    start: Point,
    end: Point,
    seed: int,
    style: str = "sweep",
    color=RED_PEN,
    samples: int = DEFAULT_SAMPLES,
    jitter: float = DEFAULT_JITTER,
    line_width: float = DEFAULT_LINE_WIDTH,
):
    """Draw a hand-drawn arrow from start to end. Styles: sweep, pointer, branch."""
    canvas.saveState()
    canvas.setStrokeColor(color)
    canvas.setFillColor(color)

    anchors = _arrow_anchor_points(start, end, style)
    pts = _wobbled_polyline(anchors, seed=seed, samples=samples, jitter=jitter)

    # Draw twice with tiny offset for pen-passed-twice feel
    _draw_polyline(canvas, pts, line_width)
    pts2 = [(x + 0.4, y - 0.3) for x, y in pts]
    _draw_polyline(canvas, pts2, line_width * 0.7)

    # Arrowhead direction: from second-to-last to last point
    if len(pts) >= 2:
        x1, y1 = pts[-2]
        x2, y2 = pts[-1]
        _draw_arrowhead(canvas, pts[-1], (x2 - x1, y2 - y1), seed, color)

    canvas.restoreState()

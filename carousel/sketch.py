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

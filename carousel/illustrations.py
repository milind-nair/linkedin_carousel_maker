"""Vector-drawn glyph illustrations and unified draw helper.

Each glyph is a callable ``(canvas, x, y, size, color)`` where ``(x, y)`` is
the bottom-left corner of the glyph's bounding box and ``size`` is the box
width in points. Glyphs are registered in ``GLYPHS`` and dispatched by name.

``draw_illustration`` accepts an ``IllustrationSpec`` dict and routes to
either the glyph registry or ``carousel.images.draw_image``, depending on
which field is populated.
"""

from __future__ import annotations
import math
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from carousel.config import DrawContext


# ── Individual glyphs ──

def _stroke_setup(c, color, size, weight_ratio=0.045):
    c.setStrokeColor(color)
    c.setLineWidth(max(1.2, size * weight_ratio))
    c.setLineCap(1)  # round
    c.setLineJoin(1)  # round


def draw_terminal(c, x, y, size, color):
    """Terminal window with prompt chevron and cursor."""
    h = size * 0.72
    r = size * 0.05
    c.saveState()
    _stroke_setup(c, color, size)
    p = c.beginPath()
    p.roundRect(x, y, size, h, r)
    c.drawPath(p, fill=0, stroke=1)
    # Title bar underline
    bar_y = y + h - size * 0.18
    c.line(x, bar_y, x + size, bar_y)
    # Three window dots
    dot_r = size * 0.028
    dot_y = y + h - size * 0.09
    c.setFillColor(color)
    for dx in (0.08, 0.16, 0.24):
        c.circle(x + size * dx, dot_y, dot_r, fill=1, stroke=0)
    # Prompt chevron ">"
    c.setLineWidth(size * 0.055)
    cx = x + size * 0.16
    cy = y + h * 0.36
    arm = size * 0.085
    c.line(cx - arm, cy + arm, cx, cy)
    c.line(cx, cy, cx - arm, cy - arm)
    # Cursor block
    c.setFillColor(color)
    c.rect(x + size * 0.32, cy - arm * 0.55, size * 0.24, size * 0.04,
           fill=1, stroke=0)
    c.restoreState()


def draw_code_brackets(c, x, y, size, color):
    """Angle brackets with slash: </>"""
    c.saveState()
    _stroke_setup(c, color, size, weight_ratio=0.07)
    cy = y + size * 0.5
    arm = size * 0.22
    gap = size * 0.14
    # Left bracket
    lx = x + size * 0.18
    c.line(lx, cy + arm, lx - arm * 0.9, cy)
    c.line(lx - arm * 0.9, cy, lx, cy - arm)
    # Right bracket
    rx = x + size * 0.82
    c.line(rx, cy + arm, rx + arm * 0.9, cy)
    c.line(rx + arm * 0.9, cy, rx, cy - arm)
    # Middle slash
    c.line(x + size * 0.5 - gap * 0.3, cy - arm,
           x + size * 0.5 + gap * 0.3, cy + arm)
    c.restoreState()


def draw_gear(c, x, y, size, color):
    """Gear: stroked outline with filled radial teeth."""
    c.saveState()
    _stroke_setup(c, color, size, weight_ratio=0.06)
    cx = x + size / 2
    cy = y + size / 2
    outer_r = size * 0.42
    inner_r = size * 0.30
    hole_r = size * 0.12
    teeth = 8
    c.setFillColor(color)
    for i in range(teeth):
        ang = (i / teeth) * 2 * math.pi
        mid_r = (inner_r + outer_r) / 2
        tx = cx + math.cos(ang) * mid_r
        ty = cy + math.sin(ang) * mid_r
        c.saveState()
        c.translate(tx, ty)
        c.rotate(math.degrees(ang) + 90)
        tw = size * 0.14
        th = outer_r - inner_r + size * 0.03
        c.rect(-tw / 2, -th / 2, tw, th, fill=1, stroke=0)
        c.restoreState()
    # Body outline
    c.circle(cx, cy, inner_r, fill=0, stroke=1)
    # Inner hole outline
    c.circle(cx, cy, hole_r, fill=0, stroke=1)
    c.restoreState()


def draw_split_path(c, x, y, size, color):
    """Two arrows diverging from a single line: fork."""
    c.saveState()
    _stroke_setup(c, color, size, weight_ratio=0.055)
    mid_x = x + size * 0.5
    base_y = y + size * 0.15
    fork_y = y + size * 0.5
    top_y = y + size * 0.85
    # Trunk
    c.line(mid_x, base_y, mid_x, fork_y)
    # Left branch
    left_x = x + size * 0.18
    c.line(mid_x, fork_y, left_x, top_y)
    # Right branch
    right_x = x + size * 0.82
    c.line(mid_x, fork_y, right_x, top_y)
    # Arrowheads (left)
    ah = size * 0.09
    # Left arrow tip
    _arrowhead(c, left_x, top_y, angle_deg=135, length=ah)
    # Right arrow tip
    _arrowhead(c, right_x, top_y, angle_deg=45, length=ah)
    c.restoreState()


def _arrowhead(c, tip_x, tip_y, angle_deg, length):
    """Draw a V arrowhead pointing in angle_deg direction from tip."""
    a = math.radians(angle_deg)
    # Arrowhead wings at +/- 35 deg from the reverse direction
    back = a + math.pi
    wing_a = math.radians(35)
    for w in (back - wing_a, back + wing_a):
        wx = tip_x + math.cos(w) * length
        wy = tip_y + math.sin(w) * length
        c.line(tip_x, tip_y, wx, wy)


def draw_lock(c, x, y, size, color):
    """Padlock glyph."""
    c.saveState()
    body_w = size * 0.68
    body_h = size * 0.52
    body_x = x + (size - body_w) / 2
    body_y = y + size * 0.08
    r = size * 0.06
    # Body
    c.setFillColor(color)
    p = c.beginPath()
    p.roundRect(body_x, body_y, body_w, body_h, r)
    c.drawPath(p, fill=1, stroke=0)
    # Shackle arc
    _stroke_setup(c, color, size, weight_ratio=0.08)
    arc_cx = x + size / 2
    arc_cy = body_y + body_h
    arc_r = size * 0.22
    # Draw semicircle
    p2 = c.beginPath()
    p2.moveTo(arc_cx - arc_r, arc_cy)
    p2.arcTo(arc_cx - arc_r, arc_cy - arc_r, arc_cx + arc_r, arc_cy + arc_r,
             startAng=180, extent=-180)
    c.drawPath(p2, fill=0, stroke=1)
    # Keyhole
    c.setFillColorRGB(1, 1, 1)
    kh_r = size * 0.05
    kh_y = body_y + body_h * 0.58
    c.circle(arc_cx, kh_y, kh_r, fill=1, stroke=0)
    c.rect(arc_cx - kh_r * 0.5, body_y + body_h * 0.22,
           kh_r, kh_y - body_y - body_h * 0.22, fill=1, stroke=0)
    c.restoreState()


def draw_flow_arrow(c, x, y, size, color):
    """Horizontal flow arrow with two connected nodes."""
    c.saveState()
    _stroke_setup(c, color, size, weight_ratio=0.055)
    cy = y + size * 0.5
    node_r = size * 0.12
    left_cx = x + node_r + size * 0.02
    right_cx = x + size - node_r - size * 0.02
    # Nodes
    c.setFillColor(color)
    c.circle(left_cx, cy, node_r, fill=1, stroke=0)
    c.circle(right_cx, cy, node_r, fill=1, stroke=0)
    # Connector
    c.setStrokeColor(color)
    arrow_start = left_cx + node_r
    arrow_end = right_cx - node_r
    c.line(arrow_start, cy, arrow_end, cy)
    # Arrowhead at end
    ah = size * 0.1
    _arrowhead(c, arrow_end, cy, angle_deg=0, length=ah)
    c.restoreState()


def draw_chip(c, x, y, size, color):
    """CPU chip with pins."""
    c.saveState()
    chip_w = size * 0.58
    chip_h = size * 0.58
    chip_x = x + (size - chip_w) / 2
    chip_y = y + (size - chip_h) / 2
    r = size * 0.04
    _stroke_setup(c, color, size, weight_ratio=0.055)
    # Chip body
    p = c.beginPath()
    p.roundRect(chip_x, chip_y, chip_w, chip_h, r)
    c.drawPath(p, fill=0, stroke=1)
    # Inner square
    inset = size * 0.12
    p2 = c.beginPath()
    p2.roundRect(chip_x + inset, chip_y + inset,
                 chip_w - 2 * inset, chip_h - 2 * inset, r * 0.6)
    c.drawPath(p2, fill=0, stroke=1)
    # Pins: 3 per side
    pin_len = size * 0.09
    c.setFillColor(color)
    pin_w = size * 0.04
    for i in range(3):
        t = (i + 1) / 4
        # Left
        px = chip_x - pin_len
        py = chip_y + chip_h * t - pin_w / 2
        c.rect(px, py, pin_len, pin_w, fill=1, stroke=0)
        # Right
        c.rect(chip_x + chip_w, py, pin_len, pin_w, fill=1, stroke=0)
        # Top
        py2 = chip_y + chip_h
        px2 = chip_x + chip_w * t - pin_w / 2
        c.rect(px2, py2, pin_w, pin_len, fill=1, stroke=0)
        # Bottom
        c.rect(px2, chip_y - pin_len, pin_w, pin_len, fill=1, stroke=0)
    c.restoreState()


def draw_wrench(c, x, y, size, color):
    """Wrench: circular head with diagonal handle."""
    c.saveState()
    _stroke_setup(c, color, size, weight_ratio=0.075)
    # Head ring
    head_cx = x + size * 0.28
    head_cy = y + size * 0.74
    head_r = size * 0.18
    c.circle(head_cx, head_cy, head_r, fill=0, stroke=1)
    # Notch opening at upper-left (punch with bg-colored rect)
    c.setFillColorRGB(1, 1, 1)
    c.setStrokeColorRGB(1, 1, 1)
    c.saveState()
    c.translate(head_cx, head_cy)
    c.rotate(135)
    c.rect(-size * 0.06, head_r * 0.7, size * 0.12, size * 0.12,
           fill=1, stroke=1)
    c.restoreState()
    # Restore stroke settings and draw handle
    _stroke_setup(c, color, size, weight_ratio=0.075)
    ang = math.radians(315)
    handle_start_x = head_cx + math.cos(ang) * head_r
    handle_start_y = head_cy + math.sin(ang) * head_r
    handle_end_x = x + size * 0.9
    handle_end_y = y + size * 0.1
    c.line(handle_start_x, handle_start_y, handle_end_x, handle_end_y)
    c.restoreState()


def draw_scale(c, x, y, size, color):
    """Balance scale: two plates on a horizontal beam."""
    c.saveState()
    _stroke_setup(c, color, size, weight_ratio=0.055)
    cx = x + size * 0.5
    # Vertical stand
    stand_top = y + size * 0.8
    stand_bot = y + size * 0.2
    c.line(cx, stand_top, cx, stand_bot)
    # Base
    c.line(cx - size * 0.2, stand_bot, cx + size * 0.2, stand_bot)
    # Beam
    beam_y = stand_top
    beam_w = size * 0.72
    c.line(cx - beam_w / 2, beam_y, cx + beam_w / 2, beam_y)
    # Left plate (arc)
    for px_offset in (-beam_w / 2, beam_w / 2):
        px = cx + px_offset
        # Support strings
        c.line(px, beam_y, px, beam_y - size * 0.1)
        # Plate
        plate_w = size * 0.22
        plate_y = beam_y - size * 0.1
        c.line(px - plate_w / 2, plate_y, px + plate_w / 2, plate_y)
        # Bowl arc
        p = c.beginPath()
        p.moveTo(px - plate_w / 2, plate_y)
        p.curveTo(
            px - plate_w / 2, plate_y - size * 0.08,
            px + plate_w / 2, plate_y - size * 0.08,
            px + plate_w / 2, plate_y,
        )
        c.drawPath(p, fill=0, stroke=1)
    # Fulcrum dot
    c.setFillColor(color)
    c.circle(cx, beam_y, size * 0.03, fill=1, stroke=0)
    c.restoreState()


def draw_layers(c, x, y, size, color):
    """Three stacked layers, isometric perspective."""
    c.saveState()
    _stroke_setup(c, color, size, weight_ratio=0.05)
    layer_w = size * 0.78
    layer_h = size * 0.14
    skew = size * 0.18
    cx = x + size / 2
    # Bottom to top
    for i, alpha_mul in enumerate((0.35, 0.65, 1.0)):
        ly = y + size * 0.15 + i * (layer_h + size * 0.05)
        # Parallelogram
        lx = cx - layer_w / 2
        c.saveState()
        c.setFillColor(color)
        c.setFillAlpha(alpha_mul)
        p = c.beginPath()
        p.moveTo(lx + skew, ly + layer_h)
        p.lineTo(lx + layer_w, ly + layer_h)
        p.lineTo(lx + layer_w - skew, ly)
        p.lineTo(lx, ly)
        p.close()
        c.drawPath(p, fill=1, stroke=1)
        c.restoreState()
    c.restoreState()


# ── Registry ──

GLYPHS: dict[str, Callable] = {
    "terminal": draw_terminal,
    "code_brackets": draw_code_brackets,
    "gear": draw_gear,
    "split_path": draw_split_path,
    "lock": draw_lock,
    "flow_arrow": draw_flow_arrow,
    "chip": draw_chip,
    "wrench": draw_wrench,
    "scale": draw_scale,
    "layers": draw_layers,
}


def draw_glyph(name: str, c, x: float, y: float, size: float, color) -> None:
    fn = GLYPHS.get(name)
    if fn is None:
        raise ValueError(
            f"Unknown glyph '{name}'. Known: {sorted(GLYPHS)}"
        )
    fn(c, x, y, size, color)


# ── Unified draw helper ──

def _compute_position(ctx: "DrawContext", spec: dict) -> tuple[float, float]:
    """Return (x, y) bottom-left for the illustration box."""
    cfg = ctx.config
    W = cfg.width
    H = cfg.height
    M = cfg.margin
    size = spec.get("size", 56)
    pos = spec.get("position", "top_right")
    if pos == "custom":
        return spec.get("x", M), spec.get("y", H - M - size)
    if pos == "top_left":
        return M, H - M - size
    # top_right (default) — aligned with pill band
    return W - M - size, H - 62 - size * 0.2


def draw_illustration(
    ctx: "DrawContext",
    spec: dict,
    default_color,
) -> None:
    """Draw an illustration from its spec — either a glyph or an image file."""
    if not spec:
        return
    x, y = _compute_position(ctx, spec)
    size = spec.get("size", 56)
    opacity = spec.get("opacity", 1.0)

    if spec.get("glyph"):
        cfg = ctx.config
        color = (
            cfg.colors.resolve(spec["color"])
            if spec.get("color")
            else default_color
        )
        c = ctx.canvas
        c.saveState()
        if opacity < 1.0:
            c.setFillAlpha(opacity)
            c.setStrokeAlpha(opacity)
        draw_glyph(spec["glyph"], c, x, y, size, color)
        c.restoreState()
    elif spec.get("source"):
        # Route through existing image pipeline
        from carousel.schema import ImageSpec
        from carousel.images import draw_image
        img_spec = ImageSpec(
            source=spec["source"],
            x=x,
            y=y,
            width=size,
            height=size,
            fit_mode=spec.get("fit_mode", "contain"),
            clip=spec.get("clip", "none"),
            clip_radius=spec.get("clip_radius", 6),
            opacity=opacity,
            anchor="bottom_left",
        )
        draw_image(ctx, img_spec)

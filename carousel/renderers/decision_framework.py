"""Renderer for decision_framework slides."""

from __future__ import annotations

from reportlab.lib.colors import white

from carousel.registry import register
from carousel.primitives import bottom_takeaway as draw_bottom_takeaway, draw_text, wrap
from carousel.layout import decorate_page, draw_footer
from carousel.illustrations import draw_illustration
from carousel.images import draw_image


def _measure_decisions(decisions, fonts, q_size, a_size, q_leading, a_leading, max_text_w):
    """Measure total height of all decision blocks at given font sizes."""
    block_heights = []
    for dec in decisions:
        q_lines = wrap(dec.get("question", ""), fonts.bold, q_size, max_text_w)
        answer_text = "\u2192  " + dec.get("answer", "")
        a_lines = wrap(answer_text, fonts.body, a_size, max_text_w)
        q_h = len(q_lines) * q_leading
        a_h = len(a_lines) * a_leading
        block_heights.append(q_h + 4 + a_h)
    return block_heights


@register("decision_framework")
def render_decision_framework(slide: dict, ctx):
    """Render a decision framework slide with numbered items."""
    c = ctx.canvas
    cfg = ctx.config
    W, H = cfg.width, cfg.height
    M = cfg.margin
    CW = cfg.content_width

    # Background
    c.setFillColor(cfg.colors.bg)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    decorate_page(ctx)

    # Image (drawn early so content renders on top)
    img = slide.get("image")
    if img:
        from carousel.schema import ImageSpec
        draw_image(ctx, ImageSpec(**img) if isinstance(img, dict) else img)

    # Illustration (top-right)
    ill = slide.get("illustration")
    if ill:
        draw_illustration(ctx, ill, cfg.colors.primary)

    # Heading
    heading = slide.get("heading", "")
    if heading:
        c.setFont(cfg.fonts.display, 26)
        c.setFillColor(cfg.colors.primary_dark)
        c.drawString(M, H - 70, heading)

    # Subheading
    subheading = slide.get("subheading")
    subheading_end = H - 115
    if subheading:
        subheading_end = draw_text(
            c, M, H - 96, subheading, cfg.fonts.bold, 13, cfg.colors.stone, max_w=CW
        )

    # Decisions — auto-scaling font sizes
    decisions = slide.get("decisions", [])
    text_x = M + 42
    max_text_w = W - M - text_x

    top_y = subheading_end - 30
    bt = slide.get("bottom_takeaway")
    if bt:
        from carousel.primitives import measure_bottom_takeaway_height
        bt_h = measure_bottom_takeaway_height(ctx, bt.get("body", ""))
        bottom_y = 54 + bt_h + 16  # takeaway y_bottom + height + padding
    else:
        bottom_y = 60
    available = top_y - bottom_y
    n = len(decisions)

    # Try font sizes from large to small until content fits
    font_tiers = [
        (15, 13.5, 19, 17),  # preferred
        (14, 12.5, 17, 16),  # medium
        (13, 12, 16, 15),    # compact
        (12, 11, 15, 14),    # tight
    ]

    q_size = a_size = q_leading = a_leading = 0
    block_heights = []
    for qs, as_, ql, al in font_tiers:
        q_size, a_size, q_leading, a_leading = qs, as_, ql, al
        block_heights = _measure_decisions(
            decisions, cfg.fonts, q_size, a_size, q_leading, a_leading, max_text_w
        )
        total = sum(block_heights)
        min_gaps = n * 12
        if total + min_gaps <= available:
            break

    total_content = sum(block_heights)
    gap = max(12, (available - total_content) / max(n, 1)) if n else 0

    # Draw decisions
    y = top_y
    for i, dec in enumerate(decisions):
        color = cfg.colors.resolve(dec.get("color", "#D97706"))

        # Number circle
        cx, cy = text_x - 26, y + 2
        c.setFillColor(color)
        c.circle(cx, cy, 14, fill=1, stroke=0)
        c.setFont(cfg.fonts.bold, 12)
        c.setFillColor(white)
        c.drawCentredString(cx, cy - 4, str(i + 1))

        # Question
        q_lines = wrap(dec.get("question", ""), cfg.fonts.bold, q_size, max_text_w)
        c.setFont(cfg.fonts.bold, q_size)
        c.setFillColor(cfg.colors.text)
        qy = y + 4
        for ql in q_lines:
            c.drawString(text_x, qy, ql)
            qy -= q_leading

        # Answer
        answer_text = "\u2192  " + dec.get("answer", "")
        a_lines = wrap(answer_text, cfg.fonts.body, a_size, max_text_w)
        c.setFont(cfg.fonts.body, a_size)
        c.setFillColor(color)
        ay = qy - 4
        for al in a_lines:
            c.drawString(text_x, ay, al)
            ay -= a_leading

        # Divider between decisions
        if i < len(decisions) - 1:
            div_y = ay - gap * 0.35
            c.setStrokeColor(cfg.colors.divider)
            c.setLineWidth(0.4)
            c.line(text_x, div_y, W - M, div_y)

        y = ay - gap

    # Bottom takeaway
    if bt:
        accent = cfg.colors.resolve(bt.get("accent_color", "#D97706"))
        bg = cfg.colors.resolve(bt["bg"]) if bt.get("bg") else None
        draw_bottom_takeaway(ctx, accent, bt["label"], bt["body"], bg=bg)

    draw_footer(ctx)

"""Renderer for decision_framework slides."""

from __future__ import annotations

from reportlab.lib.colors import white

from carousel.registry import register
from carousel.primitives import bottom_takeaway as draw_bottom_takeaway, draw_text, wrap
from carousel.layout import decorate_page, draw_footer
from carousel.illustrations import draw_illustration
from carousel.images import draw_image


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

    # Decisions
    decisions = slide.get("decisions", [])
    y = subheading_end - 35
    row_gap = 80

    text_x = M + 42
    max_text_w = W - M - text_x

    for i, dec in enumerate(decisions):
        color = cfg.colors.resolve(dec.get("color", "#D97706"))

        # Number circle
        cx, cy = text_x - 26, y + 2
        c.setFillColor(color)
        c.circle(cx, cy, 14, fill=1, stroke=0)
        c.setFont(cfg.fonts.bold, 12)
        c.setFillColor(white)
        c.drawCentredString(cx, cy - 4, str(i + 1))

        # Question (wrapped)
        q_lines = wrap(dec.get("question", ""), cfg.fonts.body, 12, max_text_w)
        c.setFont(cfg.fonts.body, 12)
        c.setFillColor(cfg.colors.text)
        qy = y + 4
        for ql in q_lines:
            c.drawString(text_x, qy, ql)
            qy -= 15

        # Answer (wrapped)
        answer_text = "\u2192  " + dec.get("answer", "")
        a_lines = wrap(answer_text, cfg.fonts.bold, 13, max_text_w)
        c.setFont(cfg.fonts.bold, 13)
        c.setFillColor(color)
        ay = qy - 4
        for al in a_lines:
            c.drawString(text_x, ay, al)
            ay -= 16

        # Divider
        if i < len(decisions) - 1:
            c.setStrokeColor(cfg.colors.divider)
            c.setLineWidth(0.4)
            div_y = ay - 8
            c.line(text_x, div_y, W - M, div_y)

        y = ay - 16

    # Bottom takeaway
    bt = slide.get("bottom_takeaway")
    if bt:
        accent = cfg.colors.resolve(bt.get("accent_color", "#D97706"))
        bg = cfg.colors.resolve(bt["bg"]) if bt.get("bg") else None
        draw_bottom_takeaway(ctx, accent, bt["label"], bt["body"], bg=bg)

    draw_footer(ctx)

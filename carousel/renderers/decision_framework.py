"""Renderer for decision_framework slides."""

from __future__ import annotations

from reportlab.lib.colors import white

from carousel.registry import register
from carousel.primitives import bottom_takeaway as draw_bottom_takeaway
from carousel.layout import decorate_page, draw_footer


@register("decision_framework")
def render_decision_framework(slide: dict, ctx):
    """Render a decision framework slide with numbered items."""
    c = ctx.canvas
    cfg = ctx.config
    W, H = cfg.width, cfg.height
    M = cfg.margin

    # Background
    c.setFillColor(cfg.colors.bg)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    decorate_page(ctx)

    # Heading
    heading = slide.get("heading", "")
    if heading:
        c.setFont(cfg.fonts.display, 26)
        c.setFillColor(cfg.colors.primary_dark)
        c.drawString(M, H - 70, heading)

    # Subheading
    subheading = slide.get("subheading")
    if subheading:
        c.setFont(cfg.fonts.body, 11)
        c.setFillColor(cfg.colors.stone)
        c.drawString(M, H - 96, subheading)

    # Decisions
    decisions = slide.get("decisions", [])
    y = H - 126
    row_gap = 80

    for i, dec in enumerate(decisions):
        color = cfg.colors.resolve(dec.get("color", "#D97706"))

        # Number circle
        cx, cy = M + 16, y + 2
        c.setFillColor(color)
        c.circle(cx, cy, 14, fill=1, stroke=0)
        c.setFont(cfg.fonts.bold, 12)
        c.setFillColor(white)
        c.drawCentredString(cx, cy - 4, str(i + 1))

        # Question
        c.setFont(cfg.fonts.body, 12)
        c.setFillColor(cfg.colors.text)
        c.drawString(M + 42, y + 4, dec.get("question", ""))

        # Answer
        c.setFont(cfg.fonts.bold, 13)
        c.setFillColor(color)
        c.drawString(M + 42, y - 16, "\u2192  " + dec.get("answer", ""))

        # Divider
        if i < len(decisions) - 1:
            c.setStrokeColor(cfg.colors.divider)
            c.setLineWidth(0.4)
            c.line(M + 42, y - 36, W - M, y - 36)

        y -= row_gap

    # Bottom takeaway
    bt = slide.get("bottom_takeaway")
    if bt:
        accent = cfg.colors.resolve(bt.get("accent_color", "#D97706"))
        bg = cfg.colors.resolve(bt["bg"]) if bt.get("bg") else None
        draw_bottom_takeaway(ctx, accent, bt["label"], bt["body"], bg=bg)

    draw_footer(ctx)

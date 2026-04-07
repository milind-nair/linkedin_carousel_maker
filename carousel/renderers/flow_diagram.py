"""Renderer for flow_diagram slides."""

from __future__ import annotations

from reportlab.lib.colors import white

from carousel.registry import register
from carousel.primitives import rrect, pill, wrap, draw_text
from carousel.layout import decorate_page, draw_footer
from carousel.illustrations import draw_illustration
from carousel.images import draw_image


@register("flow_diagram")
def render_flow_diagram(slide: dict, ctx):
    """Render a flow diagram with connected cards."""
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

    # Flow steps
    steps = slide.get("steps", [])
    y = subheading_end - 5
    item_h = 96
    gap = 16

    for i, step in enumerate(steps):
        iy = y - item_h
        color = cfg.colors.resolve(step.get("color", "#D97706"))

        rrect(c, M, iy, CW, item_h, 5,
              fill=cfg.colors.card_bg, stroke=cfg.colors.divider, sw=0.4)
        c.setFillColor(color)
        c.rect(M, iy, 4, item_h, fill=1, stroke=0)

        # Pill label
        pill(c, M + 16, iy + item_h - 28, step.get("label", ""),
             color, white, font_bold=cfg.fonts.bold, size=11)

        # Description
        desc = step.get("description", "")
        desc_lines = wrap(desc, cfg.fonts.body, 10.5, CW - 36)
        dy = iy + item_h - 50
        c.setFont(cfg.fonts.body, 10.5)
        c.setFillColor(cfg.colors.text)
        for dl in desc_lines:
            c.drawString(M + 16, dy, dl)
            dy -= 15

        # Arrow connector
        if i < len(steps) - 1:
            c.setFont(cfg.fonts.body, 12)
            c.setFillColor(cfg.colors.muted)
            c.drawCentredString(W / 2, iy - 14, "\u2193")

        y -= item_h + gap

    draw_footer(ctx)

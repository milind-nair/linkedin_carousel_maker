"""Renderer for closing_dark slides."""

from __future__ import annotations

from reportlab.lib.colors import HexColor

from carousel.registry import register
from carousel.layout import decorate_page, draw_footer
from carousel.images import draw_image


@register("closing_dark")
def render_closing_dark(slide: dict, ctx):
    """Render a dark-background closing slide."""
    c = ctx.canvas
    cfg = ctx.config
    W, H = cfg.width, cfg.height
    M = cfg.margin

    # Background
    c.setFillColor(cfg.colors.bg_dark)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    decorate_page(ctx, dark=True)

    # Geometric accent
    ga = slide.get("geometric_accent")
    if ga:
        color = cfg.colors.resolve(ga.get("color", "#D97706")) if ga.get("color") else cfg.colors.primary
        c.saveState()
        c.setFillColor(color)
        c.setFillAlpha(ga.get("alpha", 0.06))
        c.rect(W * ga.get("x_pct", 0.5), H * ga.get("y_pct", 0.65),
               W * ga.get("w_pct", 0.6), ga.get("h", 60), fill=1, stroke=0)
        c.restoreState()

    # Amber bar motif
    c.setFillColor(cfg.colors.accent)
    c.rect(M, H - 120, 40, 4, fill=1, stroke=0)

    # Quote lines
    y = H - 186
    for line in slide.get("quote_lines", []):
        c.setFont(cfg.fonts.display, 36)
        c.setFillColor(cfg.colors.text_light)
        c.drawString(M, y, line)
        y -= 48

    # Summary lines
    y -= 24
    for line in slide.get("summary_lines", []):
        c.setFont(cfg.fonts.body, 12.5)
        c.setFillColor(cfg.colors.muted)
        c.drawString(M, y, line)
        y -= 22

    # Optional image
    img = slide.get("image")
    if img:
        from carousel.schema import ImageSpec
        draw_image(ctx, ImageSpec(**img) if isinstance(img, dict) else img)

    draw_footer(ctx, dark=True)

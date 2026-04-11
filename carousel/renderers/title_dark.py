"""Renderer for title_dark slides."""

from __future__ import annotations
from reportlab.lib.colors import HexColor

from carousel.registry import register
from carousel.primitives import draw_text
from carousel.layout import decorate_page, draw_footer
from carousel.images import draw_image
from carousel.themes import resolve_dark_theme


@register("title_dark")
def render_title_dark(slide: dict, ctx):
    """Render a dark-background title slide."""
    theme = resolve_dark_theme(slide.get("theme"), ctx.output_filename)
    ctx = ctx.with_overrides(theme.as_overrides())
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
        color = cfg.colors.resolve(ga.get("color")) if ga.get("color") else cfg.colors.primary
        c.saveState()
        c.setFillColor(color)
        c.setFillAlpha(ga.get("alpha", 0.07))
        c.rect(W * ga.get("x_pct", 0.55), H * ga.get("y_pct", 0.72),
               W * ga.get("w_pct", 0.6), ga.get("h", 80), fill=1, stroke=0)
        c.restoreState()

    # Amber bar motif
    c.setFillColor(cfg.colors.accent)
    c.rect(M, H - 120, 40, 4, fill=1, stroke=0)

    # Kicker
    kicker = slide.get("kicker")
    if kicker:
        c.setFont(cfg.fonts.bold, 11)
        c.setFillColor(cfg.colors.accent)
        c.drawString(M, H - 150, kicker)

    # Title lines
    y = H - 200
    for line in slide.get("title_lines", []):
        c.setFont(cfg.fonts.display, 40)
        c.setFillColor(cfg.colors.text_light)
        c.drawString(M, y, line)
        y -= 52

    # Subtitle lines
    y -= 20
    for line in slide.get("subtitle_lines", []):
        c.setFont(cfg.fonts.body, 13)
        c.setFillColor(cfg.colors.muted)
        c.drawString(M, y, line)
        y -= 20

    # CTA text
    cta = slide.get("cta_text")
    if cta:
        c.setFont(cfg.fonts.body, 10)
        c.setFillColor(cfg.colors.stone)
        c.drawString(M, 65, cta)

    # Optional image
    img = slide.get("image")
    if img:
        from carousel.schema import ImageSpec
        draw_image(ctx, ImageSpec(**img) if isinstance(img, dict) else img)

    draw_footer(ctx, dark=True)

"""Page-level drawing — page setup, viewport decoration, footer."""

from __future__ import annotations
from pathlib import Path
from typing import TYPE_CHECKING

from reportlab.lib.colors import HexColor

if TYPE_CHECKING:
    from carousel.config import DrawContext


def new_page(ctx: "DrawContext", dark: bool = False):
    """Start a new page with background fill and viewport decoration."""
    c = ctx.canvas
    cfg = ctx.config
    c.showPage()
    c.setPageSize((cfg.width, cfg.height))
    bg = cfg.colors.bg_dark if dark else cfg.colors.bg
    c.setFillColor(bg)
    c.rect(0, 0, cfg.width, cfg.height, fill=1, stroke=0)
    decorate_page(ctx, dark=dark)


def decorate_page(ctx: "DrawContext", dark: bool = False):
    """Adds subtle structure so the lower viewport feels intentional."""
    c = ctx.canvas
    cfg = ctx.config
    W, H = cfg.width, cfg.height
    M = cfg.margin
    VB = cfg.viewport_band_height

    c.saveState()
    if dark:
        c.setFillColor(HexColor("#211D17"))
        c.rect(0, 0, W, VB, fill=1, stroke=0)
        c.setFillColor(cfg.colors.primary)
        c.setFillAlpha(0.05)
        c.rect(W * 0.58, 18, W * 0.48, 56, fill=1, stroke=0)
        c.setStrokeColor(HexColor("#2B2721"))
    else:
        c.setFillColor(HexColor("#FBF7EC"))
        c.rect(0, 0, W, VB, fill=1, stroke=0)
        c.setFillColor(cfg.colors.primary_light)
        c.setFillAlpha(0.38)
        c.rect(0, 0, W, 30, fill=1, stroke=0)
        c.setStrokeColor(HexColor("#EFE6D5"))
    c.setFillAlpha(1)
    c.setLineWidth(0.5)
    c.line(M, VB - 10, W - M, VB - 10)
    c.restoreState()


def draw_footer(ctx: "DrawContext", dark: bool = False):
    """Brand footer: name left, icon right, with subtle separator."""
    c = ctx.canvas
    cfg = ctx.config
    M = cfg.margin
    W = cfg.width
    y = 18

    # Separator line
    sep_color = HexColor("#333330") if dark else cfg.colors.divider
    c.setStrokeColor(sep_color)
    c.setLineWidth(0.5)
    c.line(M, y + 24, W - M, y + 24)

    # Name
    c.setFont(cfg.fonts.bold, 9)
    c.setFillColor(cfg.colors.accent if dark else cfg.colors.primary_dark)
    c.drawString(M, y, cfg.brand_name)

    # Icon
    icon_path = Path(cfg.brand_icon_path) if cfg.brand_icon_path else None
    if icon_path and icon_path.exists():
        icon_size = 24
        ix = W - M - icon_size
        iy = y - 4
        # Circle background behind icon
        c.saveState()
        circle_bg = HexColor("#2A2720") if dark else HexColor("#F5F0E6")
        c.setFillColor(circle_bg)
        c.circle(ix + icon_size / 2, iy + icon_size / 2, icon_size / 2 + 2, fill=1, stroke=0)
        c.restoreState()
        # Clip to circle
        c.saveState()
        p = c.beginPath()
        p.circle(ix + icon_size / 2, iy + icon_size / 2, icon_size / 2)
        c.clipPath(p, stroke=0)
        c.drawImage(
            str(icon_path), ix, iy,
            width=icon_size, height=icon_size,
            preserveAspectRatio=True, mask='auto',
        )
        c.restoreState()

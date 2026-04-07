"""Renderer for grid_cards slides."""

from __future__ import annotations

from carousel.registry import register
from carousel.primitives import draw_text, rrect, pill, bottom_takeaway as draw_bottom_takeaway, wrap
from carousel.layout import decorate_page, draw_footer
from carousel.illustrations import draw_illustration
from carousel.images import draw_image


@register("grid_cards")
def render_grid_cards(slide: dict, ctx):
    """Render a grid of small cards (e.g., the overview slide)."""
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
    subheading_end = H - 119
    if subheading:
        subheading_end = draw_text(
            c, M, H - 100, subheading, cfg.fonts.bold, 13, cfg.colors.stone, max_w=CW
        )

    # Grid items
    columns = slide.get("columns", 2)
    items = slide.get("items", [])
    gap = 14
    card_w = (CW - gap * (columns - 1)) / columns
    card_h = 98
    start_y = subheading_end - 19

    for i, item in enumerate(items):
        col = i % columns
        row = i // columns
        x = M + col * (card_w + gap)
        y = start_y - row * (card_h + gap) - card_h

        color = cfg.colors.resolve(item.get("color", "#D97706"))

        rrect(c, x, y, card_w, card_h, 5,
              fill=cfg.colors.card_bg, stroke=cfg.colors.divider, sw=0.5)
        # Top accent
        c.setFillColor(color)
        c.rect(x, y + card_h - 3, card_w, 3, fill=1, stroke=0)
        # Label
        c.setFont(cfg.fonts.bold, 15)
        c.setFillColor(color)
        c.drawString(x + 14, y + card_h - 26, item.get("label", ""))
        # Trigger
        trigger = item.get("trigger")
        if trigger:
            c.setFont(cfg.fonts.bold, 10)
            c.setFillColor(cfg.colors.muted)
            c.drawString(x + 14, y + card_h - 44, trigger)
        # Description
        desc = item.get("description", "")
        c.setFont(cfg.fonts.body, 10.5)
        c.setFillColor(cfg.colors.text)
        dy = y + card_h - 62
        for raw_line in desc.split("\n"):
            for dline in wrap(raw_line, cfg.fonts.body, 10.5, card_w - 28):
                c.drawString(x + 14, dy, dline)
                dy -= 14

    # Bottom takeaway
    bt = slide.get("bottom_takeaway")
    if bt:
        accent = cfg.colors.resolve(bt.get("accent_color", "#D97706"))
        bg = cfg.colors.resolve(bt["bg"]) if bt.get("bg") else None
        draw_bottom_takeaway(ctx, accent, bt["label"], bt["body"], bg=bg)

    draw_footer(ctx)

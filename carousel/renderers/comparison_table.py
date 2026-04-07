"""Renderer for comparison_table slides."""

from __future__ import annotations

from reportlab.lib.colors import HexColor

from carousel.registry import register
from carousel.primitives import rrect, wrap, bottom_takeaway as draw_bottom_takeaway, draw_text
from carousel.layout import decorate_page, draw_footer
from carousel.illustrations import draw_illustration
from carousel.images import draw_image


@register("comparison_table")
def render_comparison_table(slide: dict, ctx):
    """Render a comparison table slide."""
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

    # Table
    col_defs = slide.get("columns", [])
    rows = slide.get("rows", [])

    table_x = M
    table_top = subheading_end - 35
    header_h = 30
    row_h = 78

    # Header row
    rrect(c, table_x, table_top - header_h, CW, header_h, 5,
          fill=HexColor("#FCF7EA"), stroke=cfg.colors.stone, sw=1.0)

    x = table_x
    for col_def in col_defs:
        heading_text = col_def.get("header", "")
        width = col_def.get("width", 100)
        c.setFont(cfg.fonts.bold, 9)
        c.setFillColor(cfg.colors.primary_dark)
        c.drawString(x + 8, table_top - 19, heading_text.upper())
        x += width
        if x < table_x + CW:
            c.setStrokeColor(cfg.colors.stone)
            c.setLineWidth(1.0)
            c.line(x, table_top, x, table_top - header_h - (row_h * len(rows)))

    # Data rows
    for i, row in enumerate(rows):
        row_top = table_top - header_h - (i * row_h)
        row_bottom = row_top - row_h
        color = cfg.colors.resolve(row.get("color", "#D97706"))

        rrect(c, table_x, row_bottom, CW, row_h, 4,
              fill=cfg.colors.card_bg, stroke=cfg.colors.stone, sw=1.0)

        # Left colored accent + label
        c.setFillColor(color)
        c.rect(table_x, row_bottom, 4, row_h, fill=1, stroke=0)
        c.setFont(cfg.fonts.bold, 11)
        c.setFillColor(color)
        c.drawString(table_x + 8, row_top - 22, row.get("label", ""))

        # Cell values
        cells = row.get("cells", [])
        x = table_x + (col_defs[0]["width"] if col_defs else 74)
        for j, cell_text in enumerate(cells):
            col_idx = j + 1  # skip first column (label)
            width = col_defs[col_idx]["width"] if col_idx < len(col_defs) else 100

            c.setStrokeColor(cfg.colors.stone)
            c.setLineWidth(1.0)
            c.line(x, row_bottom, x, row_top)

            c.setFont(cfg.fonts.bold, 10.5)
            c.setFillColor(cfg.colors.text)
            cell_y = row_top - 22
            for line in wrap(cell_text, cfg.fonts.bold, 10.5, width - 14):
                c.drawString(x + 7, cell_y, line)
                cell_y -= 13
            x += width

    # Bottom takeaway
    bt = slide.get("bottom_takeaway")
    if bt:
        accent = cfg.colors.resolve(bt.get("accent_color", "#D97706"))
        bg = cfg.colors.resolve(bt["bg"]) if bt.get("bg") else None
        draw_bottom_takeaway(ctx, accent, bt["label"], bt["body"], bg=bg)

    draw_footer(ctx)

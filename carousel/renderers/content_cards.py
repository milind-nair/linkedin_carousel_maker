"""Renderer for content_cards slides."""

from __future__ import annotations

from carousel.registry import register
from carousel.primitives import draw_text, pill, card_block, insight_block, bottom_takeaway, wrap
from carousel.layout import new_page, draw_footer

from reportlab.pdfbase import pdfmetrics


@register("content_cards")
def render_content_cards(slide: dict, ctx):
    """Render a content cards slide with pill, heading, cards, insight, takeaway."""
    c = ctx.canvas
    cfg = ctx.config
    M = cfg.margin
    H = cfg.height
    CW = cfg.content_width

    # Background
    c.setFillColor(cfg.colors.bg)
    c.rect(0, 0, cfg.width, cfg.height, fill=1, stroke=0)
    from carousel.layout import decorate_page
    decorate_page(ctx)

    # Pill
    pill_spec = slide.get("pill")
    if pill_spec:
        pill_bg = cfg.colors.resolve(pill_spec.get("bg", "#FEF3C7"))
        pill_fg = cfg.colors.resolve(pill_spec.get("fg", "#92400E"))
        pill(c, M, H - 62, pill_spec["text"], pill_bg, pill_fg, font_bold=cfg.fonts.bold)

    # Heading
    heading = slide.get("heading", "")
    if heading:
        c.setFont(cfg.fonts.display, 26)
        c.setFillColor(cfg.colors.primary_dark)
        c.drawString(M, H - 110, heading)

    # Date line
    date_line = slide.get("date_line")
    if date_line:
        c.setFont(cfg.fonts.body, 10)
        c.setFillColor(cfg.colors.stone)
        c.drawString(M, H - 132, date_line)

    # Subheading
    subheading = slide.get("subheading")
    sub_y = H - 140
    if date_line:
        sub_y = H - 155
    if subheading:
        draw_text(c, M, sub_y, subheading, cfg.fonts.body, 11, cfg.colors.stone, max_w=CW)

    # Cards
    y = sub_y - 32
    if date_line:
        y = sub_y - 31
    for card in slide.get("cards", []):
        accent = cfg.colors.resolve(card.get("accent_color", "#D97706"))
        cbg = cfg.colors.resolve(card.get("card_bg")) if card.get("card_bg") else None
        y = card_block(ctx, y, accent, card["title"], card["body"], card_bg=cbg)
        y -= 14

    # Insight
    ins = slide.get("insight")
    if ins:
        y -= 2
        accent = cfg.colors.resolve(ins.get("accent_color", "#F59E0B"))
        lbl_color = cfg.colors.resolve(ins["label_color"]) if ins.get("label_color") else None
        bg = cfg.colors.resolve(ins["bg"]) if ins.get("bg") else None
        y = insight_block(ctx, y, accent, ins["label"], ins["body"],
                          label_color=lbl_color, bg=bg)

    # Inline text
    inline = slide.get("inline_text")
    if inline:
        y -= 16
        prefix = inline.get("prefix", "")
        prefix_color = cfg.colors.resolve(inline["prefix_color"]) if inline.get("prefix_color") else cfg.colors.primary
        text_color = cfg.colors.resolve(inline["text_color"]) if inline.get("text_color") else cfg.colors.text

        c.setFont(cfg.fonts.bold, 10.5)
        c.setFillColor(prefix_color)
        c.drawString(M, y + 4, prefix)
        c.setFont(cfg.fonts.body, 10.5)
        c.setFillColor(text_color)
        prefix_w = pdfmetrics.stringWidth(prefix + " ", cfg.fonts.bold, 10.5)
        c.drawString(M + prefix_w, y + 4, inline.get("text", ""))

    # Bottom takeaway
    bt = slide.get("bottom_takeaway")
    if bt:
        accent = cfg.colors.resolve(bt.get("accent_color", "#D97706"))
        bg = cfg.colors.resolve(bt["bg"]) if bt.get("bg") else None
        bottom_takeaway(ctx, accent, bt["label"], bt["body"], bg=bg)

    draw_footer(ctx)

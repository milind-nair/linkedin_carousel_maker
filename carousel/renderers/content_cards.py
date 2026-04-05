"""Renderer for content_cards slides."""

from __future__ import annotations

from carousel.registry import register
from carousel.primitives import (
    bottom_takeaway,
    card_block,
    draw_text,
    insight_block,
    measure_bottom_takeaway_height,
    measure_card_block_height,
    measure_insight_block_height,
    pill,
)
from carousel.layout import draw_footer
from carousel.illustrations import draw_illustration

from reportlab.pdfbase import pdfmetrics


@register("content_cards")
def render_content_cards(slide: dict, ctx):
    """Render a content cards slide with pill, heading, cards, insight, takeaway."""
    c = ctx.canvas
    cfg = ctx.config
    M = cfg.margin
    H = cfg.height
    CW = cfg.content_width
    content_gap_after_text = 16
    gap_between_cards = 14
    gap_before_insight = 16
    gap_before_inline = 16
    gap_above_takeaway = 18

    # Background
    c.setFillColor(cfg.colors.bg)
    c.rect(0, 0, cfg.width, cfg.height, fill=1, stroke=0)
    from carousel.layout import decorate_page
    decorate_page(ctx)

    # Illustration (drawn first so pill/heading can overlap if needed)
    ill = slide.get("illustration")
    if ill:
        draw_illustration(ctx, ill, cfg.colors.primary)

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
    content_top = sub_y - (31 if date_line else 32)
    if subheading:
        content_top = draw_text(
            c, M, sub_y, subheading, cfg.fonts.body, 11, cfg.colors.stone, max_w=CW
        ) - content_gap_after_text

    cards = slide.get("cards", [])
    ins = slide.get("insight")
    inline = slide.get("inline_text")
    bt = slide.get("bottom_takeaway")

    gap_count = 0
    if len(cards) > 1:
        gap_count += len(cards) - 1
    if cards and ins:
        gap_count += 1
    if (cards or ins) and inline:
        gap_count += 1

    takeaway_height = measure_bottom_takeaway_height(ctx, bt["body"], expand=True) if bt else 0
    content_bottom = cfg.viewport_band_height + 24
    if bt:
        content_bottom = 54 + takeaway_height + gap_above_takeaway

    available_height = max(0, content_top - content_bottom)

    def measure_scaled_layout(type_scale: float) -> dict[str, float | list[float]]:
        card_title_size = 12.5 + 0.8 * type_scale
        card_body_size = 11 + 1.3 * type_scale
        insight_label_size = 10.5 + 0.7 * type_scale
        insight_body_size = 10.5 + 1.1 * type_scale
        inline_size = 10.5 + 0.8 * type_scale

        card_heights = [
            measure_card_block_height(
                ctx,
                card["body"],
                title_size=card_title_size,
                body_size=card_body_size,
            )
            for card in cards
        ]
        insight_height = (
            measure_insight_block_height(
                ctx,
                ins["body"],
                label_size=insight_label_size,
                body_size=insight_body_size,
            )
            if ins else 0
        )
        inline_height = max(18, inline_size * 1.5) if inline else 0
        natural_height = sum(card_heights) + insight_height + inline_height
        if len(cards) > 1:
            natural_height += (len(cards) - 1) * gap_between_cards
        if cards and ins:
            natural_height += gap_before_insight
        if (cards or ins) and inline:
            natural_height += gap_before_inline
        return {
            "card_title_size": card_title_size,
            "card_body_size": card_body_size,
            "insight_label_size": insight_label_size,
            "insight_body_size": insight_body_size,
            "inline_size": inline_size,
            "card_heights": card_heights,
            "insight_height": insight_height,
            "inline_height": inline_height,
            "natural_height": natural_height,
        }

    base_layout = measure_scaled_layout(0.0)
    space_budget = max(0, available_height - base_layout["natural_height"])
    type_scale = min(1.0, space_budget / 160) if space_budget > 0 else 0.0
    scaled_layout = measure_scaled_layout(type_scale)

    # Larger font sizes can add wrapped lines, so clamp back to the largest size
    # that still fits in the reserved content area.
    if type_scale > 0 and scaled_layout["natural_height"] > available_height:
        low = 0.0
        high = type_scale
        best_layout = base_layout
        for _ in range(12):
            mid = (low + high) / 2
            candidate = measure_scaled_layout(mid)
            if candidate["natural_height"] <= available_height:
                low = mid
                best_layout = candidate
            else:
                high = mid
        scaled_layout = best_layout

    card_title_size = scaled_layout["card_title_size"]
    card_body_size = scaled_layout["card_body_size"]
    insight_label_size = scaled_layout["insight_label_size"]
    insight_body_size = scaled_layout["insight_body_size"]
    inline_size = scaled_layout["inline_size"]
    natural_height = scaled_layout["natural_height"]

    extra_space = max(0, available_height - natural_height)
    expandable_blocks = len(cards) + (1 if ins else 0)
    extra_block_padding = 0.0
    extra_gap = 0.0

    if extra_space > 0:
        if expandable_blocks:
            block_growth = min(extra_space * 0.6, expandable_blocks * 28)
            extra_block_padding = block_growth / expandable_blocks
        else:
            block_growth = 0.0
        remaining_after_blocks = extra_space - block_growth
        if gap_count:
            gap_growth = min(remaining_after_blocks * 0.7, gap_count * 12)
            extra_gap = gap_growth / gap_count
        else:
            gap_growth = 0.0
        used_extra = block_growth + gap_growth
        start_offset = (extra_space - used_extra) / 2
    else:
        start_offset = 0.0

    # Cards
    y = content_top - start_offset
    for index, card in enumerate(cards):
        accent = cfg.colors.resolve(card.get("accent_color", "#D97706"))
        cbg = cfg.colors.resolve(card.get("card_bg")) if card.get("card_bg") else None
        y = card_block(
            ctx,
            y,
            accent,
            card["title"],
            card["body"],
            card_bg=cbg,
            extra_padding=extra_block_padding,
            title_size=card_title_size,
            body_size=card_body_size,
        )
        if index < len(cards) - 1:
            y -= gap_between_cards + extra_gap

    # Insight
    if ins:
        if cards:
            y -= gap_before_insight + extra_gap
        accent = cfg.colors.resolve(ins.get("accent_color", "#F59E0B"))
        lbl_color = cfg.colors.resolve(ins["label_color"]) if ins.get("label_color") else None
        bg = cfg.colors.resolve(ins["bg"]) if ins.get("bg") else None
        y = insight_block(
            ctx,
            y,
            accent,
            ins["label"],
            ins["body"],
            label_color=lbl_color,
            bg=bg,
            extra_padding=extra_block_padding,
            label_size=insight_label_size,
            body_size=insight_body_size,
        )

    # Inline text
    if inline:
        if cards or ins:
            y -= gap_before_inline + extra_gap
        prefix = inline.get("prefix", "")
        prefix_color = cfg.colors.resolve(inline["prefix_color"]) if inline.get("prefix_color") else cfg.colors.primary
        text_color = cfg.colors.resolve(inline["text_color"]) if inline.get("text_color") else cfg.colors.text

        inline_baseline = y - 2
        c.setFont(cfg.fonts.bold, inline_size)
        c.setFillColor(prefix_color)
        c.drawString(M, inline_baseline, prefix)
        c.setFont(cfg.fonts.body, inline_size)
        c.setFillColor(text_color)
        prefix_w = pdfmetrics.stringWidth(prefix + " ", cfg.fonts.bold, inline_size)
        c.drawString(M + prefix_w, inline_baseline, inline.get("text", ""))

    # Bottom takeaway
    if bt:
        accent = cfg.colors.resolve(bt.get("accent_color", "#D97706"))
        bg = cfg.colors.resolve(bt["bg"]) if bt.get("bg") else None
        bottom_takeaway(ctx, accent, bt["label"], bt["body"], bg=bg, expand=True)

    draw_footer(ctx)

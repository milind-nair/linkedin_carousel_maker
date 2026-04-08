"""Low-level drawing primitives — extracted from create_v2.py."""

from __future__ import annotations
from typing import TYPE_CHECKING

from reportlab.lib.colors import HexColor, Color
from reportlab.pdfbase import pdfmetrics

if TYPE_CHECKING:
    from carousel.config import DrawContext


def wrap(text: str, font: str, size: float, max_w: float) -> list[str]:
    """Word-wrap text to fit within max_w points."""
    words = text.split()
    lines: list[str] = []
    cur = ""
    for w in words:
        test = cur + (" " if cur else "") + w
        if pdfmetrics.stringWidth(test, font, size) <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_text(
    c, x: float, y: float, text: str, font: str, size: float, color: Color,
    max_w: float | None = None, leading: float | None = None, align: str = "left",
) -> float:
    """Draw text, returns y after last line. y = top of first line baseline."""
    if leading is None:
        leading = size * 1.45
    c.setFont(font, size)
    c.setFillColor(color)
    lines = wrap(text, font, size, max_w) if max_w else [text]
    for line in lines:
        if align == "center":
            c.drawCentredString(x, y, line)
        elif align == "right":
            c.drawRightString(x, y, line)
        else:
            c.drawString(x, y, line)
        y -= leading
    return y


def rrect(c, x: float, y: float, w: float, h: float, r: float,
          fill: Color | None = None, stroke: Color | None = None, sw: float = 0.5):
    """Rounded rect. y = bottom."""
    p = c.beginPath()
    p.roundRect(x, y, w, h, r)
    c.saveState()
    if fill:
        c.setFillColor(fill)
    if stroke:
        c.setStrokeColor(stroke)
        c.setLineWidth(sw)
    c.drawPath(p, fill=1 if fill else 0, stroke=1 if stroke else 0)
    c.restoreState()


def pill(c, x: float, y: float, text: str, bg: Color, fg: Color,
         font_bold: str = "Helvetica-Bold", size: float = 12) -> float:
    """Draw a pill badge. y = baseline of text inside. Returns pill width."""
    tw = pdfmetrics.stringWidth(text, font_bold, size)
    pw, ph = tw + 20, size + 14
    rrect(c, x, y - 5, pw, ph, ph / 2, fill=bg)
    c.setFont(font_bold, size)
    c.setFillColor(fg)
    c.drawString(x + 10, y + 1, text)
    return pw


def measure_card_block_height(
    ctx: "DrawContext",
    body: str,
    title_size: float = 12.5,
    body_size: float = 11,
    extra_padding: float = 0,
) -> float:
    """Measure the full height of a content card."""
    cfg = ctx.config
    body_lines = wrap(body, cfg.fonts.body, body_size, cfg.content_width - 40)
    title_body_gap = max(20, max(title_size + 7.5, body_size + 9))
    body_leading = max(16, body_size * 1.45)
    top_pad = 22 + extra_padding / 2
    bottom_pad = 22 + extra_padding / 2
    return top_pad + title_body_gap + max(0, len(body_lines) - 1) * body_leading + bottom_pad


def card_block(ctx: "DrawContext", y_top: float, accent_color: Color,
               title: str, body: str, card_bg: Color | None = None,
               extra_padding: float = 0, title_size: float = 12.5,
               body_size: float = 11) -> float:
    """Draw a card block spanning full content width. Returns y_bottom."""
    cfg = ctx.config
    c = ctx.canvas
    if card_bg is None:
        card_bg = cfg.colors.card_bg

    body_lines = wrap(body, cfg.fonts.body, body_size, cfg.content_width - 40)
    top_pad = 22 + extra_padding / 2
    title_body_gap = max(20, max(title_size + 7.5, body_size + 9))
    body_leading = max(16, body_size * 1.45)
    bottom_pad = 22 + extra_padding / 2
    card_h = top_pad + title_body_gap + max(0, len(body_lines) - 1) * body_leading + bottom_pad
    y_bottom = y_top - card_h

    rrect(c, cfg.margin, y_bottom, cfg.content_width, card_h, 6, fill=card_bg)
    # Accent left bar
    c.setFillColor(accent_color)
    c.rect(cfg.margin, y_bottom, 4, card_h, fill=1, stroke=0)
    # Title
    c.setFont(cfg.fonts.bold, title_size)
    c.setFillColor(cfg.colors.primary_dark)
    c.drawString(cfg.margin + 20, y_top - top_pad, title)
    # Body
    c.setFont(cfg.fonts.body, body_size)
    c.setFillColor(cfg.colors.text)
    by = y_top - top_pad - title_body_gap
    for line in body_lines:
        c.drawString(cfg.margin + 20, by, line)
        by -= body_leading

    return y_bottom


def measure_insight_block_height(
    ctx: "DrawContext",
    body_text: str,
    label_size: float = 10.5,
    body_size: float = 10.5,
    extra_padding: float = 0,
) -> float:
    """Measure the full height of an insight block."""
    cfg = ctx.config
    body_lines = wrap(body_text, cfg.fonts.body, body_size, cfg.content_width - 44)
    label_body_gap = max(18, max(label_size + 7.5, body_size + 7.5))
    body_leading = max(15, body_size * 1.42)
    top_pad = 20 + extra_padding / 2
    bottom_pad = 19 + extra_padding / 2
    return top_pad + label_body_gap + max(0, len(body_lines) - 1) * body_leading + bottom_pad


def insight_block(ctx: "DrawContext", y_top: float, accent_color: Color,
                  label: str, body_text: str,
                  label_color: Color | None = None, bg: Color | None = None,
                  extra_padding: float = 0, label_size: float = 10.5,
                  body_size: float = 10.5) -> float:
    """Draw an insight/callout block. Returns y_bottom."""
    cfg = ctx.config
    c = ctx.canvas
    if label_color is None:
        label_color = accent_color
    if bg is None:
        bg = HexColor("#FFFEF5")

    body_lines = wrap(body_text, cfg.fonts.body, body_size, cfg.content_width - 44)
    top_pad = 20 + extra_padding / 2
    label_body_gap = max(18, max(label_size + 7.5, body_size + 7.5))
    body_leading = max(15, body_size * 1.42)
    bottom_pad = 19 + extra_padding / 2
    block_h = top_pad + label_body_gap + max(0, len(body_lines) - 1) * body_leading + bottom_pad
    y_bottom = y_top - block_h
    rrect(c, cfg.margin, y_bottom, cfg.content_width, block_h, 6, fill=bg)
    c.setFillColor(accent_color)
    c.rect(cfg.margin, y_bottom, 4, block_h, fill=1, stroke=0)
    c.setFont(cfg.fonts.bold, label_size)
    c.setFillColor(label_color)
    c.drawString(cfg.margin + 18, y_top - top_pad, label)
    c.setFont(cfg.fonts.body, body_size)
    c.setFillColor(cfg.colors.text)
    by = y_top - top_pad - label_body_gap
    for line in body_lines:
        c.drawString(cfg.margin + 18, by, line)
        by -= body_leading
    return y_bottom


def measure_bottom_takeaway_height(
    ctx: "DrawContext",
    body_text: str,
    expand: bool = False,
) -> float:
    """Measure the anchored takeaway height.

    By default this preserves the legacy fixed-height footer used by the
    fixed-layout renderers. Content cards can opt into an expandable block.
    """
    if not expand:
        return 64
    cfg = ctx.config
    body_lines = wrap(body_text, cfg.fonts.body, 11.5, cfg.content_width - 32)
    return max(64, 40 + len(body_lines) * 14)


def bottom_takeaway(ctx: "DrawContext", accent_color: Color,
                    label: str, body_text: str, bg: Color | None = None,
                    y_bottom: float = 54, expand: bool = False) -> float:
    """Draw an anchored lower callout so the viewport ends with useful content."""
    cfg = ctx.config
    c = ctx.canvas
    if bg is None:
        bg = HexColor("#FFFEF7")

    body_lines = wrap(body_text, cfg.fonts.body, 11.5, cfg.content_width - 32)
    block_h = measure_bottom_takeaway_height(ctx, body_text, expand=expand)

    rrect(c, cfg.margin, y_bottom, cfg.content_width, block_h, 6,
          fill=bg, stroke=cfg.colors.divider, sw=0.4)
    c.setFillColor(accent_color)
    c.rect(cfg.margin, y_bottom, 4, block_h, fill=1, stroke=0)
    c.setFont(cfg.fonts.bold, 12)
    c.setFillColor(accent_color)
    top = y_bottom + block_h
    c.drawString(cfg.margin + 16, top - 22, label.upper())
    c.setFont(cfg.fonts.body, 11.5)
    c.setFillColor(cfg.colors.text)
    text_x = cfg.margin + 16
    text_y = top - 40
    for line in body_lines:
        c.drawString(text_x, text_y, line)
        text_y -= 14
    return y_bottom

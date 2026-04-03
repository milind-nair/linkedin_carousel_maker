"""Font registration with fallback chains."""

from pathlib import Path
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from carousel.config import FontSet
from carousel.schema import FontsConfig


def register_font_with_fallback(name: str, candidates: list[str], fallback: str) -> str:
    """Try each candidate path; register the first that exists, else return fallback."""
    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            try:
                pdfmetrics.registerFont(TTFont(name, str(path)))
                return name
            except Exception:
                continue
    return fallback


def register_fonts(fonts_cfg: FontsConfig) -> FontSet:
    """Register all font roles and return a FontSet with resolved names."""
    return FontSet(
        display=register_font_with_fallback(
            fonts_cfg.display.name,
            fonts_cfg.display.candidates,
            fonts_cfg.display.fallback,
        ),
        body=register_font_with_fallback(
            fonts_cfg.body.name,
            fonts_cfg.body.candidates,
            fonts_cfg.body.fallback,
        ),
        bold=register_font_with_fallback(
            fonts_cfg.bold.name,
            fonts_cfg.bold.candidates,
            fonts_cfg.bold.fallback,
        ),
        mono=register_font_with_fallback(
            fonts_cfg.mono.name,
            fonts_cfg.mono.candidates,
            fonts_cfg.mono.fallback,
        ),
    )

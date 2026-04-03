"""Orchestrator — JSON payload → validated models → rendered PDF."""

from __future__ import annotations
import json
from pathlib import Path

from reportlab.pdfgen import canvas

from carousel.schema import CarouselPayload
from carousel.config import Config, DrawContext, resolve_config
from carousel.fonts import register_fonts
from carousel.layout import decorate_page, draw_footer
from carousel.registry import render_slide

# Import renderers to populate the registry
import carousel.renderers  # noqa: F401


def render_carousel(payload_path: str, output_path: str | None = None):
    """Load a JSON payload and render it to a PDF carousel.

    Args:
        payload_path: Path to the JSON payload file.
        output_path: Optional override for the output PDF path.
                     Defaults to meta.output_filename in the payload dir.
    """
    payload_file = Path(payload_path).resolve()
    base_dir = payload_file.parent

    # Load and validate
    raw = json.loads(payload_file.read_text(encoding="utf-8"))
    payload = CarouselPayload.model_validate(raw)

    # Resolve configuration
    cfg = resolve_config(payload.global_styles)

    # Register fonts
    font_set = register_fonts(payload.global_styles.fonts)
    cfg.fonts = font_set

    # Resolve brand icon
    brand = payload.global_styles.brand
    if brand.icon_path:
        icon = Path(brand.icon_path)
        if not icon.is_absolute():
            icon = base_dir / icon
        if icon.exists():
            cfg.brand_icon_path = str(icon)
    elif brand.icon_url:
        from carousel.images import resolve_image
        try:
            cfg.brand_icon_path = str(resolve_image(brand.icon_url, str(base_dir)))
        except Exception:
            pass  # icon is optional

    # Determine output path
    if output_path is None:
        output_path = str(base_dir / payload.meta.output_filename)

    # Create canvas
    c = canvas.Canvas(output_path, pagesize=(cfg.width, cfg.height))

    ctx = DrawContext(canvas=c, config=cfg, base_dir=str(base_dir))

    # Render slides
    slides = payload.slides
    for i, slide in enumerate(slides):
        slide_dict = slide.model_dump()

        if i == 0:
            # First page: canvas already created with initial page
            # Just set page size (already set by Canvas constructor)
            pass
        else:
            c.showPage()
            c.setPageSize((cfg.width, cfg.height))

        # Apply per-slide style overrides
        slide_ctx = ctx.with_overrides(slide_dict.get("style_overrides", {}))

        # Dispatch to registered renderer
        render_slide(slide_dict, slide_ctx)

    # Save
    c.save()
    num_pages = len(slides)
    print(f"Created: {output_path}")
    print(f"Pages: {num_pages}")
    return output_path

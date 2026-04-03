"""Slide renderer registry — dispatch by slide type string."""

from __future__ import annotations
from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from carousel.config import DrawContext

REGISTRY: dict[str, Callable] = {}


def register(slide_type: str):
    """Decorator to register a slide renderer function."""
    def decorator(fn: Callable):
        REGISTRY[slide_type] = fn
        return fn
    return decorator


def render_slide(slide_data: dict, ctx: "DrawContext"):
    """Dispatch to the registered renderer for slide_data['type']."""
    slide_type = slide_data["type"]
    renderer = REGISTRY.get(slide_type)
    if renderer is None:
        raise ValueError(
            f"Unknown slide type: {slide_type!r}. "
            f"Registered types: {sorted(REGISTRY.keys())}"
        )
    renderer(slide_data, ctx)

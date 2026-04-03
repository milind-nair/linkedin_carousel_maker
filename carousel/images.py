"""Image loading, caching, scaling, and clipping."""

from __future__ import annotations
import hashlib
import os
from pathlib import Path
from typing import TYPE_CHECKING

from reportlab.lib.utils import ImageReader

if TYPE_CHECKING:
    from carousel.config import DrawContext
    from carousel.schema import ImageSpec

CACHE_DIR = Path(os.path.expanduser("~/.cache/carousel_maker/images"))


def resolve_image(source: str, base_dir: str | Path) -> Path:
    """Resolve an image source to a local file path. Downloads URLs."""
    if source.startswith(("http://", "https://")):
        return _download_and_cache(source)
    path = Path(source)
    if not path.is_absolute():
        path = Path(base_dir) / path
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {path}")
    return path


def _download_and_cache(url: str) -> Path:
    """Download a URL image and cache it locally."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    url_hash = hashlib.md5(url.encode()).hexdigest()
    ext = Path(url.split("?")[0]).suffix or ".png"
    cached = CACHE_DIR / f"{url_hash}{ext}"
    if cached.exists():
        return cached
    import requests
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    cached.write_bytes(resp.content)
    return cached


def _get_image_dimensions(path: Path) -> tuple[float, float]:
    """Get (width, height) of an image in points."""
    img = ImageReader(str(path))
    return img.getSize()


def _translate_anchor(
    x: float, y: float, w: float, h: float, anchor: str
) -> tuple[float, float]:
    """Convert anchor-based coordinates to ReportLab bottom-left origin."""
    if anchor == "top_left":
        return x, y - h
    elif anchor == "top_right":
        return x - w, y - h
    elif anchor == "center":
        return x - w / 2, y - h / 2
    elif anchor == "bottom_right":
        return x - w, y
    else:  # bottom_left (default)
        return x, y


def draw_image(ctx: "DrawContext", spec: "ImageSpec"):
    """Draw an image on the canvas according to its spec."""
    path = resolve_image(spec.source, ctx.base_dir)
    c = ctx.canvas

    img_w, img_h = _get_image_dimensions(path)

    # Determine draw dimensions
    w = spec.width if spec.width else img_w
    h = spec.height if spec.height else img_h

    # Anchor translation
    x, y = _translate_anchor(spec.x, spec.y, w, h, spec.anchor)

    c.saveState()

    if spec.opacity < 1.0:
        c.setFillAlpha(spec.opacity)

    # Apply clipping
    if spec.clip == "circle":
        p = c.beginPath()
        p.circle(x + w / 2, y + h / 2, min(w, h) / 2)
        c.clipPath(p, stroke=0)
    elif spec.clip == "rounded_rect":
        p = c.beginPath()
        p.roundRect(x, y, w, h, spec.clip_radius)
        c.clipPath(p, stroke=0)

    # Draw with fit mode
    if spec.fit_mode == "contain":
        c.drawImage(
            str(path), x, y, width=w, height=h,
            preserveAspectRatio=True, anchor='c', mask='auto',
        )
    elif spec.fit_mode == "cover":
        scale = max(w / img_w, h / img_h)
        sw, sh = img_w * scale, img_h * scale
        ox, oy = x - (sw - w) / 2, y - (sh - h) / 2
        if spec.clip == "none":
            p = c.beginPath()
            p.rect(x, y, w, h)
            c.clipPath(p, stroke=0)
        c.drawImage(str(path), ox, oy, width=sw, height=sh, mask='auto')
    elif spec.fit_mode == "stretch":
        c.drawImage(str(path), x, y, width=w, height=h, mask='auto')
    elif spec.fit_mode == "original":
        c.drawImage(str(path), x, y, mask='auto')

    c.restoreState()

"""Dark slide theme definitions and auto-cycling resolver."""

from __future__ import annotations
import hashlib
from dataclasses import dataclass


@dataclass
class DarkTheme:
    """Color overrides for title_dark and closing_dark slides."""
    bg_dark: str
    band: str
    band_stroke: str
    accent: str
    primary: str
    separator_dark: str
    icon_bg_dark: str

    def as_overrides(self) -> dict[str, str]:
        """Return dict suitable for DrawContext.with_overrides()."""
        return {
            "bg_dark": self.bg_dark,
            "band": self.band,
            "band_stroke": self.band_stroke,
            "accent": self.accent,
            "primary": self.primary,
            "separator_dark": self.separator_dark,
            "icon_bg_dark": self.icon_bg_dark,
        }


DARK_THEMES: dict[str, DarkTheme] = {
    "warm": DarkTheme(
        bg_dark="#1A1814",
        band="#211D17",
        band_stroke="#2B2721",
        accent="#F59E0B",
        primary="#D97706",
        separator_dark="#333330",
        icon_bg_dark="#2A2720",
    ),
    "cool": DarkTheme(
        bg_dark="#131820",
        band="#171D28",
        band_stroke="#232A38",
        accent="#60A5FA",
        primary="#2563EB",
        separator_dark="#2A3040",
        icon_bg_dark="#1E2536",
    ),
    "verdant": DarkTheme(
        bg_dark="#121A16",
        band="#162019",
        band_stroke="#1E2E24",
        accent="#34D399",
        primary="#059669",
        separator_dark="#253530",
        icon_bg_dark="#1A2E22",
    ),
}

THEME_ORDER = ["warm", "cool", "verdant"]


def resolve_dark_theme(theme_name: str | None, output_filename: str) -> DarkTheme:
    """Pick a dark theme by explicit name or auto-cycle from filename hash."""
    if theme_name and theme_name in DARK_THEMES:
        return DARK_THEMES[theme_name]
    # Deterministic hash so the same filename always gets the same theme
    idx = int(hashlib.md5(output_filename.encode()).hexdigest(), 16) % len(THEME_ORDER)
    return DARK_THEMES[THEME_ORDER[idx]]

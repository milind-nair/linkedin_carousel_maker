"""Configuration resolution — converts JSON styles into resolved drawing context."""

from __future__ import annotations
from dataclasses import dataclass, field
from reportlab.lib.colors import HexColor, Color

from carousel.schema import GlobalStyles, ColorsConfig


@dataclass
class ColorPalette:
    """Resolved HexColor objects for all palette entries."""
    bg: Color = field(default_factory=lambda: HexColor("#FFFDF5"))
    bg_dark: Color = field(default_factory=lambda: HexColor("#1A1814"))
    primary: Color = field(default_factory=lambda: HexColor("#D97706"))
    primary_dark: Color = field(default_factory=lambda: HexColor("#92400E"))
    primary_light: Color = field(default_factory=lambda: HexColor("#FEF3C7"))
    accent: Color = field(default_factory=lambda: HexColor("#F59E0B"))
    text: Color = field(default_factory=lambda: HexColor("#292524"))
    text_light: Color = field(default_factory=lambda: HexColor("#F5F5F4"))
    muted: Color = field(default_factory=lambda: HexColor("#A8A29E"))
    stone: Color = field(default_factory=lambda: HexColor("#78716C"))
    card_bg: Color = field(default_factory=lambda: HexColor("#FFFFFF"))
    divider: Color = field(default_factory=lambda: HexColor("#E7E5E4"))
    # Dark-slide theme colors (defaults = warm theme)
    band: Color = field(default_factory=lambda: HexColor("#211D17"))
    band_stroke: Color = field(default_factory=lambda: HexColor("#2B2721"))
    separator_dark: Color = field(default_factory=lambda: HexColor("#333330"))
    icon_bg_dark: Color = field(default_factory=lambda: HexColor("#2A2720"))
    green: Color = field(default_factory=lambda: HexColor("#059669"))
    green_bg: Color = field(default_factory=lambda: HexColor("#ECFDF5"))
    purple: Color = field(default_factory=lambda: HexColor("#7C3AED"))
    purple_bg: Color = field(default_factory=lambda: HexColor("#F5F3FF"))
    blue: Color = field(default_factory=lambda: HexColor("#2563EB"))
    red: Color = field(default_factory=lambda: HexColor("#DC2626"))
    red_bg: Color = field(default_factory=lambda: HexColor("#FEF2F2"))

    def resolve(self, name_or_hex: str) -> Color:
        """Look up by palette name or parse as hex. Returns HexColor."""
        if hasattr(self, name_or_hex):
            return getattr(self, name_or_hex)
        return HexColor(name_or_hex)


@dataclass
class FontSet:
    """Resolved font names (after registration with fallback)."""
    display: str = "Helvetica-Bold"
    body: str = "Helvetica"
    bold: str = "Helvetica-Bold"
    mono: str = "Courier"


@dataclass
class Config:
    """Fully resolved configuration for rendering."""
    width: float = 612
    height: float = 765
    margin: float = 48
    viewport_band_height: float = 108
    content_width: float = 516  # width - 2 * margin
    colors: ColorPalette = field(default_factory=ColorPalette)
    fonts: FontSet = field(default_factory=FontSet)
    brand_name: str = "MILIND NAIR"
    brand_icon_path: str | None = None
    show_footer: bool = True


@dataclass
class DrawContext:
    """Bundle passed to all drawing functions."""
    canvas: object  # reportlab.pdfgen.canvas.Canvas
    config: Config
    base_dir: str = "."
    output_filename: str = "carousel.pdf"

    def with_overrides(self, overrides: dict[str, str]) -> "DrawContext":
        """Return a new DrawContext with per-slide color overrides applied."""
        if not overrides:
            return self
        new_palette = ColorPalette(
            **{k: getattr(self.config.colors, k) for k in vars(self.config.colors)}
        )
        for key, val in overrides.items():
            if hasattr(new_palette, key):
                setattr(new_palette, key, HexColor(val))
        new_config = Config(
            width=self.config.width,
            height=self.config.height,
            margin=self.config.margin,
            viewport_band_height=self.config.viewport_band_height,
            content_width=self.config.content_width,
            colors=new_palette,
            fonts=self.config.fonts,
            brand_name=self.config.brand_name,
            brand_icon_path=self.config.brand_icon_path,
            show_footer=self.config.show_footer,
        )
        return DrawContext(canvas=self.canvas, config=new_config, base_dir=self.base_dir,
                          output_filename=self.output_filename)


def resolve_colors(colors_cfg: ColorsConfig) -> ColorPalette:
    """Convert ColorsConfig hex strings to a ColorPalette of HexColor objects."""
    palette = ColorPalette()
    for attr in vars(colors_cfg):
        val = getattr(colors_cfg, attr)
        if isinstance(val, str) and val.startswith("#"):
            setattr(palette, attr, HexColor(val))
    return palette


def resolve_config(styles: GlobalStyles, brand_icon_resolved: str | None = None) -> Config:
    """Build a fully resolved Config from the parsed GlobalStyles."""
    dims = styles.dimensions
    return Config(
        width=dims.width,
        height=dims.height,
        margin=dims.margin,
        viewport_band_height=dims.viewport_band_height,
        content_width=dims.width - 2 * dims.margin,
        colors=resolve_colors(styles.colors),
        fonts=FontSet(),  # populated later by fonts.register_fonts()
        brand_name=styles.brand.name,
        brand_icon_path=brand_icon_resolved,
        show_footer=styles.brand.show_footer,
    )

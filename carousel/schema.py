"""Pydantic v2 models for carousel JSON payload validation."""

from __future__ import annotations
from typing import Annotated, Literal, Optional
from pydantic import BaseModel, Field, model_validator


# ── Reusable sub-models ──

class ImageSpec(BaseModel):
    source: str
    x: float = 0
    y: float = 0
    width: Optional[float] = None
    height: Optional[float] = None
    fit_mode: Literal["contain", "cover", "stretch", "original"] = "contain"
    clip: Literal["none", "circle", "rounded_rect"] = "none"
    clip_radius: float = 6
    opacity: float = 1.0
    anchor: Literal[
        "top_left", "top_right", "center", "bottom_left", "bottom_right"
    ] = "bottom_left"


class IllustrationSpec(BaseModel):
    """Visual illustration: either a named vector glyph or an image file."""
    glyph: Optional[str] = None          # e.g. "terminal", "gear", "lock"
    source: Optional[str] = None         # image path or URL
    size: float = 56                     # width in points
    position: Literal["top_right", "top_left", "custom"] = "top_right"
    x: Optional[float] = None            # used when position="custom"
    y: Optional[float] = None
    color: Optional[str] = None          # glyph stroke/fill; ignored for images
    opacity: float = 1.0
    fit_mode: Literal["contain", "cover", "stretch", "original"] = "contain"
    clip: Literal["none", "circle", "rounded_rect"] = "none"
    clip_radius: float = 6

    @model_validator(mode="after")
    def _exactly_one_source(self) -> "IllustrationSpec":
        if bool(self.glyph) == bool(self.source):
            raise ValueError(
                "IllustrationSpec requires exactly one of 'glyph' or 'source'"
            )
        return self


class GeometricAccent(BaseModel):
    color: Optional[str] = None
    alpha: float = 0.07
    x_pct: float = 0.55
    y_pct: float = 0.72
    w_pct: float = 0.6
    h: float = 80


class PillSpec(BaseModel):
    text: str
    bg: str = "#FEF3C7"
    fg: str = "#92400E"


class CardSpec(BaseModel):
    title: str
    body: str
    accent_color: str = "#D97706"
    card_bg: Optional[str] = None


class InsightSpec(BaseModel):
    label: str
    body: str
    accent_color: str = "#F59E0B"
    bg: Optional[str] = None
    label_color: Optional[str] = None


class InlineTextSpec(BaseModel):
    prefix: str
    prefix_color: Optional[str] = None
    text: str
    text_color: Optional[str] = None


class BottomTakeawaySpec(BaseModel):
    label: str
    body: str
    accent_color: str = "#D97706"
    bg: Optional[str] = None


class GridItemSpec(BaseModel):
    label: str
    trigger: Optional[str] = None
    description: str = ""
    color: str = "#D97706"


class TableColumnSpec(BaseModel):
    header: str
    width: float


class TableRowSpec(BaseModel):
    label: str
    color: str
    cells: list[str]


class FlowStepSpec(BaseModel):
    label: str
    description: str
    color: str = "#D97706"


class DecisionSpec(BaseModel):
    question: str
    answer: str
    color: str = "#D97706"


# ── Slide type models ──

class BaseSlide(BaseModel):
    style_overrides: dict[str, str] = Field(default_factory=dict)
    show_footer: bool = True
    show_viewport_band: bool = True


class TitleDarkSlide(BaseSlide):
    type: Literal["title_dark"] = "title_dark"
    kicker: Optional[str] = None
    title_lines: list[str] = Field(default_factory=list)
    subtitle_lines: list[str] = Field(default_factory=list)
    cta_text: Optional[str] = None
    geometric_accent: Optional[GeometricAccent] = None
    image: Optional[ImageSpec] = None


class ContentCardsSlide(BaseSlide):
    type: Literal["content_cards"] = "content_cards"
    pill: Optional[PillSpec] = None
    heading: str = ""
    date_line: Optional[str] = None
    subheading: Optional[str] = None
    cards: list[CardSpec] = Field(default_factory=list)
    insight: Optional[InsightSpec] = None
    inline_text: Optional[InlineTextSpec] = None
    bottom_takeaway: Optional[BottomTakeawaySpec] = None
    illustration: Optional[IllustrationSpec] = None


class GridCardsSlide(BaseSlide):
    type: Literal["grid_cards"] = "grid_cards"
    heading: str = ""
    subheading: Optional[str] = None
    columns: int = 2
    items: list[GridItemSpec] = Field(default_factory=list)
    bottom_takeaway: Optional[BottomTakeawaySpec] = None
    illustration: Optional[IllustrationSpec] = None


class ComparisonTableSlide(BaseSlide):
    type: Literal["comparison_table"] = "comparison_table"
    heading: str = ""
    subheading: Optional[str] = None
    columns: list[TableColumnSpec] = Field(default_factory=list)
    rows: list[TableRowSpec] = Field(default_factory=list)
    bottom_takeaway: Optional[BottomTakeawaySpec] = None
    illustration: Optional[IllustrationSpec] = None


class FlowDiagramSlide(BaseSlide):
    type: Literal["flow_diagram"] = "flow_diagram"
    heading: str = ""
    subheading: Optional[str] = None
    steps: list[FlowStepSpec] = Field(default_factory=list)
    connector: str = "arrow_down"
    illustration: Optional[IllustrationSpec] = None


class DecisionFrameworkSlide(BaseSlide):
    type: Literal["decision_framework"] = "decision_framework"
    heading: str = ""
    subheading: Optional[str] = None
    decisions: list[DecisionSpec] = Field(default_factory=list)
    bottom_takeaway: Optional[BottomTakeawaySpec] = None
    illustration: Optional[IllustrationSpec] = None


class ClosingDarkSlide(BaseSlide):
    type: Literal["closing_dark"] = "closing_dark"
    quote_lines: list[str] = Field(default_factory=list)
    summary_lines: list[str] = Field(default_factory=list)
    geometric_accent: Optional[GeometricAccent] = None
    image: Optional[ImageSpec] = None


# Discriminated union
Slide = Annotated[
    TitleDarkSlide
    | ContentCardsSlide
    | GridCardsSlide
    | ComparisonTableSlide
    | FlowDiagramSlide
    | DecisionFrameworkSlide
    | ClosingDarkSlide,
    Field(discriminator="type"),
]


# ── Global styles ──

class DimensionsConfig(BaseModel):
    width: float = 612
    height: float = 765
    margin: float = 48
    viewport_band_height: float = 108


class FontEntry(BaseModel):
    name: str
    candidates: list[str] = Field(default_factory=list)
    fallback: str = "Helvetica"


class FontsConfig(BaseModel):
    display: FontEntry = FontEntry(
        name="Lora",
        candidates=[
            "/usr/share/fonts/truetype/google-fonts/Lora-Variable.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ],
        fallback="Helvetica-Bold",
    )
    body: FontEntry = FontEntry(
        name="Poppins",
        candidates=[
            "/usr/share/fonts/truetype/google-fonts/Poppins-Light.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ],
        fallback="Helvetica",
    )
    bold: FontEntry = FontEntry(
        name="PoppinsBold",
        candidates=[
            "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ],
        fallback="Helvetica-Bold",
    )
    mono: FontEntry = FontEntry(
        name="LiberationMono",
        candidates=[
            "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        ],
        fallback="Courier",
    )


class ColorsConfig(BaseModel):
    bg: str = "#FFFDF5"
    bg_dark: str = "#1A1814"
    primary: str = "#D97706"
    primary_dark: str = "#92400E"
    primary_light: str = "#FEF3C7"
    accent: str = "#F59E0B"
    text: str = "#292524"
    text_light: str = "#F5F5F4"
    muted: str = "#A8A29E"
    stone: str = "#78716C"
    card_bg: str = "#FFFFFF"
    divider: str = "#E7E5E4"
    # Semantic colors
    green: str = "#059669"
    green_bg: str = "#ECFDF5"
    purple: str = "#7C3AED"
    purple_bg: str = "#F5F3FF"
    blue: str = "#2563EB"
    red: str = "#DC2626"
    red_bg: str = "#FEF2F2"


class BrandConfig(BaseModel):
    name: str = "MILIND NAIR"
    icon_path: Optional[str] = None
    icon_url: Optional[str] = None
    show_footer: bool = True


class GlobalStyles(BaseModel):
    dimensions: DimensionsConfig = Field(default_factory=DimensionsConfig)
    colors: ColorsConfig = Field(default_factory=ColorsConfig)
    fonts: FontsConfig = Field(default_factory=FontsConfig)
    brand: BrandConfig = Field(default_factory=BrandConfig)


# ── Top-level payload ──

class Meta(BaseModel):
    title: str = ""
    author: Optional[str] = None
    output_filename: str = "carousel.pdf"
    description: Optional[str] = None


class CarouselPayload(BaseModel):
    meta: Meta = Field(default_factory=Meta)
    global_styles: GlobalStyles = Field(default_factory=GlobalStyles)
    slides: list[Slide] = Field(default_factory=list)

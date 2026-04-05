# LinkedIn Carousel Maker

JSON-driven PDF rendering engine for LinkedIn carousels. Content lives in JSON payloads; the rendering engine is a stable Python package.

## How to run

```bash
source venv/bin/activate
python render.py <payload.json> [output.pdf]
```

Dependencies: `reportlab`, `pydantic>=2.0`, `requests`. Already in `requirements.txt`.

## Architecture

The `carousel/` package separates **content** (JSON) from **rendering** (ReportLab). Future sessions should produce only JSON payloads — never modify the rendering engine unless adding new features.

```
render.py              CLI entry point
carousel/
  pipeline.py          Orchestrator: load JSON → validate → render loop → save
  schema.py            Pydantic models — the JSON contract (all slide types defined here)
  config.py            Config/DrawContext dataclasses, color resolution
  fonts.py             Font registration with fallback chains
  primitives.py        Drawing helpers: wrap, draw_text, rrect, pill, card_block, insight_block, bottom_takeaway
  layout.py            Page-level: new_page, decorate_page, draw_footer
  images.py            Image loading (local + URL), fit modes, clipping
  illustrations.py     Vector glyph registry + unified draw_illustration() helper
  registry.py          @register("type") decorator + dispatch
  renderers/
    __init__.py        Auto-imports all renderer modules
    title_dark.py      Dark title slide (slide 1)
    content_cards.py   Cards with pill/heading/insight/takeaway (slides 3-8)
    grid_cards.py      2-column grid of small cards (slide 2)
    comparison_table.py Table with colored rows (slide 9)
    flow_diagram.py    Vertical flow with arrow connectors (slide 10)
    decision_framework.py Numbered Q&A with circles (slide 11)
    closing_dark.py    Dark closing slide with quote (slide 12)
```

## Where to change things

### Adding a new slide type
1. `carousel/schema.py` — Add a new Pydantic model (e.g. `TimelineSlide`) and add it to the `Slide` union at the bottom of the file
2. `carousel/renderers/<new_type>.py` — Create renderer with `@register("new_type")` decorator
3. `carousel/renderers/__init__.py` — Add `from . import <new_type>`

### Changing colors or brand defaults
- **Global defaults** live in `carousel/schema.py` in the `ColorsConfig`, `BrandConfig`, and `DimensionsConfig` classes
- **Per-payload overrides**: set values in the JSON payload under `global_styles.colors`, `global_styles.brand`, etc.
- **Per-slide overrides**: use the `style_overrides` dict on any slide in the JSON payload
- **Color resolution** happens in `carousel/config.py` — the `ColorPalette.resolve()` method accepts both palette names (`"primary"`) and hex strings (`"#D97706"`)

### Changing fonts
- **Font candidates/fallbacks**: `carousel/schema.py` → `FontsConfig` class has the default paths and fallbacks
- **Font registration logic**: `carousel/fonts.py` — tries each candidate path, falls back to built-in ReportLab font
- Font paths are Linux-specific (`/usr/share/fonts/truetype/`). macOS/Windows will use fallbacks (Helvetica, Courier)

### Changing page dimensions or margins
- Default dimensions: `carousel/schema.py` → `DimensionsConfig` (W=612, H=765, margin=48)
- Override per-payload in JSON under `global_styles.dimensions`

### Changing card/block visual style
- `carousel/primitives.py` — all reusable drawing components:
  - `card_block()` — the standard card with left accent bar
  - `insight_block()` — callout block with colored label
  - `bottom_takeaway()` — anchored at Y=54, always near page bottom
  - `pill()` — colored badge/tag
  - `rrect()` — rounded rectangle primitive
  - `draw_text()` — text with word wrap and alignment

### Changing page chrome (footer, viewport band, decorations)
- `carousel/layout.py` — `decorate_page()` draws the subtle lower band, `draw_footer()` draws brand name + icon

### Adding image support to a slide type
- Use `carousel/images.py` → `draw_image(ctx, ImageSpec(...))` in any renderer
- `ImageSpec` supports: `fit_mode` (contain/cover/stretch/original), `clip` (none/circle/rounded_rect), `anchor`, `opacity`

### Adding illustrations (vector glyphs or images) to a slide type
- `content_cards`, `grid_cards`, `comparison_table`, `flow_diagram`, and `decision_framework` all accept an optional `illustration: IllustrationSpec` field
- `IllustrationSpec` requires exactly one of `glyph` (named vector glyph) or `source` (image path/URL)
- Built-in glyphs in `carousel/illustrations.py`: `terminal`, `code_brackets`, `gear`, `split_path`, `lock`, `flow_arrow`, `chip`, `wrench`, `scale`, `layers`
- To add a new glyph: write a function `(canvas, x, y, size, color)` in `illustrations.py` and register it in the `GLYPHS` dict
- Positioning: `position` is `top_right` (default), `top_left`, or `custom` (pairs with `x`/`y`)
- Renderer usage: `from carousel.illustrations import draw_illustration; draw_illustration(ctx, slide.get("illustration"), cfg.colors.primary)`

JSON example:
```json
"illustration": { "glyph": "terminal", "size": 54, "color": "#D97706" }
```
or
```json
"illustration": { "source": "assets/logo.png", "size": 64, "position": "top_right" }
```

## JSON payload structure

See `example_payload.json` for the full 12-slide reference. Minimal payload:

```json
{
  "meta": { "output_filename": "my-carousel.pdf" },
  "slides": [
    {
      "type": "title_dark",
      "kicker": "TOPIC",
      "title_lines": ["Line One", "Line Two"],
      "subtitle_lines": ["A short description."],
      "cta_text": "Swipe →"
    },
    {
      "type": "content_cards",
      "pill": { "text": "SECTION", "bg": "#FEF3C7", "fg": "#92400E" },
      "heading": "Section Title",
      "cards": [
        { "title": "Card Title", "body": "Card body text.", "accent_color": "#D97706" }
      ],
      "bottom_takeaway": { "label": "Takeaway", "body": "Key point.", "accent_color": "#D97706" }
    },
    {
      "type": "closing_dark",
      "quote_lines": ["Final", "message."],
      "summary_lines": ["Bullet one.", "Bullet two."]
    }
  ]
}
```

All `global_styles` fields are optional — brand defaults are baked into the schema.

## Slide types reference

| Type | JSON `type` value | Key fields |
|------|-------------------|------------|
| Title (dark bg) | `title_dark` | `kicker`, `title_lines`, `subtitle_lines`, `cta_text`, `geometric_accent`, `image` |
| Content cards | `content_cards` | `pill`, `heading`, `subheading`, `cards[]`, `insight`, `inline_text`, `bottom_takeaway`, `illustration` |
| Grid cards | `grid_cards` | `heading`, `subheading`, `columns`, `items[]`, `bottom_takeaway`, `illustration` |
| Comparison table | `comparison_table` | `heading`, `columns[]`, `rows[]`, `bottom_takeaway`, `illustration` |
| Flow diagram | `flow_diagram` | `heading`, `subheading`, `steps[]`, `illustration` |
| Decision framework | `decision_framework` | `heading`, `decisions[]`, `bottom_takeaway`, `illustration` |
| Closing (dark bg) | `closing_dark` | `quote_lines`, `summary_lines`, `geometric_accent`, `image` |

## Original reference

`create_v2.py` is the original monolithic script. It is preserved for visual reference but is not used by the engine.

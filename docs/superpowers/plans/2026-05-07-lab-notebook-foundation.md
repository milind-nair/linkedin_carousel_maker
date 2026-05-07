# Lab Notebook Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Land Phase 1 of the lab notebook redesign — fonts, color palette, page chassis (cream paper + dot grid + masthead + signature footer), and the `carousel/sketch.py` hand-drawn primitives module — and end at the visual tuning gate where we eyeball whether the sketch primitives feel hand-drawn enough to commit to.

**Architecture:** Add new fields/functions alongside the existing engine without removing any. Old renderers (`title_dark`, `content_cards`, etc.) keep working unchanged. New chassis lives in `layout.py` next to the old chassis. New `carousel/sketch.py` module provides hand-drawn arrows, circles, checks, crosses, underlines, and brackets — all deterministic given a seed, all rendered in red ink. Validation is two-tier: pytest tests for determinism/bounds/structure on `sketch.py`, plus a manual visual smoke test that renders a single-PDF chassis-and-primitives page.

**Tech Stack:** Python 3, ReportLab 4.x, Pydantic 2.x, pytest (newly added). Fonts: IBM Plex Serif, IBM Plex Mono, Source Serif Pro, Caveat — all OFL/SIL licensed.

**Spec:** [`docs/superpowers/specs/2026-05-07-lab-notebook-redesign-design.md`](../specs/2026-05-07-lab-notebook-redesign-design.md)

---

## File Structure

**Created:**
- `tests/__init__.py` — make tests a package
- `tests/test_palette.py` — palette resolution tests
- `tests/test_dimensions.py` — dimension config tests
- `tests/test_fonts_config.py` — font registration tests
- `tests/test_sketch.py` — sketch primitive tests (the bulk)
- `tests/test_layout_chassis.py` — chassis function tests
- `tests/payloads/chassis_test.json` — visual smoke test payload
- `scripts/download_fonts.sh` — one-time font fetcher
- `assets/fonts/` — committed `.ttf` files
- `carousel/sketch.py` — hand-drawn primitives module (the moat)
- `carousel/renderers/_chassis_test.py` — temporary visual smoke test renderer (kept as debug tool)

**Modified:**
- `requirements.txt` — add pytest
- `carousel/schema.py` — extend `ColorsConfig`, `FontsConfig`, `DimensionsConfig`; add `_ChassisTestSlide` to the `Slide` union
- `carousel/config.py` — extend `ColorPalette`, `FontSet`, `Config`; update `resolve_config`
- `carousel/fonts.py` — extend `register_fonts` to register new font roles
- `carousel/layout.py` — add `draw_dot_grid`, `draw_masthead`, `draw_signature_footer`, `new_lab_page` (old functions untouched)
- `carousel/renderers/__init__.py` — import `_chassis_test`
- `.gitignore` — keep as-is (assets/fonts is intentionally committed)

**Out of scope for this plan:** any new public renderer (`cover`, `lab_notes`, `colophon`, etc.) — those land in Plan 2.

---

## Task 1: Set up pytest infrastructure

**Files:**
- Modify: `requirements.txt`
- Create: `tests/__init__.py`
- Create: `tests/payloads/.gitkeep`
- Create: `tests/test_smoke.py`

- [ ] **Step 1: Add pytest to requirements**

Edit `requirements.txt`. Final contents:

```
reportlab>=4.0
pydantic>=2.0
requests>=2.28
pytest>=8.0
```

- [ ] **Step 2: Install pytest**

Run:
```bash
source venv/bin/activate && pip install pytest>=8.0
```
Expected: pytest installed in venv.

- [ ] **Step 3: Create tests package**

Create empty file `tests/__init__.py`. Create empty file `tests/payloads/.gitkeep`.

- [ ] **Step 4: Write smoke test**

Create `tests/test_smoke.py`:
```python
def test_pytest_runs():
    assert 1 + 1 == 2
```

- [ ] **Step 5: Run pytest, verify pass**

Run:
```bash
source venv/bin/activate && pytest tests/ -v
```
Expected: `1 passed`.

- [ ] **Step 6: Commit**

```bash
git add requirements.txt tests/
git commit -m "test: add pytest infrastructure"
```

---

## Task 2: Download fonts

**Files:**
- Create: `scripts/download_fonts.sh`
- Create: `assets/fonts/IBMPlexSerif-Regular.ttf`
- Create: `assets/fonts/IBMPlexSerif-Bold.ttf`
- Create: `assets/fonts/IBMPlexMono-Regular.ttf`
- Create: `assets/fonts/SourceSerif4-Regular.ttf`
- Create: `assets/fonts/Caveat-Regular.ttf`

- [ ] **Step 1: Write the download script**

Create `scripts/download_fonts.sh`:
```bash
#!/usr/bin/env bash
set -euo pipefail

FONTS_DIR="$(dirname "$0")/../assets/fonts"
mkdir -p "$FONTS_DIR"

declare -a URLS=(
  "https://github.com/IBM/plex/raw/master/IBM-Plex-Serif/fonts/complete/ttf/IBMPlexSerif-Regular.ttf"
  "https://github.com/IBM/plex/raw/master/IBM-Plex-Serif/fonts/complete/ttf/IBMPlexSerif-Bold.ttf"
  "https://github.com/IBM/plex/raw/master/IBM-Plex-Mono/fonts/complete/ttf/IBMPlexMono-Regular.ttf"
  "https://github.com/adobe-fonts/source-serif/raw/release/TTF/SourceSerif4-Regular.ttf"
  "https://github.com/googlefonts/caveat/raw/main/fonts/ttf/Caveat-Regular.ttf"
)

for url in "${URLS[@]}"; do
  filename="$(basename "$url")"
  out="$FONTS_DIR/$filename"
  if [[ -f "$out" ]]; then
    echo "exists: $filename"
    continue
  fi
  echo "downloading: $filename"
  curl -fsSL "$url" -o "$out"
done

echo "done. fonts in $FONTS_DIR"
ls -la "$FONTS_DIR"
```

Make it executable: `chmod +x scripts/download_fonts.sh`.

- [ ] **Step 2: Run the script**

Run:
```bash
bash scripts/download_fonts.sh
```

Expected: 5 `.ttf` files appear in `assets/fonts/`. If a URL has changed (Google Fonts/GitHub repos do shift paths occasionally), look up the current direct URL on the project's GitHub and update the script. The license names to confirm: IBM Plex (OFL), Source Serif (OFL), Caveat (OFL).

- [ ] **Step 3: Verify font files load**

Run:
```bash
source venv/bin/activate && python -c "
from reportlab.pdfbase.ttfonts import TTFont
for f in ['IBMPlexSerif-Regular', 'IBMPlexSerif-Bold', 'IBMPlexMono-Regular', 'SourceSerif4-Regular', 'Caveat-Regular']:
    TTFont(f, f'assets/fonts/{f}.ttf')
    print('ok:', f)
"
```
Expected: 5 `ok:` lines.

- [ ] **Step 4: Commit**

```bash
git add scripts/download_fonts.sh assets/fonts/
git commit -m "feat: add lab-notebook font assets (IBM Plex, Source Serif, Caveat)"
```

---

## Task 3: Add new color palette fields

**Files:**
- Modify: `carousel/schema.py:270-296` (`ColorsConfig`)
- Modify: `carousel/config.py:10-36` (`ColorPalette`)
- Test: `tests/test_palette.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_palette.py`:
```python
from carousel.schema import GlobalStyles
from carousel.config import resolve_config
from reportlab.lib.colors import HexColor


def test_lab_palette_defaults_resolve():
    cfg = resolve_config(GlobalStyles())
    assert cfg.colors.paper == HexColor("#FAF7F0")
    assert cfg.colors.ink == HexColor("#2A2A2A")
    assert cfg.colors.red_pen == HexColor("#B22222")
    assert cfg.colors.diagram_blue == HexColor("#3E5C76")


def test_lab_palette_resolves_by_name():
    cfg = resolve_config(GlobalStyles())
    assert cfg.colors.resolve("red_pen") == HexColor("#B22222")
    assert cfg.colors.resolve("#123456") == HexColor("#123456")
```

- [ ] **Step 2: Run test, verify it fails**

Run: `pytest tests/test_palette.py -v`. Expected: FAIL with `AttributeError: 'ColorPalette' object has no attribute 'paper'` (or similar).

- [ ] **Step 3: Add new fields to schema `ColorsConfig`**

In `carousel/schema.py`, inside `ColorsConfig` (line ~270), add the four new fields just after the existing `red_bg` line (keep all existing fields untouched):

```python
    # Lab notebook palette
    paper: str = "#FAF7F0"
    ink: str = "#2A2A2A"
    red_pen: str = "#B22222"
    diagram_blue: str = "#3E5C76"
```

- [ ] **Step 4: Add new fields to `ColorPalette`**

In `carousel/config.py`, inside `ColorPalette` (line ~10), add the four new fields just after the existing `red_bg` line:

```python
    # Lab notebook palette
    paper: Color = field(default_factory=lambda: HexColor("#FAF7F0"))
    ink: Color = field(default_factory=lambda: HexColor("#2A2A2A"))
    red_pen: Color = field(default_factory=lambda: HexColor("#B22222"))
    diagram_blue: Color = field(default_factory=lambda: HexColor("#3E5C76"))
```

(`resolve_colors` already iterates over `ColorsConfig` fields and copies hex strings into the palette via `setattr`, so no change there.)

- [ ] **Step 5: Run test, verify pass**

Run: `pytest tests/test_palette.py -v`. Expected: 2 passed.

- [ ] **Step 6: Verify old engine still works**

Run: `python render.py example_payload.json /tmp/regression.pdf`. Expected: PDF created without errors. (Old fields are untouched.)

- [ ] **Step 7: Commit**

```bash
git add carousel/schema.py carousel/config.py tests/test_palette.py
git commit -m "feat: add lab notebook color palette (paper/ink/red_pen/diagram_blue)"
```

---

## Task 4: Add new dimension fields

**Files:**
- Modify: `carousel/schema.py:221-225` (`DimensionsConfig`)
- Modify: `carousel/config.py:54-66` (`Config`)
- Modify: `carousel/config.py:113-127` (`resolve_config`)
- Test: `tests/test_dimensions.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_dimensions.py`:
```python
from carousel.schema import GlobalStyles
from carousel.config import resolve_config


def test_lab_dimensions_default():
    cfg = resolve_config(GlobalStyles())
    assert cfg.body_column_width == 432
    assert cfg.left_gutter == 60
    assert cfg.right_gutter == 120
    # Sum equals page width
    assert cfg.left_gutter + cfg.body_column_width + cfg.right_gutter == cfg.width
```

- [ ] **Step 2: Run test, verify fail**

Run: `pytest tests/test_dimensions.py -v`. Expected: FAIL.

- [ ] **Step 3: Extend `DimensionsConfig`**

In `carousel/schema.py`, inside `DimensionsConfig`, add three fields:
```python
class DimensionsConfig(BaseModel):
    width: float = 612
    height: float = 765
    margin: float = 48
    viewport_band_height: float = 108
    # Lab notebook layout
    body_column_width: float = 432
    left_gutter: float = 60
    right_gutter: float = 120
```

- [ ] **Step 4: Extend `Config`**

In `carousel/config.py`, inside `Config`, add three fields after `viewport_band_height`:
```python
@dataclass
class Config:
    """Fully resolved configuration for rendering."""
    width: float = 612
    height: float = 765
    margin: float = 48
    viewport_band_height: float = 108
    content_width: float = 516  # width - 2 * margin
    # Lab notebook layout
    body_column_width: float = 432
    left_gutter: float = 60
    right_gutter: float = 120
    colors: ColorPalette = field(default_factory=ColorPalette)
    fonts: FontSet = field(default_factory=FontSet)
    brand_name: str = "MILIND NAIR"
    brand_icon_path: str | None = None
    show_footer: bool = True
```

- [ ] **Step 5: Update `resolve_config`**

In `carousel/config.py`, update `resolve_config` to populate the new fields:
```python
def resolve_config(styles: GlobalStyles, brand_icon_resolved: str | None = None) -> Config:
    """Build a fully resolved Config from the parsed GlobalStyles."""
    dims = styles.dimensions
    return Config(
        width=dims.width,
        height=dims.height,
        margin=dims.margin,
        viewport_band_height=dims.viewport_band_height,
        content_width=dims.width - 2 * dims.margin,
        body_column_width=dims.body_column_width,
        left_gutter=dims.left_gutter,
        right_gutter=dims.right_gutter,
        colors=resolve_colors(styles.colors),
        fonts=FontSet(),
        brand_name=styles.brand.name,
        brand_icon_path=brand_icon_resolved,
        show_footer=styles.brand.show_footer,
    )
```

Also update `with_overrides` in the same file (lines ~77-100) — the new `Config(...)` call must include `body_column_width`, `left_gutter`, `right_gutter` propagated from `self.config`:
```python
        new_config = Config(
            width=self.config.width,
            height=self.config.height,
            margin=self.config.margin,
            viewport_band_height=self.config.viewport_band_height,
            content_width=self.config.content_width,
            body_column_width=self.config.body_column_width,
            left_gutter=self.config.left_gutter,
            right_gutter=self.config.right_gutter,
            colors=new_palette,
            fonts=self.config.fonts,
            brand_name=self.config.brand_name,
            brand_icon_path=self.config.brand_icon_path,
            show_footer=self.config.show_footer,
        )
```

- [ ] **Step 6: Run test, verify pass**

Run: `pytest tests/test_dimensions.py -v`. Expected: 1 passed.

- [ ] **Step 7: Regression — old engine still works**

Run: `python render.py example_payload.json /tmp/regression.pdf`. Expected: PDF created.

- [ ] **Step 8: Commit**

```bash
git add carousel/schema.py carousel/config.py tests/test_dimensions.py
git commit -m "feat: add lab notebook dimensions (body_column_width/left_gutter/right_gutter)"
```

---

## Task 5: Add new font roles

**Files:**
- Modify: `carousel/schema.py:234-267` (`FontsConfig`)
- Modify: `carousel/config.py:45-51` (`FontSet`)
- Modify: `carousel/fonts.py:24-47` (`register_fonts`)
- Test: `tests/test_fonts_config.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_fonts_config.py`:
```python
from carousel.schema import FontsConfig
from carousel.fonts import register_fonts


def test_lab_font_roles_register():
    font_set = register_fonts(FontsConfig())
    # New roles populated (either with the registered font name or fallback)
    assert font_set.headline_serif
    assert font_set.body_serif
    assert font_set.handwriting
    # Old roles still work
    assert font_set.display
    assert font_set.body
    assert font_set.bold
    assert font_set.mono
```

- [ ] **Step 2: Run test, verify fail**

Run: `pytest tests/test_fonts_config.py -v`. Expected: FAIL with `AttributeError`.

- [ ] **Step 3: Add new `FontEntry` instances to `FontsConfig`**

In `carousel/schema.py`, inside `FontsConfig`, add three new entries after `mono` (keep existing fields untouched):
```python
    headline_serif: FontEntry = FontEntry(
        name="IBMPlexSerifBold",
        candidates=[
            "assets/fonts/IBMPlexSerif-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
        ],
        fallback="Times-Bold",
    )
    body_serif: FontEntry = FontEntry(
        name="SourceSerif",
        candidates=[
            "assets/fonts/SourceSerif4-Regular.ttf",
            "assets/fonts/IBMPlexSerif-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
        ],
        fallback="Times-Roman",
    )
    handwriting: FontEntry = FontEntry(
        name="Caveat",
        candidates=[
            "assets/fonts/Caveat-Regular.ttf",
        ],
        fallback="Helvetica-Oblique",
    )
```

Also update the `mono` entry's candidates list to prefer the new IBM Plex Mono:
```python
    mono: FontEntry = FontEntry(
        name="IBMPlexMono",
        candidates=[
            "assets/fonts/IBMPlexMono-Regular.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        ],
        fallback="Courier",
    )
```

- [ ] **Step 4: Add new fields to `FontSet`**

In `carousel/config.py`, inside `FontSet`:
```python
@dataclass
class FontSet:
    """Resolved font names (after registration with fallback)."""
    display: str = "Helvetica-Bold"
    body: str = "Helvetica"
    bold: str = "Helvetica-Bold"
    mono: str = "Courier"
    # Lab notebook roles
    headline_serif: str = "Times-Bold"
    body_serif: str = "Times-Roman"
    handwriting: str = "Helvetica-Oblique"
```

- [ ] **Step 5: Extend `register_fonts`**

In `carousel/fonts.py`, update the function to register the three new roles:
```python
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
        headline_serif=register_font_with_fallback(
            fonts_cfg.headline_serif.name,
            fonts_cfg.headline_serif.candidates,
            fonts_cfg.headline_serif.fallback,
        ),
        body_serif=register_font_with_fallback(
            fonts_cfg.body_serif.name,
            fonts_cfg.body_serif.candidates,
            fonts_cfg.body_serif.fallback,
        ),
        handwriting=register_font_with_fallback(
            fonts_cfg.handwriting.name,
            fonts_cfg.handwriting.candidates,
            fonts_cfg.handwriting.fallback,
        ),
    )
```

- [ ] **Step 6: Run test, verify pass**

Run: `pytest tests/test_fonts_config.py -v`. Expected: 1 passed.

Sanity-check the registered names by running:
```bash
source venv/bin/activate && python -c "
from carousel.fonts import register_fonts
from carousel.schema import FontsConfig
fs = register_fonts(FontsConfig())
print(fs)
"
```
Expected: `headline_serif='IBMPlexSerifBold'`, `body_serif='SourceSerif'`, `handwriting='Caveat'`. (If a fallback is shown instead, the corresponding `.ttf` is missing or unreadable — re-run `scripts/download_fonts.sh`.)

- [ ] **Step 7: Regression**

Run: `python render.py example_payload.json /tmp/regression.pdf`. Expected: PDF created.

- [ ] **Step 8: Commit**

```bash
git add carousel/schema.py carousel/config.py carousel/fonts.py tests/test_fonts_config.py
git commit -m "feat: register lab notebook font roles (headline_serif/body_serif/handwriting)"
```

---

## Task 6: Sketch helpers — seed and wobbled points

**Files:**
- Create: `carousel/sketch.py`
- Test: `tests/test_sketch.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_sketch.py`:
```python
from carousel.sketch import make_seed, _wobbled_polyline


def test_make_seed_is_deterministic():
    assert make_seed("k8s heap leak", 4) == make_seed("k8s heap leak", 4)
    assert make_seed("k8s heap leak", 4) != make_seed("k8s heap leak", 5)


def test_wobbled_polyline_is_deterministic():
    pts_a = _wobbled_polyline([(0, 0), (100, 0)], seed=42, samples=20, jitter=1.5)
    pts_b = _wobbled_polyline([(0, 0), (100, 0)], seed=42, samples=20, jitter=1.5)
    assert pts_a == pts_b


def test_wobbled_polyline_jitters():
    pts = _wobbled_polyline([(0, 0), (100, 0)], seed=42, samples=30, jitter=1.5)
    # Output is the right shape
    assert len(pts) == 30
    # No point sits exactly on the straight line (jitter applied)
    off_axis = sum(1 for (x, y) in pts if abs(y) > 0.01)
    assert off_axis >= 25  # almost all points are jittered


def test_wobbled_polyline_stays_within_jitter_envelope():
    pts = _wobbled_polyline([(0, 0), (100, 0)], seed=42, samples=40, jitter=1.5)
    # Endpoints are pinned (start/end never jitter so arrows connect to anchors)
    assert pts[0] == (0, 0)
    assert pts[-1] == (100, 0)
    # Interior points stay roughly within ±5pt (jitter=1.5 should give ~3σ envelope ≈ 4.5pt)
    for x, y in pts[1:-1]:
        assert abs(y) < 6
```

- [ ] **Step 2: Run tests, verify fail**

Run: `pytest tests/test_sketch.py -v`. Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Create `carousel/sketch.py`**

```python
"""Hand-drawn primitives for the lab notebook aesthetic.

All functions are deterministic given a seed, so a given carousel renders
identically on every run. All output is rendered in red ink (red_pen) by
default. The wobble technique is inspired by rough.js: sample a path,
perturb interior points with Gaussian noise, draw the path twice with a
small offset to simulate "pen passed twice".
"""

from __future__ import annotations
import hashlib
import math
import random
from typing import Iterable, Tuple

Point = Tuple[float, float]

# Default wobble parameters — tuned in the visual gate (Task 17).
DEFAULT_JITTER = 1.5      # std-dev of point perturbation, in points
DEFAULT_SAMPLES = 32      # points sampled along a curve
DEFAULT_LINE_WIDTH = 1.2  # stroke weight for hand-drawn lines


def make_seed(text: str, slide_index: int) -> int:
    """Deterministic 32-bit seed from slide identity. Same identity = same wobble."""
    h = hashlib.sha256(f"{text}|{slide_index}".encode("utf-8")).digest()
    return int.from_bytes(h[:4], "big")


def _wobbled_polyline(
    anchor_points: list[Point],
    seed: int,
    samples: int = DEFAULT_SAMPLES,
    jitter: float = DEFAULT_JITTER,
) -> list[Point]:
    """Sample a polyline interpolated through anchor_points, with Gaussian
    perturbation on each interior sample. Endpoints are pinned (so arrows
    connect cleanly to the anchors they're aiming at)."""
    if len(anchor_points) < 2:
        raise ValueError("anchor_points must have at least 2 points")
    if samples < 2:
        raise ValueError("samples must be >= 2")

    rng = random.Random(seed)
    # Build a piecewise-linear length parameterization
    seg_lengths = [
        math.hypot(b[0] - a[0], b[1] - a[1])
        for a, b in zip(anchor_points, anchor_points[1:])
    ]
    total = sum(seg_lengths) or 1.0
    cum = [0.0]
    for s in seg_lengths:
        cum.append(cum[-1] + s)

    out: list[Point] = []
    for i in range(samples):
        t = i / (samples - 1)
        target = t * total
        # Find segment
        for j in range(len(seg_lengths)):
            if target <= cum[j + 1] or j == len(seg_lengths) - 1:
                seg_t = (target - cum[j]) / max(seg_lengths[j], 1e-9)
                a, b = anchor_points[j], anchor_points[j + 1]
                x = a[0] + seg_t * (b[0] - a[0])
                y = a[1] + seg_t * (b[1] - a[1])
                break
        # Pin endpoints
        if i == 0 or i == samples - 1:
            out.append((x, y))
        else:
            out.append((x + rng.gauss(0, jitter), y + rng.gauss(0, jitter)))
    return out
```

- [ ] **Step 4: Run tests, verify pass**

Run: `pytest tests/test_sketch.py -v`. Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add carousel/sketch.py tests/test_sketch.py
git commit -m "feat: sketch.py — wobbled polyline + deterministic seed"
```

---

## Task 7: Sketch — `draw_arrow` (sweep + pointer + branch)

**Files:**
- Modify: `carousel/sketch.py`
- Modify: `tests/test_sketch.py`

- [ ] **Step 1: Add the failing test**

Append to `tests/test_sketch.py`:
```python
from unittest.mock import MagicMock
from carousel.sketch import draw_arrow


def _record_canvas() -> MagicMock:
    """A fake canvas that records all method calls."""
    return MagicMock(name="canvas")


def test_arrow_sweep_draws_on_canvas():
    c = _record_canvas()
    draw_arrow(c, (50, 100), (200, 100), seed=1, style="sweep")
    # Stroke color was set to red_pen
    assert c.setStrokeColorRGB.called or c.setStrokeColor.called
    # A path was drawn
    assert c.line.called or c.bezier.called or c.drawPath.called or c.beginPath.called


def test_arrow_is_deterministic():
    c1, c2 = _record_canvas(), _record_canvas()
    draw_arrow(c1, (50, 100), (200, 100), seed=1, style="sweep")
    draw_arrow(c2, (50, 100), (200, 100), seed=1, style="sweep")
    # Same number of canvas operations either way
    assert c1.method_calls == c2.method_calls


def test_arrow_pointer_is_straighter_than_sweep():
    """Pointer style should produce shorter total path length than sweep
    for the same endpoints — sweep curves, pointer doesn't."""
    from carousel.sketch import _arrow_anchor_points
    sweep = _arrow_anchor_points((0, 0), (100, 0), style="sweep")
    pointer = _arrow_anchor_points((0, 0), (100, 0), style="pointer")
    # Sweep has at least one off-axis control point; pointer does not
    sweep_off = max(abs(y) for x, y in sweep)
    pointer_off = max(abs(y) for x, y in pointer)
    assert sweep_off > pointer_off


def test_arrow_branch_changes_direction():
    from carousel.sketch import _arrow_anchor_points
    branch = _arrow_anchor_points((0, 0), (50, -80), style="branch")
    # Branch first travels horizontally before turning down
    assert any(abs(y) < 1 and x > 5 for x, y in branch)
```

- [ ] **Step 2: Run tests, verify fail**

Run: `pytest tests/test_sketch.py -v`. Expected: 4 new failures.

- [ ] **Step 3: Implement `_arrow_anchor_points` and `draw_arrow`**

Append to `carousel/sketch.py`:
```python
from reportlab.lib.colors import HexColor

RED_PEN = HexColor("#B22222")


def _arrow_anchor_points(start: Point, end: Point, style: str) -> list[Point]:
    """Return the anchor points that the arrow path interpolates through.
    These are the 'idealized' points before wobble is applied."""
    sx, sy = start
    ex, ey = end
    if style == "sweep":
        # One off-axis control point ~30% along, perpendicular offset
        mx, my = (sx + ex) / 2, (sy + ey) / 2
        dx, dy = ex - sx, ey - sy
        length = math.hypot(dx, dy) or 1.0
        # Perpendicular unit vector
        px, py = -dy / length, dx / length
        # Offset magnitude: a quarter of the run, capped
        offset = min(length * 0.18, 28)
        ctrl = (mx + px * offset, my + py * offset)
        return [start, ctrl, end]
    if style == "pointer":
        return [start, end]
    if style == "branch":
        # Move horizontally first, then turn 90° to the endpoint
        elbow = (ex, sy)
        return [start, elbow, end]
    raise ValueError(f"unknown arrow style: {style!r}")


def _draw_polyline(canvas, points: list[Point], line_width: float):
    p = canvas.beginPath()
    p.moveTo(*points[0])
    for x, y in points[1:]:
        p.lineTo(x, y)
    canvas.setLineWidth(line_width)
    canvas.drawPath(p, stroke=1, fill=0)


def _draw_arrowhead(canvas, tip: Point, direction: Point, seed: int, color):
    """Small triangle at `tip`, pointing along `direction` (a unit-ish vector)."""
    rng = random.Random(seed ^ 0xA17A1)
    dx, dy = direction
    length = math.hypot(dx, dy) or 1.0
    ux, uy = dx / length, dy / length
    # Perpendicular
    px, py = -uy, ux
    head_len = 7.0
    head_wide = 3.5
    # ±5° rotation jitter
    angle_jitter = math.radians(rng.uniform(-5, 5))
    cos_a, sin_a = math.cos(angle_jitter), math.sin(angle_jitter)
    rux = ux * cos_a - uy * sin_a
    ruy = ux * sin_a + uy * cos_a
    rpx = -ruy
    rpy = rux
    base = (tip[0] - rux * head_len, tip[1] - ruy * head_len)
    left = (base[0] + rpx * head_wide, base[1] + rpy * head_wide)
    right = (base[0] - rpx * head_wide, base[1] - rpy * head_wide)
    p = canvas.beginPath()
    p.moveTo(*tip)
    p.lineTo(*left)
    p.lineTo(*right)
    p.close()
    canvas.setFillColor(color)
    canvas.drawPath(p, stroke=1, fill=1)


def draw_arrow(
    canvas,
    start: Point,
    end: Point,
    seed: int,
    style: str = "sweep",
    color=RED_PEN,
    samples: int = DEFAULT_SAMPLES,
    jitter: float = DEFAULT_JITTER,
    line_width: float = DEFAULT_LINE_WIDTH,
):
    """Draw a hand-drawn arrow from start to end. Styles: sweep, pointer, branch."""
    canvas.saveState()
    canvas.setStrokeColor(color)
    canvas.setFillColor(color)

    anchors = _arrow_anchor_points(start, end, style)
    pts = _wobbled_polyline(anchors, seed=seed, samples=samples, jitter=jitter)

    # Draw twice with tiny offset for pen-passed-twice feel
    _draw_polyline(canvas, pts, line_width)
    pts2 = [(x + 0.4, y - 0.3) for x, y in pts]
    _draw_polyline(canvas, pts2, line_width * 0.7)

    # Arrowhead direction: from second-to-last to last point
    if len(pts) >= 2:
        x1, y1 = pts[-2]
        x2, y2 = pts[-1]
        _draw_arrowhead(canvas, pts[-1], (x2 - x1, y2 - y1), seed, color)

    canvas.restoreState()
```

- [ ] **Step 4: Run tests, verify pass**

Run: `pytest tests/test_sketch.py -v`. Expected: 8 passed.

- [ ] **Step 5: Commit**

```bash
git add carousel/sketch.py tests/test_sketch.py
git commit -m "feat: sketch — draw_arrow (sweep, pointer, branch)"
```

---

## Task 8: Sketch — `draw_circle_around`, `draw_underline`

**Files:**
- Modify: `carousel/sketch.py`
- Modify: `tests/test_sketch.py`

- [ ] **Step 1: Add the failing tests**

Append to `tests/test_sketch.py`:
```python
from carousel.sketch import draw_circle_around, draw_underline


def test_circle_around_is_deterministic():
    c1, c2 = _record_canvas(), _record_canvas()
    draw_circle_around(c1, 100, 100, radius=20, seed=7)
    draw_circle_around(c2, 100, 100, radius=20, seed=7)
    assert c1.method_calls == c2.method_calls


def test_underline_is_deterministic():
    c1, c2 = _record_canvas(), _record_canvas()
    draw_underline(c1, 50, 80, width=120, seed=11)
    draw_underline(c2, 50, 80, width=120, seed=11)
    assert c1.method_calls == c2.method_calls


def test_circle_around_calls_path_methods():
    c = _record_canvas()
    draw_circle_around(c, 100, 100, radius=20, seed=7)
    assert c.beginPath.called
    assert c.drawPath.called
```

- [ ] **Step 2: Run, verify fail**

Run: `pytest tests/test_sketch.py -v`. Expected: 3 new failures.

- [ ] **Step 3: Implement**

Append to `carousel/sketch.py`:
```python
def draw_circle_around(
    canvas,
    cx: float,
    cy: float,
    radius: float,
    seed: int,
    color=RED_PEN,
    samples: int = 40,
    jitter: float = 1.2,
    line_width: float = DEFAULT_LINE_WIDTH,
):
    """Hand-drawn ellipse-ish circle (closed wobbled path).

    Slight horizontal stretch (1.05x) so it reads as a quick pen-circle
    rather than a perfect compass curve.
    """
    rng = random.Random(seed ^ 0xC1C1E)
    canvas.saveState()
    canvas.setStrokeColor(color)
    radius_x = radius * 1.05
    pts: list[Point] = []
    # Random starting angle so circles don't all begin at 3 o'clock
    start_angle = rng.uniform(0, 2 * math.pi)
    for i in range(samples + 1):
        t = i / samples
        angle = start_angle + t * 2 * math.pi
        # Radius wobble grows slightly — pen drift on a closed loop
        r_jitter = rng.gauss(0, jitter * 0.6)
        x = cx + (radius_x + r_jitter) * math.cos(angle)
        y = cy + (radius + r_jitter) * math.sin(angle)
        pts.append((x, y))
    _draw_polyline(canvas, pts, line_width)
    canvas.restoreState()


def draw_underline(
    canvas,
    x: float,
    y: float,
    width: float,
    seed: int,
    color=RED_PEN,
    samples: int = 24,
    jitter: float = 0.9,
    line_width: float = DEFAULT_LINE_WIDTH * 1.3,
):
    """Wavy hand-drawn underline."""
    canvas.saveState()
    canvas.setStrokeColor(color)
    pts = _wobbled_polyline(
        [(x, y), (x + width, y)],
        seed=seed,
        samples=samples,
        jitter=jitter,
    )
    _draw_polyline(canvas, pts, line_width)
    canvas.restoreState()
```

- [ ] **Step 4: Run tests, verify pass**

Run: `pytest tests/test_sketch.py -v`. Expected: 11 passed.

- [ ] **Step 5: Commit**

```bash
git add carousel/sketch.py tests/test_sketch.py
git commit -m "feat: sketch — draw_circle_around, draw_underline"
```

---

## Task 9: Sketch — `draw_check`, `draw_cross`, `draw_bracket`

**Files:**
- Modify: `carousel/sketch.py`
- Modify: `tests/test_sketch.py`

- [ ] **Step 1: Add the failing tests**

Append to `tests/test_sketch.py`:
```python
from carousel.sketch import draw_check, draw_cross, draw_bracket


def test_check_deterministic():
    c1, c2 = _record_canvas(), _record_canvas()
    draw_check(c1, 100, 100, size=20, seed=3)
    draw_check(c2, 100, 100, size=20, seed=3)
    assert c1.method_calls == c2.method_calls


def test_cross_deterministic():
    c1, c2 = _record_canvas(), _record_canvas()
    draw_cross(c1, 100, 100, size=20, seed=3)
    draw_cross(c2, 100, 100, size=20, seed=3)
    assert c1.method_calls == c2.method_calls


def test_bracket_left_and_right_differ():
    c_left, c_right = _record_canvas(), _record_canvas()
    draw_bracket(c_left, 100, 100, height=40, side="left", seed=3)
    draw_bracket(c_right, 100, 100, height=40, side="right", seed=3)
    assert c_left.method_calls != c_right.method_calls
```

- [ ] **Step 2: Run, verify fail**

Run: `pytest tests/test_sketch.py -v`. Expected: 3 new failures.

- [ ] **Step 3: Implement**

Append to `carousel/sketch.py`:
```python
def draw_check(
    canvas, cx: float, cy: float, size: float, seed: int,
    color=RED_PEN, line_width: float = DEFAULT_LINE_WIDTH * 1.4,
):
    """Editor's-pen ✓ centered at (cx, cy)."""
    canvas.saveState()
    canvas.setStrokeColor(color)
    s = size / 2
    # ✓ shape — short down-stroke into long up-stroke
    anchors = [
        (cx - s * 0.9, cy + s * 0.1),
        (cx - s * 0.2, cy - s * 0.7),
        (cx + s * 1.0, cy + s * 0.7),
    ]
    pts = _wobbled_polyline(anchors, seed=seed, samples=20, jitter=0.7)
    _draw_polyline(canvas, pts, line_width)
    canvas.restoreState()


def draw_cross(
    canvas, cx: float, cy: float, size: float, seed: int,
    color=RED_PEN, line_width: float = DEFAULT_LINE_WIDTH * 1.4,
):
    """Editor's-pen ✗ centered at (cx, cy)."""
    canvas.saveState()
    canvas.setStrokeColor(color)
    s = size / 2
    # First stroke: top-left to bottom-right
    pts1 = _wobbled_polyline(
        [(cx - s, cy + s), (cx + s, cy - s)],
        seed=seed, samples=18, jitter=0.7,
    )
    _draw_polyline(canvas, pts1, line_width)
    # Second stroke: top-right to bottom-left, with a different sub-seed
    pts2 = _wobbled_polyline(
        [(cx + s, cy + s), (cx - s, cy - s)],
        seed=seed ^ 0xC0FFEE, samples=18, jitter=0.7,
    )
    _draw_polyline(canvas, pts2, line_width)
    canvas.restoreState()


def draw_bracket(
    canvas, x: float, y: float, height: float, side: str, seed: int,
    color=RED_PEN, line_width: float = DEFAULT_LINE_WIDTH,
):
    """Vertical grouping bracket. side='left' draws [, 'right' draws ]."""
    if side not in ("left", "right"):
        raise ValueError(f"side must be 'left' or 'right', got {side!r}")
    canvas.saveState()
    canvas.setStrokeColor(color)
    tick = 6  # length of the perpendicular caps
    if side == "left":
        anchors = [
            (x + tick, y),
            (x, y),
            (x, y + height),
            (x + tick, y + height),
        ]
    else:
        anchors = [
            (x - tick, y),
            (x, y),
            (x, y + height),
            (x - tick, y + height),
        ]
    pts = _wobbled_polyline(anchors, seed=seed, samples=28, jitter=0.7)
    _draw_polyline(canvas, pts, line_width)
    canvas.restoreState()
```

- [ ] **Step 4: Run tests, verify pass**

Run: `pytest tests/test_sketch.py -v`. Expected: 14 passed.

- [ ] **Step 5: Commit**

```bash
git add carousel/sketch.py tests/test_sketch.py
git commit -m "feat: sketch — draw_check, draw_cross, draw_bracket"
```

---

## Task 10: Layout chassis — `draw_dot_grid`

**Files:**
- Modify: `carousel/layout.py`
- Test: `tests/test_layout_chassis.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_layout_chassis.py`:
```python
from unittest.mock import MagicMock
from carousel.layout import draw_dot_grid


def test_dot_grid_draws_expected_dot_count():
    """At spacing=12 over a 612x765 page with margin=24, expect roughly
    (612-48)/12 * (765-48)/12 ≈ 47 * 60 = 2820 circles."""
    c = MagicMock(name="canvas")
    draw_dot_grid(c, width=612, height=765, margin=24, spacing=12,
                  color=MagicMock(), opacity=0.03, dot_radius=0.5)
    # Each dot is one circle() call
    assert 2500 < c.circle.call_count < 3200


def test_dot_grid_sets_alpha():
    c = MagicMock(name="canvas")
    color = MagicMock()
    draw_dot_grid(c, 612, 765, margin=24, spacing=12, color=color,
                  opacity=0.03, dot_radius=0.5)
    c.setFillAlpha.assert_any_call(0.03)
```

- [ ] **Step 2: Run, verify fail**

Run: `pytest tests/test_layout_chassis.py -v`. Expected: FAIL with ImportError.

- [ ] **Step 3: Implement**

Append to `carousel/layout.py`:
```python
def draw_dot_grid(canvas, width: float, height: float, margin: float,
                  spacing: float, color, opacity: float, dot_radius: float):
    """Draw a subtle dot grid background. Used by new_lab_page."""
    canvas.saveState()
    canvas.setFillColor(color)
    canvas.setFillAlpha(opacity)
    canvas.setStrokeAlpha(0)
    x = margin
    while x <= width - margin:
        y = margin
        while y <= height - margin:
            canvas.circle(x, y, dot_radius, fill=1, stroke=0)
            y += spacing
        x += spacing
    canvas.restoreState()
```

- [ ] **Step 4: Run, verify pass**

Run: `pytest tests/test_layout_chassis.py -v`. Expected: 2 passed.

- [ ] **Step 5: Commit**

```bash
git add carousel/layout.py tests/test_layout_chassis.py
git commit -m "feat: layout — draw_dot_grid"
```

---

## Task 11: Layout chassis — `draw_masthead`

**Files:**
- Modify: `carousel/layout.py`
- Modify: `tests/test_layout_chassis.py`

- [ ] **Step 1: Add the failing test**

Append to `tests/test_layout_chassis.py`:
```python
from carousel.layout import draw_masthead


def test_masthead_draws_text_and_rule():
    c = MagicMock(name="canvas")
    draw_masthead(c, width=612, height=765, margin=24,
                  font_name="Helvetica", color=MagicMock(),
                  volume="VOL III", issue="ISSUE 14",
                  topic="K8S HEAP LEAK", page_num=4, total_pages=12)
    # Some text was drawn
    assert c.drawString.called or c.drawRightString.called
    # And a rule line
    assert c.line.called
    # The composed string includes the topic
    drawn_args = []
    for call in c.method_calls:
        if call[0] in ("drawString", "drawRightString"):
            drawn_args.append(call[1])  # positional args
    flat = " ".join(repr(a) for a in drawn_args)
    assert "K8S HEAP LEAK" in flat
    assert "04" in flat or "4" in flat
```

- [ ] **Step 2: Run, verify fail**

Run: `pytest tests/test_layout_chassis.py -v`. Expected: 1 new failure.

- [ ] **Step 3: Implement**

Append to `carousel/layout.py`:
```python
def draw_masthead(
    canvas, width: float, height: float, margin: float,
    font_name: str, color,
    volume: str, issue: str, topic: str,
    page_num: int, total_pages: int,
    masthead_size: float = 8.5,
    rule_offset: float = 4,
):
    """Top-of-page masthead: VOL · ISSUE · TOPIC ............ pg NN/MM
    + thin horizontal rule below."""
    canvas.saveState()
    y_text = height - margin
    canvas.setFont(font_name, masthead_size)
    canvas.setFillColor(color)

    left = " · ".join([volume, issue, topic])
    right = f"pg {page_num:02d}/{total_pages:02d}"
    canvas.drawString(margin, y_text, left.upper())
    canvas.drawRightString(width - margin, y_text, right)

    canvas.setStrokeColor(color)
    canvas.setLineWidth(0.4)
    y_rule = y_text - rule_offset
    canvas.line(margin, y_rule, width - margin, y_rule)
    canvas.restoreState()
```

- [ ] **Step 4: Run, verify pass**

Run: `pytest tests/test_layout_chassis.py -v`. Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add carousel/layout.py tests/test_layout_chassis.py
git commit -m "feat: layout — draw_masthead"
```

---

## Task 12: Layout chassis — `draw_signature_footer`

**Files:**
- Modify: `carousel/layout.py`
- Modify: `tests/test_layout_chassis.py`

- [ ] **Step 1: Add the failing test**

Append to `tests/test_layout_chassis.py`:
```python
from carousel.layout import draw_signature_footer


def test_signature_footer_draws_signature_and_page_number():
    c = MagicMock(name="canvas")
    draw_signature_footer(
        c, width=612, margin=24,
        handwriting_font="Helvetica-Oblique",
        body_font="Helvetica",
        ink_color=MagicMock(), red_pen_color=MagicMock(),
        signature="✎ milind nair", page_num=4,
    )
    # Rule, signature text, and page number
    assert c.line.called
    drawn = []
    for call in c.method_calls:
        if call[0] in ("drawString", "drawRightString"):
            drawn.append(" ".join(repr(a) for a in call[1]))
    blob = " | ".join(drawn)
    assert "milind nair" in blob
    assert "04" in blob or "4" in blob
```

- [ ] **Step 2: Run, verify fail**

Run: `pytest tests/test_layout_chassis.py -v`. Expected: 1 new failure.

- [ ] **Step 3: Implement**

Append to `carousel/layout.py`:
```python
def draw_signature_footer(
    canvas, width: float, margin: float,
    handwriting_font: str, body_font: str,
    ink_color, red_pen_color,
    signature: str, page_num: int,
    y: float = 22,
    signature_size: float = 13,
    page_size: float = 8.5,
):
    """Bottom-of-page footer: thin rule, handwritten signature on the left
    in red ink, page number on the right in body ink."""
    canvas.saveState()
    canvas.setStrokeColor(ink_color)
    canvas.setLineWidth(0.4)
    canvas.line(margin, y + 14, width - margin, y + 14)

    canvas.setFont(handwriting_font, signature_size)
    canvas.setFillColor(red_pen_color)
    canvas.drawString(margin, y, signature)

    canvas.setFont(body_font, page_size)
    canvas.setFillColor(ink_color)
    canvas.drawRightString(width - margin, y, f"{page_num:02d}")
    canvas.restoreState()
```

- [ ] **Step 4: Run, verify pass**

Run: `pytest tests/test_layout_chassis.py -v`. Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add carousel/layout.py tests/test_layout_chassis.py
git commit -m "feat: layout — draw_signature_footer"
```

---

## Task 13: Layout chassis — `new_lab_page`

**Files:**
- Modify: `carousel/layout.py`
- Modify: `tests/test_layout_chassis.py`

- [ ] **Step 1: Add the failing test**

Append to `tests/test_layout_chassis.py`:
```python
from carousel.layout import new_lab_page


def test_new_lab_page_runs_full_chassis():
    """Integration: paper fill + dot grid + masthead + footer all called."""
    from carousel.config import Config
    cfg = Config()  # defaults

    c = MagicMock(name="canvas")
    ctx = MagicMock()
    ctx.canvas = c
    ctx.config = cfg

    new_lab_page(ctx, volume="VOL III", issue="ISSUE 14",
                 topic="K8S HEAP LEAK", page_num=4, total_pages=12)

    # Paper background filled
    assert c.rect.called
    # Dot grid drew lots of circles
    assert c.circle.call_count > 100
    # Masthead drew a top-of-page rule and text
    assert c.drawString.called
    assert c.line.call_count >= 2  # masthead rule + footer rule
```

- [ ] **Step 2: Run, verify fail**

Run: `pytest tests/test_layout_chassis.py -v`. Expected: 1 new failure.

- [ ] **Step 3: Implement**

Append to `carousel/layout.py`:
```python
def new_lab_page(
    ctx, volume: str, issue: str, topic: str,
    page_num: int, total_pages: int,
    *, first_page: bool = False,
):
    """Lay down the lab notebook chassis on the current page.

    Call at the start of every interior renderer. Does NOT call showPage()
    on the first page (matches pipeline.py which already started the canvas).
    """
    c = ctx.canvas
    cfg = ctx.config

    if not first_page:
        c.showPage()
        c.setPageSize((cfg.width, cfg.height))

    # Paper background
    c.setFillColor(cfg.colors.paper)
    c.rect(0, 0, cfg.width, cfg.height, fill=1, stroke=0)

    # Dot grid
    draw_dot_grid(
        c,
        width=cfg.width, height=cfg.height,
        margin=cfg.margin, spacing=12,
        color=cfg.colors.ink,
        opacity=0.05,
        dot_radius=0.45,
    )

    # Masthead
    draw_masthead(
        c,
        width=cfg.width, height=cfg.height, margin=cfg.margin,
        font_name=cfg.fonts.mono, color=cfg.colors.ink,
        volume=volume, issue=issue, topic=topic,
        page_num=page_num, total_pages=total_pages,
    )

    # Signature footer
    draw_signature_footer(
        c,
        width=cfg.width, margin=cfg.margin,
        handwriting_font=cfg.fonts.handwriting,
        body_font=cfg.fonts.mono,
        ink_color=cfg.colors.ink,
        red_pen_color=cfg.colors.red_pen,
        signature=f"✎ {cfg.brand_name.lower()}",
        page_num=page_num,
    )
```

- [ ] **Step 4: Run, verify pass**

Run: `pytest tests/test_layout_chassis.py -v`. Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
git add carousel/layout.py tests/test_layout_chassis.py
git commit -m "feat: layout — new_lab_page chassis"
```

---

## Task 14: Visual smoke test — `_chassis_test` slide type and renderer

**Files:**
- Modify: `carousel/schema.py` — add `_ChassisTestSlide`
- Create: `carousel/renderers/_chassis_test.py`
- Modify: `carousel/renderers/__init__.py`
- Create: `tests/payloads/chassis_test.json`

- [ ] **Step 1: Add `_ChassisTestSlide` to schema**

In `carousel/schema.py`, just before the `Slide` union (line ~206), add:
```python
class _ChassisTestSlide(BaseSlide):
    """Internal slide type for visually validating the lab notebook chassis
    and sketch primitives. Not part of the public slide vocabulary."""
    type: Literal["_chassis_test"] = "_chassis_test"
    mode: Literal["chassis", "primitives"] = "chassis"
    volume: str = "VOL I"
    issue: str = "ISSUE 01"
    topic: str = "FOUNDATION TEST"
    page_num: int = 1
    total_pages: int = 2
```

Then update the `Slide` union to include it:
```python
Slide = Annotated[
    TitleDarkSlide
    | ContentCardsSlide
    | GridCardsSlide
    | ComparisonTableSlide
    | FlowDiagramSlide
    | DecisionFrameworkSlide
    | ClosingDarkSlide
    | _ChassisTestSlide,
    Field(discriminator="type"),
]
```

- [ ] **Step 2: Create the chassis-test renderer**

Create `carousel/renderers/_chassis_test.py`:
```python
"""Internal: visual smoke test for the chassis + sketch primitives.

Two modes:
  - "chassis": draw the empty chassis (paper, dot grid, masthead, footer).
  - "primitives": draw a labeled grid of every sketch primitive.

This renderer is for manual eyeball validation; no public carousel uses it.
"""

from __future__ import annotations

from carousel.registry import register
from carousel.layout import new_lab_page
from carousel.sketch import (
    make_seed,
    draw_arrow, draw_circle_around, draw_underline,
    draw_check, draw_cross, draw_bracket,
)


@register("_chassis_test")
def render_chassis_test(slide: dict, ctx):
    cfg = ctx.config
    c = ctx.canvas

    new_lab_page(
        ctx,
        volume=slide.get("volume", "VOL I"),
        issue=slide.get("issue", "ISSUE 01"),
        topic=slide.get("topic", "FOUNDATION TEST"),
        page_num=slide.get("page_num", 1),
        total_pages=slide.get("total_pages", 2),
        first_page=(slide.get("page_num", 1) == 1),
    )

    if slide.get("mode") == "primitives":
        _draw_primitive_grid(c, cfg, slide.get("topic", "PRIMITIVES"))


def _draw_primitive_grid(c, cfg, topic: str):
    """Lay out one labeled cell per primitive."""
    body_y_top = cfg.height - cfg.margin - 60
    cell_w, cell_h = 240, 110
    cells = [
        ("arrow / sweep",
         lambda x, y, s: draw_arrow(c, (x + 30, y - 50), (x + 200, y - 30), seed=s, style="sweep")),
        ("arrow / pointer",
         lambda x, y, s: draw_arrow(c, (x + 30, y - 50), (x + 200, y - 60), seed=s, style="pointer")),
        ("arrow / branch",
         lambda x, y, s: draw_arrow(c, (x + 30, y - 20), (x + 200, y - 80), seed=s, style="branch")),
        ("circle around",
         lambda x, y, s: draw_circle_around(c, x + 115, y - 50, radius=32, seed=s)),
        ("underline",
         lambda x, y, s: draw_underline(c, x + 30, y - 50, width=180, seed=s)),
        ("check",
         lambda x, y, s: draw_check(c, x + 115, y - 50, size=36, seed=s)),
        ("cross",
         lambda x, y, s: draw_cross(c, x + 115, y - 50, size=36, seed=s)),
        ("bracket",
         lambda x, y, s: draw_bracket(c, x + 60, y - 80, height=60, side="left", seed=s)),
    ]

    cols = 2
    for i, (label, draw_fn) in enumerate(cells):
        col = i % cols
        row = i // cols
        cell_x = cfg.margin + col * (cell_w + 8)
        cell_y = body_y_top - row * (cell_h + 16)

        # Label in mono
        c.setFont(cfg.fonts.mono, 8.5)
        c.setFillColor(cfg.colors.ink)
        c.drawString(cell_x, cell_y, label.upper())

        # Primitive
        seed = make_seed(label, i)
        draw_fn(cell_x, cell_y, seed)
```

- [ ] **Step 3: Register the renderer**

Modify `carousel/renderers/__init__.py`:
```python
"""Auto-import all slide renderers to populate the registry."""

from . import (
    title_dark,
    content_cards,
    grid_cards,
    comparison_table,
    flow_diagram,
    decision_framework,
    closing_dark,
    _chassis_test,
)
```

- [ ] **Step 4: Create the test payload**

Create `tests/payloads/chassis_test.json`:
```json
{
  "meta": {
    "output_filename": "chassis_test.pdf",
    "title": "Chassis & primitives smoke test"
  },
  "slides": [
    {
      "type": "_chassis_test",
      "mode": "chassis",
      "volume": "VOL I",
      "issue": "ISSUE 01",
      "topic": "FOUNDATION TEST",
      "page_num": 1,
      "total_pages": 2
    },
    {
      "type": "_chassis_test",
      "mode": "primitives",
      "volume": "VOL I",
      "issue": "ISSUE 01",
      "topic": "SKETCH PRIMITIVES",
      "page_num": 2,
      "total_pages": 2
    }
  ]
}
```

- [ ] **Step 5: Render the smoke test**

Run:
```bash
source venv/bin/activate && python render.py tests/payloads/chassis_test.json
```

Expected: `outputs/chassis_test.pdf` created with two pages. No errors.

- [ ] **Step 6: Run the full test suite**

Run:
```bash
pytest tests/ -v
```
Expected: all tests pass.

- [ ] **Step 7: Commit**

```bash
git add carousel/schema.py carousel/renderers/_chassis_test.py carousel/renderers/__init__.py tests/payloads/chassis_test.json
git commit -m "feat: visual smoke test — _chassis_test slide type and renderer"
```

---

## Task 15: Visual tuning gate (manual)

**This is the gate. Don't skip.** The whole rest of the redesign assumes the sketch primitives feel hand-drawn but credible. Right now you have a `outputs/chassis_test.pdf` to look at. This task is the eyeball pass and any tuning adjustments that come out of it.

- [ ] **Step 1: Open the smoke-test PDF**

Open `outputs/chassis_test.pdf` in a PDF viewer (or convert to PNG with `python -c "import fitz; d=fitz.open('outputs/chassis_test.pdf'); [p.get_pixmap(dpi=216).save(f'/tmp/chassis-{i}.png') for i, p in enumerate(d)]"` and view).

- [ ] **Step 2: Review the chassis page (page 1)**

Check against the spec ([Section 1, Visual Foundation](../specs/2026-05-07-lab-notebook-redesign-design.md)):

| Question | Pass criterion |
|---|---|
| Background reads as cream paper, not white | Yes |
| Dot grid is visible but not distracting | Faint, doesn't compete with content |
| Masthead reads "VOL I · ISSUE 01 · FOUNDATION TEST · pg 01/02" in small-caps mono | Yes |
| Thin rule sits below masthead | Yes |
| Bottom rule + handwritten signature in red + page number on the right | Yes |
| Page feels like a notebook page | Yes |

If any fail: adjust parameters in `new_lab_page`/`draw_dot_grid`/`draw_masthead`/`draw_signature_footer`. Common knobs: dot grid `opacity` (try 0.03–0.08), `spacing` (try 10–14), masthead `masthead_size` (try 8–10), signature `signature_size` (try 11–14).

- [ ] **Step 3: Review the primitives page (page 2)**

For each primitive in the labeled grid:

| Primitive | Pass criterion |
|---|---|
| Arrow (sweep) | Curves naturally; arrowhead visible; doesn't look ruler-straight or scribbled |
| Arrow (pointer) | Mostly straight with slight wobble; arrowhead visible |
| Arrow (branch) | Goes horizontal then turns down; both segments wobble |
| Circle around | Closed loop; slight imperfection; reads as "I circled this" not as compass-perfect |
| Underline | Wavy, not ruler-straight; weight visible |
| Check (✓) | Reads clearly as a ✓; no weird crossing |
| Cross (✗) | Reads as ✗; both strokes visible; not perfectly aligned |
| Bracket [ | Vertical stroke + perpendicular caps top/bottom; reads as a notebook bracket |

- [ ] **Step 4: Tune if needed**

If primitives feel:
- **Too clean / mechanical**: increase `DEFAULT_JITTER` from 1.5 to 1.8–2.0 in `carousel/sketch.py`.
- **Too messy / scribbled**: drop to 1.0–1.2.
- **Lines too thin**: increase `DEFAULT_LINE_WIDTH` from 1.2 to 1.5.
- **Pen-passed-twice doubling too obvious**: in `draw_arrow`, drop the offset from `(0.4, -0.3)` to `(0.2, -0.15)`, or remove the second pass entirely.
- **Arrowheads look weird**: tune `head_len` (7) and `head_wide` (3.5) in `_draw_arrowhead`.

After each tuning change, re-run `python render.py tests/payloads/chassis_test.json` and re-open the PDF.

Iterate until all rows pass. **Hard stop:** budget at most one focused session on this. If after a session the primitives still feel either too clean or too messy, document the failure mode in `docs/superpowers/specs/2026-05-07-lab-notebook-redesign-design.md` (under the risk register) and pivot to the fallback: a pre-rendered SVG arrow library. Plan 2 will be revised accordingly.

- [ ] **Step 5: Commit any tuning changes**

```bash
git add carousel/sketch.py carousel/layout.py
git commit -m "tune: visual tuning gate adjustments"
```

(If no changes were needed, skip this commit.)

- [ ] **Step 6: Regression — old engine still works**

Run:
```bash
python render.py example_payload.json /tmp/regression.pdf
```
Expected: PDF created without errors, visually identical to the pre-Phase-1 baseline (since none of the old renderer code paths were modified).

- [ ] **Step 7: Final sanity — all tests pass**

Run:
```bash
pytest tests/ -v
```
Expected: all pass (sketch + palette + dimensions + fonts + chassis + smoke).

---

## End of Plan 1

At the end of Plan 1:
- `carousel/sketch.py` exists with 6 hand-drawn primitives, all tested and tuned.
- `carousel/layout.py` has a working `new_lab_page` chassis next to the old `new_page`/`decorate_page`.
- New color palette, dimensions, and font roles are all live in the schema/config.
- A `_chassis_test` payload renders a 2-page PDF that visually validates the foundation.
- All existing renderers still work unchanged.

**Plan 2 (slide types) is held until this gate is passed.** If the tuning gate revealed that vector wobble doesn't carry the aesthetic, Plan 2 is revised before being written — the SVG-arrow-library fallback changes how `draw_arrow` is called from each renderer.

---

## Self-Review Notes

Spec coverage check:
- §1 Visual Foundation (palette, typography, page chrome) → Tasks 3, 4, 5, 10, 11, 12, 13 ✓
- §3 Sketch primitives library → Tasks 6–9 ✓
- §3 Marginalia data model → deferred to Plan 2 (renderers consume marginalia; the library doesn't need it yet)
- §3 Sketch arrow rendering technique → Task 7 ✓
- §4 Phase 1 tuning gate → Task 15 ✓

Type/name consistency check:
- `make_seed` introduced in Task 6, used in Task 14's `_chassis_test` — consistent ✓
- `_wobbled_polyline`, `_arrow_anchor_points`, `_draw_polyline`, `_draw_arrowhead` — private helpers, not referenced cross-task ✓
- `RED_PEN` defined in Task 7, used as default arg in Tasks 7, 8, 9 — consistent ✓
- `new_lab_page(ctx, volume, issue, topic, page_num, total_pages, *, first_page=False)` introduced in Task 13, called with these exact kwargs in Task 14 ✓
- `cfg.colors.paper`, `cfg.colors.ink`, `cfg.colors.red_pen` — added in Task 3, used in Tasks 13 (chassis) and 7–9 (defaults reference RED_PEN constant directly) ✓
- `cfg.fonts.handwriting`, `cfg.fonts.mono` — added in Task 5, used in Tasks 11, 12, 13 ✓
- `cfg.body_column_width`, `cfg.left_gutter`, `cfg.right_gutter` — added in Task 4. Not directly used by any chassis function in this plan (the chassis uses `margin` for its own outer rules); these dimensions are for renderer use in Plan 2. Listed in the file structure as future-facing. ✓

Placeholder scan:
- All steps have concrete code or commands ✓
- All test code is complete and runnable ✓
- Font URLs in Task 2 may break — flagged in the task with recovery instruction ✓

Scope check:
- One plan, one validation gate, ends at a clean handoff to Plan 2 ✓

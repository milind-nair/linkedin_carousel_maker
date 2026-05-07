# Lab Notebook Redesign — Design Spec

**Date:** 2026-05-07
**Author:** Milind Nair
**Status:** Approved for implementation planning

## Problem

The current carousel rendering engine produces a visual style — amber/cream palette, sans-serif, rounded card blocks with left accent bars, generic vector glyphs, pill badges — that has become the default "Claude-generated carousel" look across LinkedIn. Other creators using Claude to author carousels are now producing visually identical output. The differentiation moat that the current engine provided is gone.

The fix is not to remove AI defaults (a moving target) but to commit to a specific, opinionated visual identity that depends on artifacts and discipline AI cannot easily replicate at the same level of consistency.

## Direction: Lab Notebook / Engineering Zine

The aesthetic anchor is **dev lab notebook** — closer to *Andy Matuschak's working notes*, *Bret Victor's essays*, *Tufte handouts*, and *annotated technical writeups* than to template-driven slide decks. Specifically a hybrid:

- **Spine: dev lab notebook** — annotated screenshots, terminal output, code blocks, real diagrams, density over whitespace.
- **Typographic discipline: clean technical zine** — serif headlines, mono code, generous use of figure numbering, off-grid but disciplined.
- **Garnish: raw sketchbook** — hand-drawn arrows and marginalia in a handwriting layer, layered onto otherwise rigorous technical layouts.

The defensibility comes from layering. Any single layer (cream paper, serif headlines, marginalia) can be copied. The full stack — sustained across an entire carousel with consistency — requires a tuned engine and authoring discipline.

## Five signature elements (all in)

The carousel system commits to all five distinguishing elements:

1. **Numbered observations as the unit of thought** — every prose slide is structured as `Obs. 1`, `Obs. 2`, `Obs. 3` with the numbers in the left gutter outside the body column.
2. **Annotated screenshots / artifacts** — full-bleed real images with hand-drawn arrows + handwritten labels pointing at specific elements.
3. **Hand-drawn box-and-line diagrams** — every carousel includes 1+ custom system diagram presented with `Fig. N` caption.
4. **Signature cover treatment** — masthead-style cover with volume/issue numbering: `VOL III · ISSUE 14 · TOPIC` plus a custom illustration.
5. **Voice-in-the-margin** — persistent handwritten narrator voice in the right margin: asides, jokes, "I tried this and it broke", contradictions. The personality layer.

## Section 1 — Visual Foundation

### Color palette (3 ink colors + paper)

| Role | Color | Use |
|---|---|---|
| Paper | `#FAF7F0` (cream off-white) | Page background — reads as real paper, not screen |
| Ink | `#2A2A2A` (charcoal, never pure black) | All text, rules, diagram strokes |
| Red pen | `#B22222` (editor's red) | Marginalia, sketch arrows, corrections, observation numbers, signature accents |
| Diagram blue | `#3E5C76` (muted ink) | Diagram fills/secondary strokes only — used sparingly when red would clash |

Retired: amber `#D97706`, all pastel pill backgrounds (`#FEF3C7`, etc.), all rounded card backgrounds.

### Typography

**Sans-serif is retired entirely.** This is the strongest "AI carousel" tell.

| Use | Font | Notes |
|---|---|---|
| Headlines / titles | IBM Plex Serif or Source Serif Pro | Editorial weight |
| Body prose | Source Serif Pro at 13pt | Readable serif |
| Code & data | IBM Plex Mono / JetBrains Mono | First-class — used liberally, not just in code slides |
| Marginalia / personality | Caveat (handwriting) | Always red ink |

All open-source. Linux paths primary; fallback chain to system serif/mono if not installed.

### Page chrome (consistent across all interior slides)

```
┌──────────────────────────────────────────────────────────────┐
│  VOL III · ISSUE 14 · K8S HEAP LEAK            ·  pg 04/12   │ ← top masthead, small caps
│  ────────────────────────────────────────────────────────────  ← thin charcoal rule
│                                                              │
│  ┌─────────────────────────────┐  │                          │
│  │                             │  │  margin notes here       │
│  │  body column                │  │  in handwriting,         │
│  │  (serif or mono)            │  │  red ink, ~11pt          │
│  │                             │  │                          │
│  │  ~432pt wide                │  │  ~120pt wide             │
│  │                             │  │                          │
│  └─────────────────────────────┘  │                          │
│                                                              │
│  ────────────────────────────────────────────────────────────  ← thin rule
│  ✎ milind nair                                          12   │ ← handwritten signature
└──────────────────────────────────────────────────────────────┘
```

- **Subtle dot grid** at ~3% opacity over the full page.
- **Top masthead**: `VOL · ISSUE · TOPIC · PG N/M` in small-caps mono. Volume can correspond to year, issue to post number.
- **Body column**: 432pt wide (down from current 516pt) for readability.
- **Right margin**: 120pt reserved for marginalia.
- **Left margin**: 60pt for observation/figure numbers that sit *outside* the body column.
- **Bottom**: thin rule, handwritten signature wordmark, page number.

The current decorative band and sans-serif footer are retired.

## Section 2 — Slide Type Inventory

Eight slide types. Two current types (`grid_cards`, `flow_diagram`) are retired entirely because they ARE the AI-default look — a 2-column grid and a vertical "boxes-with-arrows" flow are exactly what every Claude-generated carousel reaches for.

| Slide type | Role | Replaces | Signature elements |
|---|---|---|---|
| `cover` | Masthead opener with vol/issue, big serif title, custom illustration | `title_dark` | D |
| `lab_notes` | Numbered observations + marginalia. The workhorse | `content_cards` | A + E |
| `annotated_artifact` | Full-bleed screenshot/terminal/log with hand-drawn arrows + handwritten labels | (new) | B + E |
| `diagram_page` | Full-page hand-drawn box-and-line diagram with `Fig. N` caption | (new); absorbs `flow_diagram` | C + E |
| `code_listing` | Code as a textbook "Listing 2.3" with marginal commentary explaining specific lines | (new) | E |
| `comparison_table` | Restyled — no pills, no rounded cards, ruled rows + editor's-pen ✓/✗ marks | `comparison_table` | E |
| `decision_tree` | Restyled — numbered Qs + hand-drawn branch arrows | `decision_framework` | A + E |
| `colophon` | Back-of-magazine close: "in this issue" recap, signature, "next issue" tease, handwritten note | `closing_dark` | D + E |

Retired entirely: `grid_cards`, `flow_diagram` (folded into `diagram_page`).

### The core workhorse: `lab_notes`

```
─────────────────────────────────────────────────
VOL III · ISSUE 14 · K8S HEAP LEAK         pg 04
─────────────────────────────────────────────────

       ┌─ heading: "What the heap actually showed"
       │
 OBS   │  Pods that crashed all shared one trait:
  1.   │  they'd been running > 14 days. Younger        ← arrow to "14 days"
       │  pods on the same nodes were healthy.            │ "this was the
       │                                                  │  first real clue"
 OBS   │  The leak wasn't rate-based. It was time-       │
  2.   │  based. Memory grew with uptime regardless      │
       │  of request volume. ← that ruled out request                       
       │  handlers as the source.                        │ "ruled this out
                                                         │  Tuesday night"
 OBS   │  Heap dumps revealed 1.2M zombie goroutines     │
  3.   │  parked on a channel that no longer had a       │
       │  receiver.                                      │
                                                         │
─────────────────────────────────────────────────
✎ milind nair                                  04
─────────────────────────────────────────────────
```

Structural rules:
- Numbered observations in the **left gutter** (60pt column) — `OBS 1.`, `OBS 2.`, etc.
- Body in serif prose at 13pt.
- Marginalia in the **right gutter** (120pt column) — handwriting font, red ink, ~11pt.
- Hand-drawn arrows connecting margin notes to specific observations.
- **2–4 observations per slide max.** Never more.
- Code can appear inline within an observation.

### Typical 10-slide composition

A carousel becomes more like a magazine spread than a deck:

1. `cover`
2. `lab_notes` — the setup / what I was looking at
3. `annotated_artifact` — show the actual symptom (real terminal/log/dashboard)
4. `lab_notes` — observations from the artifact
5. `diagram_page` — the system diagram (Fig. 1)
6. `lab_notes` — what the diagram doesn't show
7. `code_listing` — the actual fix
8. `lab_notes` — what I'd do differently
9. `comparison_table` or `decision_tree` — the takeaway as a tool
10. `colophon`

Compare to current default (cover → 6× content_cards → comparison → flow → close). The new shape forces variety — every other slide is a real artifact (screenshot, diagram, code) rather than another card grid.

## Section 3 — Marginalia, Arrows & Sketch Primitives

The cross-cutting personality layer. Applies to all interior slide types.

### Three things, all hand-drawn-feeling, all reproducible

| Thing | Lives in JSON | Used by |
|---|---|---|
| Marginalia — short handwritten asides in the right gutter | `marginalia: [...]` on the slide | `lab_notes`, `code_listing`, `annotated_artifact`, `diagram_page`, `decision_tree` |
| Sketch arrows — hand-drawn-feeling arrows connecting margin → body, or label → target | `arrows: [...]` (or implicit from marginalia) | All interior slides |
| Sketch primitives — circles around things, checks/crosses, underlines, brackets | `annotations: [...]` or rendered automatically | `annotated_artifact`, `comparison_table`, ad-hoc anywhere |

### Marginalia data model

```json
"marginalia": [
  {
    "text": "this was the first real clue",
    "anchor_obs": 1,
    "arrow": true
  },
  {
    "text": "ruled this out Tuesday night",
    "anchor_obs": 2,
    "arrow": true
  },
  {
    "text": "wild, right?",
    "anchor_y": 320,
    "arrow": false
  }
]
```

- `anchor_obs: N` — the renderer knows where Obs. N starts on the laid-out slide and draws a curving arrow from the margin note to that point. No manual Y math.
- `anchor_y: <int>` — escape hatch for explicit placement.
- `arrow: false` — margin note exists alone, no connector. Used for asides commenting on the whole slide.

**Authoring rule: 2–3 marginalia per slide max.** More becomes noise. Most slides have 1–2.

### Sketch arrow rendering technique

Inspired by rough.js. Implementation steps for each arrow:

1. Define a Bezier curve from start → end.
2. Sample 30–40 points along it.
3. Perturb each point with small Gaussian noise (~1.5pt), deterministic from a per-slide seed (`hash(slide.title + slide_index)`) so a given carousel always renders identically.
4. Draw the path twice with slight offset — mimics "pen passed twice."
5. Arrowhead is a small triangle with ±5° rotation jitter.

Three arrow styles:
- **`sweep`** — curves from margin into body. Default for marginalia.
- **`pointer`** — mostly straight. Used in `annotated_artifact`.
- **`branch`** — used by `decision_tree`.

All arrows are red ink (`#B22222`) always.

### Sketch primitives library — new module `carousel/sketch.py`

```python
draw_arrow(canvas, start, end, style="sweep", seed=...)
draw_circle_around(canvas, x, y, radius, seed=...)   # circling things in screenshots
draw_underline(canvas, x, y, width, seed=...)         # emphasis under text
draw_check(canvas, x, y, size, seed=...)              # ✓ for comparison_table
draw_cross(canvas, x, y, size, seed=...)              # ✗ for comparison_table
draw_bracket(canvas, x, y, height, side, seed=...)    # grouping bracket
```

Deterministic given a seed, all red ink, all using the same wobble technique. ~200–300 lines of careful tuning. **This module is the moat** — anyone can imitate the cream/serif/marginalia surface, but consistent hand-drawn feel across an entire carousel comes from a tuned primitive library.

### Diagrams — two paths

For `diagram_page` (signature element C):

**Path 1 — Generated image (default for v1)**
```json
{
  "type": "diagram_page",
  "figure_number": 1,
  "caption": "Pod lifecycle when a parent goroutine leaks",
  "image": "assets/figures/fig1-pod-lifecycle.png",
  "overlays": [
    { "type": "circle", "at": [240, 400], "radius": 32 },
    { "type": "arrow", "from_margin": true, "to": [275, 400], "label": "the leak" }
  ]
}
```

The diagram is generated externally (Excalidraw, image-gen model, scanned hand-drawing — author's choice). The engine layers sketch overlays on top. This is the realistic v1 path; the existing image-generation workflow already exists.

**Path 2 — Programmatic (deferred for v2)**

A JSON sub-language for box-and-line diagrams that the sketch primitives render directly. Out of scope for the first build.

### Annotated artifacts — the screenshot slide

`annotated_artifact` is image-first. The engine's job is precise overlay positioning:

```json
{
  "type": "annotated_artifact",
  "image": "assets/screenshots/heap-dump.png",
  "annotations": [
    { "type": "circle", "at": [340, 280], "radius": 40, "label": "1.2M goroutines", "label_side": "right" },
    { "type": "arrow", "from": [200, 100], "to": [180, 240], "label": "this number is the giveaway" }
  ],
  "marginalia": [
    { "text": "took me 3 hours to notice this", "anchor_y": 280, "arrow": false }
  ]
}
```

Labels render in red Caveat (handwriting). Circles/arrows use sketch primitives.

### Authoring effort

Every interior slide now expects:
- 1–2 marginalia notes (where Milind's voice lives)
- For artifact/diagram slides: at least one sketch annotation
- The sketch seed is automatic; authors never think about it

This is the meaningful jump in authoring effort. The mitigation: marginalia is exactly where the existing writing-style voice already lives — short, observational, slightly self-deprecating asides. Not extra invented work; it's the work the current engine has no place for.

## Section 4 — Build Plan & Migration

### Coexistence, not hard cut

Old renderers in `carousel/renderers/` (`title_dark`, `content_cards`, etc.) stay in place during the build. New renderers ship under new type names — no naming collision, no broken state mid-build. Already-published PDFs stay as-is; no retroactive re-rendering.

After 2–3 carousels render successfully in the new system, delete the old renderers in one cleanup commit. Until then they're a working fallback.

### Phase 1 — Foundation (one build session)

Engine plumbing the new slide types depend on. Nothing renders yet, but the chassis is ready.

- Install fonts (IBM Plex Serif, Source Serif Pro, IBM Plex Mono, Caveat) with Linux paths + fallback chain
- New color defaults in `schema.py` — cream paper, charcoal ink, red pen, diagram blue
- New margin defaults — body 432pt, right margin 120pt, left margin 60pt
- `carousel/layout.py` rewrite — dot-grid background, masthead top rule, handwritten signature footer
- **`carousel/sketch.py` — new module.** Hand-drawn arrow, circle, check, cross, underline, bracket. Deterministic seed.

**Tuning gate at end of Phase 1.** Before any renderer is built, render a stub page using `sketch.py` (an arrow, a circle, a check, a cross) and visually confirm the hand-drawn feel lands. If after a session of tuning the primitives still feel either too clean or too noisy, fall back to a pre-rendered SVG arrow library. This is the highest-risk piece of the whole build.

### Phase 2 — Slide types (two to three build sessions)

Build order:

| Order | Renderer | Why this order |
|---|---|---|
| 1 | `cover` | Sets identity at first glance. If the cover doesn't land, nothing else does. |
| 2 | `lab_notes` | The workhorse. Validates marginalia + sketch arrows + numbered observations together. ~80% of the visual system gets stress-tested here. |
| 3 | `colophon` | Bookend. Closes the loop on identity. Now we can render a 3-slide carousel end-to-end. |
| 4 | `annotated_artifact` | First fully image-driven slide. Validates overlay positioning. |
| 5 | `diagram_page` | Same overlay system as artifact, different framing. |
| 6 | `code_listing` | Tests mono typography + margin commentary together. |
| 7 | `comparison_table` | Restyle of existing — easy after the system is in place. |
| 8 | `decision_tree` | Restyle of existing — easy after the system is in place. |

Validation gate after each renderer: render a stub slide and eyeball it before moving to the next.

### Phase 3 — First real carousel (one session)

Pick a recent topic (or the next one queued) and author it in the new system. Visual tuning happens here — the first real content always exposes things stub slides hide. Expect 1–2 rounds of revision on Phase 1 chassis based on what the first carousel reveals.

### Phase 4 — Cleanup (small)

Once 2–3 real carousels look right:
- Delete old renderers (`title_dark`, `content_cards`, `grid_cards`, `flow_diagram`, `decision_framework`, `closing_dark`)
- Update `example_payload.json` to the new system
- Update `CLAUDE.md` with the new architecture
- Update the `carousel-maker` skill so future Claude sessions author in the new system by default

### What we explicitly defer

- **Programmatic diagrams** (Section 3, Path 2) — diagrams stay externally-generated images for v1. Revisit if we discover we want them often.
- **Custom illustration pipeline for covers** — covers use images from the existing image-gen workflow. No new generation tooling.
- **Multi-page spreads** (left page + right page composition) — single-page only.
- **Per-carousel theme overrides** beyond what `style_overrides` already supports — the system is opinionated on purpose.

### Risk register

| Risk | Mitigation |
|---|---|
| `sketch.py` arrows look bad — too clean or too noisy | Tuning gate at end of Phase 1 before any renderer depends on it. Fallback: pre-rendered SVG arrow library. |
| Handwriting font Caveat feels too cute / not credible | Alternative candidates: Kalam, Patrick Hand, Architects Daughter. Pick during Phase 1 tuning. |
| Marginalia authoring becomes a bottleneck | Marginalia is built on existing writing-style voice. Authoring rule (2–3 per slide max) prevents over-investment. |
| First carousel reveals page chrome doesn't work | Phase 3 budget includes 1–2 chassis revisions. |

### Total scope estimate

~4–5 focused sessions to "first carousel published in new system." Phase 1 is the tightest — fonts and `sketch.py` need to land cleanly because everything else builds on them.

## Success criteria

1. A first real carousel is rendered in the new system that visually does not look like other Claude-generated carousels.
2. The five signature elements (numbered observations, annotated artifacts, hand-drawn diagrams, signature cover, voice-in-margin) are all present and feel cohesive across slides.
3. `sketch.py` produces hand-drawn arrows/circles/checks that are reproducible across renders and visually credible.
4. Authoring a new carousel in the new system takes no more than 2× the effort of the current system, with the extra effort going to marginalia (voice work) and one diagram per carousel.
5. Old renderers are deleted and the engine is single-system.

from unittest.mock import MagicMock
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


def _normalize_calls(canvas):
    """Replace MagicMock args with a sentinel so two canvases with
    different fresh path-mock identities compare equal."""
    out = []
    for name, args, kwargs in canvas.method_calls:
        norm_args = tuple(
            "<mock>" if isinstance(a, MagicMock) else a for a in args
        )
        norm_kwargs = tuple(sorted(kwargs.items()))
        out.append((name, norm_args, norm_kwargs))
    return out


def test_arrow_is_deterministic():
    c1, c2 = _record_canvas(), _record_canvas()
    draw_arrow(c1, (50, 100), (200, 100), seed=1, style="sweep")
    draw_arrow(c2, (50, 100), (200, 100), seed=1, style="sweep")
    assert _normalize_calls(c1) == _normalize_calls(c2)


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


from carousel.sketch import draw_circle_around, draw_underline


def test_circle_around_is_deterministic():
    c1, c2 = _record_canvas(), _record_canvas()
    draw_circle_around(c1, 100, 100, radius=20, seed=7)
    draw_circle_around(c2, 100, 100, radius=20, seed=7)
    assert _normalize_calls(c1) == _normalize_calls(c2)


def test_underline_is_deterministic():
    c1, c2 = _record_canvas(), _record_canvas()
    draw_underline(c1, 50, 80, width=120, seed=11)
    draw_underline(c2, 50, 80, width=120, seed=11)
    assert _normalize_calls(c1) == _normalize_calls(c2)


def test_circle_around_calls_path_methods():
    c = _record_canvas()
    draw_circle_around(c, 100, 100, radius=20, seed=7)
    assert c.beginPath.called
    assert c.drawPath.called

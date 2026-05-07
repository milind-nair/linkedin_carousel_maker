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

from carousel.schema import GlobalStyles
from carousel.config import resolve_config


def test_lab_dimensions_default():
    cfg = resolve_config(GlobalStyles())
    assert cfg.body_column_width == 432
    assert cfg.left_gutter == 60
    assert cfg.right_gutter == 120
    # Sum equals page width
    assert cfg.left_gutter + cfg.body_column_width + cfg.right_gutter == cfg.width

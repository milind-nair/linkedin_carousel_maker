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

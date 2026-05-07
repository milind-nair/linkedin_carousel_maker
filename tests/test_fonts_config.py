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

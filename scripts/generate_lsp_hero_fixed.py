from __future__ import annotations

from pathlib import Path
import sys

from PIL import Image, ImageDraw, ImageFont


DARK = "#1A1814"
AMBER = "#D97706"
AMBER_LIGHT = "#FEF3C7"
WHITE = "#FFFDF5"
STONE = "#78716C"
GREEN = "#059669"
BLUE = "#2563EB"
MUTED = "#A8A29E"


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


DARK_RGB = hex_to_rgb(DARK)
AMBER_RGB = hex_to_rgb(AMBER)
AMBER_LIGHT_RGB = hex_to_rgb(AMBER_LIGHT)
WHITE_RGB = hex_to_rgb(WHITE)
STONE_RGB = hex_to_rgb(STONE)
GREEN_RGB = hex_to_rgb(GREEN)
BLUE_RGB = hex_to_rgb(BLUE)
MUTED_RGB = hex_to_rgb(MUTED)


def load_font(path: str, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


FONT_LG = load_font("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
FONT_CODE = load_font("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 20)


def draw_arrowhead(
    draw: ImageDraw.ImageDraw,
    tip: tuple[int, int],
    direction: str,
    color: tuple[int, int, int],
) -> None:
    x, y = tip
    if direction == "down":
        points = [(x, y), (x - 8, y - 16), (x + 8, y - 16)]
    elif direction == "right":
        points = [(x, y), (x - 16, y - 8), (x - 16, y + 8)]
    else:
        raise ValueError(f"Unsupported direction: {direction}")
    draw.polygon(points, fill=color)


def generate(output_path: Path) -> None:
    w, h = 1120, 600
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    token_bounds: dict[str, tuple[int, int, int, int]] = {}

    draw.rounded_rectangle([40, 20, w - 40, h - 20], radius=16, fill=DARK_RGB)
    draw.rectangle([40, 20, w - 40, 70], fill=(30, 28, 24))
    draw.rounded_rectangle([40, 20, w - 40, 50], radius=16, fill=(30, 28, 24))

    for i, color in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        draw.ellipse([70 + i * 36, 30, 94 + i * 36, 54], fill=color)

    lines_data = [
        [
            ("  def ", STONE_RGB, None),
            ("handle_request", AMBER_RGB, None),
            ("(self, req):", STONE_RGB, None),
        ],
        [
            ("      ", STONE_RGB, None),
            ("config", STONE_RGB, "config_decl"),
            (" = ", STONE_RGB, None),
            ("self.config", GREEN_RGB, None),
        ],
        [
            ("      result = ", STONE_RGB, None),
            ("validate", AMBER_RGB, "validate_call"),
            ("(config)", STONE_RGB, None),
        ],
        [
            ("      return ", STONE_RGB, None),
            ("Response", BLUE_RGB, None),
            ("(result)", STONE_RGB, None),
        ],
    ]

    y = 100
    for parts in lines_data:
        x = 90
        for text, color, token_id in parts:
            draw.text((x, y), text, fill=color, font=FONT_CODE)
            bbox = FONT_CODE.getbbox(text)
            width = bbox[2] - bbox[0]
            if token_id:
                token_bounds[token_id] = (x, y + bbox[1], x + width, y + bbox[3])
            x += width
        y += 44

    tooltip = (120, 280, 560, 360)
    definition = (680, 365, w - 80, 460)

    draw.rounded_rectangle(
        tooltip,
        radius=8,
        fill=(45, 42, 38),
        outline=AMBER_RGB,
        width=2,
    )
    draw.text((145, 295), "config: AppConfig", fill=AMBER_LIGHT_RGB, font=FONT_CODE)
    draw.text((145, 325), "LSP: Hover Info", fill=MUTED_RGB, font=FONT_CODE)

    draw.rounded_rectangle(definition, radius=8, outline=AMBER_RGB, width=3)
    draw.text((710, 380), "def validate(cfg):", fill=AMBER_RGB, font=FONT_CODE)
    draw.text((710, 412), "  # LSP: Go to Definition", fill=MUTED_RGB, font=FONT_CODE)

    # Hover arrow: visibly attach the arrow to the config token itself.
    config_left, _, config_right, config_bottom = token_bounds["config_decl"]
    underline_y = config_bottom + 10
    draw.line([config_left, underline_y, config_right, underline_y], fill=AMBER_RGB, width=3)
    config_anchor_x = (config_left + config_right) // 2
    config_route_y = underline_y + 12
    config_gutter_x = config_left - 24
    draw.line([config_anchor_x, underline_y, config_anchor_x, config_route_y], fill=AMBER_RGB, width=3)
    draw.line([config_anchor_x, config_route_y, config_gutter_x, config_route_y], fill=AMBER_RGB, width=3)
    draw.line([config_gutter_x, config_route_y, config_gutter_x, 262], fill=AMBER_RGB, width=3)
    draw_arrowhead(draw, (config_gutter_x, 278), "down", AMBER_RGB)

    # Go-to-definition arrow: visibly attach it to the validate call.
    validate_left, _, validate_right, validate_bottom = token_bounds["validate_call"]
    validate_underline_y = validate_bottom + 10
    draw.line([validate_left, validate_underline_y, validate_right, validate_underline_y], fill=AMBER_RGB, width=3)
    validate_anchor_x = (validate_left + validate_right) // 2
    validate_route_y = validate_underline_y + 16
    draw.line([validate_anchor_x, validate_underline_y, validate_anchor_x, validate_route_y], fill=AMBER_RGB, width=3)
    draw.line([validate_anchor_x, validate_route_y, 760, validate_route_y], fill=AMBER_RGB, width=3)
    draw.line([760, validate_route_y, 760, 346], fill=AMBER_RGB, width=3)
    draw_arrowhead(draw, (760, 362), "down", AMBER_RGB)

    draw.rounded_rectangle([w - 220, h - 90, w - 60, h - 40], radius=20, fill=AMBER_RGB)
    draw.text((w - 196, h - 84), "LSP", fill=DARK_RGB, font=FONT_LG)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path)
    print(f"Created {output_path}")


if __name__ == "__main__":
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("assets/lsp-hero.png")
    generate(output)

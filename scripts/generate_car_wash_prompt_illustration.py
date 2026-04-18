"""Generate a light-background prompt illustration for the car-wash deck.

Transparent PNG with warm line art so it can sit on the cream content slide.
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 760, 260
SCALE = 3
SW, SH = W * SCALE, H * SCALE

BG = (0, 0, 0, 0)
DARK = (68, 43, 27, 255)
ACCENT = (217, 119, 6, 255)
MUTED = (168, 162, 158, 255)
LIGHT = (254, 243, 199, 255)


def _s(value: float) -> int:
    return int(round(value * SCALE))


def _load_font(paths: list[str], size: int) -> ImageFont.ImageFont:
    for path in paths:
        try:
            return ImageFont.truetype(path, _s(size))
        except Exception:
            continue
    return ImageFont.load_default()


def draw_person(draw: ImageDraw.ImageDraw, cx: float, feet_y: float) -> None:
    head_r = 13
    head_cy = feet_y - 84
    body_top = head_cy + head_r + 4
    body_bot = feet_y - 28

    draw.ellipse(
        [_s(cx - head_r), _s(head_cy - head_r), _s(cx + head_r), _s(head_cy + head_r)],
        outline=DARK,
        width=_s(5),
    )
    draw.line([(_s(cx), _s(body_top)), (_s(cx), _s(body_bot))], fill=DARK, width=_s(5))
    draw.line(
        [(_s(cx), _s(body_top + 16)), (_s(cx - 26), _s(body_top + 40))],
        fill=DARK,
        width=_s(5),
    )
    draw.line(
        [(_s(cx), _s(body_top + 16)), (_s(cx + 30), _s(body_top + 36))],
        fill=DARK,
        width=_s(5),
    )
    draw.line([(_s(cx), _s(body_bot)), (_s(cx - 28), _s(feet_y))], fill=DARK, width=_s(5))
    draw.line([(_s(cx), _s(body_bot)), (_s(cx + 24), _s(feet_y - 4))], fill=DARK, width=_s(5))


def draw_car(draw: ImageDraw.ImageDraw, cx: float, ground_y: float) -> None:
    body_w, body_h = 128, 34
    body_x = cx - body_w / 2
    body_y = ground_y - body_h - 12
    cabin_w, cabin_h = 74, 24
    cabin_x = body_x + 28
    cabin_y = body_y - cabin_h + 4
    wheel_r = 12

    draw.rounded_rectangle(
        [_s(body_x), _s(body_y), _s(body_x + body_w), _s(body_y + body_h)],
        radius=_s(10),
        outline=DARK,
        width=_s(5),
    )
    draw.rounded_rectangle(
        [_s(cabin_x), _s(cabin_y), _s(cabin_x + cabin_w), _s(cabin_y + cabin_h)],
        radius=_s(8),
        outline=DARK,
        width=_s(5),
    )
    for wheel_x in (body_x + 25, body_x + body_w - 25):
        draw.ellipse(
            [_s(wheel_x - wheel_r), _s(ground_y - wheel_r), _s(wheel_x + wheel_r), _s(ground_y + wheel_r)],
            outline=DARK,
            width=_s(5),
        )


def draw_car_wash(draw: ImageDraw.ImageDraw, x: float, base_y: float) -> None:
    arch_w, arch_h = 116, 86
    arch_x = x
    arch_y = base_y - arch_h
    roof_y = arch_y + 20

    draw.rounded_rectangle(
        [_s(arch_x), _s(arch_y), _s(arch_x + arch_w), _s(base_y)],
        radius=_s(16),
        outline=ACCENT,
        width=_s(6),
    )
    draw.rectangle(
        [_s(arch_x + 14), _s(base_y - 18), _s(arch_x + arch_w - 14), _s(base_y)],
        fill=LIGHT,
    )
    for offset in (22, 40, 58, 76, 94):
        draw.line(
            [(_s(arch_x + offset), _s(roof_y)), (_s(arch_x + offset), _s(base_y - 12))],
            fill=ACCENT,
            width=_s(3),
        )

    font = _load_font(
        [
            "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ],
        13,
    )
    bbox = draw.textbbox((0, 0), "CAR WASH", font=font)
    text_x = _s(arch_x + arch_w / 2) - (bbox[2] - bbox[0]) // 2
    text_y = _s(arch_y + 9) - bbox[1]
    draw.text((text_x, text_y), "CAR WASH", fill=ACCENT, font=font)


def draw_path(draw: ImageDraw.ImageDraw, start_x: float, end_x: float, y: float) -> None:
    dash, gap = 18, 12
    x = start_x
    while x < end_x:
        draw.line(
            [(_s(x), _s(y)), (_s(min(x + dash, end_x)), _s(y))],
            fill=MUTED,
            width=_s(3),
        )
        x += dash + gap


def draw_question(draw: ImageDraw.ImageDraw, cx: float, cy: float) -> None:
    bubble_w, bubble_h = 104, 104
    draw.rounded_rectangle(
        [_s(cx - bubble_w / 2), _s(cy - bubble_h / 2), _s(cx + bubble_w / 2), _s(cy + bubble_h / 2)],
        radius=_s(28),
        fill=LIGHT,
        outline=ACCENT,
        width=_s(4),
    )
    font = _load_font(
        [
            "/usr/share/fonts/truetype/google-fonts/Lora-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ],
        64,
    )
    bbox = draw.textbbox((0, 0), "?", font=font)
    text_x = _s(cx) - (bbox[2] - bbox[0]) // 2 - bbox[0]
    text_y = _s(cy) - (bbox[3] - bbox[1]) // 2 - bbox[1]
    draw.text((text_x, text_y), "?", fill=ACCENT, font=font)


def draw_label(draw: ImageDraw.ImageDraw, text: str, cx: float, y: float, fill: tuple[int, int, int, int]) -> None:
    font = _load_font(
        [
            "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ],
        15,
    )
    bbox = draw.textbbox((0, 0), text, font=font)
    text_x = _s(cx) - (bbox[2] - bbox[0]) // 2 - bbox[0]
    text_y = _s(y) - bbox[1]
    draw.text((text_x, text_y), text, fill=fill, font=font)


def generate(out_path: Path) -> None:
    img = Image.new("RGBA", (SW, SH), BG)
    draw = ImageDraw.Draw(img)

    ground_y = 188
    car_cx = 522
    wash_x = 624
    draw_path(draw, 90, 690, ground_y)
    draw_person(draw, cx=118, feet_y=ground_y)
    draw_question(draw, cx=360, cy=88)
    draw_car(draw, cx=car_cx, ground_y=ground_y)
    draw_car_wash(draw, x=wash_x, base_y=ground_y - 4)
    draw_label(draw, "walk?", cx=118, y=214, fill=DARK)
    draw_label(draw, "50 m", cx=360, y=210, fill=MUTED)
    draw_label(draw, "drive?", cx=car_cx, y=214, fill=DARK)

    final = img.resize((W, H), Image.LANCZOS)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    final.save(out_path, "PNG")
    print(f"Wrote {out_path} ({W}x{H})")


if __name__ == "__main__":
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("assets/car-wash/prompt-illustration.png")
    generate(output)

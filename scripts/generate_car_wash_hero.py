"""Generate the hero illustration for the car-wash carousel title slide.

Minimalist line art: walking figure on the left, car on the right,
large question mark between them. Renders at 3x scale and downsamples
for crisp edges. Output is transparent-background PNG.
"""
from __future__ import annotations
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 600, 320
SCALE = 3
SW, SH = W * SCALE, H * SCALE

CREAM = (245, 245, 244, 255)
ACCENT = (245, 158, 11, 255)
MUTED = (168, 162, 158, 180)
DOT = (26, 24, 20, 255)


def _s(v: float) -> int:
    return int(round(v * SCALE))


def _load_font(paths: list[str], size: int) -> ImageFont.ImageFont:
    for p in paths:
        try:
            return ImageFont.truetype(p, _s(size))
        except Exception:
            continue
    return ImageFont.load_default()


def draw_person(draw: ImageDraw.ImageDraw, cx: float, feet_y: float) -> None:
    """Walking stick figure, centered horizontally at cx, feet planted at feet_y."""
    head_r = 14
    head_cy = feet_y - 115
    body_top = head_cy + head_r + 2
    body_bot = feet_y - 40

    draw.ellipse(
        [_s(cx - head_r), _s(head_cy - head_r),
         _s(cx + head_r), _s(head_cy + head_r)],
        outline=CREAM, width=_s(4),
    )
    draw.line([(_s(cx), _s(body_top)), (_s(cx), _s(body_bot))],
              fill=CREAM, width=_s(4))
    arm_y = body_top + 18
    draw.line([(_s(cx), _s(arm_y)), (_s(cx + 22), _s(arm_y + 28))],
              fill=CREAM, width=_s(4))
    draw.line([(_s(cx), _s(arm_y)), (_s(cx - 20), _s(arm_y + 22))],
              fill=CREAM, width=_s(4))
    draw.line([(_s(cx), _s(body_bot)), (_s(cx + 20), _s(feet_y))],
              fill=CREAM, width=_s(4))
    draw.line([(_s(cx), _s(body_bot)), (_s(cx - 22), _s(feet_y - 2))],
              fill=CREAM, width=_s(4))


def draw_car(draw: ImageDraw.ImageDraw, cx: float, ground_y: float) -> None:
    """Simple side-view car centered at cx, sitting on ground_y."""
    body_w, body_h = 130, 32
    body_x = cx - body_w / 2
    body_y = ground_y - body_h - 10

    draw.rounded_rectangle(
        [_s(body_x), _s(body_y),
         _s(body_x + body_w), _s(body_y + body_h)],
        radius=_s(8), outline=CREAM, width=_s(4),
    )
    cabin_w = body_w - 50
    cabin_h = 20
    cabin_x = body_x + 25
    cabin_y = body_y - cabin_h + 2
    draw.rounded_rectangle(
        [_s(cabin_x), _s(cabin_y),
         _s(cabin_x + cabin_w), _s(cabin_y + cabin_h)],
        radius=_s(6), outline=CREAM, width=_s(4),
    )
    wheel_r = 11
    wheel_cy = ground_y - wheel_r + 2
    for wx in (body_x + 24, body_x + body_w - 24):
        draw.ellipse(
            [_s(wx - wheel_r), _s(wheel_cy - wheel_r),
             _s(wx + wheel_r), _s(wheel_cy + wheel_r)],
            fill=DOT, outline=CREAM, width=_s(4),
        )


def draw_question_mark(draw: ImageDraw.ImageDraw, cx: float, cy: float) -> None:
    """Large bold question mark centered at (cx, cy)."""
    font = _load_font(
        [
            "/usr/share/fonts/truetype/google-fonts/Lora-Bold.ttf",
            "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ],
        size=180,
    )
    bbox = draw.textbbox((0, 0), "?", font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text(
        (_s(cx) - tw // 2 - bbox[0], _s(cy) - th // 2 - bbox[1]),
        "?", font=font, fill=ACCENT,
    )


def draw_ground(draw: ImageDraw.ImageDraw, y: float,
                x_start: float, x_end: float) -> None:
    dash, gap = 10, 7
    x = x_start
    while x < x_end:
        draw.line(
            [(_s(x), _s(y)), (_s(min(x + dash, x_end)), _s(y))],
            fill=MUTED, width=_s(2),
        )
        x += dash + gap


def draw_label(draw: ImageDraw.ImageDraw, text: str, cx: float, cy: float) -> None:
    font = _load_font(
        [
            "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ],
        size=16,
    )
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text(
        (_s(cx) - tw // 2 - bbox[0], _s(cy) - th // 2 - bbox[1]),
        text, font=font, fill=CREAM,
    )


def generate(out_path: Path) -> None:
    img = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    ground_y = 260
    draw_ground(draw, ground_y, 70, 530)
    draw_question_mark(draw, cx=W / 2, cy=130)
    draw_person(draw, cx=135, feet_y=ground_y)
    draw_car(draw, cx=465, ground_y=ground_y)
    draw_label(draw, "50 m", cx=W / 2, cy=ground_y + 22)

    final = img.resize((W, H), Image.LANCZOS)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    final.save(out_path, "PNG")
    print(f"Wrote {out_path} ({W}x{H})")


if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
        "assets/car-wash/hero.png")
    generate(out)

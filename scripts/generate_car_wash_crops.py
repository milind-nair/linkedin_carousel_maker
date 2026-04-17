"""Crop raw car-wash screenshots into panels for carousel use.

Crops tight to the prompt + answer, then scales each to a uniform 900px
width. Heights vary based on content length. Output goes to
assets/car-wash/cropped/. Slides then size each image slot to match
the natural aspect ratio of that screenshot.
"""
from __future__ import annotations
from pathlib import Path
from PIL import Image

SRC_DIR = Path(__file__).resolve().parents[1] / "assets" / "car-wash"
OUT_DIR = SRC_DIR / "cropped"

TARGET_W = 900

CROPS = {
    "chatgpt.png": ("Screenshot 2026-04-17 215146.png", (380, 35, 1300, 660)),
    "claude-sonnet.png": ("Screenshot 2026-04-17 215256.png", (50, 25, 665, 175)),
    "claude-opus.png": ("Screenshot 2026-04-17 215339.png", (40, 15, 655, 215)),
    "grok.png": ("Screenshot 2026-04-17 215433.png", (105, 55, 935, 602)),
    "gemini.png": ("Screenshot 2026-04-17 215504.png", (115, 80, 810, 325)),
}


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print("Crops (for slide image_height calculations):")
    for out_name, (src_name, box) in CROPS.items():
        src_path = SRC_DIR / src_name
        img = Image.open(src_path).convert("RGB")
        cropped = img.crop(box)
        w, h = cropped.size
        new_h = int(round(h * TARGET_W / w))
        final = cropped.resize((TARGET_W, new_h), Image.LANCZOS)
        out_path = OUT_DIR / out_name
        final.save(out_path, "PNG")
        aspect = TARGET_W / new_h
        print(f"  {out_name}: {TARGET_W}x{new_h}  aspect={aspect:.2f}")


if __name__ == "__main__":
    main()

"""Generate images for the Claude Mythos carousel.

Renders at 3x scale and downsamples with LANCZOS for crisp edges.

Usage:
    python scripts/generate_mythos_images.py
"""

from __future__ import annotations
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT = Path("assets/claude-mythos")
OUT.mkdir(parents=True, exist_ok=True)

W, H = 580, 440
SCALE = 3
SW, SH = W * SCALE, H * SCALE

RED = (220, 38, 38)
RED_LIGHT = (254, 242, 242)
RED_MID = (180, 30, 30)
RED_DESC = (140, 100, 100)
GREEN = (5, 150, 105)
GREEN_DARK = (4, 120, 84)
GREEN_BG = (245, 253, 250)
GREEN_PILL_BG = (236, 253, 245)
GREEN_DESC = (80, 140, 120)
PURPLE = (124, 58, 237)
PURPLE_LIGHT = (240, 237, 255)
PURPLE_BG = (250, 248, 255)
PURPLE_BORDER = (220, 215, 240)
PURPLE_TEXT = (80, 60, 130)
WHITE = (255, 255, 255)


def s(val: float) -> int:
    return int(round(val * SCALE))


def load_fonts():
    sizes = {}
    base = "/usr/share/fonts/truetype/dejavu"
    for name, file, pts in [
        ("sm", "DejaVuSans.ttf", 11),
        ("md", "DejaVuSans.ttf", 13),
        ("xs", "DejaVuSans.ttf", 10),
        ("bold_sm", "DejaVuSans-Bold.ttf", 11),
        ("bold", "DejaVuSans-Bold.ttf", 13),
        ("bold_lg", "DejaVuSans-Bold.ttf", 16),
    ]:
        try:
            sizes[name] = ImageFont.truetype(f"{base}/{file}", s(pts))
        except OSError:
            sizes[name] = ImageFont.load_default()
    return sizes


fonts = load_fonts()


def finish(img: Image.Image, name: str):
    out = img.resize((W, H), Image.LANCZOS)
    out.save(OUT / name)
    print(f"  {name}")


def rrect(draw, box, radius, **kw):
    draw.rounded_rectangle(box, radius=s(radius), **kw)


# ─────────────────────────────────────────────
# 1. exploit-chain.png
# ─────────────────────────────────────────────
def gen_exploit_chain():
    img = Image.new("RGB", (SW, SH), RED_LIGHT)
    draw = ImageDraw.Draw(img)

    stages = [
        ("JIT Heap Spray", "Trigger JIT, spray controlled objects"),
        ("Renderer Escape", "Corrupt vtable via use-after-free"),
        ("OS Sandbox Bypass", "Shared-memory mmap to escape sandbox"),
        ("Privilege Escalation", "Race condition + KASLR bypass"),
    ]

    box_w = s(320)
    box_h = s(56)
    start_x = (SW - box_w) // 2
    start_y = s(38)
    gap = s(30)
    accent_w = s(5)
    circle_r = s(14)

    for i, (title, desc) in enumerate(stages):
        y = start_y + i * (box_h + gap)
        x = start_x

        # Card
        rrect(draw, [x, y, x + box_w, y + box_h], radius=8,
              fill=WHITE, outline=(235, 220, 220), width=s(1))
        # Left accent
        draw.rectangle([x + s(2), y + s(8), x + s(2) + accent_w, y + box_h - s(8)], fill=RED)

        # Step number
        cn_x = x + s(30)
        cn_y = y + box_h // 2
        draw.ellipse([cn_x - circle_r, cn_y - circle_r, cn_x + circle_r, cn_y + circle_r], fill=RED)
        draw.text((cn_x, cn_y), str(i + 1), fill=WHITE, font=fonts["bold"], anchor="mm")

        # Title + desc
        draw.text((x + s(52), y + s(16)), title, fill=RED_MID, font=fonts["bold"], anchor="lm")
        draw.text((x + s(52), y + s(38)), desc, fill=RED_DESC, font=fonts["sm"], anchor="lm")

        # Arrow
        if i < len(stages) - 1:
            ax = SW // 2
            ay1 = y + box_h + s(3)
            ay2 = y + box_h + gap - s(3)
            draw.line([(ax, ay1), (ax, ay2)], fill=RED, width=s(2))
            tri_h = s(6)
            tri_w = s(5)
            draw.polygon([
                (ax, ay2),
                (ax - tri_w, ay2 - tri_h),
                (ax + tri_w, ay2 - tri_h),
            ], fill=RED)

    # Badge
    badge_y = start_y + len(stages) * (box_h + gap) - gap + s(14)
    bw = s(88)
    bh = s(14)
    bcx = SW // 2
    rrect(draw, [bcx - bw, badge_y, bcx + bw, badge_y + s(28)], radius=14, fill=RED)
    draw.text((bcx, badge_y + s(14)), "FULL CHAIN ACHIEVED", fill=WHITE, font=fonts["bold_sm"], anchor="mm")

    finish(img, "exploit-chain.png")


# ─────────────────────────────────────────────
# 2. glasswing.png
# ─────────────────────────────────────────────
def gen_glasswing():
    img = Image.new("RGB", (SW, SH), GREEN_BG)
    draw = ImageDraw.Draw(img)

    cx, cy = SW // 2, s(195)
    hub_r = s(38)

    # Partners with explicit positions (no overlaps)
    partners = [
        ("Apple",       cx,        cy - s(125), True),
        ("AWS",         cx - s(170), cy - s(65),  True),
        ("Microsoft",   cx + s(170), cy - s(65),  True),
        ("Google",      cx + s(165), cy + s(65),  True),
        ("CrowdStrike", cx - s(165), cy + s(65),  True),
        ("Palo Alto",   cx,        cy + s(125), True),
        ("NVIDIA",      cx - s(95),  cy - s(125), False),
        ("JPMorgan",    cx + s(95),  cy - s(125), False),
        ("Cisco",       cx + s(230), cy,         False),
        ("Broadcom",    cx + s(95),  cy + s(125), False),
        ("Linux Fdn",   cx - s(95),  cy + s(125), False),
    ]

    # Draw lines first (stop at hub edge, not center)
    for name, px, py, primary in partners:
        dx = px - cx
        dy = py - cy
        dist = math.sqrt(dx * dx + dy * dy)
        if dist == 0:
            continue
        # Start line at hub edge
        edge_x = cx + hub_r * dx / dist
        edge_y = cy + hub_r * dy / dist
        lw = s(2) if primary else s(1)
        col = GREEN if primary else (150, 210, 190)
        draw.line([(edge_x, edge_y), (px, py)], fill=col, width=lw)

    # Hub on top of lines
    draw.ellipse([cx - hub_r, cy - hub_r, cx + hub_r, cy + hub_r],
                 fill=GREEN, outline=GREEN_DARK, width=s(2))
    draw.text((cx, cy - s(7)), "Anthropic", fill=WHITE, font=fonts["bold_sm"], anchor="mm")
    draw.text((cx, cy + s(8)), "Mythos", fill=(220, 255, 240), font=fonts["xs"], anchor="mm")

    # Partner nodes on top of lines
    for name, px, py, primary in partners:
        f = fonts["bold"] if primary else fonts["sm"]
        tw = f.getlength(name)
        pad_x = s(14)
        pad_y = s(11)
        bx1 = px - tw / 2 - pad_x
        by1 = py - pad_y
        bx2 = px + tw / 2 + pad_x
        by2 = py + pad_y

        if primary:
            rrect(draw, [bx1, by1, bx2, by2], radius=10,
                  fill=WHITE, outline=GREEN, width=s(2))
            draw.text((px, py), name, fill=GREEN_DARK, font=fonts["bold"], anchor="mm")
        else:
            rrect(draw, [bx1, by1, bx2, by2], radius=8,
                  fill=GREEN_PILL_BG, outline=GREEN, width=s(1))
            draw.text((px, py), name, fill=GREEN_DARK, font=fonts["sm"], anchor="mm")

    # Bottom badge
    badge_cx = SW // 2
    badge_y = s(368)
    bw = s(56)
    rrect(draw, [badge_cx - bw, badge_y, badge_cx + bw, badge_y + s(26)], radius=13, fill=GREEN)
    draw.text((badge_cx, badge_y + s(13)), "+40 more orgs", fill=WHITE, font=fonts["bold_sm"], anchor="mm")
    draw.text((badge_cx, s(414)), "$100M in compute credits committed", fill=GREEN_DESC, font=fonts["sm"], anchor="mm")

    finish(img, "glasswing.png")


# ─────────────────────────────────────────────
# 3. crossroads.png
# ─────────────────────────────────────────────
def gen_crossroads():
    img = Image.new("RGB", (SW, SH), PURPLE_BG)
    draw = ImageDraw.Draw(img)

    lanes = [
        {"title": "Open Source", "icon": "</>",
         "items": ["Patch volume spike", "Auto disclosures", "Dependency audits"]},
        {"title": "Security Teams", "icon": "SEC",
         "items": ["CVE triage wave", "New threat models", "AI-assisted response"]},
        {"title": "AI Builders", "icon": "AI",
         "items": ["Dual-use rules", "Capability evals", "Access controls"]},
    ]

    lane_w = s(172)
    lane_h = s(395)
    lane_gap = s(12)
    total_w = 3 * lane_w + 2 * lane_gap
    sx = (SW - total_w) // 2
    sy = s(22)

    icon_r = s(20)
    num_r = s(11)

    for i, lane in enumerate(lanes):
        lx = sx + i * (lane_w + lane_gap)

        # Lane card
        rrect(draw, [lx, sy, lx + lane_w, sy + lane_h], radius=12,
              fill=WHITE, outline=PURPLE_BORDER, width=s(1))

        # Top accent
        rrect(draw, [lx, sy, lx + lane_w, sy + s(6)], radius=12, fill=PURPLE)
        draw.rectangle([lx, sy + s(3), lx + lane_w, sy + s(6)], fill=PURPLE)

        # Icon circle
        icon_cx = lx + lane_w // 2
        icon_cy = sy + s(42)
        draw.ellipse([icon_cx - icon_r, icon_cy - icon_r, icon_cx + icon_r, icon_cy + icon_r], fill=PURPLE)
        draw.text((icon_cx, icon_cy), lane["icon"], fill=WHITE, font=fonts["bold_sm"], anchor="mm")

        # Title
        draw.text((lx + lane_w // 2, sy + s(74)), lane["title"], fill=PURPLE, font=fonts["bold"], anchor="mm")

        # Divider
        draw.line([(lx + s(15), sy + s(92)), (lx + lane_w - s(15), sy + s(92))],
                  fill=PURPLE_BORDER, width=s(1))

        # Items
        item_h = s(48)
        item_gap = s(20)
        item_start = sy + s(110)
        inner_pad = s(10)

        for j, text in enumerate(lane["items"]):
            iy = item_start + j * (item_h + item_gap)
            ix1 = lx + inner_pad
            ix2 = lx + lane_w - inner_pad

            rrect(draw, [ix1, iy, ix2, iy + item_h], radius=8,
                  fill=PURPLE_LIGHT, outline=PURPLE_BORDER, width=s(1))

            # Number circle
            nc_x = ix1 + s(16)
            nc_y = iy + item_h // 2
            draw.ellipse([nc_x - num_r, nc_y - num_r, nc_x + num_r, nc_y + num_r], fill=PURPLE)
            draw.text((nc_x, nc_y), str(j + 1), fill=WHITE, font=fonts["sm"], anchor="mm")

            # Text — measure and verify it fits
            text_x = nc_x + s(18)
            avail = ix2 - text_x - s(4)
            tw = fonts["sm"].getlength(text)
            f = fonts["sm"] if tw <= avail else fonts["xs"]
            draw.text((text_x, nc_y), text, fill=PURPLE_TEXT, font=f, anchor="lm")

            # Connector dot
            if j < len(lane["items"]) - 1:
                dot_y = iy + item_h + item_gap // 2
                dot_cx = lx + lane_w // 2
                draw.ellipse([dot_cx - s(2), dot_y - s(2), dot_cx + s(2), dot_y + s(2)], fill=PURPLE)

    finish(img, "crossroads.png")


if __name__ == "__main__":
    print("Generating Claude Mythos images (3x LANCZOS)...")
    gen_exploit_chain()
    gen_glasswing()
    gen_crossroads()
    print("Done.")

"""Generate the social/link-preview (Open Graph) image -> app/static/og.png.

A premium 1200x630 "hero" card in the style of a marketing banner: an
atmospheric, code-drawn city skyline (bokeh window lights, hazy depth) under a
deep-navy colour wash, with the PIPTHEORY logo, a pill badge, a bold two-tone
headline, the five methodology pillars as chips, and the URL.

    ./.venv/Scripts/python.exe -m scripts.make_og_image

Deterministic, pure-code, no network, no external images (no licensing risk).
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageEnhance

ROOT = Path(__file__).resolve().parent.parent
STATIC = ROOT / "app" / "static"
OUT = STATIC / "og.png"

W, H = 1200, 630
NAVY_TOP = (10, 22, 46)
NAVY_BOT = (6, 15, 35)
WASH     = (5, 12, 30)
ACCENT   = (27, 175, 208)     # brand cyan
ACCENT_HI= (96, 212, 240)
WHITE    = (243, 247, 252)
SUB      = (198, 212, 230)
DIM      = (150, 168, 196)
B_BACK   = (17, 36, 66)       # far buildings (hazy)
B_FRONT  = (8, 20, 42)        # near buildings
WIN_COOL = (130, 195, 222)
WIN_WARM = (228, 198, 150)

PILLARS = ["Interest Rates", "Growth", "Positioning", "Risk", "Commodities"]


def font(names, size):
    for n in names:
        try:
            return ImageFont.truetype(f"C:/Windows/Fonts/{n}", size)
        except Exception:
            continue
    return ImageFont.load_default()

F_H   = font(["seguibl.ttf", "segoeuib.ttf", "arialbd.ttf"], 74)
F_EB  = font(["seguisb.ttf", "segoeuib.ttf", "arialbd.ttf"], 19)
F_SUB = font(["segoeui.ttf", "arial.ttf"], 25)
F_CHIP= font(["seguisb.ttf", "segoeuib.ttf", "arialbd.ttf"], 20)
F_URL = font(["seguisb.ttf", "segoeuib.ttf", "arialbd.ttf"], 28)


def spaced(draw, xy, text, fnt, fill, tracking=0):
    """Letter-spaced text; xy is the LEFT-MIDDLE anchor (vertically centered)."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill, anchor="lm")
        x += draw.textlength(ch, font=fnt) + tracking


def spaced_w(draw, text, fnt, tracking=0):
    return sum(draw.textlength(c, font=fnt) + tracking for c in text) - tracking


def build():
    # 1) photographic background (Pexels, free license) — cover-fit + darken
    src = ROOT / "assets" / "og-bg.jpg"
    photo = ImageOps.fit(Image.open(src).convert("RGB"), (W, H),
                         method=Image.LANCZOS, centering=(0.5, 0.45))
    photo = ImageEnhance.Brightness(photo).enhance(0.82)
    img = photo.convert("RGBA")

    # 2) navy duotone wash over the whole photo (the "dark overlay")
    img.alpha_composite(Image.new("RGBA", (W, H), (8, 17, 38, 155)))

    # 3) cyan brand glow, lower-right
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([770, 220, 1330, 720], fill=(*ACCENT, 52))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(160)))

    # 6) left wash for text legibility + bottom darken
    xf = np.linspace(0, 1, W)
    la = (np.clip((0.62 - xf) / 0.62, 0, 1) * 215).astype("uint8")
    ov = np.zeros((H, W, 4), "uint8")
    ov[..., 0], ov[..., 1], ov[..., 2] = WASH
    ov[..., 3] = np.repeat(la[None, :], H, axis=0)
    img.alpha_composite(Image.fromarray(ov, "RGBA"))
    yf = np.linspace(0, 1, H)
    ba = (np.clip((yf - 0.74) / 0.26, 0, 1) * 150).astype("uint8")
    ov2 = np.zeros((H, W, 4), "uint8")
    ov2[..., 0], ov2[..., 1], ov2[..., 2] = (4, 10, 26)
    ov2[..., 3] = np.repeat(ba[:, None], W, axis=1)
    img.alpha_composite(Image.fromarray(ov2, "RGBA"))

    d = ImageDraw.Draw(img)
    M = 72                                   # single left/right margin for everything

    # 7) logo — crop transparent padding so its visible left edge sits exactly at M
    logo = Image.open(STATIC / "logo-text-light.png").convert("RGBA")
    logo = logo.crop(logo.getbbox())
    logo = logo.resize((round(logo.width * 44 / logo.height), 44), Image.LANCZOS)
    img.alpha_composite(logo, (M, 64))

    # 8) two-tone headline — the hero (moves up now the badge is gone)
    hy, lh = 176, 80
    d.text((M, hy), "Macro Currency", font=F_H, fill=(*WHITE, 255))
    d.text((M, hy + lh), "Strength Meter", font=F_H, fill=(*ACCENT_HI, 255))

    # 9) subline (3 lines, even leading; no cadence claim)
    sub = ["A free, systematic score that ranks the eight",
           "major currencies by the macro forces",
           "that actually move them."]
    for i, line in enumerate(sub):
        d.text((M, 360 + i * 32), line, font=F_SUB, fill=(*SUB, 255))

    # 11) bottom row: pillar chips (left) + URL (right), all on one centered baseline
    row_top, chh = 512, 44
    mid = row_top + chh // 2
    cx = M
    for label in PILLARS:
        cw = d.textlength(label, font=F_CHIP) + 36
        d.rounded_rectangle([cx, row_top, cx + cw, row_top + chh], radius=chh // 2,
                            outline=(255, 255, 255, 74), width=2)
        d.text((cx + 18, mid), label, font=F_CHIP, fill=(*WHITE, 240), anchor="lm")
        cx += cw + 14
    d.text((W - M, mid), "piptheory.com", font=F_URL, fill=(*ACCENT_HI, 255), anchor="rm")

    img.convert("RGB").save(OUT, "PNG")
    print(f"wrote {OUT}  ({OUT.stat().st_size // 1024} KB, {W}x{H})")


if __name__ == "__main__":
    build()

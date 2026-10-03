"""Draw the home-screen icons into site/ (run: python3 tools/make_icons.py).

iOS composites any transparency onto black and applies its own rounded mask, so the icon is
an opaque, square, un-rounded PNG. The motif foregrounds the arts rather than scheduling (a
plain calendar page reads as the magazine's production calendar): four paper tiles — music,
film, theatre, art — on a charcoal ground, in the page's own palette. The 2x2 grid still hints
at calendar days. Drawn at 1024px and downsampled to 180 (apple-touch-icon) and 192/512
(web-app manifest).
"""

from pathlib import Path

from PIL import Image, ImageChops, ImageDraw

INK = (42, 39, 34)        # #2a2722 — page headings
PAPER = (246, 244, 238)   # #f6f4ee — the sheet
SLATE = (58, 90, 102)     # #3a5a66 — links / active buttons
OCHRE = (154, 124, 68)    # #9a7c44 — category labels
RUST = (138, 90, 43)      # #8a5a2b — freshness note

OUT = Path(__file__).resolve().parents[1] / "site"
S = 1024
BICUBIC = Image.Resampling.BICUBIC


def layer(s: int):
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    return im, ImageDraw.Draw(im)


def rot_ellipse(dst: Image.Image, cx: float, cy: float, w: float, h: float, angle: float, color):
    side = int(max(w, h) * 1.6)
    im, d = layer(side)
    d.ellipse(((side - w) / 2, (side - h) / 2, (side + w) / 2, (side + h) / 2), fill=color)
    dst.alpha_composite(im.rotate(angle, resample=BICUBIC), (int(cx - side / 2), int(cy - side / 2)))


def music(s: int) -> Image.Image:
    """Two beamed eighth notes."""
    im, d = layer(s)
    hw, hh, sw = 0.25 * s, 0.18 * s, 0.055 * s
    notes = [(0.31 * s, 0.71 * s, 0.25 * s), (0.66 * s, 0.63 * s, 0.17 * s)]  # head cx, cy, stem top
    xs = []
    for cx, cy, top in notes:
        rot_ellipse(im, cx, cy, hw, hh, 22, SLATE)
        x = cx + 0.095 * s
        d.rectangle((x, top, x + sw, cy - 0.01 * s), fill=SLATE)
        xs.append((x, top))
    (x1, t1), (x2, t2) = xs
    beam = 0.11 * s
    d.polygon([(x1, t1), (x2 + sw, t2), (x2 + sw, t2 + beam), (x1, t1 + beam)], fill=SLATE)
    return im


def striped_bar(s: int, box, radius: float) -> Image.Image:
    bar, bd = layer(s)
    bd.rounded_rectangle(box, radius=radius, fill=INK)
    mask = Image.new("L", (s, s), 0)
    ImageDraw.Draw(mask).rounded_rectangle(box, radius=radius, fill=255)
    stripes, sd = layer(s)
    x0, y0, x1, y1 = box
    h, period = y1 - y0, (x1 - x0) / 4.4
    x = x0 - h
    while x < x1 + h:
        sd.polygon([(x + h, y0), (x + h + period / 2, y0), (x + period / 2, y1), (x, y1)], fill=PAPER)
        x += period
    stripes.putalpha(ImageChops.multiply(stripes.getchannel("A"), mask))
    bar.alpha_composite(stripes)
    return bar


def film(s: int) -> Image.Image:
    """A clapperboard, its arm swung open."""
    im, d = layer(s)
    x0, x1 = 0.17 * s, 0.83 * s
    d.rounded_rectangle((x0, 0.45 * s, x1, 0.81 * s), radius=0.05 * s, fill=INK)
    im.alpha_composite(striped_bar(s, (x0, 0.45 * s, x1, 0.57 * s), 0.02 * s))
    arm = striped_bar(s, (x0, 0.29 * s, x1, 0.40 * s), 0.02 * s)
    im.alpha_composite(arm.rotate(16, resample=BICUBIC, center=(x0, 0.40 * s)))
    return im


def mask_face(s: int, color, comedy: bool) -> Image.Image:
    im, d = layer(s)
    w, h = 0.56 * s, 0.68 * s
    x0, y0 = (s - w) / 2, (s - h) / 2
    pad = 0.035 * s  # paper keyline so the front mask separates from the one behind it
    d.ellipse((x0 - pad, y0 - pad, x0 + w + pad, y0 + h + pad), fill=PAPER)
    d.ellipse((x0, y0, x0 + w, y0 + h), fill=color)
    ew, eh, ey = 0.17 * w, 0.11 * h, y0 + 0.30 * h
    for side, ex in ((-1, x0 + 0.20 * w), (1, x0 + 0.80 * w - ew)):
        if comedy:
            d.chord((ex, ey, ex + ew, ey + 2 * eh), 180, 360, fill=PAPER)        # ∩ laughing eyes
        else:  # almond eyes tilted so the outer corners droop
            rot_ellipse(im, ex + ew / 2, ey + eh, ew * 1.15, eh * 0.95, -22 * side, PAPER)
    mw, mh = 0.52 * w, 0.34 * h
    mx = x0 + (w - mw) / 2
    if comedy:
        d.chord((mx, y0 + 0.50 * h, mx + mw, y0 + 0.50 * h + mh), 0, 180, fill=PAPER)   # grin
    else:
        d.chord((mx, y0 + 0.66 * h, mx + mw, y0 + 0.66 * h + mh), 180, 360, fill=PAPER)  # frown
    return im


def theatre(s: int) -> Image.Image:
    """Comedy and tragedy masks."""
    im, _ = layer(s)
    k = int(s * 0.72)  # overlap only at the cheeks, so both faces stay readable at icon size
    back = mask_face(s, SLATE, comedy=False).rotate(14, resample=BICUBIC).resize((k, k), Image.LANCZOS)
    front = mask_face(s, OCHRE, comedy=True).rotate(-12, resample=BICUBIC).resize((k, k), Image.LANCZOS)
    im.alpha_composite(back, (int(-0.02 * s), int(0.02 * s)))
    im.alpha_composite(front, (int(0.30 * s), int(0.26 * s)))
    return im


def art(s: int) -> Image.Image:
    """A framed landscape."""
    im, d = layer(s)
    d.rounded_rectangle((0.15 * s, 0.21 * s, 0.85 * s, 0.79 * s), radius=0.035 * s, fill=RUST)
    ix0, iy0, ix1, iy1 = 0.245 * s, 0.30 * s, 0.755 * s, 0.70 * s
    d.rectangle((ix0, iy0, ix1, iy1), fill=PAPER)
    d.ellipse((0.57 * s, 0.35 * s, 0.68 * s, 0.46 * s), fill=OCHRE)
    d.polygon([(ix0, iy1), (0.40 * s, 0.44 * s), (0.56 * s, iy1)], fill=SLATE)
    d.polygon([(0.44 * s, iy1), (0.62 * s, 0.52 * s), (ix1, iy1)], fill=INK)
    return im


def draw() -> Image.Image:
    img = Image.new("RGBA", (S, S), INK + (255,))
    d = ImageDraw.Draw(img)
    tile, gap = 372, 40                      # 2x2 grid sits inside iOS's squircle safe area
    m = (S - (2 * tile + gap)) // 2
    glyphs = [music, film, theatre, art]
    for i, glyph in enumerate(glyphs):
        x = m + (i % 2) * (tile + gap)
        y = m + (i // 2) * (tile + gap)
        d.rounded_rectangle((x, y, x + tile, y + tile), radius=44, fill=PAPER)
        img.alpha_composite(glyph(tile), (x, y))
    return img.convert("RGB")


def main() -> None:
    OUT.mkdir(exist_ok=True)
    master = draw()
    for name, size in (("apple-touch-icon.png", 180), ("icon-192.png", 192), ("icon-512.png", 512)):
        master.resize((size, size), Image.LANCZOS).save(OUT / name, optimize=True)
        print("wrote", OUT / name)


if __name__ == "__main__":
    main()

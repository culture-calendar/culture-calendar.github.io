"""Draw the home-screen icons into site/ (run: python3 tools/make_icons.py).

iOS composites any transparency onto black and applies its own rounded mask, so the icon is
an opaque, square, un-rounded PNG. The motif — a paper calendar leaf with the page's slate
header band, binding rings, and one day picked out in ochre — is drawn at 1024px and
downsampled, then saved at 180 (apple-touch-icon) and 192/512 (web-app manifest).
"""

from pathlib import Path

from PIL import Image, ImageDraw

INK = (42, 39, 34)        # #2a2722 — page headings
PAPER = (246, 244, 238)   # #f6f4ee — the sheet
SLATE = (58, 90, 102)     # #3a5a66 — links / active buttons
OCHRE = (154, 124, 68)    # #9a7c44 — category labels
DAY = (207, 200, 182)     # #cfc8b6 — rules / borders

OUT = Path(__file__).resolve().parents[1] / "site"
S = 1024


def draw() -> Image.Image:
    img = Image.new("RGB", (S, S), INK)
    d = ImageDraw.Draw(img)
    # The leaf sits inside iOS's squircle safe area (~19% margin clears the corner mask).
    x0, y0, x1, y1 = 196, 250, 828, 832
    d.rounded_rectangle((x0, y0, x1, y1), radius=56, fill=PAPER)
    # Slate header band (square bottom edge: overdraw the lower radius).
    band = y0 + 150
    d.rounded_rectangle((x0, y0, x1, band), radius=56, fill=SLATE)
    d.rectangle((x0, band - 60, x1, band), fill=SLATE)
    # Binding rings: paper pegs rising above the leaf, with an ink notch where they pierce it.
    for cx in (372, 652):
        d.rounded_rectangle((cx - 30, y0 - 78, cx + 30, y0 + 74), radius=30, fill=PAPER)
        d.rounded_rectangle((cx - 12, y0 + 16, cx + 12, y0 + 58), radius=12, fill=INK)
    # Day grid: 4 x 3, one day lifted out in ochre.
    cols, rows, cell, gap = 4, 3, 96, 38
    gx0 = (x0 + x1 - (cols * cell + (cols - 1) * gap)) // 2
    gy0 = band + 58
    for r in range(rows):
        for c in range(cols):
            x = gx0 + c * (cell + gap)
            y = gy0 + r * (cell + gap)
            fill = OCHRE if (r, c) == (1, 2) else DAY
            d.rounded_rectangle((x, y, x + cell, y + cell), radius=18, fill=fill)
    return img


def main() -> None:
    OUT.mkdir(exist_ok=True)
    master = draw()
    for name, size in (("apple-touch-icon.png", 180), ("icon-192.png", 192), ("icon-512.png", 512)):
        master.resize((size, size), Image.LANCZOS).save(OUT / name, optimize=True)
        print("wrote", OUT / name)


if __name__ == "__main__":
    main()

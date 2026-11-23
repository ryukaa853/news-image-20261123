#!/usr/bin/env python3
"""The World in One Day -- Monday, 23 November 2026.

A newspaper front page drawn entirely in code: Python standard library
only, no network, no randomness, no wall clock. Running this file twice
writes byte-identical PNG bytes to $MAKEFUN_OUTPUT_DIR/entry.png
(or ./out/entry.png when the variable is unset).

Layout: a masthead naming the day, then six illustrated story cards in a
3-by-2 grid -- climate, markets, US politics, a warship at sea, trade,
and the Middle East. Every story was checked against real reporting
published on 23 November 2026; where an event itself happened on Sunday
22 November, the card says so in its own words (see SOURCES.md).
"""

import os
import struct
import zlib

W = 1024
H = 1024

PAPER = (247, 241, 227)
CARD = (252, 248, 238)
INK = (22, 22, 22)
SOFT = (84, 78, 66)
RED = (178, 32, 38)
NAVY = (24, 52, 88)
TEAL = (18, 104, 92)
SKY = (158, 198, 228)
SEA = (52, 96, 138)
GOLD = (198, 148, 42)
SAND = (232, 210, 164)
ORANGE = (206, 102, 38)
GREEN = (52, 122, 72)
CREAM = (240, 228, 200)
DUSK = (232, 164, 96)
DARK = (28, 32, 40)
WHITE = (255, 255, 255)
GREY = (150, 146, 136)

# ------------------------------------------------------------------ PNG out
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    return out + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)


def write_png(path, width, height, px):
    raw = b"".join(
        b"\x00" + bytes(px[y * width * 3:(y + 1) * width * 3])
        for y in range(height)
    )
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    png += _chunk(b"IDAT", zlib.compress(raw, 9))
    png += _chunk(b"IEND", b"")
    with open(path, "wb") as fh:
        fh.write(png)


# ------------------------------------------------------------------ canvas
class Page:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.box(0, 0, w, h, bg)

    def dot(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def box(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = c

    def frame(self, x, y, w, h, c, t=2):
        self.box(x, y, w, t, c)
        self.box(x, y + h - t, w, t, c)
        self.box(x, y, t, h, c)
        self.box(x + w - t, y, t, h, c)

    def hline(self, x, y, w, c, t=1):
        self.box(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.box(x, y, t, h, c)

    def disc(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.dot(xx, yy, c)

    def ring(self, cx, cy, r, c, t=3):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d = (xx - cx) ** 2 + (yy - cy) ** 2
                if (r - t) ** 2 <= d <= r * r:
                    self.dot(xx, yy, c)

    def seg(self, x0, y0, x1, y1, c, t=1):
        steps = max(abs(x1 - x0), abs(y1 - y0), 1)
        for s in range(steps + 1):
            x = x0 + (x1 - x0) * s // steps
            y = y0 + (y1 - y0) * s // steps
            self.disc(x, y, max(1, t // 2), c)

    def tri(self, pts, c):
        # scanline fill of a triangle
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        for yy in range(min(ys), max(ys) + 1):
            spans = []
            for i in range(3):
                ax, ay = pts[i]
                bx, by = pts[(i + 1) % 3]
                if ay == by:
                    continue
                if min(ay, by) <= yy < max(ay, by):
                    x = ax + (bx - ax) * (yy - ay) // (by - ay)
                    spans.append(x)
            if len(spans) >= 2:
                for xx in range(min(spans), max(spans) + 1):
                    self.dot(xx, yy, c)

    def half_disc(self, cx, cy, r, c):
        # upper half of a filled disc (a dome)
        for yy in range(cy - r, cy + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.dot(xx, yy, c)


# ------------------------------------------------------------ 5x7 cap font
# Each glyph: 7 rows of 5 bits, '#' on. Written for this page only.
GLYPHS = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
}


def text_w(s, scale):
    return len(s) * (5 * scale + scale) - scale


def draw_text(pg, x, y, s, scale, c):
    for ch in s:
        g = GLYPHS.get(ch.upper(), GLYPHS["?"])
        for r in range(7):
            for col in range(5):
                if g[r][col] == "1":
                    pg.box(x + col * scale, y + r * scale, scale, scale, c)
        x += 5 * scale + scale
    return x


def draw_centered(pg, cx, y, s, scale, c):
    draw_text(pg, cx - text_w(s, scale) // 2, y, s, scale, c)


def wrap(s, scale, max_w):
    """Greedy word wrap; returns lines that fit max_w pixels."""
    cw = 5 * scale + scale
    per = max(1, (max_w + scale) // cw)
    lines, cur = [], ""
    for word in s.split(" "):
        trial = word if not cur else cur + " " + word
        if len(trial) <= per:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ------------------------------------------------------------- illustrations
def pic_climate(pg, x, y, w, h):
    pg.box(x, y, w, h, SKY)
    pg.disc(x + w // 2, y + 70, 62, SEA)
    pg.disc(x + w // 2 - 22, y + 50, 16, GREEN)
    pg.disc(x + w // 2 + 24, y + 88, 13, GREEN)
    pg.disc(x + w // 2 + 8, y + 44, 9, GREEN)
    pg.ring(x + w // 2, y + 70, 62, INK, 3)
    pg.seg(x + w // 2 - 52, y + 22, x + w // 2 + 52, y + 120, RED, 7)
    pg.box(x + 14, y + h - 46, w - 28, 30, RED)
    draw_centered(pg, x + w // 2, y + h - 40, "NO DEAL", 2, WHITE)


def pic_markets(pg, x, y, w, h):
    pg.box(x, y, w, h, DARK)
    for gx in range(0, w, 44):
        pg.vline(x + gx, y + 12, h - 24, (52, 56, 66), 1)
    for gy in range(0, h, 40):
        pg.hline(x + 12, y + gy, w - 24, (52, 56, 66), 1)
    pts = [(x + 18, y + 52), (x + 78, y + 66), (x + 138, y + 58),
           (x + 198, y + 96), (x + 258, y + 128), (x + 296, y + 158)]
    for a, b in zip(pts, pts[1:]):
        pg.seg(a[0], a[1], b[0], b[1], RED, 6)
    pg.tri([(x + 296, y + 158), (x + 282, y + 142), (x + 300, y + 138)], RED)
    draw_text(pg, x + 16, y + h - 34, "-5.06%", 3, WHITE)


def pic_house(pg, x, y, w, h):
    pg.box(x, y, w, h, NAVY)
    for sx, sy in [(x + 34, y + 34), (x + w - 40, y + 34), (x + 44, y + 150),
                   (x + w - 50, y + 150)]:
        pg.disc(sx, sy, 4, WHITE)
    cx = x + w // 2
    pg.half_disc(cx, y + 118, 52, WHITE)
    pg.box(cx - 6, y + 52, 12, 14, WHITE)
    pg.disc(cx, y + 50, 5, WHITE)
    pg.box(cx - 62, y + 118, 124, 12, WHITE)
    for i in range(6):
        pg.box(cx - 56 + i * 20, y + 130, 10, 34, WHITE)
    pg.box(cx - 68, y + 164, 136, 10, WHITE)
    draw_centered(pg, cx, y + 8, "258", 3, WHITE)


def pic_ship(pg, x, y, w, h):
    pg.box(x, y, w, h, SEA)
    pg.box(x, y + 118, w, h - 118, (34, 74, 116))
    for wx in range(0, w, 52):
        pg.seg(x + wx, y + 132, x + wx + 26, y + 126, WHITE, 3)
        pg.seg(x + wx + 26, y + 126, x + wx + 52, y + 132, WHITE, 3)
    cx, cy = x + w // 2, y + 92
    pg.seg(cx - 108, cy + 8, cx + 108, cy + 8, (70, 76, 84), 14)
    pg.tri([(cx - 108, cy + 8), (cx + 108, cy + 8), (cx + 96, cy - 22)], (70, 76, 84))
    pg.box(cx - 20, cy - 44, 8, 40, INK)
    pg.box(cx - 34, cy - 58, 36, 12, RED)
    pg.disc(cx + 78, cy - 34, 12, GREY)
    pg.disc(cx + 92, cy - 48, 9, GREY)
    pg.disc(cx + 64, cy - 52, 8, (200, 200, 200))
    pg.tri([(cx + 96, cy - 26), (cx + 116, cy - 52), (cx + 122, cy - 20)], ORANGE)
    pg.tri([(cx + 100, cy - 22), (cx + 112, cy - 40), (cx + 116, cy - 18)], GOLD)


def pic_trade(pg, x, y, w, h):
    pg.box(x, y, w, h, SAND)
    pg.box(x, y + 128, w, h - 128, (44, 96, 140))
    pg.seg(x + 20, y + 96, x + w - 16, y + 96, (90, 40, 40), 16)
    pg.box(x + 20, y + 104, w - 36, 12, (60, 60, 66))
    cols = [RED, NAVY, TEAL, GOLD, GREEN, ORANGE]
    for i, c in enumerate(cols):
        pg.box(x + 26 + i * 44, y + 44, 40, 52, c)
        pg.frame(x + 26 + i * 44, y + 44, 40, 52, INK, 2)
    pg.box(x + w - 108, y + 26, 84, 62, DARK)
    pg.box(x + w - 96, y + 38, 60, 38, GOLD)
    for px in range(5):
        pg.box(x + w - 92 + px * 12, y + 48, 6, 6, DARK)
        pg.box(x + w - 92 + px * 12, y + 60, 6, 6, DARK)
    draw_text(pg, x + 16, y + h - 34, "$1 TRILLION", 2, WHITE)


def pic_refinery(pg, x, y, w, h):
    pg.box(x, y, w, h, DUSK)
    pg.disc(x + w - 52, y + 40, 26, GOLD)
    pg.box(x, y + 118, w, h - 118, (58, 44, 40))
    for i, tx in enumerate([x + 30, x + 84, x + 138]):
        pg.box(tx, y + 52, 34, 66, (96, 92, 88))
        pg.box(tx + 8, y + 36, 18, 16, (96, 92, 88))
        pg.seg(tx + 17, y + 36, tx + 17, y + 22, (96, 92, 88), 5)
    pg.tri([(x + 210, y + 118), (x + 238, y + 118), (x + 224, y + 62)], (120, 116, 110))
    pg.seg(x + 224, y + 62, x + 258, y + 34, INK, 4)
    pg.disc(x + 262, y + 32, 7, INK)
    pg.tri([(x + 42, y + 52), (x + 60, y + 8), (x + 78, y + 52)], ORANGE)
    pg.tri([(x + 52, y + 52), (x + 60, y + 26), (x + 68, y + 52)], GOLD)
    pg.tri([(x + 96, y + 52), (x + 108, y + 20), (x + 120, y + 52)], ORANGE)
    draw_text(pg, x + 16, y + h - 34, "CLAIM: UNVERIFIED", 2, WHITE)


# ------------------------------------------------------------------- stories
STORIES = [
    ("CLIMATE", "ANTALYA", "CLIMATE TALKS", "COLLAPSE",
     "COP31 ends Sunday in Antalya with no deal, after the EU and 130 nations reject a text with no fossil fuels.",
     pic_climate),
    ("MARKETS", "TOKYO", "NIKKEI DIVES", "5.06% IN A DAY",
     "Tokyo shares fall Monday as the US AI sell-off spreads across Asia; Hong Kong hits a 19-month low.",
     pic_markets),
    ("POLITICS", "WASHINGTON", "DEMOCRATS TAKE", "THE HOUSE",
     "Chuck Hubbard wins in North Carolina on Sunday after a recount, giving Democrats at least 258 seats.",
     pic_house),
    ("CONFLICT", "BENGHAZI", "WARSHIP SINKS", "AT BENGHAZI",
     "Russian corvette Merkury sinks at a Libyan naval base, reported Monday, after a suspected drone attack.",
     pic_ship),
    ("TRADE", "SEOUL", "KOREA PASSES", "$1 TRILLION",
     "Monday customs data: $77.4bn exported in 20 days; the year total reaches $1.0076tn.",
     pic_trade),
    ("CONFLICT", "RIYADH", "HOUTHIS CLAIM", "SAUDI STRIKE",
     "Houthis say they hit a Saudi refinery and a radar site; the claim is unverified.",
     pic_refinery),
]


def draw_card(pg, x, y, w, h, story):
    kicker, place, h1, h2, sub, pic = story
    pg.box(x, y, w, h, CARD)
    pg.frame(x, y, w, h, INK, 2)
    pic(pg, x + 2, y + 2, w - 4, 178)
    pg.hline(x + 2, y + 180, w - 4, INK, 2)
    ty = y + 194
    draw_text(pg, x + 14, ty, kicker + "  -  " + place, 2, RED)
    hy = ty + 26
    draw_text(pg, x + 14, hy, h1, 3, INK)
    draw_text(pg, x + 14, hy + 26, h2, 3, INK)
    sy = hy + 58
    for i, line in enumerate(wrap(sub, 2, w - 28)[:5]):
        draw_text(pg, x + 14, sy + i * 16, line, 2, SOFT)
    pg.hline(x + 14, y + h - 26, w - 28, GREY, 1)
    draw_text(pg, x + 14, y + h - 20, "REPORTED MON 23 NOV", 1, SOFT)


def build():
    pg = Page(W, H, PAPER)
    pg.box(0, 0, W, 10, RED)
    draw_centered(pg, W // 2, 30, "THE WORLD IN ONE DAY", 4, INK)
    pg.hline(24, 82, W - 48, INK, 3)
    draw_centered(pg, W // 2, 96, "MONDAY, 23 NOVEMBER 2026", 3, RED)
    draw_centered(pg, W // 2, 130, "SIX STORIES FROM AROUND THE WORLD", 2, SOFT)
    pg.hline(24, 156, W - 48, INK, 3)

    gx, gy = 24, 170
    cw = (W - 48 - 2 * 14) // 3
    ch = 396
    for i, story in enumerate(STORIES):
        cx = gx + (i % 3) * (cw + 14)
        cy = gy + (i // 3) * (ch + 14)
        draw_card(pg, cx, cy, cw, ch, story)

    fy = gy + 2 * ch + 14 + 8
    pg.hline(24, fy, W - 48, INK, 2)
    draw_centered(pg, W // 2, fy + 10,
                  "ALL SIX STORIES REPORTED ON MONDAY, 23 NOVEMBER 2026", 2, SOFT)
    return pg


def main():
    out = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out, exist_ok=True)
    pg = build()
    write_png(os.path.join(out, "entry.png"), W, H, pg.px)


if __name__ == "__main__":
    main()

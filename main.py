#!/usr/bin/env python3
"""news-image-20261121 v1 — one-day world news poster, 1024x1024.

Draws the whole image with Pillow from the story list embedded below.
Deterministic: same bytes on every run, no network, no clock, no random.
Writes ONLY to $MAKEFUN_OUTPUT_DIR/entry.png (default /output/entry.png).
"""

import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
OUT_PATH = os.path.join(OUT_DIR, "entry.png")

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
SERIF_B = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")
SANS = os.path.join(FONT_DIR, "DejaVuSans.ttf")
SANS_B = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


# ---------------------------------------------------------------- palette
PAPER = (247, 243, 234)
INK = (20, 20, 20)
NAVY = (16, 42, 67)
NAVY2 = (28, 68, 102)
TEAL = (14, 94, 88)
RED = (178, 34, 34)
GOLD = (176, 132, 24)
CARD = (255, 255, 255)
LINE = (180, 172, 156)
MUTED = (90, 86, 76)
BAND = (232, 226, 210)

ACCENTS = [RED, NAVY2, TEAL, (122, 63, 20), (90, 40, 90), (30, 90, 40),
           (150, 60, 20), (60, 60, 120)]


# ---------------------------------------------------------------- text tools
def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_line(draw, text, fnt, max_w):
    """Truncate one line with an ellipsis so it fits max_w."""
    if draw.textlength(text, font=fnt) <= max_w:
        return text
    while text and draw.textlength(text + "...", font=fnt) > max_w:
        text = text[:-1]
    return text + "..."


# ---------------------------------------------------------------- glyphs
def glyph_quake(d, x, y, s, col):
    # mountains + crack zigzag
    d.polygon([(x, y + s), (x + s * 0.3, y + s * 0.25), (x + s * 0.6, y + s)],
              fill=col)
    d.polygon([(x + s * 0.4, y + s), (x + s * 0.7, y + s * 0.1),
               (x + s, y + s)], fill=(col[0] // 2 + 60, col[1] // 2 + 60,
                                      col[2] // 2 + 60))
    pts = [(x + s * 0.1, y + s * 0.55), (x + s * 0.3, y + s * 0.75),
           (x + s * 0.5, y + s * 0.5), (x + s * 0.7, y + s * 0.8),
           (x + s * 0.9, y + s * 0.55)]
    d.line(pts, fill=(255, 255, 255), width=3)


def glyph_summit(d, x, y, s, col):
    # three podiums / three leaders at a table
    for i, c in enumerate([(178, 34, 34), (16, 42, 67), (176, 132, 24)]):
        bx = x + i * s * 0.36
        d.ellipse([bx, y + s * 0.1, bx + s * 0.24, y + s * 0.34], fill=c)
        d.rectangle([bx - s * 0.02, y + s * 0.4, bx + s * 0.26, y + s],
                    fill=c)
    d.rectangle([x, y + s * 0.62, x + s, y + s * 0.72], fill=(255, 255, 255))


def glyph_burst(d, x, y, s, col):
    # explosion starburst
    cx, cy = x + s / 2, y + s / 2
    for k in range(8):
        ang = k * 3.14159 / 4
        import math
        ex = cx + math.cos(ang) * s * 0.5
        ey = cy + math.sin(ang) * s * 0.5
        d.line([cx, cy, ex, ey], fill=col, width=4)
    d.ellipse([cx - s * 0.2, cy - s * 0.2, cx + s * 0.2, cy + s * 0.2],
              fill=(255, 200, 40))


def glyph_chart_down(d, x, y, s, col):
    d.line([(x, y + s * 0.2), (x + s * 0.3, y + s * 0.45),
            (x + s * 0.55, y + s * 0.35), (x + s * 0.85, y + s * 0.85)],
           fill=col, width=5)
    d.polygon([(x + s * 0.85, y + s * 0.85), (x + s * 0.62, y + s * 0.85),
               (x + s * 0.85, y + s * 0.62)], fill=col)
    d.line([(x, y + s), (x + s, y + s)], fill=MUTED, width=2)


def glyph_shield(d, x, y, s, col):
    d.polygon([(x + s * 0.5, y), (x + s, y + s * 0.2), (x + s, y + s * 0.6),
               (x + s * 0.5, y + s), (x, y + s * 0.6), (x, y + s * 0.2)],
              outline=col, width=4)
    d.line([(x + s * 0.3, y + s * 0.5), (x + s * 0.45, y + s * 0.68),
            (x + s * 0.75, y + s * 0.32)], fill=col, width=4)


def glyph_scales(d, x, y, s, col):
    d.line([(x + s * 0.5, y + s * 0.05), (x + s * 0.5, y + s * 0.9)],
           fill=col, width=3)
    d.line([(x + s * 0.1, y + s * 0.25), (x + s * 0.9, y + s * 0.25)],
           fill=col, width=3)
    for cx in (x + s * 0.18, x + s * 0.82):
        d.line([(cx, y + s * 0.25), (cx - s * 0.14, y + s * 0.6),
                (cx + s * 0.14, y + s * 0.6)], fill=col, width=2)
        d.line([(cx - s * 0.14, y + s * 0.6), (cx + s * 0.14, y + s * 0.6)],
               fill=col, width=3)
    d.rectangle([x + s * 0.35, y + s * 0.9, x + s * 0.65, y + s], fill=col)


def glyph_bars(d, x, y, s, col):
    for i in range(5):
        bx = x + i * s * 0.22
        d.rectangle([bx, y, bx + s * 0.09, y + s], fill=col)
    d.line([(x, y + s * 0.18), (x + s, y + s * 0.18)], fill=col, width=3)


def glyph_server(d, x, y, s, col):
    for i in range(3):
        by = y + i * s * 0.34
        d.rectangle([x, by, x + s * 0.8, by + s * 0.26], outline=col, width=3)
        d.ellipse([x + s * 0.08, by + s * 0.08, x + s * 0.16, by + s * 0.18],
                  fill=col)
    d.line([(x + s * 0.85, y + s * 0.1), (x + s * 0.85, y + s * 0.9)],
           fill=col, width=3)


GLYPHS = [glyph_quake, glyph_summit, glyph_burst, glyph_chart_down,
          glyph_shield, glyph_scales, glyph_bars, glyph_server]

# ---------------------------------------------------------------- stories
FEATURED = [
    ("PERU", "6.8 quake shakes central Peru",
     "Junin region hit Fri; tremors felt in Lima, 320 km away.",
     "PERU GEOPHYSICAL INSTITUTE"),
    ("SHENZHEN", "Trump, Xi and Putin hold trilateral talks",
     "Joint declaration: nuclear war 'cannot be won and must never be fought'.",
     "APEC SUMMIT"),
    ("POLAND", "Russian missile hits Poland, Tusk says",
     "NATO calls it a grave airspace violation.",
     "BBC"),
    ("MARKETS", "Stocks plunge: S&P -3.7%, Nasdaq -5.28%",
     "Nvidia falls ~14% as SEC probes its accounting.",
     "REUTERS / BBC"),
    ("DENMARK", "Denmark says it foiled a Russian assassination plot",
     "Target: a US-Ukrainian rapper; diplomat expelled.",
     "BBC"),
    ("THE HAGUE", "World Court: Myanmar committed genocide",
     "ICJ: state responsibility over Rohingya (Thu).",
     "AP / PBS"),
    ("NEW YORK", "Mamdani: close Rikers Island jail by 2032",
     "Plan pushes past the 2027 legal deadline by five years.",
     "BBC"),
    ("WASHINGTON", "Trump threatens ban on overseas data centres",
     "US firms face a 'tremendous tax' abroad.",
     "BBC"),
]

# (group, headline) — one line each, kept short for the column width
BRIEFS = [
    ("NORTH AMERICA (10)", [
        "Trump urges Nvidia to reinstate Huang; board says no",
        "US declassifies more UFO footage filmed in Middle East",
        "White House removes cyber-security chief after outages",
        "US judge rejects Trump homelessness plan revamp",
        "Virginia child dies in first measles death of 2026",
        "Hackers breached US Dept of Agriculture, NBC reports",
        "GTA 6: $3.79bn in first-day retail sales (Fri)",
        "YouTube nears ~$3bn payout to US school districts (Fri)",
        "Court approves $7.25bn Bayer Roundup settlement (Fri)",
        "LA jury convicts man who started 2025 Palisades Fire",
    ]),
    ("EUROPE (10)", [
        "UK-EU deal: food trade, carbon, youth mobility (Fri)",
        "Cost-of-living protests sweep 25+ countries (Fri)",
        "French police sentenced for 2020 Zecler beating",
        "Depardieu probed over sexual allegations",
        "German metalworkers in first 24h strike in 8 years",
        "Lufthansa to cut 1,000 jobs at Frankfurt, Munich",
        "De Villepin announces 2027 French presidency bid",
        "Lagarde gives final address as ECB president (Fri)",
        "EU Council adopts EUR 1bn military aid to Ukraine",
        "Kyiv crossings hit; Kryvyi Rih: 2 dead, 42 hurt",
    ]),
    ("ASIA (9)", [
        "Cyclone Akvan crosses Odisha coast near Gopalpur",
        "Record Rs 1.22 lakh crore flows into Indian shares",
        "KL Rahul: Test 100s in all four SENA countries",
        "Nepal PM Balen Shah heads to Delhi on first trip",
        "Indian man jailed 19+ yrs in US Sikh murder plot",
        "India firm on Indus Treaty as SCO forum meets",
        "Top court allows Deepathoon lamp, one-time only",
        "Sensex rallies nearly 898 points (Fri)",
        "India women beat Malaysia 4-1 in hockey opener",
    ]),
    ("MIDDLE EAST & AFRICA (5)", [
        "US adds four Iranians to OFAC sanctions list",
        "Tanker fire reported in Strait of Hormuz (Fri)",
        "ANC fights to hold South Africa's key cities",
        "Nearly 600 women killed in South Africa in 3 months",
        "COP31 talks enter crucial final stage in Turkey",
    ]),
    ("SCIENCE, TECH & SPORT (4)", [
        "Anthropic mathematician claims Riemann proof (unverified)",
        "F1 Las Vegas: Russell fastest; contact with Verstappen",
        "Norway warns AI in public cases can discriminate",
        "Spain: data centres must use 80% renewables",
    ]),
]

TIMELINE = [
    ("02:27", "Kryvyi Rih toll"),
    ("03:34", "4 Iranians sanctioned"),
    ("04:04", "Donbas-NATO idea"),
    ("05:57", "Denmark plot foiled"),
    ("07:08", "Riemann claim"),
    ("08:01", "Rikers 2032"),
    ("08:34", "ANC cities"),
    ("09:02", "Migrant-scam probe"),
]

# dots on the stylised map: (x fraction, y fraction, label, label dx, label dy)
MAP_DOTS = [
    (0.16, 0.62, "PERU", 6, -5),
    (0.24, 0.30, "NEW YORK", 6, -5),
    (0.46, 0.24, "POLAND", -52, -6),
    (0.50, 0.34, "DENMARK", 6, -12),
    (0.44, 0.44, "THE HAGUE", 6, 2),
    (0.60, 0.55, "HORMUZ", 6, -5),
    (0.84, 0.36, "SHENZHEN", -62, -6),
    (0.76, 0.58, "ODISHA", 6, 2),
]


def draw_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(22, 68, 88))
    # rough continent blobs (stylised, not to scale)
    blobs = [
        [(0.03, 0.25), (0.10, 0.15), (0.20, 0.18), (0.24, 0.35),
         (0.20, 0.55), (0.16, 0.75), (0.10, 0.70), (0.05, 0.45)],
        [(0.28, 0.30), (0.36, 0.18), (0.45, 0.20), (0.48, 0.35),
         (0.44, 0.55), (0.38, 0.75), (0.32, 0.60), (0.28, 0.45)],
        [(0.48, 0.18), (0.60, 0.12), (0.72, 0.18), (0.78, 0.30),
         (0.74, 0.45), (0.66, 0.55), (0.58, 0.45), (0.52, 0.30)],
        [(0.82, 0.25), (0.90, 0.20), (0.97, 0.30), (0.95, 0.55),
         (0.88, 0.70), (0.84, 0.50), (0.82, 0.35)],
        [(0.55, 0.70), (0.65, 0.65), (0.72, 0.75), (0.62, 0.85),
         (0.55, 0.80)],
    ]
    for blob in blobs:
        pts = [(x + fx * w, y + fy * h) for fx, fy in blob]
        d.polygon(pts, fill=(120, 160, 140))
    f_dot = font(SANS_B, 9)
    for fx, fy, label, ldx, ldy in MAP_DOTS:
        cx, cy = x + fx * w, y + fy * h
        d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(255, 90, 60),
                  outline=(255, 255, 255), width=1)
        d.text((cx + ldx, cy + ldy), label, font=f_dot, fill=(255, 255, 255))


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---------------------------------------------------------------- masthead
    d.rectangle([0, 0, W, 96], fill=NAVY)
    d.rectangle([0, 96, W, 100], fill=GOLD)
    f_title = font(SERIF_B, 44)
    f_sub = font(SANS_B, 15)
    f_check = font(SANS, 11)
    d.text((16, 8), "THE WORLD IN ONE DAY", font=f_title, fill=(255, 255, 255))
    d.text((16, 62), "SATURDAY, 21 NOVEMBER 2026  |  46 VERIFIED STORIES",
           font=f_sub, fill=(255, 214, 90))
    d.text((16, 82), "DATE CHECK: every item below was reported 21 Nov 2026 (UTC); "
           "events from Fri 20 Nov are marked 'Fri'.",
           font=f_check, fill=(200, 210, 220))
    right_txt = "EARLY-DAY EDITION  |  v1"
    d.text((W - 16 - d.textlength(right_txt, font=f_sub), 62),
           right_txt, font=f_sub, fill=(255, 214, 90))

    # ------------------------------------------------------- UTC timeline strip
    d.rectangle([0, 100, W, 132], fill=BAND)
    d.line([0, 132, W, 132], fill=LINE, width=1)
    f_tl = font(SANS, 9)
    f_tlb = font(SANS_B, 9)
    x = 16
    d.text((x, 106), "UTC WIRE", font=f_tlb, fill=NAVY)
    x += d.textlength("UTC WIRE  ", font=f_tlb)
    for t, label in TIMELINE:
        seg = t + " " + label
        wseg = d.textlength(seg, font=f_tl) + 10
        d.text((x, 106), t, font=f_tlb, fill=RED)
        d.text((x + d.textlength(t + " ", font=f_tlb), 106), label,
               font=f_tl, fill=INK)
        x += wseg
        if x > W - 20:
            break
    d.text((16, 118), "All times UTC, 21 Nov 2026. Full-day rebuild planned this evening.",
           font=f_tl, fill=MUTED)

    # ------------------------------------------------------------ featured rows
    f_kick = font(SANS_B, 11)
    f_head = font(SANS_B, 16)
    f_head_big = font(SANS_B, 19)
    f_det = font(SANS, 11)
    f_src = font(SANS, 9)

    def panel(px, py, pw, ph, idx):
        kick, head, det, src = FEATURED[idx]
        col = ACCENTS[idx % len(ACCENTS)]
        d.rectangle([px, py, px + pw, py + ph], fill=CARD,
                    outline=LINE, width=1)
        d.rectangle([px, py, px + pw, py + 22], fill=col)
        d.text((px + 8, py + 4), kick, font=f_kick, fill=(255, 255, 255))
        d.text((px + pw - 8 - d.textlength("F" + str(idx + 1), font=f_kick),
                py + 4), "F" + str(idx + 1), font=f_kick,
               fill=(255, 255, 255))
        big = ph > 140
        gh = 52 if big else 40
        gy = py + 30
        GLYPHS[idx](d, px + 8, gy, gh, col)
        tx = px + 8 + gh + 10
        tw = px + pw - 8 - tx
        hf = f_head_big if big else f_head
        lines = wrap(d, head, hf, tw)
        ly = gy
        for ln in lines[:3]:
            d.text((tx, ly), ln, font=hf, fill=INK)
            ly += 22 if big else 19
        d.text((px + 8, py + ph - 34),
               fit_line(d, det, f_det, pw - 16), font=f_det, fill=MUTED)
        d.text((px + 8, py + ph - 19), "SOURCE: " + src, font=f_src,
               fill=MUTED)

    # row A: 2 large panels
    panel(8, 140, 500, 150, 0)
    panel(516, 140, 500, 150, 1)
    # row B: 3 panels
    bx = [8, 348, 688]
    for i, px in enumerate(bx):
        panel(px, 298, 328, 122, 2 + i)
    # row C: 3 panels
    for i, px in enumerate(bx):
        panel(px, 428, 328, 122, 5 + i)

    # ---------------------------------------------------------------- briefs
    by = 558
    f_bh = font(SANS_B, 13)
    f_gh = font(SANS_B, 10)
    f_bi = font(SANS, 10)
    d.rectangle([0, by, W, by + 24], fill=NAVY2)
    d.text((16, by + 4), "WORLD BRIEFS  —  38 MORE STORIES, GROUPED BY REGION",
           font=f_bh, fill=(255, 255, 255))
    d.text((W - 16 - d.textlength("1 line = 1 verified story", font=f_gh),
            by + 6), "1 line = 1 verified story", font=f_gh,
           fill=(200, 210, 220))

    col_w = 488
    col_x = [16, 520]
    # columns: 0 -> North America + Europe ; 1 -> Asia + ME&Afr + Sci/Tech/Sport
    col_groups = [[0, 1], [2, 3, 4]]
    row_h = 15
    iy = by + 30
    for ci, groups in enumerate(col_groups):
        cx = col_x[ci]
        yy = iy
        for gi in groups:
            gname, items = BRIEFS[gi]
            d.text((cx, yy), gname, font=f_gh, fill=NAVY)
            yy += row_h
            for it in items:
                d.text((cx, yy), "- " + fit_line(d, it, f_bi, col_w - 12),
                       font=f_bi, fill=INK)
                yy += row_h
            yy += 4

    # ---------------------------------------------------------------- map strip
    my = 924
    d.rectangle([0, my, W, my + 60], fill=(255, 255, 255))
    d.line([0, my, W, my], fill=LINE, width=1)
    draw_map(d, 16, my + 4, 700, 52)
    f_map = font(SANS_B, 10)
    f_map2 = font(SANS, 10)
    d.text((736, my + 8), "WHERE IT HAPPENED", font=f_map, fill=NAVY)
    d.text((736, my + 24), "Red dots mark the 8 featured", font=f_map2,
           fill=INK)
    d.text((736, my + 38), "stories, from Peru to Shenzhen.", font=f_map2,
           fill=INK)
    d.text((736, my + 52), "Map stylised, not to scale.", font=f_map2,
           fill=MUTED)

    # ---------------------------------------------------------------- footer
    fy = 988
    d.rectangle([0, fy, W, H], fill=NAVY)
    f_ft = font(SANS, 10)
    d.text((16, fy + 6),
           "Editorial illustrations, not photographs. Sources: Reuters, AP, AFP, "
           "BBC, Al Jazeera, Xinhua, wire reports — 21 November 2026 (UTC).",
           font=f_ft, fill=(220, 225, 230))
    d.text((16, fy + 22),
           "46 verified stories  |  v1 early-day edition — full-day rebuild planned "
           "this evening.  |  make.fun bounty news-image-20261121",
           font=f_ft, fill=(180, 190, 200))

    os.makedirs(OUT_DIR, exist_ok=True)
    img.save(OUT_PATH, format="PNG", optimize=True)


if __name__ == "__main__":
    main()

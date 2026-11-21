"""news-image-20261121 v2 -- one-page newspaper, 1024x1024 PNG.

Renders "The World in One Day -- 21 November 2026": 8 featured stories
plus 47 briefs (55 verified stories, Mon 17 - Sat 21 Nov 2026 window).

Stdlib + Pillow only. Deterministic: no clock, no randomness, no network.
Writes ONLY to $MAKEFUN_OUTPUT_DIR (default /output/entry.png).
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 14

# ---------------------------------------------------------------- palette
PAPER = (253, 253, 248)
INK = (18, 18, 18)
MUTED = (90, 90, 86)
RED = (178, 28, 28)
NAVY = (26, 42, 74)
RULE = (150, 150, 142)
PANEL = (244, 244, 238)
PANEL_EDGE = (205, 205, 196)
MAP_OCEAN = (214, 230, 240)
MAP_LAND = (206, 204, 178)
MAP_DOT = (178, 28, 28)
WIRE_BG = (238, 238, 230)
FOOT_BG = (238, 238, 230)

WARNINGS = []


def warn(msg):
    WARNINGS.append(msg)


# ---------------------------------------------------------------- fonts
def load_font(bold=False, serif=False, size=11):
    base = "/usr/share/fonts/truetype/dejavu/"
    names = []
    if serif:
        names = ["DejaVuSerif-Bold.ttf"] if bold else ["DejaVuSerif.ttf"]
    else:
        names = ["DejaVuSans-Bold.ttf"] if bold else ["DejaVuSans.ttf"]
    for name in names:
        path = base + name
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default(size)


# ---------------------------------------------------------------- text wrap
def wrap_words(draw, words, fonts, max_w):
    """Greedy wrap. words: list of str; fonts: list of ImageFont, same length.
    Returns list of lines, each a list of (word, font)."""
    lines = []
    cur = []
    cur_w = 0
    for word, font in zip(words, fonts):
        ww = draw.textlength(word, font=font)
        space = draw.textlength(" ", font=font) if cur else 0
        if cur and cur_w + space + ww > max_w:
            lines.append(cur)
            cur = [(word, font)]
            cur_w = ww
        else:
            if cur:
                cur_w += space
            cur.append((word, font))
            cur_w += ww
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(draw, lines, x, y, lh):
    for line in lines:
        cx = x
        for word, font in line:
            draw.text((cx, y), word, font=font, fill=INK)
            cx += draw.textlength(word, font=font) + draw.textlength(" ", font=font)
        y += lh
    return y


def mixed_block(draw, lead, rest, f_bold, f_reg, max_w, max_lines, tag):
    """One brief: bold lead words then regular rest, wrapped to max_lines.
    Returns lines used. Records a warning on overflow."""
    words = lead.split() + rest.split()
    fonts = [f_bold] * len(lead.split()) + [f_reg] * len(rest.split())
    lines = wrap_words(draw, words, fonts, max_w)
    if len(lines) > max_lines:
        warn("%s overflow: %d lines (max %d): %s" % (tag, len(lines), max_lines, lead))
        lines = lines[:max_lines]
    return lines


# ---------------------------------------------------------------- content
# All display lines composed in-session from verified wire reporting.
# Day marks: (Tue)/(Thu)/(Fri) on Mon-Fri briefs; Sat items unmarked.
FEATURED = [
    ("F1", "COP31",
     "COP31 in overtime as talks miss deadline",
     "Talks run past their Friday close with no deal and a third draft is due "
     "on Saturday morning. The EU calls the text too weak, and Panama vows "
     "to block it."),
    ("F2", "RIYADH",
     "Three Houthi missiles downed over Riyadh",
     "Saudi defences down the rockets early on Saturday, the third "
     "straight night of alerts. The Houthis warn Jeddah and Red Sea "
     "ports may be next."),
    ("F3", "PERU",
     "M6.7 quake shakes Peru's Junin region",
     "The tremor strikes at 00:09 UTC, 108 km deep, and is felt in Lima. "
     "Early reports list no deaths and no major damage from the shaking."),
    ("F4", "UKRAINE",
     "Deadly strikes hit Kryvyi Rih and Kyiv",
     "Three die, a boy of seven among them, and 42 are hurt in Kryvyi "
     "Rih; Kyiv's crossings are damaged. Kyiv says it hit three Russian "
     "systems."),
    ("F5", "CRICKET",
     "Rahul's ton puts India on top in Wellington",
     "KL Rahul reaches 136 and becomes the first Indian opener with Test "
     "hundreds in all four SENA nations, as India moves to 344 for 2 at tea."),
    ("F6", "MARKETS",
     "Bitcoin slides below $59,000",
     "The coin trades near $58,983, down 3.9%, as the tech sell-off spreads. "
     "Anthropic shares fall 8.5% a day after their stock-market debut."),
    ("F7", "UK-EU",
     "UK and EU seal post-Brexit reset",
     "Brussels agrees easier food trade, linked carbon markets and a youth "
     "scheme offering 100,000 visas a year for under-32s to live, work "
     "and study."),
    ("F8", "WASHINGTON",
     "Trump threatens tax on overseas data centres",
     "The president says US firms will face a 'tremendous tax' if they build "
     "AI data centres abroad, naming a project in Finland. No rate or "
     "mechanism is given."),
]

# (lead, rest) -- lead renders bold, rest regular. Keep each to 2 lines.
BRIEFS_A = [
    ("SAT 21 NOV", [
        ("COP31 'fossil summit' warning.",
         "EU envoys say the draft risks a summit with no fossil-fuel language."),
        ("Panama vows to block text.",
         "Panama says it will veto any final deal that ignores its demands."),
        ("PLN signs six clean-energy deals.",
         "Indonesia's state utility inks six green power agreements."),
        ("Houthis threaten Jeddah ports.",
         "The group warns Red Sea ports and Jeddah are in range after Riyadh."),
        ("Vance: Iran call is Trump's.",
         "The vice-president says any strike on Iran rests with the president."),
        ("SpaceX funding under threat.",
         "US lawmakers move to put SpaceX funding at risk."),
        ("(Thu) Texas execution: 63 minutes.",
         "Reinaldo Dennes's lethal injection ran over an hour in Huntsville."),
        ("Palisades arsonist convicted.",
         "A jury finds the man who started LA's deadly 2025 fire guilty."),
        ("Roundup deal approved: $7.25bn.",
         "A court signs off Bayer's settlement of cancer claims."),
        ("Freight train derails in Sejong.",
         "A goods train comes off the rails in South Korea's Sejong city."),
    ]),
    ("THU 19 NOV", [
        ("(Thu) Shenzhen peace declaration.",
         "Trump, Xi and Putin: nuclear war 'cannot be won, must never be fought'."),
        ("(Thu) Anthropic shares jump 17%.",
         "The AI firm's stock debuts with a 17% first-day rise."),
        ("(Thu) GTA VI: $3.79bn in a day.",
         "The game's first-day retail sales set an entertainment record."),
        ("(Thu) Fiona the hippo dies, 9.",
         "Cincinnati's beloved hippo dies after swallowing a visitor's knit hat."),
        ("(Tue) Voyager 1, a light-day away.",
         "NASA's probe passes 25.9bn km from Earth; a signal now takes a day."),
    ]),
]

BRIEFS_B = [
    ("SAT 21 NOV, CONT.", [
        ("Taipei passes budget, cash payout.",
         "Taiwan's capital approves its budget plus a payout to residents."),
        ("Bangkok arsenic river plan.",
         "The city unveils a plan to tackle arsenic in a river."),
        ("Odisha: 372,000 displaced by Akvan.",
         "Akvan's aftermath leaves hundreds of thousands uprooted."),
        ("World backs ICJ Myanmar ruling.",
         "Switzerland welcomes it; rights groups press for sanctions."),
        ("Verstappen called to stewards.",
         "The champion faces the stewards in Las Vegas GP practice."),
        ("Frosty APEC reception for Takaichi.",
         "Japan's premier meets a cool welcome on the summit sidelines."),
        ("Ottawa: US leadership doubted.",
         "Doubts about American leadership surface at a security forum."),
        ("Kabul ISIS-K drone warning.",
         "The UN warns over an ISIS-K drone threat in Kabul."),
        ("Berlin students protest rearmament.",
         "Students march in Berlin against the rearmament drive."),
        ("Brasilia indigenous land bill.",
         "A bill on indigenous land advances in Brazil's capital."),
    ]),
    ("FRI 20 NOV", [
        ("(Fri) Russian missiles land in Poland.",
         "Two missiles and a drone come down as allies drill nearby."),
        ("(Fri) Kyiv bridges hit.",
         "Russian strikes damage three crossings over the Dnipro in the capital."),
        ("(Fri) Cyclone Akvan makes landfall.",
         "The storm crosses the Odisha coast near Gopalpur."),
        ("(Thu) ICJ: Myanmar committed genocide.",
         "The world court finds Myanmar guilty over the Rohingya."),
        ("(Fri) Wall Street enters correction.",
         "S&P falls 3.7% and Nasdaq 5.28%; Nvidia drops ~14% on a probe report."),
    ]),
]

BRIEFS_C = [
    ("SAT 21 NOV, CONT.", [
        ("Sydney heatwave.",
         "Temperatures soar as a heatwave grips Sydney."),
        ("Asset-seizure law advances.",
         "Jakarta moves ahead with a law to confiscate criminal assets."),
        ("Iran engagement cost $48.3bn.",
         "Washington tallies the price of its Iran engagement."),
        ("Kyiv: 3 Russian missile systems hit.",
         "Ukraine says its forces destroyed three Russian missile systems."),
        ("ANC fights for its cities.",
         "After its 31% local-election low, the ANC battles to hold key cities."),
        ("Zelensky: Crimea bridge 'will not survive'.",
         "Kyiv's leader calls the Crimean bridge a legitimate target."),
        ("Air Niugini 767 lands safely in Davao.",
         "All 146 aboard escape injury after an engine-fire warning."),
        ("Nigeria funeral boat sinks.",
         "At least four die as a boat carrying mourners sinks in Bayelsa."),
        ("Antonelli fastest, Verstappen on pole.",
         "Antonelli tops Las Vegas qualifying; a penalty hands Verstappen pole."),
    ]),
    ("FRI 20 NOV, CONT.", [
        ("(Fri) First US measles death of 2026.",
         "A young child in Virginia dies; the state had seen none since 1978."),
        ("(Fri) Record EU payment to Ukraine.",
         "Brussels disburses 7.9bn euros, its biggest single Ukraine tranche."),
        ("(Fri) Denmark expels Russian attache.",
         "Copenhagen acts after foiling an alleged plot to kill a rapper."),
        ("(Fri) India unveils first H5N1 vaccine.",
         "A home-grown bird-flu vaccine for chickens is dedicated in Bhopal."),
        ("(Thu) 900,000 AI chips for China.",
         "House panel counts 879,000 Nvidia and AMD licences."),
        ("(Fri) Tanker fire in Hormuz strait.",
         "A tanker burns after a strike in the Strait of Hormuz."),
        ("(Fri) SCO forum opens in Delhi.",
         "Pakistan's minister attends the Shanghai forum in New Delhi."),
        ("(Fri) Mamdani: Rikers to close by 2032.",
         "New York's mayor sets a new date to shut the island jail complex."),
    ]),
]

WIRE = [
    ("00:09", "Peru quake, Junin"),
    ("02:27", "Kryvyi Rih toll reported"),
    ("03:34", "OFAC sanctions published"),
    ("04:04", "Zelenskyy: US floated Donbas-for-NATO idea"),
    ("04:32", "Zelenskyy: Putin 'a killer'"),
    ("04:34", "Palisades arson verdict"),
    ("05:57", "Denmark plot exposed"),
    ("08:34", "ANC fights for its cities"),
]

# (label, lon, lat, label dx, label dy) -- offsets keep labels from colliding
MAP_DOTS = [
    ("F1", 30.7, 36.9, -26, 4),    # Antalya
    ("F2", 46.7, 24.7, 8, 6),     # Riyadh
    ("F3", -76.0, -10.9, 8, 6),   # Junin, Peru
    ("F4", 33.4, 47.9, 8, -14),   # Kryvyi Rih
    ("F5", 174.8, -41.3, -26, -4),  # Wellington
    ("F6", -74.0, 40.7, -26, 6),  # New York markets
    ("F7", 4.35, 50.85, -26, -14),  # Brussels
    ("F8", -77.0, 38.9, 8, -14),  # Washington DC
]

# Rough continent outlines in (lon, lat). Schematic, not survey-grade.
CONTINENTS = [
    [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80), (-85, 80),
     (-80, 73), (-65, 62), (-55, 52), (-60, 47), (-70, 42), (-75, 35),
     (-80, 26), (-84, 30), (-90, 21), (-97, 16), (-105, 20), (-115, 28),
     (-125, 40), (-125, 49), (-140, 60), (-155, 58), (-165, 60)],
    [(-58, 64), (-45, 60), (-40, 70), (-30, 76), (-20, 70), (-25, 60)],
    [(-80, 9), (-75, 11), (-62, 10), (-52, 5), (-50, 0), (-44, -3),
     (-35, -8), (-40, -20), (-48, -28), (-58, -38), (-65, -45), (-70, -54),
     (-73, -37), (-73, -18), (-80, -5)],
    [(-10, 36), (-9, 43), (-2, 48), (-4, 50), (0, 51), (5, 53), (8, 57),
     (10, 59), (18, 56), (21, 55), (24, 58), (28, 60), (30, 70), (40, 68),
     (45, 60), (40, 50), (35, 45), (30, 42), (28, 40), (23, 36), (19, 40),
     (12, 44), (3, 42), (-2, 37)],
    [(-6, 35), (10, 37), (20, 32), (32, 31), (35, 28), (43, 12), (51, 11),
     (48, 2), (41, -10), (36, -18), (32, -26), (26, -34), (19, -35),
     (15, -27), (12, -18), (9, 4), (-8, 5), (-15, 11), (-17, 15)],
    [(40, 68), (60, 70), (75, 73), (90, 75), (110, 77), (130, 72),
     (160, 70), (178, 66), (170, 60), (162, 56), (158, 50), (142, 45),
     (140, 40), (135, 35), (127, 33), (122, 30), (120, 25), (110, 20),
     (105, 10), (100, 8), (98, 16), (92, 21), (88, 22), (80, 15),
     (77, 8), (72, 20), (66, 25), (60, 25), (56, 26), (52, 28), (48, 30),
     (44, 30), (40, 36), (36, 36), (30, 36)],
    [(113, -22), (114, -30), (115, -35), (124, -33), (130, -32),
     (137, -35), (140, -38), (147, -39), (153, -32), (153, -27),
     (146, -19), (142, -11), (136, -12), (132, -12), (126, -14),
     (122, -17)],
]

DATE_CHECK = ("Top stories of the week, Mon 17 - Sat 21 Nov 2026 (UTC). "
              "Featured: Sat 21 Nov. Briefs marked (Mon)-(Fri) happened on "
              "those days; unmarked briefs are Sat 21 Nov.")
FOOTER_SRC = ("Sources: BBC, Reuters, AP, AFP, USGS, NASA, European Commission. "
              "All times UTC. Figures as reported at build time.")


# ---------------------------------------------------------------- drawing
def draw_masthead(draw):
    y = 8
    f_kick = load_font(bold=True, size=11)
    kick = "WEEK IN REVIEW  |  MON 17 - SAT 21 NOV 2026"
    tw = draw.textlength(kick, font=f_kick)
    draw.text(((W - tw) / 2, y), kick, font=f_kick, fill=RED)
    y += 16
    f_title = load_font(bold=True, serif=True, size=32)
    title = "The World in One Day"
    tw = draw.textlength(title, font=f_title)
    draw.text(((W - tw) / 2, y), title, font=f_title, fill=INK)
    y += 38
    f_sub = load_font(bold=True, size=12)
    sub = "Saturday 21 November 2026  -  55 Verified Stories"
    tw = draw.textlength(sub, font=f_sub)
    draw.text(((W - tw) / 2, y), sub, font=f_sub, fill=NAVY)
    draw.line([(MARGIN, 78), (W - MARGIN, 78)], fill=INK, width=2)


def draw_wire(draw, y0, y1):
    draw.rectangle([MARGIN, y0, W - MARGIN, y1], fill=WIRE_BG)
    draw.rectangle([MARGIN, y0, W - MARGIN, y1], outline=RULE, width=1)
    f_lab = load_font(bold=True, size=10)
    f_txt = load_font(size=10)
    f_bold = load_font(bold=True, size=10)
    label = "UTC WIRE"
    draw.text((MARGIN + 6, y0 + 4), label, font=f_lab, fill=RED)
    lx = MARGIN + 6 + draw.textlength(label, font=f_lab) + 10
    # Two lines of wire items, 4 per line.
    items = ["%s %s" % (t, s) for t, s in WIRE]
    for row, chunk in enumerate((items[:4], items[4:])):
        words = []
        fonts = []
        for it in chunk:
            time_part, _, rest = it.partition(" ")
            words += [time_part] + rest.split() + ["|"]
            fonts += [f_bold] + [f_txt] * len(rest.split()) + [f_txt]
        words = words[:-1]
        fonts = fonts[:-1]
        lines = wrap_words(draw, words, fonts, W - 2 * MARGIN - (lx - MARGIN) - 6)
        draw_wrapped(draw, lines, lx, y0 + 3 + row * 13, 13)


def draw_featured(draw, y0):
    f_tag = load_font(bold=True, size=9)
    f_head = load_font(bold=True, size=13)
    f_body = load_font(size=11)
    pw = (W - 2 * MARGIN - 3 * 8) // 4
    ph = 110
    for i, (fid, place, head, body) in enumerate(FEATURED):
        r, c = divmod(i, 4)
        x = MARGIN + c * (pw + 8)
        y = y0 + r * (ph + 4)
        draw.rectangle([x, y, x + pw, y + ph], fill=PANEL, outline=PANEL_EDGE)
        tx = x + 8
        ty = y + 6
        draw.text((tx, ty), "%s  %s" % (fid, place), font=f_tag, fill=RED)
        ty += 14
        lines = wrap_words(draw, head.split(), [f_head] * len(head.split()), pw - 16)
        if len(lines) > 2:
            warn("featured %s headline %d lines" % (fid, len(lines)))
            lines = lines[:2]
        ty = draw_wrapped(draw, lines, tx, ty, 16)
        ty += 2
        blines = wrap_words(draw, body.split(), [f_body] * len(body.split()), pw - 16)
        if len(blines) > 4:
            warn("featured %s body %d lines" % (fid, len(blines)))
            blines = blines[:4]
        draw_wrapped(draw, blines, tx, ty, 13)
    return y0 + 2 * ph + 4


def draw_map(draw, y0, y1):
    f_lab = load_font(bold=True, size=10)
    f_dot = load_font(bold=True, size=8)
    draw.text((MARGIN, y0), "WORLD MAP -- WHERE TODAY'S TOP STORIES HAPPENED",
              font=f_lab, fill=NAVY)
    mx0, mx1 = MARGIN, W - MARGIN
    my0, my1 = y0 + 14, y1 - 2
    draw.rectangle([mx0, my0, mx1, my1], fill=MAP_OCEAN, outline=RULE)
    mw, mh = mx1 - mx0, my1 - my0

    def proj(lon, lat):
        return (mx0 + (lon + 180.0) / 360.0 * mw,
                my0 + (80.0 - lat) / 135.0 * mh)

    for poly in CONTINENTS:
        pts = [proj(lon, lat) for lon, lat in poly]
        draw.polygon(pts, fill=MAP_LAND, outline=(150, 148, 120))
    for label, lon, lat, dx, dy in MAP_DOTS:
        x, yy = proj(lon, lat)
        draw.ellipse([x - 5, yy - 5, x + 5, yy + 5], fill=MAP_DOT,
                     outline=(255, 255, 255))
        lx = min(max(x + dx, mx0 + 2), mx1 - 16)
        ly = min(max(yy + dy, my0 + 1), my1 - 10)
        draw.line([(x, yy), (lx + 7, ly + 4)], fill=MAP_DOT, width=1)
        draw.text((lx, ly), label, font=f_dot, fill=INK,
                  stroke_width=2, stroke_fill=MAP_OCEAN)


def draw_briefs(draw, y0, y1):
    f_sec = load_font(bold=True, size=11)
    f_bold = load_font(bold=True, size=11)
    f_reg = load_font(size=11)
    col_w = (W - 2 * MARGIN - 2 * 10) // 3
    for ci, groups in enumerate((BRIEFS_A, BRIEFS_B, BRIEFS_C)):
        x = MARGIN + ci * (col_w + 10)
        y = y0
        for header, items in groups:
            draw.rectangle([x, y, x + col_w, y + 17], fill=NAVY)
            draw.text((x + 6, y + 3), header, font=f_sec, fill=(255, 255, 255))
            y += 17 + 4
            for lead, rest in items:
                lines = mixed_block(draw, lead, rest, f_bold, f_reg,
                                    col_w - 4, 2, lead[:28])
                y = draw_wrapped(draw, lines, x + 2, y, 13)
                y += 3
            y += 2
        if y > y1:
            warn("briefs column %d overflows by %d px" % (ci + 1, y - y1))


def draw_footer(draw, y0):
    draw.rectangle([MARGIN, y0, W - MARGIN, y0 + 34], fill=FOOT_BG)
    f_txt = load_font(size=10)
    f_b = load_font(bold=True, size=10)
    lines = wrap_words(draw, DATE_CHECK.split(),
                       [f_txt] * len(DATE_CHECK.split()), W - 2 * MARGIN - 12)
    draw_wrapped(draw, lines, MARGIN + 6, y0 + 3, 12)
    draw.text((MARGIN + 6, y0 + 21), FOOTER_SRC, font=f_b, fill=MUTED)


def render():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    draw_masthead(draw)
    draw_wire(draw, 82, 116)
    y = draw_featured(draw, 122)
    draw_map(draw, y + 6, y + 76)
    draw_briefs(draw, y + 82, 984)
    draw_footer(draw, 988)
    return img


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    img = render()
    out_path = os.path.join(out_dir, "entry.png")
    img.save(out_path, format="PNG", optimize=True)
    for w in WARNINGS:
        print("WARNING: " + w, file=sys.stderr)
    print("wrote %s (%dx%d)" % (out_path, W, H))


if __name__ == "__main__":
    main()

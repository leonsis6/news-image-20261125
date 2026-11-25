#!/usr/bin/env python3
"""Render news-image-20261125: 'Wednesday 25 November 2026 in one picture'.

Code-rendered newspaper front page, 1024x1024, Python + PIL only.
All content comes from STORIES.md (verified wire reporting) — nothing invented.
Layout: superskie template — kicker, count line, masthead, UTC strip, numbers
strip, 3 illustrated leads, 10 illustrated cards, world map with pins 1-34,
numbered briefs 14-34, DATE CHECK, source footer.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 28
CW = W - 2 * MARGIN  # 968 content width

PAPER = (247, 242, 231)
INK = (20, 18, 16)
RED = (179, 35, 27)
NAVY = (31, 58, 95)
TEAL = (31, 110, 110)
OCHRE = (196, 138, 30)
GREY = (110, 104, 94)
FAINT = (232, 224, 208)
LAND = (222, 214, 196)
LAND_EDGE = (90, 80, 66)

SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"

_font_cache = {}


def F(path, size):
    key = (path, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(path, size)
    return _font_cache[key]


def wrap(text, font, width):
    """Greedy word wrap; returns list of lines."""
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if font.getlength(t) <= width:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text_h(font):
    return int(round(font.size * 1.24))


# ---------------------------------------------------------------- data
# (headline, body, tag) — facts from STORIES.md, shortened for layout only.
LEADS = [
    ("PUTIN VOWS RETALIATION AS UKRAINE HITS OIL PLANTS",
     "Putin says Ukraine keeps hitting Russian oil refineries despite Trump "
     "asking it to stop, and vows retaliation; processing is down 45% since "
     "late October.",
     "CONFIRMED \u00b7 Reuters"),
    ("HOUTHI STRIKE HITS RIYADH\u2019S TALLEST TOWER \u2014 11 WOUNDED",
     "A projectile hits Riyadh\u2019s PIF tower \u2014 the second strike in five "
     "days. Eleven wounded: 2 Saudi, 2 Indian, 3 Nepali, 4 Egyptian. The "
     "coalition blames the Houthis.",
     "CONFIRMED \u00b7 Reuters"),
    ("ANTHROPIC BREAKS BELOW ITS $83 IPO PRICE",
     "Shares close at $81.91, down 6.5% (low $75.61). The largest IPO in "
     "history ($81.3B) opened at $111.50 on 19 Nov and has fallen every day "
     "since; Nasdaq \u22121.4%.",
     "CONFIRMED \u00b7 Reuters / Dow Jones"),
]

CARDS = [
    ("HUAWEI GUILTY ON 10 OF 12 COUNTS",
     "Brooklyn jury finds trade-secret theft, bank/wire fraud and money "
     "laundering; cleared of RICO.",
     "CONFIRMED \u00b7 AP"),
    ("IRGC: FOURTH TANKER HITS MINE IN HORMUZ",
     "IRGC claims a fourth tanker hit a mine east of the strait. No ship "
     "names given; the claim is unverified.",
     "REPORTED \u00b7 Tasnim via ANI"),
    ("TRUMP TO UNVEIL NEW TARIFFS ON 16 PARTNERS",
     "Section 301 findings due Tue or Wed; new duties stack on old tariffs, "
     "China the main target.",
     "REPORTED \u00b7 Reuters"),
    ("BAGHDAD MOVES ON KURDISH OILFIELDS",
     "Baghdad to run Kurdish oilfields and take border crossings. KRG PM "
     "Barzani: \u201cin no way acceptable\u201d.",
     "CONFIRMED \u00b7 Reuters"),
    ("NATO SENDS AWACS TO POLAND",
     "AWACS deploy forward after three Kh-101 missiles fell in Poland; a "
     "Russian drone crossed overnight.",
     "CONFIRMED \u00b7 NATO"),
    ("M5.6 QUAKE SHAKES EASTERN NEPAL",
     "Taplejung, ~275 km east of Kathmandu; felt in India, Bhutan and "
     "Bangladesh. No casualties so far.",
     "CONFIRMED \u00b7 Nepal centre"),
    ("ENGLAND THRASH AUSTRALIA IN 2ND T20I",
     "Donald 85 off 32, Salt 58; England chase 185 in 13.1 overs, win by "
     "8 wickets. Series 1\u20131.",
     "CONFIRMED \u00b7 ESPNcricinfo"),
    ("KIM YO-JONG THREATENS TO SHUT SWISS OFFICE",
     "Pyongyang to shut the Swiss office after sanctions on the Songdowon "
     "camp. Kim: \u201can open hostile act\u201d.",
     "OFFICIAL \u00b7 KCNA"),
    ("SENEGAL GET THEIR AFCON TITLE BACK",
     "CAS annuls Morocco\u2019s 3\u20130 forfeit win; Senegal keep the 1\u20130 final. "
     "Morocco to appeal in Switzerland.",
     "CONFIRMED \u00b7 CAS / AP"),
    ("SOORYAVANSHI, 15, SMASHES 204 OFF 53 BALLS",
     "Fastest List A 100 (28 balls), 150 (40), 200 (52); 28 sixes, a record. "
     "India A chase 250 in 14.2 overs.",
     "CONFIRMED \u00b7 ICC"),
]

# (number, body, tag) — one line each in the brief columns.
BRIEFS = [
    (14, "BJP + Akali Dal reunite after 6 years for Punjab 2027 (117 seats).",
     "CONFIRMED \u00b7 ANI"),
    (15, "Israel kills Gaza security chief Naim Mohammed Abu Nahl in airstrike.",
     "REPORTED \u00b7 Al Manassa"),
    (16, "Gaza declares meningitis alert; 15 deaths in 2026, 5 since Sep.",
     "REPORTED \u00b7 Gaza Health Min."),
    (17, "Nvidia \u22125.2% premarket after +31.5% Monday; Nasdaq fut. \u22121.64%.",
     "CONFIRMED \u00b7 Reuters"),
    (18, "EU will not return to Russian gas even if there is peace \u2014 Jorgensen.",
     "CONFIRMED \u00b7 Riviera"),
    (19, "Today: UN Day for the Elimination of Violence against Women.",
     "OFFICIAL \u00b7 UN"),
    (20, "UK sanctions Houthis + 4 officials over alleged torture, sex violence.",
     "CONFIRMED \u00b7 Reuters"),
    (21, "Modi takes call from Germany\u2019s Merz on defence, tech, India\u2013EU FTA.",
     "CONFIRMED \u00b7 PIB India"),
    (22, "Indian markets shut for Guru Nanak Jayanti after Sensex \u22121,484 Mon.",
     "CONFIRMED \u00b7 Hindu BusinessLine"),
    (23, "UN: Russia rejects new Black Sea grain deal; 164 ship attacks Jun\u2013Oct.",
     "CONFIRMED \u00b7 UN"),
    (24, "Bus\u2013truck crash in Ras Al Khaimah, UAE, kills 11 on Al Watan Road.",
     "CONFIRMED \u00b7 Reuters"),
    (25, "Lahj, Yemen attack kills 26 (12 Houthi, 14 civilians, officials say).",
     "REPORTED \u00b7 AFP"),
    (26, "Bitcoin back below $60,000; Nov ETF outflows hit record $4.71M.",
     "CONFIRMED \u00b7 CoinDesk"),
    (27, "Gold \u221224.6% in 60 days to 23 Nov, steepest fall since 1982.",
     "CONFIRMED \u00b7 Bloomberg"),
    (28, "FAA: busiest US Thanksgiving in 16 years \u2014 417,000+ flights in 9 days.",
     "CONFIRMED \u00b7 FAA/DOT"),
    (29, "8th US\u2013Qatar Strategic Dialogue in Washington; minerals pact signed.",
     "OFFICIAL \u00b7 Qatar MFA"),
    (30, "S. African court jails Zimbabwean man 24 yrs for bid to fight in Ukraine.",
     "CONFIRMED \u00b7 AP"),
    (31, "SpaceX shares \u22125.7% Tuesday as AI stocks slide.",
     "CONFIRMED \u00b7 Motley Fool"),
    (32, "UN: 360,000+ displaced in Yemen since August as war escalates.",
     "CONFIRMED \u00b7 UN"),
    (33, "Yemen army claims 647 strikes in \u201cDawn of Yemen\u201d killed 122 Houthis.",
     "REPORTED \u00b7 Yemeni Army"),
    (34, "ICRC: shelter limits leave Gaza\u2019s displaced exposed to winter.",
     "CONFIRMED \u00b7 ICRC"),
]

UTC_ITEMS = [
    ("01:32", "M5.6 quake shakes Nepal"),
    ("02:59", "Bitcoin breaks below $60,000"),
    ("12:04", "UK sanctions Houthis + 4 officials"),
    ("15:08", "England seal 8-wicket T20I win"),
    ("16:19", "Trump tariffs: Section 301 findings due"),
    ("19:40", "Putin: retaliation \u201cinevitable\u201d"),
    ("21:00", "Anthropic closes $81.91, below IPO"),
]

NUMBERS = [
    ("11", "wounded in Riyadh tower strike"),
    ("45%", "fall in Russian refinery output since late Oct"),
    ("$81.91", "Anthropic close, below $83 IPO; \u22126.5%"),
    ("28", "sixes by Sooryavanshi in 204 off 53"),
    ("5.6", "magnitude of Nepal quake (EMSC 5.3)"),
    ("$4.71M", "Nov outflows, US spot Bitcoin ETFs"),
]

REGION_COUNTS = ("Middle East 10 \u00b7 N. America 7 \u00b7 Asia 6 \u00b7 Europe 4 "
                  "\u00b7 World 4 \u00b7 Africa 2 \u00b7 Oceania 1")

DATE_CHECK = ("LEFT OUT ON PURPOSE \u2014 in the 24 Nov edition: Merkury sinking; "
              "Nvidia / Huang; \u201cEl Chapo Isidro\u201d; Kh-101 in Poland; 49ers 35\u201310; "
              "Skubal $450M; Wembanyama 50; 153 drones; Hormuz tankers Sat. Too old: "
              "ICJ Rohingya ruling; EU 22nd sanctions; Sparta II damaged, NOT sunk. "
              "Not yet: Hera Dimorphos image; US PCE + GDP; Section 301 findings; "
              "OPEC+ (~29 Nov); Thanksgiving (26 Nov).")

FOOTER = ("All stories happened or were first reported Tue 24 Nov 2026. Sources: "
          "Reuters \u00b7 AP \u00b7 AFP \u00b7 ANI \u00b7 ICC \u00b7 FAA/DOT \u00b7 Qatar MFA \u00b7 "
          "PIB India \u00b7 UN \u00b7 UKMTO. CONFIRMED = wire-confirmed \u00b7 OFFICIAL = "
          "on the record \u00b7 REPORTED = single outlet.")

# pins: (number, lon, lat, dx, dy) — offsets declutter clusters.
PINS = [
    (1, 50, 55, 0, 0), (2, 47, 24.7, 0, 0), (3, -122, 37.7, 0, -6),
    (4, -74, 40.7, -4, -8), (5, 56.5, 26.5, 6, 6), (6, -77, 39, -10, 6),
    (7, 44, 33, 0, -6), (8, 19, 52, 0, 0), (9, 88, 27.7, 0, 0),
    (10, 153, -28, 0, 0), (11, 127, 39, 0, 0), (12, -17, 14.7, 0, 0),
    (13, 51.5, 25.3, 10, -4), (14, 76, 30.9, 0, 0), (15, 34.5, 31.5, -8, -8),
    (16, 34.5, 31.5, 8, -10), (17, -122, 37.4, -2, 8), (18, 4.4, 50.8, -8, -4),
    (19, -74, 40.7, 8, 2), (20, -0.1, 51.5, 6, -6), (21, 77, 28.6, -6, 6),
    (22, 72.8, 19, -10, -2), (23, 33, 43, 0, 0), (24, 56, 25.8, -6, -8),
    (25, 45, 13, -8, 4), (26, -74, 40.7, 2, 10), (27, -0.1, 51.5, -8, 6),
    (28, -95, 38, 0, 0), (29, -77, 39, 8, -8), (30, 28, -26, 0, 0),
    (31, -118, 34, 6, -4), (32, 45, 15, 10, -6), (33, 45, 15, 2, 10),
    (34, 34.5, 31.5, -2, 10),
]

CONTINENTS = [
    # North America
    [(-168, 66), (-158, 71), (-140, 70), (-125, 72), (-110, 73), (-95, 80),
     (-85, 76), (-80, 73), (-70, 62), (-60, 55), (-55, 47), (-65, 44),
     (-70, 42), (-75, 35), (-80, 26), (-84, 30), (-90, 21), (-97, 16),
     (-105, 20), (-110, 24), (-120, 32), (-125, 40), (-125, 49), (-135, 58),
     (-150, 60), (-165, 60)],
    # South America
    [(-80, 10), (-75, 11), (-65, 10), (-60, 5), (-52, 4), (-50, 0),
     (-44, -3), (-35, -6), (-38, -15), (-40, -22), (-48, -28), (-55, -35),
     (-62, -41), (-68, -50), (-70, -54), (-73, -45), (-73, -35), (-71, -20),
     (-77, -12), (-80, -5), (-81, 0)],
    # Africa
    [(-17, 15), (-15, 25), (-10, 31), (-5, 35), (0, 36), (10, 37), (15, 32),
     (20, 32), (30, 31), (33, 27), (37, 22), (39, 18), (43, 12), (48, 11),
     (51, 12), (46, 5), (41, -2), (40, -10), (36, -18), (33, -26), (28, -33),
     (20, -35), (17, -30), (14, -22), (12, -12), (9, 4), (0, 6), (-8, 5),
     (-13, 8), (-17, 12)],
    # Europe
    [(-10, 36), (-9, 38), (-9, 43), (-2, 44), (-2, 48), (-4, 50), (0, 51),
     (3, 53), (7, 54), (8, 57), (10, 59), (12, 56), (18, 56), (21, 55),
     (24, 58), (28, 60), (30, 62), (30, 66), (25, 70), (20, 70), (15, 68),
     (12, 65), (10, 62), (5, 58), (5, 55), (0, 52), (-3, 48), (-5, 43),
     (-9, 38)],
    # Asia
    [(30, 62), (35, 66), (45, 68), (55, 69), (65, 69), (75, 72), (85, 74),
     (95, 76), (105, 77), (115, 73), (125, 72), (135, 72), (145, 72),
     (155, 70), (165, 69), (175, 66), (178, 65), (170, 60), (162, 58),
     (158, 52), (150, 59), (142, 52), (141, 45), (138, 38), (132, 35),
     (128, 33), (122, 30), (118, 25), (112, 22), (108, 18), (105, 10),
     (103, 8), (100, 6), (98, 10), (95, 16), (92, 21), (89, 22), (86, 20),
     (82, 15), (80, 10), (77, 8), (74, 12), (72, 20), (68, 22), (65, 25),
     (60, 25), (57, 26), (54, 27), (51, 28), (48, 29), (45, 30), (42, 31),
     (38, 32), (36, 36), (33, 36), (30, 36), (28, 40), (27, 41), (23, 40),
     (22, 37), (26, 39), (30, 41), (30, 46), (30, 52), (28, 56), (28, 60)],
    # Australia
    [(113, -22), (114, -28), (115, -33), (118, -35), (124, -33), (129, -32),
     (132, -32), (135, -35), (138, -35), (140, -38), (145, -38), (150, -37),
     (153, -32), (153, -27), (150, -22), (146, -19), (142, -15), (142, -11),
     (137, -12), (135, -15), (132, -12), (130, -13), (126, -14), (122, -17),
     (118, -20), (114, -22)],
    # Greenland
    [(-45, 60), (-40, 64), (-32, 68), (-25, 70), (-20, 74), (-25, 76),
     (-35, 80), (-45, 79), (-55, 76), (-58, 72), (-55, 68), (-52, 64),
     (-48, 60)],
    # Japan
    [(130, 31), (131, 33), (134, 34), (137, 35), (139, 35), (140, 38),
     (141, 40), (142, 43), (144, 44), (143, 42), (141, 39), (140, 36),
     (137, 34), (134, 33), (131, 32)],
    # UK
    [(-5, 50), (-3, 53), (-5, 55), (-3, 58), (-1, 57), (1, 53), (1, 51),
     (-2, 50), (-4, 50)],
    # SE Asia islands (rough)
    [(95, 5), (98, 2), (100, -2), (103, -4), (106, -6), (110, -7),
     (114, -8), (118, -9), (120, -10), (119, -5), (116, -2), (112, 1),
     (108, 2), (104, 1), (101, 3), (98, 6), (95, 6)],
    [(117, -1), (120, 0), (123, 1), (122, 4), (120, 6), (118, 5),
     (116, 3), (115, 0), (116, -3)],
    [(131, -1), (133, -2), (136, -3), (139, -4), (141, -6), (138, -8),
     (134, -7), (132, -4)],
]

# ---------------------------------------------------------------- illustrations
# Each takes (d, x0, y0, x1, y1) and draws one flat geometric scene.
# All geometry is fractions of the box (w, h) plus a unit u = h/80, so the
# same drawing works in a tall lead box and a short card strip. No text
# inside illustrations; no photos.

def _sky(d, x0, y0, x1, y1, top, bot):
    d.rectangle([x0, y0, x1, y1], fill=top)
    d.rectangle([x0, (y0 + y1) // 2, x1, y1], fill=bot)


def illo_01(d, x0, y0, x1, y1):  # oil refinery, flames
    w, h = x1 - x0, y1 - y0
    u = max(0.25, h / 80.0)
    _sky(d, x0, y0, x1, y1, (214, 226, 232), (196, 188, 168))
    gy = y1 - int(h * 0.16)
    d.rectangle([x0, gy, x1, y1], fill=(120, 110, 90))
    for i, tw in enumerate((0.16, 0.11, 0.13)):
        tx = x0 + int(w * (0.14 + i * 0.28))
        twpx = int(w * tw)
        d.rectangle([tx, y0 + int(h * 0.30), tx + twpx, gy], fill=NAVY)
        d.rectangle([tx - 3, y0 + int(h * 0.26), tx + twpx + 3, y0 + int(h * 0.30)],
                    fill=(60, 80, 115))
        fx = tx + twpx // 2
        d.polygon([(fx - int(9 * u), y0 + int(h * 0.26)),
                   (fx + int(9 * u), y0 + int(h * 0.26)),
                   (fx, y0 + int(h * 0.06))], fill=(230, 120, 30))
        d.polygon([(fx - int(4 * u), y0 + int(h * 0.26)),
                   (fx + int(4 * u), y0 + int(h * 0.26)),
                   (fx, y0 + int(h * 0.14))], fill=(245, 200, 60))
    d.rectangle([x0 + int(w * 0.10), gy - int(6 * u), x1 - int(w * 0.08), gy - int(2 * u)],
                fill=(90, 84, 74))
    for cx, cy, r in ((0.72, 0.16, 6), (0.80, 0.11, 7), (0.88, 0.18, 5)):
        rr = int(r * u)
        d.ellipse([x0 + int(w * cx) - rr, y0 + int(h * cy) - rr,
                   x0 + int(w * cx) + rr, y0 + int(h * cy) + rr], fill=(150, 148, 142))


def illo_02(d, x0, y0, x1, y1):  # Riyadh tower, projectile streak
    w, h = x1 - x0, y1 - y0
    u = max(0.25, h / 80.0)
    _sky(d, x0, y0, x1, y1, (238, 228, 205), (226, 210, 180))
    cx = x0 + int(w * 0.42)
    top = y0 + int(h * 0.08)
    d.polygon([(cx - 26, y1), (cx - 12, top), (cx + 12, top), (cx + 26, y1)],
              fill=NAVY)
    for i in range(5):
        yy = top + int(h * 0.14) + i * int(h * 0.15)
        d.rectangle([cx - 20 + i, yy, cx + 20 - i, yy + max(2, int(3 * u))],
                    fill=(196, 164, 90))
    d.rectangle([x0, y1 - max(3, int(6 * u)), x1, y1], fill=(120, 110, 90))
    d.line([x1 - int(w * 0.06), y0 + int(h * 0.18),
            x0 + int(w * 0.62), y0 + int(h * 0.42)], fill=RED, width=max(2, int(4 * u)))
    bx, by = x0 + int(w * 0.62), y0 + int(h * 0.42)
    import math
    for ang in range(0, 360, 45):
        a = math.radians(ang)
        d.line([bx, by, bx + int(11 * u * math.cos(a)), by + int(11 * u * math.sin(a))],
               fill=(230, 120, 30), width=2)
    rr = max(2, int(4 * u))
    d.ellipse([bx - rr, by - rr, bx + rr, by + rr], fill=RED)


def illo_03(d, x0, y0, x1, y1):  # stock chart falling below IPO line
    w, h = x1 - x0, y1 - y0
    u = max(0.25, h / 80.0)
    _sky(d, x0, y0, x1, y1, (235, 232, 226), (228, 222, 210))
    for i in range(1, 4):
        yy = y0 + int(h * i / 4)
        d.line([x0 + 6, yy, x1 - 6, yy], fill=(200, 194, 182), width=1)
    iy = y0 + int(h * 0.34)
    for xx in range(x0 + 6, x1 - 6, 10):
        d.line([xx, iy, min(xx + 6, x1 - 6), iy], fill=NAVY, width=2)
    pts = [(0.06, 0.22), (0.22, 0.30), (0.38, 0.28), (0.54, 0.44),
           (0.70, 0.58), (0.86, 0.74), (0.96, 0.86)]
    xy = [(x0 + int(w * px), y0 + int(h * py)) for px, py in pts]
    d.line(xy, fill=RED, width=max(2, int(4 * u)), joint="curve")
    for px, py in xy:
        rr = max(2, int(3 * u))
        d.ellipse([px - rr, py - rr, px + rr, py + rr], fill=RED)
    ex, ey = xy[-1]
    ah = max(6, int(12 * u))
    d.polygon([(ex, ey), (ex - ah, ey - 2), (ex - 2, ey - ah)], fill=RED)


def illo_04(d, x0, y0, x1, y1):  # courthouse + gavel
    w, h = x1 - x0, y1 - y0
    u = max(0.25, h / 80.0)
    _sky(d, x0, y0, x1, y1, (232, 226, 214), (220, 212, 196))
    cx = x0 + w // 2
    d.polygon([(cx - int(w * 0.34), y0 + int(h * 0.34)),
               (cx + int(w * 0.34), y0 + int(h * 0.34)),
               (cx, y0 + int(h * 0.10))], fill=NAVY)
    cr = max(3, int(7 * u))
    d.ellipse([cx - cr, y0 + int(h * 0.16) - cr, cx + cr, y0 + int(h * 0.16) + cr],
              fill=(196, 164, 90))
    for i in range(4):
        colx = x0 + int(w * (0.16 + i * 0.19))
        d.rectangle([colx, y0 + int(h * 0.36), colx + int(w * 0.09), y1 - int(h * 0.18)],
                    fill=(244, 238, 224), outline=NAVY, width=2)
    d.rectangle([x0 + int(w * 0.08), y1 - int(h * 0.18), x1 - int(w * 0.08), y1 - int(h * 0.12)],
                fill=NAVY)
    d.rectangle([x0 + int(w * 0.05), y1 - int(h * 0.11), x1 - int(w * 0.05), y1 - int(h * 0.05)],
                fill=NAVY)
    gx, gy = x1 - int(w * 0.22), y1 - int(h * 0.30)
    gl = max(10, int(26 * u))
    d.line([gx, gy, gx + gl, gy - int(14 * u)], fill=(120, 80, 40),
           width=max(2, int(5 * u)))
    hs = max(5, int(12 * u))
    d.rectangle([gx - hs, gy - int(18 * u), gx + 2, gy - int(6 * u)], fill=(120, 80, 40))


def illo_05(d, x0, y0, x1, y1):  # tanker + mine in the strait
    w, h = x1 - x0, y1 - y0
    u = max(0.25, h / 80.0)
    _sky(d, x0, y0, x1, y1, (228, 236, 238), (198, 220, 228))
    wy = y0 + int(h * 0.55)
    d.rectangle([x0, wy, x1, y1], fill=(70, 120, 150))
    hx0, hx1 = x0 + int(w * 0.06), x0 + int(w * 0.62)
    d.polygon([(hx0, wy - int(h * 0.14)), (hx1, wy - int(h * 0.14)),
               (hx1 + 14, wy + 2), (hx0, wy + 2)], fill=(30, 40, 60))
    for i, c in enumerate((RED, TEAL, OCHRE)):
        d.rectangle([hx0 + 8 + i * 26, wy - int(h * 0.34),
                     hx0 + 30 + i * 26, wy - int(h * 0.14)], fill=c)
    d.rectangle([hx0 + 8, wy - int(h * 0.48), hx0 + 34, wy - int(h * 0.34)],
                fill=(240, 238, 230))
    mx, my = x0 + int(w * 0.82), y0 + int(h * 0.42)
    import math
    spike = max(8, int(20 * u))
    for k in range(8):
        a = math.radians(k * 45)
        d.line([mx, my, mx + int(spike * math.cos(a)), my + int(spike * math.sin(a))],
               fill=(30, 30, 30), width=max(2, int(3 * u)))
    rr = max(4, int(11 * u))
    d.ellipse([mx - rr, my - rr, mx + rr, my + rr], fill=(30, 30, 30))
    ir = max(2, int(4 * u))
    d.ellipse([mx - ir, my - ir, mx + ir, my + ir], fill=RED)
    for yy in (wy + int(h * 0.12), wy + int(h * 0.26)):
        for xx in range(x0 + 4, x1 - 10, 22):
            d.arc([xx, yy, xx + 20, yy + max(4, int(10 * u))], 180, 360,
                  fill=(240, 244, 246), width=2)


def illo_06(d, x0, y0, x1, y1):  # tariff document + percent
    w, h = x1 - x0, y1 - y0
    _sky(d, x0, y0, x1, y1, (236, 230, 220), (228, 220, 206))
    dx0, dy0 = x0 + int(w * 0.08), y0 + int(h * 0.10)
    dx1, dy1 = x0 + int(w * 0.58), y1 - int(h * 0.10)
    d.rectangle([dx0, dy0, dx1, dy1], fill=(250, 248, 242), outline=NAVY, width=2)
    d.polygon([(dx1 - 14, dy0), (dx1, dy0), (dx1, dy0 + 14)], fill=FAINT)
    for i in range(4):
        yy = dy0 + 16 + i * 12
        if yy > dy1 - 6:
            break
        d.rectangle([dx0 + 8, yy, dx1 - 8 - (10 if i == 3 else 0), yy + 4],
                    fill=(160, 154, 142))
    d.rectangle([dx0 + 8, dy0 + 8, dx0 + 26, dy0 + 8], fill=RED)
    pct = F(SERIF_B, max(9, int(h * 0.52)))
    d.text((x0 + int(w * 0.60), y0 + int(h * 0.16)), "%", font=pct, fill=RED)
    bx = x0 + int(w * 0.62)
    for i, bh in enumerate((0.16, 0.26, 0.38)):
        d.rectangle([bx + i * 16, y1 - int(h * 0.12) - int(h * bh),
                     bx + i * 16 + 11, y1 - int(h * 0.12)], fill=NAVY if i < 2 else RED)


def illo_07(d, x0, y0, x1, y1):  # oil derrick + pumpjack
    w, h = x1 - x0, y1 - y0
    u = max(0.25, h / 80.0)
    _sky(d, x0, y0, x1, y1, (240, 228, 200), (228, 210, 172))
    sr = max(4, int(h * 0.11))
    d.ellipse([x1 - int(w * 0.30) - sr, y0 + int(h * 0.06) - sr,
               x1 - int(w * 0.30) + sr, y0 + int(h * 0.06) + sr], fill=OCHRE)
    gy = y1 - int(h * 0.14)
    d.rectangle([x0, gy, x1, y1], fill=(150, 128, 92))
    bx = x0 + int(w * 0.16)
    lw = max(2, int(4 * u))
    d.line([bx, gy, bx + 16, y0 + int(h * 0.14)], fill=NAVY, width=lw)
    d.line([bx + 44, gy, bx + 28, y0 + int(h * 0.14)], fill=NAVY, width=lw)
    d.line([bx + 4, y0 + int(h * 0.44), bx + 40, y0 + int(h * 0.44)], fill=NAVY, width=3)
    d.line([bx + 8, y0 + int(h * 0.66), bx + 36, y0 + int(h * 0.66)], fill=NAVY, width=3)
    px = x0 + int(w * 0.62)
    d.rectangle([px, gy - int(h * 0.30), px + 6, gy], fill=(40, 40, 40))
    d.line([px - 22, gy - int(h * 0.34), px + 34, gy - int(h * 0.48)],
           fill=(40, 40, 40), width=max(3, int(5 * u)))
    d.line([px + 30, gy - int(h * 0.46), px + 30, gy - int(h * 0.20)],
           fill=(40, 40, 40), width=3)
    d.rectangle([px - 26, gy - int(h * 0.38), px - 16, gy - int(h * 0.30)],
                fill=(40, 40, 40))


def illo_08(d, x0, y0, x1, y1):  # AWACS plane with radar dome
    w, h = x1 - x0, y1 - y0
    u = max(0.25, h / 80.0)
    _sky(d, x0, y0, x1, y1, (210, 224, 234), (196, 212, 226))
    cy = y0 + int(h * 0.52)
    d.ellipse([x0 + int(w * 0.10), cy - int(h * 0.15),
               x1 - int(w * 0.08), cy + int(h * 0.15)], fill=NAVY)
    d.polygon([(x1 - int(w * 0.10), cy - int(h * 0.12)),
               (x1 - int(w * 0.02), cy),
               (x1 - int(w * 0.10), cy + int(h * 0.12))], fill=NAVY)
    d.polygon([(x0 + int(w * 0.42), cy - int(h * 0.07)),
               (x0 + int(w * 0.58), cy - int(h * 0.07)),
               (x0 + int(w * 0.66), cy - int(h * 0.30)),
               (x0 + int(w * 0.50), cy - int(h * 0.30))], fill=(60, 80, 115))
    d.polygon([(x0 + int(w * 0.44), cy + int(h * 0.07)),
               (x0 + int(w * 0.56), cy + int(h * 0.07)),
               (x0 + int(w * 0.62), cy + int(h * 0.26)),
               (x0 + int(w * 0.50), cy + int(h * 0.26))], fill=(60, 80, 115))
    d.polygon([(x0 + int(w * 0.12), cy - int(h * 0.10)),
               (x0 + int(w * 0.20), cy - int(h * 0.10)),
               (x0 + int(w * 0.16), cy - int(h * 0.30)),
               (x0 + int(w * 0.10), cy - int(h * 0.30))], fill=(60, 80, 115))
    dx = x0 + int(w * 0.50)
    dw = max(8, int(w * 0.11))
    d.ellipse([dx - dw // 2, cy - int(h * 0.42), dx + dw // 2, cy - int(h * 0.14)],
              fill=(240, 238, 230), outline=NAVY, width=2)
    d.line([dx, cy - int(h * 0.14), dx, cy - int(h * 0.07)], fill=NAVY, width=3)
    for i in range(4):
        wx = x0 + int(w * (0.62 + i * 0.06))
        wr = max(2, int(3 * u))
        d.ellipse([wx, cy - wr, wx + 2 * wr, cy + wr], fill=(200, 220, 235))
    for sx, sy in ((0.12, 0.18), (0.88, 0.22), (0.80, 0.80)):
        px, py = x0 + int(w * sx), y0 + int(h * sy)
        sl = max(3, int(5 * u))
        d.line([px - sl, py, px + sl, py], fill=RED, width=2)
        d.line([px, py - sl, px, py + sl], fill=RED, width=2)


def illo_09(d, x0, y0, x1, y1):  # mountains + quake crack
    w, h = x1 - x0, y1 - y0
    u = max(0.25, h / 80.0)
    _sky(d, x0, y0, x1, y1, (230, 228, 222), (214, 208, 196))
    d.polygon([(x0, y1), (x0 + int(w * 0.30), y0 + int(h * 0.18)),
               (x0 + int(w * 0.55), y1)], fill=(110, 116, 124))
    d.polygon([(x0 + int(w * 0.30), y0 + int(h * 0.18)),
               (x0 + int(w * 0.40), y0 + int(h * 0.34)),
               (x0 + int(w * 0.20), y0 + int(h * 0.34))], fill=(250, 250, 248))
    d.polygon([(x0 + int(w * 0.45), y1), (x0 + int(w * 0.72), y0 + int(h * 0.08)),
               (x1, y1)], fill=(70, 80, 96))
    d.polygon([(x0 + int(w * 0.72), y0 + int(h * 0.08)),
               (x0 + int(w * 0.82), y0 + int(h * 0.26)),
               (x0 + int(w * 0.62), y0 + int(h * 0.26))], fill=(250, 250, 248))
    cx = x0 + int(w * 0.58)
    pts = [(cx, y0 + 4), (cx - 8, y0 + int(h * 0.25)), (cx + 8, y0 + int(h * 0.45)),
           (cx - 6, y0 + int(h * 0.65)), (cx + 4, y0 + int(h * 0.85)), (cx, y1 - 4)]
    d.line(pts, fill=RED, width=max(2, int(4 * u)), joint="curve")
    for rx, ry, r in ((0.30, 0.55, 4), (0.82, 0.60, 5), (0.68, 0.78, 3)):
        rr = max(2, int(r * u))
        d.ellipse([x0 + int(w * rx) - rr, y0 + int(h * ry) - rr,
                   x0 + int(w * rx) + rr, y0 + int(h * ry) + rr], fill=(90, 88, 84))


def illo_10(d, x0, y0, x1, y1):  # cricket: bat, ball, stumps
    w, h = x1 - x0, y1 - y0
    u = max(0.25, h / 80.0)
    _sky(d, x0, y0, x1, y1, (206, 224, 196), (190, 212, 178))
    gy = y1 - int(h * 0.14)
    d.rectangle([x0, gy, x1, y1], fill=(150, 170, 120))
    sx = x0 + int(w * 0.16)
    sh = int(h * 0.32)
    for i in range(3):
        d.rectangle([sx + i * 9, gy - sh, sx + i * 9 + 6, gy], fill=OCHRE)
    d.rectangle([sx, gy - sh - 4, sx + 24, gy - sh], fill=OCHRE)
    bx, by = x0 + int(w * 0.52), y0 + int(h * 0.62)
    d.polygon([(bx - int(w * 0.04), by + int(h * 0.20)),
               (bx + int(w * 0.04), by + int(h * 0.18)),
               (bx + int(w * 0.14), by - int(h * 0.30)),
               (bx + int(w * 0.06), by - int(h * 0.34))],
              fill=(244, 238, 224), outline=NAVY, width=2)
    d.line([bx + int(w * 0.10), by - int(h * 0.32),
            bx + int(w * 0.18), by - int(h * 0.52)], fill=NAVY,
           width=max(2, int(5 * u)))
    ballx, bally = x0 + int(w * 0.84), y0 + int(h * 0.30)
    br = max(3, int(h * 0.11))
    d.ellipse([ballx - br, bally - br, ballx + br, bally + br], fill=RED)
    d.arc([ballx - br, bally - br, ballx + br, bally + br], 200, 340,
          fill=(250, 250, 248), width=2)
    for i, yy in enumerate((0.22, 0.30, 0.38)):
        d.line([x0 + int(w * 0.60), y0 + int(h * yy), x0 + int(w * 0.72), y0 + int(h * yy)],
               fill=(255, 255, 255), width=2)


def illo_11(d, x0, y0, x1, y1):  # diplomatic office, closed
    w, h = x1 - x0, y1 - y0
    u = max(0.25, h / 80.0)
    _sky(d, x0, y0, x1, y1, (234, 230, 224), (222, 216, 202))
    bx0, bx1 = x0 + int(w * 0.18), x1 - int(w * 0.18)
    by0, by1 = y0 + int(h * 0.10), y1 - int(h * 0.10)
    d.rectangle([bx0, by0, bx1, by1], fill=NAVY)
    gx0, gy0 = bx0 + int(w * 0.05), by0 + int(h * 0.08)
    gx1, gy1 = bx1 - int(w * 0.05), by0 + int(h * 0.52)
    cell_w = (gx1 - gx0) / 4.0
    cell_h = (gy1 - gy0) / 3.0
    for r in range(3):
        for c in range(4):
            wx = int(gx0 + c * cell_w + 2)
            wy = int(gy0 + r * cell_h + 2)
            ww = max(2, int(cell_w) - 4)
            wh = max(2, int(cell_h) - 2)
            d.rectangle([wx, wy, wx + ww, wy + wh], fill=(240, 232, 200))
    doorx = (bx0 + bx1) // 2
    dw = max(8, int(w * 0.13))
    dh = int(h * 0.30)
    d.rectangle([doorx - dw // 2, by1 - dh, doorx + dw // 2, by1],
                fill=(240, 232, 200))
    cx, cy = doorx, by1 - dh // 2
    cr = max(5, int(h * 0.18))
    d.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], outline=RED,
              width=max(2, int(4 * u)))
    d.line([cx - int(cr * 0.7), cy + int(cr * 0.7),
            cx + int(cr * 0.7), cy - int(cr * 0.7)], fill=RED,
           width=max(2, int(4 * u)))


def illo_12(d, x0, y0, x1, y1):  # trophy + football
    w, h = x1 - x0, y1 - y0
    u = max(0.25, h / 80.0)
    _sky(d, x0, y0, x1, y1, (238, 232, 214), (228, 220, 198))
    cx = x0 + int(w * 0.38)
    ty = y0 + int(h * 0.10)
    bh = int(h * 0.42)
    d.polygon([(cx - int(w * 0.17), ty), (cx + int(w * 0.17), ty),
               (cx + int(w * 0.12), ty + bh), (cx - int(w * 0.12), ty + bh)],
              fill=(212, 160, 40))
    d.arc([cx - int(w * 0.26), ty - int(h * 0.02), cx - int(w * 0.09), ty + int(h * 0.26)],
          90, 270, fill=(212, 160, 40), width=max(2, int(5 * u)))
    d.arc([cx + int(w * 0.09), ty - int(h * 0.02), cx + int(w * 0.26), ty + int(h * 0.26)],
          270, 90, fill=(212, 160, 40), width=max(2, int(5 * u)))
    d.rectangle([cx - int(w * 0.025), ty + bh, cx + int(w * 0.025), ty + bh + int(h * 0.18)],
                fill=(212, 160, 40))
    d.rectangle([cx - int(w * 0.12), ty + bh + int(h * 0.18),
                 cx + int(w * 0.12), ty + bh + int(h * 0.28)], fill=(160, 110, 20))
    fx, fy = x0 + int(w * 0.76), y0 + int(h * 0.66)
    fr = max(4, int(h * 0.22))
    d.ellipse([fx - fr, fy - fr, fx + fr, fy + fr], fill=(250, 250, 248),
              outline=INK, width=2)
    pr = max(2, int(fr * 0.4))
    d.polygon([(fx, fy - pr), (fx + pr, fy - int(pr * 0.3)), (fx + int(pr * 0.6), fy + pr),
               (fx - int(pr * 0.6), fy + pr), (fx - pr, fy - int(pr * 0.3))], fill=INK)
    for px, py in ((fx - int(fr * 0.7), fy - int(fr * 0.55)),
                   (fx + int(fr * 0.7), fy - int(fr * 0.55)), (fx, fy + int(fr * 0.75))):
        rr = max(1, int(fr * 0.16))
        d.ellipse([px - rr, py - rr, px + rr, py + rr], fill=INK)
    for px, py, c in ((0.10, 0.20, RED), (0.88, 0.16, TEAL), (0.92, 0.86, OCHRE),
                      (0.08, 0.82, RED)):
        rr = max(2, int(3 * u))
        d.ellipse([x0 + int(w * px) - rr, y0 + int(h * py) - rr,
                   x0 + int(w * px) + rr, y0 + int(h * py) + rr], fill=c)


def illo_13(d, x0, y0, x1, y1):  # sixes: bat + flying ball
    w, h = x1 - x0, y1 - y0
    u = max(0.25, h / 80.0)
    _sky(d, x0, y0, x1, y1, (206, 224, 196), (190, 212, 178))
    gy = y1 - int(h * 0.14)
    d.rectangle([x0, gy, x1, y1], fill=(150, 170, 120))
    sx = x0 + int(w * 0.10)
    sh = int(h * 0.32)
    for i in range(3):
        d.rectangle([sx + i * 9, gy - sh, sx + i * 9 + 6, gy], fill=OCHRE)
    bx, by = x0 + int(w * 0.44), y0 + int(h * 0.62)
    d.polygon([(bx - int(w * 0.05), by + int(h * 0.20)),
               (bx + int(w * 0.05), by + int(h * 0.18)),
               (bx + int(w * 0.16), by - int(h * 0.34)),
               (bx + int(w * 0.06), by - int(h * 0.38))],
              fill=(244, 238, 224), outline=NAVY, width=2)
    d.line([bx + int(w * 0.11), by - int(h * 0.36),
            bx + int(w * 0.20), by - int(h * 0.52)], fill=NAVY,
           width=max(2, int(5 * u)))
    ballx, bally = x0 + int(w * 0.82), y0 + int(h * 0.22)
    br = max(3, int(h * 0.11))
    for i in range(3):
        yy = bally + (i - 1) * max(4, int(12 * u))
        d.line([ballx - int(w * 0.25), yy, ballx - int(w * 0.09), yy],
               fill=(255, 255, 255), width=3)
    d.ellipse([ballx - br, bally - br, ballx + br, bally + br], fill=RED)
    d.arc([ballx - br, bally - br, ballx + br, bally + br], 200, 340,
          fill=(250, 250, 248), width=2)
    for i in range(4):
        px = x0 + int(w * (0.14 + i * 0.12))
        py = y0 + int(h * 0.82)
        rr = max(2, int(h * 0.06))
        d.ellipse([px - rr, py - rr, px + rr, py + rr], fill=RED)


ILLOS = [illo_01, illo_02, illo_03, illo_04, illo_05, illo_06, illo_07,
         illo_08, illo_09, illo_10, illo_11, illo_12, illo_13]

# ---------------------------------------------------------------- layout

def fs(base, s):
    return max(7, int(round(base * s)))


def section_header(d, y, text, s, right=None):
    f = F(SANS_B, fs(12, s))
    d.text((MARGIN, y), text, font=f, fill=RED)
    tw = f.getlength(text)
    ry = y + f.size // 2
    x_end = W - MARGIN
    if right:
        fr = F(SANS, fs(10, s))
        rw = fr.getlength(right)
        d.text((x_end - rw, y + 1), right, font=fr, fill=INK)
        x_end = x_end - rw - 10
    d.line([MARGIN + tw + 8, ry, x_end, ry], fill=INK, width=1)
    return y + fs(12, s) + 4


def draw_centered(d, y, text, font, fill):
    w = font.getlength(text)
    d.text(((W - w) / 2, y), text, font=font, fill=fill)
    return y + font.size + 2


def render_page(s):
    warns = []
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    y = 10

    # kicker + count line + masthead
    y = draw_centered(d, y, "ONE DAY OF WORLD NEWS, ONE PICTURE",
                      F(SANS_B, fs(13, s)), RED)
    y = draw_centered(d, y, "34 STORIES \u00b7 6 CONTINENTS + WORLD \u00b7 "
                      "13 FIELDS \u00b7 ALL FROM TUESDAY", F(SANS, fs(11, s)), INK)
    y += 1
    y = draw_centered(d, y, "WEDNESDAY 25 NOVEMBER 2026",
                      F(SERIF_B, fs(38, s)), INK)
    y += 1
    d.line([MARGIN, y, W - MARGIN, y], fill=INK, width=2)
    y += 4
    d.line([MARGIN, y, W - MARGIN, y], fill=INK, width=1)
    y += 7

    # ---- THE DAY IN UTC
    y = section_header(d, y, "THE DAY IN UTC", s)
    col_w = CW / 7.0
    f_time = F(SANS_B, fs(11, s))
    f_lab = F(SANS, fs(10, s))
    lh = text_h(f_lab)
    utc_h = text_h(f_time) + 2 * lh
    for i, (t, label) in enumerate(UTC_ITEMS):
        x = MARGIN + i * col_w
        d.text((x + 2, y), t, font=f_time, fill=RED)
        lines = wrap(label, f_lab, col_w - 6)
        if len(lines) > 2:
            warns.append(f"UTC item {i + 1} wraps to {len(lines)} lines")
        for j, ln in enumerate(lines[:2]):
            d.text((x + 2, y + text_h(f_time) + j * lh), ln, font=f_lab, fill=INK)
    y += utc_h + 5

    # ---- THE DAY IN NUMBERS
    y = section_header(d, y, "THE DAY IN NUMBERS", s)
    ncol_w = CW / 6.0
    f_val = F(SERIF_B, fs(22, s))
    f_nlab = F(SANS, fs(10, s))
    nlh = text_h(f_nlab)
    num_h = text_h(f_val) + 2 * nlh
    for i, (val, label) in enumerate(NUMBERS):
        x = MARGIN + i * ncol_w
        d.text((x + 2, y), val, font=f_val, fill=RED)
        lines = wrap(label, f_nlab, ncol_w - 6)
        if len(lines) > 2:
            warns.append(f"number {i + 1} label wraps to {len(lines)} lines")
        for j, ln in enumerate(lines[:2]):
            d.text((x + 2, y + text_h(f_val) + j * nlh), ln, font=f_nlab, fill=INK)
    y += num_h + 5
    d.line([MARGIN, y, W - MARGIN, y], fill=INK, width=1)
    y += 7

    # ---- 3 LEADS
    lead_gap = 10
    lead_w = (CW - 2 * lead_gap) // 3
    pad = 8
    illo_h = int(80 * s)
    f_lhead = F(SERIF_B, fs(19, s))
    f_lbody = F(SANS, fs(11, s))
    f_ltag = F(SANS_B, fs(10, s))
    lead_blocks = []
    for n, (head, body, tag) in enumerate(LEADS, start=1):
        hl = wrap(head, f_lhead, lead_w - 2 * pad)
        bl = wrap(body, f_lbody, lead_w - 2 * pad)
        if len(hl) > 2:
            warns.append(f"lead {n} headline wraps to {len(hl)} lines")
        if len(bl) > 4:
            warns.append(f"lead {n} body wraps to {len(bl)} lines")
        if f_ltag.getlength(tag) > lead_w - 2 * pad:
            warns.append(f"lead {n} tag too wide")
        bh = (pad + illo_h + 5 + len(hl) * text_h(f_lhead) + 4
              + len(bl) * text_h(f_lbody) + 6 + text_h(f_ltag) + pad)
        lead_blocks.append((n, head, body, tag, hl, bl, bh))
    box_h = max(b[6] for b in lead_blocks)
    for i, (n, head, body, tag, hl, bl, bh) in enumerate(lead_blocks):
        x = MARGIN + i * (lead_w + lead_gap)
        d.rectangle([x, y, x + lead_w, y + box_h], outline=INK, width=1)
        ix0, iy0 = x + 1, y + 1
        ILLOS[n - 1](d, ix0, iy0, x + lead_w - 1, iy0 + illo_h)
        # number badge
        d.rectangle([ix0, iy0, ix0 + 22, iy0 + 22], fill=RED)
        fb = F(SANS_B, fs(13, s))
        d.text((ix0 + 11 - fb.getlength(str(n)) / 2, iy0 + 3), str(n),
               font=fb, fill=(255, 255, 255))
        ty = iy0 + illo_h + 5
        for ln in hl:
            d.text((x + pad, ty), ln, font=f_lhead, fill=INK)
            ty += text_h(f_lhead)
        ty += 4
        for ln in bl:
            d.text((x + pad, ty), ln, font=f_lbody, fill=INK)
            ty += text_h(f_lbody)
        d.text((x + pad, y + box_h - pad - text_h(f_ltag)), tag,
               font=f_ltag, fill=RED)
    y += box_h + 7

    # ---- 10 SMALL CARDS (5 x 2)
    d.line([MARGIN, y, W - MARGIN, y], fill=INK, width=1)
    y += 6
    card_gap = 8
    card_w = (CW - 4 * card_gap) // 5
    cpad = 6
    cillo_h = int(28 * s)
    f_chead = F(SANS_B, fs(13, s))
    f_cbody = F(SANS, fs(10, s))
    f_ctag = F(SANS_B, fs(9, s))
    for row in range(2):
        row_cards = CARDS[row * 5:(row + 1) * 5]
        blocks = []
        for k, (head, body, tag) in enumerate(row_cards):
            n = row * 5 + k + 4
            hl = wrap(head, f_chead, card_w - 2 * cpad)
            bl = wrap(body, f_cbody, card_w - 2 * cpad)
            if len(hl) > 2:
                warns.append(f"card {n} headline wraps to {len(hl)} lines")
            if len(bl) > 3:
                warns.append(f"card {n} body wraps to {len(bl)} lines")
            if f_ctag.getlength(tag) > card_w - 2 * cpad:
                warns.append(f"card {n} tag too wide")
            bh = (cpad + cillo_h + 4 + len(hl) * text_h(f_chead) + 3
                  + len(bl) * text_h(f_cbody) + 5 + text_h(f_ctag) + cpad)
            blocks.append((n, hl, bl, tag, bh))
        row_h = max(b[4] for b in blocks)
        for i, (n, hl, bl, tag, bh) in enumerate(blocks):
            x = MARGIN + i * (card_w + card_gap)
            d.rectangle([x, y, x + card_w, y + row_h], outline=INK, width=1)
            ix0, iy0 = x + 1, y + 1
            ILLOS[n - 1](d, ix0, iy0, x + card_w - 1, iy0 + cillo_h)
            d.rectangle([ix0, iy0, ix0 + 16, iy0 + 16], fill=RED)
            fb = F(SANS_B, fs(10, s))
            d.text((ix0 + 8 - fb.getlength(str(n)) / 2, iy0 + 2), str(n),
                   font=fb, fill=(255, 255, 255))
            ty = iy0 + cillo_h + 4
            for ln in hl:
                d.text((x + cpad, ty), ln, font=f_chead, fill=INK)
                ty += text_h(f_chead)
            ty += 3
            for ln in bl:
                d.text((x + cpad, ty), ln, font=f_cbody, fill=INK)
                ty += text_h(f_cbody)
            d.text((x + cpad, y + row_h - cpad - text_h(f_ctag)), tag,
                   font=f_ctag, fill=RED)
        y += row_h + 6

    # ---- WHERE IT HAPPENED (map)
    y = section_header(d, y, "WHERE IT HAPPENED", s, right=REGION_COUNTS)
    map_h = int(84 * s)
    map_y0 = y
    d.rectangle([MARGIN, map_y0, W - MARGIN, map_y0 + map_h], outline=INK, width=1)

    def proj(lon, lat):
        px = MARGIN + (lon + 180.0) / 360.0 * CW
        py = map_y0 + (78.0 - lat) / 140.0 * map_h
        return px, py

    for poly in CONTINENTS:
        pts = [proj(lon, lat) for lon, lat in poly]
        d.polygon(pts, fill=LAND, outline=LAND_EDGE)
    f_pin = F(SANS_B, fs(9, s))
    for num, lon, lat, dx, dy in PINS:
        px, py = proj(lon, lat)
        cx, cy = px + dx, py + dy
        if dx or dy:
            d.line([px, py, cx, cy], fill=RED, width=1)
        r = 8
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED,
                  outline=(255, 255, 255), width=1)
        nw = f_pin.getlength(str(num))
        d.text((cx - nw / 2, cy - f_pin.size / 2 - 1), str(num),
               font=f_pin, fill=(255, 255, 255))
    y = map_y0 + map_h + 6

    # ---- ALSO ON TUESDAY (briefs 14-34)
    y = section_header(d, y, "ALSO ON TUESDAY", s)
    f_bnum = F(SANS_B, fs(10, s))
    f_bbody = F(SANS, fs(10, s))
    f_btag = F(SANS_B, fs(10, s))
    brow_h = text_h(f_bbody) + 1
    bcol_w = (CW - 16) // 2
    for idx, (num, body, tag) in enumerate(BRIEFS):
        col = idx // 11
        row = idx % 11
        x = MARGIN + col * (bcol_w + 16)
        yy = y + row * brow_h
        num_s = f"{num} "
        tag_s = f" [{tag}]"
        total = (f_bnum.getlength(num_s) + f_bbody.getlength(body)
                 + f_btag.getlength(tag_s))
        if total > bcol_w:
            warns.append(f"brief {num} too wide by {int(total - bcol_w)}px")
        d.text((x, yy), num_s, font=f_bnum, fill=RED)
        bx = x + f_bnum.getlength(num_s)
        d.text((bx, yy), body, font=f_bbody, fill=INK)
        d.text((bx + f_bbody.getlength(body), yy), tag_s, font=f_btag, fill=RED)
    y += 11 * brow_h + 3

    # ---- DATE CHECK
    y = section_header(d, y, "DATE CHECK", s)
    f_dc = F(SANS, fs(10, s))
    dc_lines = wrap(DATE_CHECK, f_dc, CW)
    for ln in dc_lines:
        d.text((MARGIN, y), ln, font=f_dc, fill=INK)
        y += text_h(f_dc)
    y += 2

    # ---- footer
    f_ft = F(SANS, fs(9, s))
    ft_lines = wrap(FOOTER, f_ft, CW)
    for ln in ft_lines:
        d.text((MARGIN, y), ln, font=f_ft, fill=GREY)
        y += text_h(f_ft)

    return img, y, warns


def main():
    chosen = None
    for s in (1.0, 0.96, 0.92, 0.88, 0.84, 0.80):
        img, fy, warns = render_page(s)
        print(f"scale={s} final y = {fy}")
        if fy <= 1016:
            chosen = (s, img, fy, warns)
            break
    if chosen is None:
        s, img, fy, warns = 0.80, img, fy, warns
        print("WARNING: still over 1016 at smallest scale")
    else:
        s, img, fy, warns = chosen
    for wmsg in warns:
        print("WARN:", wmsg)
    img.save("entry.png", optimize=True)
    print("scale =", s)
    print("final y =", fy)
    print("entry.png bytes =", os.path.getsize("entry.png"))


if __name__ == "__main__":
    main()

"""The Nabla house style: every look of the series in one place. Scenes use only the names below, never a hex
value or a loose number for a colour, size, stroke or time.

Rules
-----
- Colour = meaning. A quantity has the same colour everywhere: in the circuit, the formula and the graph
  (U and E yellow, I blue, R orange, P green, Q red). Everything else is white or grey on black.
- The five brand colours together (BRAND_STRIPES) are only for brand moments: nabla.branding.
  The one exception is LED_COLORS (real LED colours, video on sensors).
- Current arrows are white and run from + to −; electrons are yellow and run the other way.
- Numbers use a decimal comma: value("U", 6, "V") gives U = 6,0 V; comma() in hand-written formulas.
"""
import re
from pathlib import Path

import manimgx as m
import yaml

# ── Brand palette (taken from the logo; never change) ─────────────────────
N_RED, N_ORANGE, N_YELLOW, N_GREEN, N_BLUE = "#FF0020", "#FF601C", "#FFB31F", "#15CD36", "#008EFE"
WHITE, BLACK, GREY = "#FFFFFF", "#000000", "#808080"
BRAND_STRIPES = (N_RED, N_ORANGE, N_YELLOW, N_GREEN, N_BLUE)  # all five together: brand moments only

# ── Semantic colours ──────────────────────────────────────────────────────
C_BG, C_TEXT, C_WIRE, C_EDGE = BLACK, WHITE, WHITE, WHITE   # C_EDGE: outlines of 3D models
C_MUTED = GREY             # side issues, greyed-out parts, panel edges
C_ACCENT = N_RED           # "watch out": danger, short circuit, broken, frames that call for attention

C_VOLTAGE = N_YELLOW       # U
C_ENERGY = N_YELLOW        # E (shares yellow with U: energy per charge is the voltage)
C_CURRENT = N_BLUE         # I
C_RESISTANCE = N_ORANGE    # R
C_POWER = N_GREEN          # P
C_CHARGE = N_RED           # Q (shares red with C_ACCENT)

C_CURRENT_ARROW = WHITE    # the moving current arrows (the formula letter I stays blue)
C_ELECTRON = N_YELLOW
C_JOULE = N_YELLOW         # light blobs leaving a lamp, one joule each
C_LIGHT = N_YELLOW         # a lamp that is on
C_WATER = N_BLUE           # water analogy: flows like the current
C_FIELD = N_BLUE           # magnetic field
C_COPPER = N_ORANGE
C_HOT = N_ORANGE           # glowing heating element
C_USEFUL = C_ENERGY        # useful / electrical energy in energy bars
C_LOSS = N_RED             # energy lost as heat
C_PROTON, C_NEUTRON, C_INSULATOR = N_RED, GREY, GREY

LED_COLORS = (N_RED, N_ORANGE, N_YELLOW, N_GREEN, N_BLUE, WHITE)  # the exception to the brand-stripes rule

# Capital letters that formula() colours by itself.
# shortcut: also colours letters inside \text{...}; use m.MathTex directly there.
QUANTITY_COLORS = {"U": C_VOLTAGE, "I": C_CURRENT, "R": C_RESISTANCE, "P": C_POWER, "E": C_ENERGY, "Q": C_CHARGE}

# ── Type ──────────────────────────────────────────────────────────────────
FONT = ""  # manimgx's default (New Computer Modern): the same on every machine
FS_TITLE, FS_HEADING, FS_LABEL, FS_SUBTITLE, FS_SMALL = 48, 36, 28, 26, 22
FS_FORMULA_KEY, FS_FORMULA, FS_FORMULA_STEP = 52, 44, 38  # key formula, formula, line of a calculation

# ── Strokes ───────────────────────────────────────────────────────────────
SW_SYMBOL = 4     # circuit symbols, rulers, emphasised wires
SW_WIRE = 3       # every wire: diagrams, 3D circuits, meter leads
SW_FRAME = 3      # outlines of drawn objects (meter cabinet, ...)
BOX_BAR = 0.09    # the coloured bar on the left of a box(), in frame units
SW_THIN = 2       # panel edges, 3D model edges, small instruments
SW_HEAVY = 6      # the one stroke a scene points at, "broken" cross

# ── Circuit symbols ───────────────────────────────────────────────────────
SYMBOL_LENGTH = 1.2   # every symbol, leads included
SYMBOL_SMALL = 0.7    # the only allowed scale for a symbol (meters on the side, icons)
NODE_RADIUS = 0.07

# ── Current, electrons, water ─────────────────────────────────────────────
ARROW_FRONT, ARROW_BACK, ARROW_HALF_WIDTH = 0.08, 0.05, 0.06  # a current arrow: tip, back, half width
CURRENT_SPEED = 0.9        # density mode: every arrow moves this fast (units/s)
CHARGE_PER_ARROW = 1.0     # density mode: one arrow per coulomb (A·s)
ARROW_SPACING = 0.6        # speed mode: fixed distance between arrows
ELECTRON_R_WIRE = 0.03     # electrons (and water) in a wire
ELECTRON_R_FREE = 0.07     # loose electrons: in an atom, in a metal lattice
ELECTRON_SPACING = 0.3
JOULE_R = 0.05

# ── A lamp that is on ─────────────────────────────────────────────────────
GLOW_RADII, GLOW_RINGS, GLOW_OPACITY = (0.35, 1.0), 8, 0.08    # 2D: soft rings around the lamp symbol
HALO_RADII, HALO_LAYERS, HALO_OPACITY = (0.35, 1.0), 10, 0.09  # 3D: spheres around the bulb
LAMP_LIGHT = 5                                                 # 3D: strength of the light from the bulb

# ── 3D material: the white, translucent, lit stuff of every model ──────────
MAT_OPACITY, MAT_ROUGHNESS = 0.35, 0.5

# ── Timing ────────────────────────────────────────────────────────────────
T_FAST, T_NORMAL, T_SLOW = 0.5, 1.0, 2.0  # run_time of an animation
T_CAMERA = 3.0       # a camera move that changes the view (top view ↔ tilted, lifting a circuit)
T_PAUSE = 1.0        # still after a new step
T_THINK = 2.0        # extra after "pause the video and try it yourself"
T_END_HOLD = 3.0     # still at the end of a video, after the last subtitle
T_END_SCREEN = 20.0  # the end screen: YouTube end-screen elements need 5–20 s
WORDS_PER_SEC = 2.6  # speaking pace for subtitles; tune to your own voice-over

# ── Layout (the frame is 14.2 × 8) ────────────────────────────────────────
MARGIN = 0.5                                  # to the frame edge: titles, panels
ZONE_CIRCUIT = 3 * m.LEFT + 0.3 * m.DOWN      # centre of the circuit when formulas sit beside it
ZONE_FORMULAS = 3.6 * m.RIGHT + 0.3 * m.DOWN  # centre of the formula column
ABOVE_SUBTITLES = 1.1                         # shift a bottom-corner panel up by this, clear of the subtitles
SUBTITLE_BUFF, SUBTITLE_WRAP = 0.3, 64        # subtitle: distance to the bottom edge, characters per line
BOARD_LEFT_X, BOARD_TOP_Y = 0.9, 2.9          # calculation board: its left edge, top of its first line
FIGURE_SHIFT, FIGURE_SCALE = 3.6, 0.85        # the figure beside the board: camera shift, zoom factor
PANEL_OPACITY = 0.9
FRAME_RADIUS = 0.08                           # panel / formula card: corner radius of the outline
CAM_TOP = dict(phi=0, theta=-90 * m.DEGREES, focal_distance=400)    # 2D: straight from above, no perspective
CAM_TILTED = dict(phi=62 * m.DEGREES, theta=-62 * m.DEGREES, focal_distance=20)  # 3D: height = voltage

# ── Render settings (custom_config.yml) ───────────────────────────────────
_here = Path(__file__).parent
_config_file = next(p for p in (_here / "custom_config.yml", _here.parent / "custom_config.yml") if p.exists())
CONFIG = yaml.safe_load(_config_file.read_text(encoding="utf8"))
m.config.pixel_width, m.config.pixel_height = CONFIG["resolution"]
m.config.frame_rate = CONFIG["fps"]
m.config.background_color = CONFIG["background_color"]
MATH_PREAMBLE = CONFIG.get("math_preamble") or ""


# ── Text and formulas ─────────────────────────────────────────────────────
def text(s, size=FS_LABEL, color=C_TEXT, **kw):
    return m.Text(s, font=FONT, font_size=size, color=color, **kw)


def title(s):
    """Title in the top-left corner."""
    return text(s, FS_TITLE, weight="BOLD").to_corner(m.UL, buff=MARGIN)


def label(s, target, direction=m.UP, size=FS_LABEL, color=C_TEXT):
    return text(s, size, color).next_to(target, direction, buff=0.15)


def box(mob, color=C_ACCENT):
    """mob on its own piece of white board: a white plate with square corners, mob in black on it (coloured
    quantities keep their colour), and a bar on the left in `color`: C_ACCENT for "watch out", C_MUTED for a quiet
    box. Returns VGroup(plate, bar, mob): show the group, not mob (mob is recoloured)."""
    return m.VGroup(*board_plate(mob, color, 0.2), on_board(mob))


def frame_plate(mob, buff=0.25):
    """The plate of panel and formula card: dark (PANEL_OPACITY) with a thin white outline, slightly rounded
    corners (FRAME_RADIUS). mob stays white."""
    plate = m.SurroundingRectangle(mob, buff=buff, corner_radius=FRAME_RADIUS).set_stroke(C_TEXT, SW_THIN)
    return plate.set_fill(C_BG, PANEL_OPACITY)


def board_plate(mob, color=C_MUTED, buff=0.25):
    """The plate of box: a piece of white board around mob, square corners, a bar of
    `color` on the left. Returns VGroup(white, bar); put on_board(mob) on top."""
    white = m.SurroundingRectangle(mob, buff=buff, corner_radius=0).set_stroke(width=0).set_fill(WHITE, 1)
    white.stretch_to_fit_width(white.width + BOX_BAR, about_edge=m.RIGHT)  # the bar takes its width from the left margin
    bar = m.Rectangle(width=BOX_BAR, height=white.height).set_stroke(width=0).set_fill(color, 1)
    return m.VGroup(white, bar.align_to(white, m.LEFT).align_to(white, m.UP))


def on_board(mob):
    """For the white board: plain (white) text becomes black; coloured quantities keep their colour."""
    for part in mob.get_family():
        part.on_board = True  # swap_value: a line that replaces this one goes black too
        if part.get_fill_opacity() > 0 and m.ManimColor(part.get_fill_color()) == m.ManimColor(C_TEXT):
            part.set_fill(BLACK, family=False)
        if part.get_stroke_width() > 0 and m.ManimColor(part.get_stroke_color()) == m.ManimColor(C_TEXT):
            part.set_stroke(BLACK, family=False)
    return mob


def formula(tex, size=FS_FORMULA, **kw):
    """MathTex in which U, I, R, P, E and Q get their own colour."""
    colors = {k: v for k, v in QUANTITY_COLORS.items() if k in tex}
    if MATH_PREAMBLE:
        kw.setdefault("typst_preamble", MATH_PREAMBLE)
    return m.MathTex(tex, tex_to_color_map=colors, font_size=size, color=C_TEXT, **kw)


def comma(s):
    r"""Dutch decimal comma without a space after it; only between two digits (so not in \, or a, b)."""
    return re.sub(r"(?<=\d),(?=\d)", lambda _: r"\mathord{,}", s)


def value(symbol, number, unit, decimals=1, size=FS_FORMULA):
    """value("I", 0.25, "A", 2) -> I = 0,25 A."""
    n = f"{number:.{decimals}f}".replace(".", r"\mathord{,}")
    return formula(rf"{symbol} = {n}\ \mathrm{{{unit}}}", size)


def material(mob, opacity=MAT_OPACITY, color=WHITE, roughness=MAT_ROUGHNESS, metallic=0.0):
    """Colour + material: the object is lit by the lights in the scene."""
    return mob.set_fill(color, opacity).set_stroke(width=0).set_material(m.Material(metallic=metallic,
                                                                                    roughness=roughness))


assert comma(r"1,5 \, a, b") == r"1\mathord{,}5 \, a, b"

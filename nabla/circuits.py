"""Circuit symbols (IEC/NEN, as in Binas: a resistor is a rectangle, never a zigzag).

Every component lies horizontally, SYMBOL_LENGTH wide, centred on the origin, and has the same strokes.
Submobjects 0 and 1 are its leads; .a and .b are its terminals and stay right after rotating or moving,
so wires attach exactly:

    r = Resistor().place(p, q)        # body midway between p and q, pointing from p to q
    loop = VGroup(Wire(p0, r.a), r, Wire(r.b, q0))   # or: branch(p0, q0, Resistor())
"""
import numpy as np
import manimgx as m

from .style import *


class Component(m.VGroup):
    half = 0.35  # half the width of the body: the leads run from there to the ends

    def __init__(self, *body, labels=()):
        lead_a = m.Line(SYMBOL_LENGTH / 2 * m.LEFT, self.half * m.LEFT)
        lead_b = m.Line(self.half * m.RIGHT, SYMBOL_LENGTH / 2 * m.RIGHT)
        super().__init__(lead_a, lead_b, *body)
        self.set_stroke(C_TEXT, SW_SYMBOL)
        lead_a.set_stroke(width=SW_WIRE)  # leads as thick as the wires: they join seamlessly
        lead_b.set_stroke(width=SW_WIRE)
        self.add(*labels)  # after the strokes: letters keep their own look

    @property
    def a(self):
        return self[0].get_start()

    @property
    def b(self):
        return self[1].get_end()

    def place(self, p, q):
        """Put the component midway between p and q, pointing from p to q. Letters stay upright."""
        p, q = np.array(p, float), np.array(q, float)
        angle = m.angle_of_vector(q - p)
        self.rotate(angle)
        self.shift((p + q) / 2 - (self.a + self.b) / 2)  # centre on the terminals, not on the bounding box
        for sub in self:
            if isinstance(sub, m.Text):
                sub.rotate(-angle)
        return self


def _upright(s, at, size=FS_SMALL):
    return text(s, size).move_to(at)


class Battery(Component):
    """DC source: long thin plate = +, short thick plate = −. Terminal a is the +."""
    half = 0.1

    def __init__(self, plus_sign=True):
        gap = m.Rectangle(width=0.16, height=0.7, fill_color=C_BG, fill_opacity=1)  # current arrows vanish between the plates
        super().__init__(gap, m.Line(0.1 * m.LEFT + 0.35 * m.UP, 0.1 * m.LEFT + 0.35 * m.DOWN),
                         m.Line(0.1 * m.RIGHT + 0.18 * m.UP, 0.1 * m.RIGHT + 0.18 * m.DOWN),
                         labels=[_upright("+", 0.3 * m.LEFT + 0.35 * m.UP, FS_LABEL)] if plus_sign else [])
        gap.set_stroke(width=0)
        self[4].set_stroke(width=2.5 * SW_SYMBOL)


Source = Battery


class AcSource(Component):
    """AC source (the mains socket): a circle with a wave."""
    half = 0.3

    def __init__(self):
        xs = np.linspace(-0.17, 0.17, 25)
        wave = m.VMobject().set_points_smoothly([[x, 0.09 * np.sin(2 * np.pi * x / 0.34), 0] for x in xs])
        super().__init__(m.Circle(radius=0.3, fill_color=C_BG, fill_opacity=1), wave)


class Resistor(Component):
    def __init__(self):
        super().__init__(m.Rectangle(width=0.7, height=0.28, fill_color=C_BG, fill_opacity=1))


class VariableResistor(Resistor):
    def __init__(self):
        super().__init__()
        self.add(m.Arrow(0.45 * m.DL, 0.45 * m.UR, buff=0, stroke_width=SW_SYMBOL, color=C_TEXT,
                         max_tip_length_to_length_ratio=0.25))


class _Thermistor(Resistor):
    sign = ""

    def __init__(self):
        super().__init__()
        self.add(m.VMobject().set_points_as_corners([0.5 * m.LEFT + 0.3 * m.DOWN, 0.3 * m.LEFT + 0.3 * m.DOWN,
                                                     0.3 * m.RIGHT + 0.3 * m.UP]).set_stroke(C_TEXT, SW_SYMBOL / 2),
                 _upright(f"{self.sign}t°", 0.45 * m.RIGHT + 0.4 * m.DOWN))


class NTC(_Thermistor):
    """Warmer = smaller resistance."""
    sign = "−"


class PTC(_Thermistor):
    """Warmer = larger resistance."""
    sign = "+"


class LDR(Resistor):
    def __init__(self):
        super().__init__()
        for dx in (-0.12, 0.12):  # light falls on it: arrows towards the symbol
            self.add(m.Arrow(dx * m.RIGHT + 0.75 * m.UP + 0.25 * m.LEFT, dx * m.RIGHT + 0.2 * m.UP, buff=0,
                             stroke_width=SW_SYMBOL / 2, color=C_TEXT, max_tip_length_to_length_ratio=0.3))


class Lamp(Component):
    """Circle with a cross. brightness 0…1 fills the circle with C_LIGHT; draw lamp_glow() under it."""
    half = 0.28

    def __init__(self, brightness=0.0):
        k = 0.28 / np.sqrt(2)
        super().__init__(m.Circle(radius=0.28, fill_color=C_BG, fill_opacity=1),
                         m.Line(k * m.UL, k * m.DR), m.Line(k * m.UR, k * m.DL))
        self.set_brightness(brightness)

    def set_brightness(self, h):
        # a lamp that is on is clearly yellow, yet it starts smoothly from 0 (no jump)
        mix = 0.55 * min(h / 0.2, 1) + 0.45 * h
        self[2].set_fill(m.interpolate_color(m.ManimColor(C_BG), m.ManimColor(C_LIGHT), mix), 1)
        self.brightness = h
        return self

    def glow(self):
        return lamp_glow(self[2].get_center() - 0.01 * m.OUT, self.brightness)


def lamp_glow(center, strength=1.0):
    """Soft yellow rings around a lamp that is on (2D); draw it just under the symbol."""
    return m.VGroup(*(m.Circle(radius=r, stroke_width=0).set_fill(C_LIGHT, GLOW_OPACITY * (1 - i / GLOW_RINGS) * strength)
                      for i, r in enumerate(np.linspace(*GLOW_RADII, GLOW_RINGS)))).move_to(center)


class Diode(Component):
    """Forward direction from a to b."""
    half = 0.18

    def __init__(self):
        super().__init__(m.Polygon(0.18 * m.LEFT + 0.22 * m.UP, 0.18 * m.LEFT + 0.22 * m.DOWN, 0.18 * m.RIGHT),
                         m.Line(0.18 * m.RIGHT + 0.22 * m.UP, 0.18 * m.RIGHT + 0.22 * m.DOWN))


class LED(Diode):
    def __init__(self):
        super().__init__()
        for dx in (-0.05, 0.15):  # light goes out: arrows away from the symbol
            self.add(m.Arrow(dx * m.RIGHT + 0.25 * m.UP, dx * m.RIGHT + 0.25 * m.RIGHT + 0.7 * m.UP, buff=0,
                             stroke_width=SW_SYMBOL / 2, color=C_TEXT, max_tip_length_to_length_ratio=0.3))


class Switch(Component):
    """angle in degrees: 30 = open, 0 = closed; anything in between to let it snap shut."""
    half = 0.3
    OPEN = 30

    def __init__(self, angle=OPEN):
        arm = m.Line(0.3 * m.LEFT, 0.3 * m.RIGHT).rotate(angle * m.DEGREES, about_point=0.3 * m.LEFT)
        super().__init__(arm, m.Dot(0.3 * m.LEFT, radius=0.05), m.Dot(0.3 * m.RIGHT, radius=0.05))


class Fuse(Component):
    """Rectangle with a wire through it; blown, the wire is broken in the middle."""
    half = 0.3

    def __init__(self, blown=False):
        wire = ([m.Line(0.3 * m.LEFT, 0.08 * m.LEFT), m.Line(0.08 * m.RIGHT, 0.3 * m.RIGHT)] if blown
                else [m.Line(0.3 * m.LEFT, 0.3 * m.RIGHT)])
        super().__init__(m.Rectangle(width=0.6, height=0.22, fill_color=C_BG, fill_opacity=1), *wire)


class Meter(Component):
    """Circle with a letter; the letter stays upright when placed."""
    half = 0.3
    letter = "?"

    def __init__(self, letter=None):
        super().__init__(m.Circle(radius=0.3, fill_color=C_BG, fill_opacity=1),
                         labels=[text(letter or self.letter, FS_LABEL)])


class Ammeter(Meter):
    letter = "A"


class Voltmeter(Meter):
    letter = "V"


class Motor(Meter):
    letter = "M"


class Ground(m.VGroup):
    """Earth symbol hanging from point p; .a is the connection at the top."""

    def __init__(self, p=m.ORIGIN):
        p = np.asarray(p, float)
        bars = [m.Line(p + [-w, -0.25 - 0.1 * i, 0], p + [w, -0.25 - 0.1 * i, 0]) for i, w in enumerate((0.25, 0.16, 0.07))]
        super().__init__(m.Line(p, p + [0, -0.25, 0]), *bars)
        self.set_stroke(C_TEXT, SW_SYMBOL)

    @property
    def a(self):
        return self[0].get_start()


class Wire(m.VMobject):
    """A wire through the given points, with corners."""

    def __init__(self, *points, **kw):
        super().__init__(**kw)
        if points:  # manimgx may make an empty copy
            self.set_points_as_corners([np.array(p, float) for p in points])
        self.set_stroke(C_WIRE, SW_WIRE)


class Node(m.Dot):
    """Junction dot where wires branch."""

    def __init__(self, p=m.ORIGIN, **kw):
        super().__init__(p, radius=NODE_RADIUS, color=C_WIRE, **kw)


def branch(p, q, component):
    """Wire from p to q with the component in the middle. Returns VGroup(wire, component, wire)."""
    component.place(p, q)
    return m.VGroup(Wire(p, component.a), component, Wire(component.b, q))

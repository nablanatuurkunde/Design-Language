"""Fixed ways for things to enter, leave and change, and the standard way to show current and electrons.

Entering and leaving
    appear(*mobs)            panels, labels, formulas, symbols: always a plain fade
    vanish(*mobs)            the same, out
    draw(mob)                wires, rulers, a short circuit: drawn along their length
    point_at(mob, color)     draw attention: in the colour of the quantity (C_VOLTAGE on a battery, ...),
                             C_ACCENT for danger
    swap_value(old, new)     a line whose numbers change: the new line takes the old one's place

Current (white arrows, + → −) and electrons (yellow dots, the other way), along a closed loop of points:
    current_by_density(...)  fixed speed; the current is in how close the arrows are (charge per second)
    current_by_speed(...)    fixed spacing; the current is in how fast they go
    electron_flow(...)       yellow dots against the current
Arrows and dots sit behind the symbols (z-index −1), whose bodies are filled with the background:
so they disappear under a symbol by themselves.
"""
import numpy as np
import manimgx as m

from .style import *


def appear(*mobs, **kw):
    return [m.FadeIn(x, **kw) for x in mobs]


def vanish(*mobs, **kw):
    return [m.FadeOut(x, **kw) for x in mobs]


def draw(mob, **kw):
    return m.Create(mob, **kw)


def point_at(mob, color, **kw):
    return m.Indicate(mob, color=color, scale_factor=1.1, **kw)


def swap_value(old, new, **kw):
    """Replace a line (of a panel or board) by a new one, left-aligned on the same spot."""
    return m.Transform(old, new.move_to(old, aligned_edge=m.LEFT), **kw)


# ── Current and electrons ──────────────────────────────────────────────────
def arrow_corners(at, direction):
    """The three corners of a current arrow at `at`, pointing along `direction` (unit vector in the xy-plane)."""
    across = np.array([-direction[1], direction[0], 0])
    return [at + ARROW_FRONT * direction, at - ARROW_BACK * direction + ARROW_HALF_WIDTH * across,
            at - ARROW_BACK * direction - ARROW_HALF_WIDTH * across]


class Loop:
    """A closed polyline, parametrised by distance travelled: what moves along it, moves equally fast everywhere
    (point_from_proportion goes per segment, not per length)."""

    def __init__(self, points):
        self.p = np.array([*points, points[0]], float)
        self.seg = np.linalg.norm(np.diff(self.p, axis=0), axis=1)
        self.cum = np.concatenate([[0], np.cumsum(self.seg)])
        self.length = self.cum[-1]

    def at(self, s):
        """(point, direction) at distance s."""
        s %= self.length
        i = min(np.searchsorted(self.cum, s, side="right") - 1, len(self.seg) - 1)
        d = (self.p[i + 1] - self.p[i]) / self.seg[i]
        return self.p[i] + (s - self.cum[i]) * d, d


_sq = Loop([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]])
assert _sq.length == 4 and np.allclose(_sq.at(2.5)[0], [0.5, 1, 0]) and np.allclose(_sq.at(4.25)[0], [0.25, 0, 0])


def _arrows(n):
    g = m.VGroup(*(m.VMobject().set_fill(C_CURRENT_ARROW, 0).set_stroke(width=0) for _ in range(n)))
    return g.set_z_index(-1)


def _put_arrow(arrow, loop, s, opacity):
    at, d = loop.at(s)
    corners = arrow_corners(at, d)
    arrow.set_points_as_corners(corners + corners[:1])
    arrow.set_fill(opacity=opacity)


def current_by_density(points, current, max_current, visible=None):
    """Arrows from + to − along the loop `points` (start at the +), all at CURRENT_SPEED; current (ValueTracker,
    amperes) sets how many are visible: at max_current one per CHARGE_PER_ARROW coulomb. When the current changes,
    arrows fade in or out one by one, evenly spread; at (almost) no current they stand still and fade.
    visible: optional ValueTracker 0…1 to fade the whole flow."""
    loop = Loop(points)
    n = max(2, int(loop.length * max_current / (CURRENT_SPEED * CHARGE_PER_ARROW)))
    # each arrow its own threshold (van der Corput: 0, ½, ¼, ¾, …): whatever the current, the visible ones are evenly spread
    threshold = [sum(((k >> b) & 1) / 2 ** (b + 1) for b in range(16)) for k in range(n)]
    g = _arrows(n)
    g.s = 0.0

    def move(grp, dt):
        i = current.get_value()
        running = np.clip(i / 0.05, 0, 1)
        grp.s += dt * CURRENT_SPEED * running
        share = np.clip(i / max_current, 0, 1)
        fade = visible.get_value() if visible else 1
        for k, arrow in enumerate(grp):
            on = np.clip((share - threshold[k]) * n, 0, 1)  # the edge arrow fades softly
            _put_arrow(arrow, loop, grp.s + k * loop.length / n, on * running * fade)

    g.add_updater(move)
    move(g, 0)
    return g


def current_by_speed(points, speed, visible=None, spacing=ARROW_SPACING):
    """Arrows from + to − along the loop `points`, a fixed distance apart, moving at speed (ValueTracker, units/s)."""
    loop = Loop(points)
    n = max(2, int(loop.length / spacing))
    g = _arrows(n)
    g.s = 0.0

    def move(grp, dt):
        grp.s += dt * speed.get_value()
        for k, arrow in enumerate(grp):
            _put_arrow(arrow, loop, grp.s + k * loop.length / n, visible.get_value() if visible else 1)

    g.add_updater(move)
    move(g, 0)
    return g


def electron_flow(points, speed, visible=None, spacing=ELECTRON_SPACING):
    """Yellow electrons along the same loop as the current (start at the +), but the other way: − → +."""
    loop = Loop(points)
    n = max(2, int(loop.length / spacing))
    g = m.VGroup(*(m.Dot(radius=ELECTRON_R_WIRE, color=C_ELECTRON) for _ in range(n))).set_z_index(-1)
    g.s = 0.0

    def move(grp, dt):
        grp.s -= dt * speed.get_value()
        for k, dot in enumerate(grp):
            dot.move_to(loop.at(grp.s + k * loop.length / n)[0])
            dot.set_fill(opacity=visible.get_value() if visible else 1)

    g.add_updater(move)
    move(g, 0)
    return g

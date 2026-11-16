"""Telling the story: subtitles, panels and the calculation board, and Lesson, the base of every video.

A video is a Lesson; in it:
    d = say(self, "sentence")      show a subtitle; d = speaking time in seconds
    self.do(d, *animations)        an animation of a second, then stand still until the sentence is done
    self.play(*self.show(panel))   put something fixed in frame and fade it in
    self.end()                     clear the subtitle and hold for T_END_HOLD
"""
import textwrap

import numpy as np
import manimgx as m

from .style import *


# ── Subtitles ──────────────────────────────────────────────────────────────
SUBTITLES_IN_FRAME = True  # False: only the .srt beside the video (for YouTube captions)


def speaking_time(s):
    """How long saying s takes (say() uses the same)."""
    return max(1.2, len(s.split()) / WORDS_PER_SEC)


def say(scene, s, duration=None):
    """Show s as a subtitle (in frame and in the .srt) and return the speaking time; fill that time with
    animations or wait(). say(scene, "") removes the subtitle."""
    if getattr(scene, "_subtitle", None) is not None:
        scene.remove(scene._subtitle)
        scene._subtitle = None
    if not s:
        return 0
    duration = duration or speaking_time(s)
    scene.add_subcaption(s, duration=duration)
    if SUBTITLES_IN_FRAME:
        t = text("\n".join(textwrap.wrap(s, SUBTITLE_WRAP)), FS_SUBTITLE).to_edge(m.DOWN, buff=SUBTITLE_BUFF)
        back = m.BackgroundRectangle(t, color=C_BG, fill_opacity=0.8, buff=0.12)
        scene._subtitle = m.VGroup(back, t).set_z_index(10)
        if isinstance(scene, m.ThreeDScene):
            scene.add_fixed_in_frame_mobjects(scene._subtitle)
        else:
            scene.add(scene._subtitle)
    return duration


# ── Panels (fixed in frame) ────────────────────────────────────────────────
def panel(*lines, corner=m.UL, size=FS_LABEL):
    """Lines on an (almost) opaque plate with a white square outline (frame_plate), fixed in a corner: readable,
    also over a moving circuit. A line may be a string or a mobject. panel[0] is the plate, panel[1] the lines, so
    they can appear apart."""
    group = m.VGroup(*(text(s, size) if isinstance(s, str) else s for s in lines))
    group.arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.25)
    result = m.VGroup(frame_plate(group), group).to_corner(corner, buff=MARGIN)  # plate first: the text lies on top
    if corner[1] < 0:
        result.shift(ABOVE_SUBTITLES * m.UP)
    return result


def panel_parts(*lines, corner=m.UR):
    """A panel whose plate and lines can appear apart: returns (panel, plate, lines)."""
    p = panel(*lines, corner=corner)
    return p, p[0], p[1]


# ── Calculation board: a long calculation on the right, the figure on the left ──
def board(*lines):
    """A calculation for the right side of the frame: a white board from BOARD_LEFT_X to the right edge, with the
    lines in black on it. Returns VGroup(plate, lines), like panel. In with Lesson.board_in, out with board_out."""
    width = m.config.frame_width / 2 - BOARD_LEFT_X + 0.2
    plate = m.Rectangle(width=width, height=m.config.frame_height + 0.2).set_stroke(width=0).set_fill(WHITE, 1)
    plate.move_to([BOARD_LEFT_X + width / 2, 0, 0])
    rows = on_board(m.VGroup(*(text(s) if isinstance(s, str) else s for s in lines)))
    rows.arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.45)
    room = m.config.frame_width / 2 - BOARD_LEFT_X - 1.0
    if rows.width > room:
        rows.scale(room / rows.width)
    rows.next_to(plate.get_left(), m.RIGHT, buff=0.5).align_to(np.array([0, BOARD_TOP_Y, 0]), m.UP)
    return m.VGroup(plate, rows)


def figure_left(cam, shift=FIGURE_SHIFT, smaller=FIGURE_SCALE):
    """The same camera, but the figure smaller and in the left half: the camera moves to the right."""
    c = dict(cam, zoom=cam["zoom"] * smaller)
    right = np.array([-np.sin(cam["theta"]), np.cos(cam["theta"]), 0])  # 'right' on screen, in the scene
    c["frame_center"] = np.asarray(cam["frame_center"], float) + shift / c["zoom"] * right
    return c


# ── Background ─────────────────────────────────────────────────────────────
_Q = np.array([[1, 0], [1, 0.5523], [0.5523, 1], [0, 1]])  # a quarter circle as one cubic curve
# a dot of radius 1, as points: four curves (m.Dot has eight, twice the work for a dot of a few pixels)
DOT = np.concatenate([_Q @ np.array([[c, s], [-s, c]]) for c, s in ((1, 0), (0, 1), (-1, 0), (0, -1))])


DOT_STEP, DOT_RADIUS, DOT_BANDS = 0.6, 0.03, 8


def chain(shapes):
    """Many closed outlines (n, k, 2) as the points of one: after each outline a straight bridge to the start of the
    next, and at the end all bridges back again, so the bridges enclose nothing and only the outlines are filled.
    manimgx does slow work per separate outline (np.allclose for each, every frame): a layer of hundreds of dots
    costs far less as one."""
    if len(shapes) < 2:
        return shapes.reshape(-1, 2)
    a, b = shapes[:-1, 0], shapes[1:, 0]
    bridges = np.stack([a, a + (b - a) / 3, a + 2 * (b - a) / 3, b], axis=1)
    return np.concatenate([np.concatenate([shapes[:-1], bridges], axis=1).reshape(-1, 2), shapes[-1],
                           bridges[::-1, ::-1].reshape(-1, 2)])


def dots_grid():
    """The resting places of the background dots, in frame coordinates (a little past the frame on all sides)."""
    nx, ny = int(18 / DOT_STEP) + 2, int(11 / DOT_STEP) + 2
    return np.array([[(i - nx / 2) * DOT_STEP, (j - ny / 2) * DOT_STEP] for i in range(nx) for j in range(ny)])


def dots_at(grid, t, speed=0.12):
    """(places, brightness band) of the dots at time t: a slow diagonal drift and a soft wave of light."""
    P = grid + (t * speed) % DOT_STEP  # drift; after one step the grid falls on itself
    wave = 0.5 + 0.5 * np.sin(0.8 * (P[:, 0] + P[:, 1]) - 0.6 * t)
    return P, np.minimum((wave * DOT_BANDS).astype(int), DOT_BANDS - 1)


def dots_layers():
    """One layer per brightness band."""
    return [m.VMobject().set_fill(C_MUTED, 0.1 + 0.25 * (b + 0.5) / DOT_BANDS).set_stroke(width=0)
            for b in range(DOT_BANDS)]


def dots_pattern():
    """A grid of faint dots drifting slowly diagonally, with a soft wave of light through it (one layer per
    brightness). Returns (layers, shapes): shapes(t) gives each layer's points at time t, in frame coordinates."""
    grid = dots_grid()

    def shapes(t):
        P, band = dots_at(grid, t)
        return [chain(P[band == b, None, :] + DOT_RADIUS * DOT[None]) for b in range(DOT_BANDS)]
    return m.VGroup(*dots_layers()), shapes


# ── The base of every video ────────────────────────────────────────────────
class Lesson(m.ThreeDScene):
    def setup(self):
        super().setup()
        self.dots = self.background()  # every video the same quiet, moving background

    def hud(self, *mobs):
        """Fix in frame (stays put whatever the camera does)."""
        self.add_fixed_in_frame_mobjects(*mobs)

    def show(self, *mobs):
        """Fix in frame and fade in: self.play(*self.show(a, b))."""
        self.hud(*mobs)
        return [m.FadeIn(x) for x in mobs]

    def one_by_one(self, rows, duration, *alongside):
        """Rows fade in fixed in frame one after the other, `duration` seconds in all; `alongside` runs with the
        first. No LaggedStart: in it, the rows whose turn has not come are already fully in frame."""
        for i, r in enumerate(rows):
            self.play(*self.show(r), *(alongside if i == 0 else ()), run_time=duration / len(rows))

    def do(self, d, *anims, duration=T_NORMAL):
        """An animation of `duration` seconds, then stand still until the sentence (d seconds) is done."""
        self.play(*anims, run_time=min(duration, d))
        self.wait(max(d - duration, 0))

    def think(self, d):
        """After "pause the video and try it yourself": the sentence plus T_THINK seconds."""
        self.wait(d + T_THINK)

    def end(self):
        say(self, "")
        self.wait(T_END_HOLD)

    def camera_state(self):
        """The current camera, as a dict for move_camera / figure_left()."""
        c = self.camera
        return dict(phi=c.get_phi(), theta=c.get_theta(), zoom=c.get_zoom(), frame_center=np.array(c.frame_center, float),
                    focal_distance=c.get_focal_distance())

    def camera_path(self, keys, start="soft", finish="soft"):
        """One smooth camera move through key states [(time, dict(phi, theta, zoom, frame_center)), ...]; if all
        states also give focal_distance, it moves along. Cubic (Hermite) through the states: no kink and no stop
        at an intermediate state. start/finish "soft": leave/land at rest; "through": with the speed of the
        first/last piece (at a cut). Returns play_to(t, *anims): play the path up to time t, with anims alongside."""
        times = np.array([t for t, _ in keys], float)
        focal = all("focal_distance" in k for _, k in keys)
        V = np.array([[k["phi"], k["theta"], np.log(k["zoom"]), *k["frame_center"]]
                      + ([np.log(k["focal_distance"])] if focal else []) for _, k in keys], float)
        R = np.zeros_like(V)  # tangents: slope between the neighbours
        R[1:-1] = (V[2:] - V[:-2]) / (times[2:] - times[:-2])[:, None]
        if start == "through":
            R[0] = (V[1] - V[0]) / (times[1] - times[0])
        if finish == "through":
            R[-1] = (V[-1] - V[-2]) / (times[-1] - times[-2])

        def state(t):
            i = int(np.clip(np.searchsorted(times, t, side="right") - 1, 0, len(V) - 2))
            h = times[i + 1] - times[i]
            u = np.clip((t - times[i]) / h, 0, 1)
            v = ((2 * u ** 3 - 3 * u ** 2 + 1) * V[i] + (u ** 3 - 2 * u ** 2 + u) * h * R[i]
                 + (-2 * u ** 3 + 3 * u ** 2) * V[i + 1] + (u ** 3 - u ** 2) * h * R[i + 1])
            self.set_camera_orientation(phi=v[0], theta=v[1], zoom=np.exp(v[2]), frame_center=v[3:6],
                                        focal_distance=np.exp(v[6]) if focal else None)

        clock = m.ValueTracker(times[0])
        carrier = m.Mobject().add_updater(lambda _: state(clock.get_value()))
        state(times[0])

        def play_to(t, *anims):
            if t <= clock.get_value() + 1e-6:
                return
            self.add(carrier)
            self.play(clock.animate(rate_func=m.linear).set_value(t), *anims, run_time=t - clock.get_value())
            self.remove(carrier)
        return play_to

    def board_in(self, brd, camera=None, *anims, duration=T_NORMAL):
        """The figure moves left (camera; default: the current state, to the left) and the white board slides
        in from the right. Show its lines afterwards: self.show(brd[1][i])."""
        brd.back = self.camera_state()
        plate = brd[0]
        shown = [r for r in brd[1] if r in self.mobjects]  # lines already in anims (show)
        self.hud(plate)
        self.remove(*shown)
        self.hud(*shown)  # on top of the white plate
        plate.shift(8 * m.RIGHT)
        self.move_camera(**(camera or figure_left(brd.back)), added_anims=[plate.animate.shift(8 * m.LEFT), *anims],
                         run_time=duration)

    def board_out(self, brd, camera=None, *anims, duration=T_NORMAL):
        """The other way: the board slides out with the calculation, and the figure goes to camera
        (default: back to where it was before board_in)."""
        self.move_camera(**(camera or brd.back), added_anims=[brd.animate.shift(9 * m.RIGHT), *anims],
                         run_time=duration)
        self.remove(brd)

    def board_swap(self, old, new, *anims, duration=T_FAST):
        """The white board stays; only the calculation goes. Show the new lines afterwards with self.show."""
        new.back = old.back
        self.hud(new[0])
        self.remove(old[0])
        self.play(m.FadeOut(old[1]), *anims, run_time=duration)
        self.remove(old[1])

    def background(self, distance=0.35):
        """Quiet moving background: faint dots drifting slowly (dots_pattern)."""
        return self.backdrop(*dots_pattern(), distance=distance)

    def backdrop(self, layers, shapes, distance=0.35, t=0.0):
        """Add a moving pattern behind everything: shapes(t) gives each layer's points in frame coordinates.
        Fixed layers always lie on top, so the pattern lies in 3D far behind the scene (distance × the focal
        distance) and follows the camera: in every camera state it fills exactly the frame, and it always faces
        the camera."""
        layers.t = t  # shapes starts at this time

        def follow(g, dt):
            g.t += dt
            c = self.camera
            phi, theta, f, zoom = c.get_phi(), c.get_theta(), c.get_focal_distance(), c.get_zoom()
            to_camera = np.array([np.sin(phi) * np.cos(theta), np.sin(phi) * np.sin(theta), np.cos(phi)])
            right = np.array([-np.sin(theta), np.cos(theta), 0])
            centre = np.asarray(c.frame_center, float) - distance * f * to_camera
            plane = (1 + distance) / zoom * np.array([right, np.cross(to_camera, right)])  # frame x and y in the scene
            for mob, pts in zip(g, shapes(g.t)):
                mob.set_points(centre + pts @ plane if len(pts) else np.repeat([centre], 4, axis=0))
        layers.add_updater(follow)
        follow(layers, 0)
        self.add(layers)
        return layers

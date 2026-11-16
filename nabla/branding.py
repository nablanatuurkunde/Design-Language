"""Brand moments: the intro, a chapter card, a formula card in Binas style and the end screen.

This is the only place where the five brand colours appear together (BRAND_STRIPES). Each moment comes as a
builder (a mobject to place yourself) and a play_... function that shows it the standard way:

    play_intro(self)                         the logo animation of Intro.mov, from the logo files in brand/
    play_transition(self)                    a ripple of little ∇s through the background, e.g. before a chapter card
    play_chapter_card(self, 3, "Stroom")     between two parts of a video
    self.play(*self.show(formula_card(r"U = I \\cdot R", [("U", "spanning", "V"), ...], "Wet van Ohm")))
    play_end_screen(self)                    with room for YouTube's end-screen elements
"""
from pathlib import Path

import numpy as np
import manimgx as m
from PIL import Image

from .style import *
from .scene import DOT, DOT_BANDS, DOT_RADIUS, DOT_STEP, chain, dots_at, dots_grid, dots_layers


def _fix(scene, *mobs):
    """Fixed in frame in a 3D scene (Lesson), plainly added in a 2D one."""
    if isinstance(scene, m.ThreeDScene):
        scene.add_fixed_in_frame_mobjects(*mobs)
    else:
        scene.add(*mobs)


# ── Intro ──────────────────────────────────────────────────────────────────
# The logo animation of assets/Intro.mov (without its bloom), from the logo files in brand/. Every number here is
# measured from that video (60 fps, 1920×1080) and the PNGs, so the entrance matches it frame for frame.
BRAND_DIR = Path(__file__).parent / "brand"
_F = 1 / 60                       # one frame of Intro.mov, in seconds
# The timeline, in frames. Up to _SLID it is Intro.mov; the ending is ours: the logo stays a second longer than in
# the video (which cuts at frame 164), then undoes its entrance and shrinks into the background.
_SPLIT, _SLID, _BACK, _HOME, _GONE, _END = 52, 105, 224, 254, 272, 320
_LEAD, _GROW = 40, 18  # frames before the timeline, and how many of them the ∇ takes to grow
_ARTBOARD = (8000, 4000)          # both PNGs share this artboard, so they share one scale


def _px():
    """One pixel of the 1080p video, in frame units."""
    return m.config.frame_height / 1080


def _logo_png(pixels, png_x, video_x):
    """A logo PNG (RGBA array on the artboard), placed so its column png_x lands on pixel column video_x of the video."""
    k = 204 / 1706 * _px()  # frame units per PNG pixel: the ∇ is 204 px tall in the video, 1706 px in the PNG
    # Shrunk to exactly its size on screen: Lanczos anti-aliases every edge (the GPU would skip pixels of a bigger
    # texture), and the 8000×4000 originals would stall the live preview.
    on_screen = _ARTBOARD[1] * k * m.config.pixel_height / m.config.frame_height
    size = (round(_ARTBOARD[0] / _ARTBOARD[1] * on_screen), round(on_screen))
    img = m.ImageMobject(np.asarray(Image.fromarray(pixels).resize(size, Image.LANCZOS)))
    img.scale(_ARTBOARD[1] * k / img.height)
    return img.move_to([(video_x - 960) * _px() + (_ARTBOARD[0] / 2 - png_x) * k, 0, 0])


def intro():
    """The logo as the intro starts: Group(word mark, ∇), the ∇ in the middle. In logo.png a black band runs from the
    ∇'s slanted left edge to the right and hides the word until it slides out; here the black is made transparent
    (so the background shows) and word.mask(word) cuts the word off along that edge instead."""
    logo = np.array(Image.open(BRAND_DIR / "logo.png").convert("RGBA"))
    band = logo.copy()
    logo[logo[..., :3].max(-1) < 60, 3] = 0  # the black band and the black inside the ∇: transparent
    word = _logo_png(np.array(Image.open(BRAND_DIR / "wordmark.png").convert("RGBA")), 897, 484 + 435)  # 897: left of the N
    nabla = _logo_png(logo, 968, 834)                                                                 # 968: left of the red stripe
    # per row of the image: where the band starts, in pixels from the left, with sub-pixel precision (the band is
    # opaque from its edge to the right side of the artboard, so the transparent part is all to its left)
    edge = (1 - _logo_png(band, 968, 834).pixel_array[..., 3] / 255).sum(axis=1)
    full = word.pixel_array.copy()
    columns = np.arange(full.shape[1])

    def mask(w):
        shift = (w.get_x() - nabla.get_x()) * full.shape[1] / w.width  # word column c lies on band column c + shift
        cover = np.clip(edge[:, None] - shift - columns[None, :], 0, 1)  # share of each pixel left of the edge
        pixels = full.copy()
        pixels[..., 3] = (pixels[..., 3] * cover).astype(np.uint8)
        pixels.flags.writeable = False
        w.paint = w.paint.but(texture=pixels)

    word.mask = mask
    mask(word)
    # where they are, in frame coordinates (per PNG pixel: height / artboard, also while the image is scaled)
    nabla.core = lambda: np.array([nabla.get_x() + (1950 - _ARTBOARD[0] / 2) * nabla.height / _ARTBOARD[1], 0])  # 1950: middle of the ∇
    word.core = lambda: np.array([word.get_x() + (897 - _ARTBOARD[0] / 2) * word.height / _ARTBOARD[1], 0])     # its leading (left) edge
    return m.Group(word, nabla)


def intro_field(word, nabla, start=0.0, lead=0):
    """The intro's background, as (layers, shapes) for Lesson.backdrop: the background dots, four times as many and
    larger, as little ∇s (triangles point down, like the logo) that behave like rigid bodies on springs. It reacts
    to the logo: when the logo splits a shock runs outward that knocks them away and sets them spinning, and the
    sliding ∇ and word drag those near them along and roll them; each swings back to its place, turns point down
    again and comes to rest. Light is separate from the motion, so it never hangs or dies halfway: a
    ring of light runs with the shock, at full strength until it has left the frame, and the discs beside what
    slides light up only while it slides. After the cut every disc shrinks to a dot, so the video's own background
    takes over unnoticed.
    start: the time of the background's drift at which the intro begins (so the dots stay where they are);
    lead: frames before the timeline in which the dots first grow into the little ∇s (0: they are ∇s at once)."""
    half = DOT_STEP / 2
    grid = np.concatenate([dots_grid() + o for o in ([0, 0], [half, 0], [0, half], [half, half])])
    n = len(grid)
    extra = np.arange(n) >= n // 4  # not a dot of the plain background
    a, b, c = np.array([0.866, 0.5]), np.array([-0.866, 0.5]), np.array([0.0, -1.0])  # point down, radius 1
    # four straight sides like the dot's four curves (the top in two halves), so the triangle can round off into the dot
    triangle = np.concatenate([np.linspace(p, q, 4) for p, q in ((a, (a + b) / 2), ((a + b) / 2, b), (b, c), (c, a))])
    flip = np.where(np.random.default_rng(0).random(n) < 0.5, -1.0, 1.0)  # which way the shock spins each one
    turn, spin = np.zeros(n), np.zeros(n)
    lights = (0.2, 0.32, 0.44, 0.56)  # steps of light above the grey bands
    layers = m.VGroup(*dots_layers(), *(m.VMobject().set_fill(C_TEXT, o).set_stroke(width=0) for o in lights))
    split, shocks, cut_t, end_t = nabla.core(), ((_SPLIT + 4) * _F, _GONE * _F), _GONE * _F, _END * _F
    offset, speed, wake = np.zeros((n, 2)), np.zeros((n, 2)), np.zeros(n)
    before, last = [], [start]

    def shapes(drift):
        dt, last[0] = drift - last[0], drift
        P, band = dots_at(grid, drift)
        t = drift - start - lead * _F  # on the timeline
        now = [nabla.core(), word.core()]
        away = P - split
        distance = np.linalg.norm(away, axis=1) + 1e-9
        ring, push = np.zeros(n), np.zeros(n)  # a shock when the logo splits and one when the ∇ lands in the field
        for s in shocks:
            if t > s:
                radius = 9 * (t - s)
                ring = np.maximum(ring, np.exp(-((distance - radius) / 0.6) ** 2))
                push += np.exp(-((distance - radius) / 0.6) ** 2 - radius / 5)  # weaker further out
        if dt > 0:
            wake[:] *= 0.5 ** (dt / 0.12)  # the light beside what slides is gone as soon as it stops
            for a, b in zip(now, before):  # what slides drags the discs near it along
                near = np.exp(-((P + offset - a) ** 2).sum(1) / 0.9 ** 2)
                if t < _BACK * _F:  # the way back leaves the field alone (only the light): it moves again when the ∇ shrinks
                    speed[:] += 12 * dt * near[:, None] * ((a - b) / dt - speed)
                    spin[:] -= 30 * (a[0] - b[0]) * near * (P[:, 1] - a[1])  # rolled: above one way, below the other
                if t < _BACK * _F:  # no light while the logo closes up: the field lights again when the ∇ lands
                    wake[:] = np.maximum(wake, near * min(abs(a[0] - b[0]) / dt / 4, 1))
            speed[:] += 40 * dt * push[:, None] * away / distance[:, None]  # the shock: a push outward
            if _HOME * _F < t < _GONE * _F:  # the shrinking ∇ draws the field in around it, before the shock throws it out
                speed[:] -= 14 * dt * np.exp(-(distance / 2.5) ** 2)[:, None] * away / distance[:, None]
            speed[:] += dt * (-40 * offset - 5 * speed)  # a spring back to its place, damped
            spin[:] += 60 * dt * push * flip
            spin[:] += dt * (-30 * np.sin(3 * turn) / 3 - 2.5 * spin)  # and back to point down: the nearest third of a turn
            offset[:] += dt * speed
            turn[:] += dt * spin
        before[:] = now
        disc = 1 - m.smooth(np.clip((t - cut_t) / (end_t - cut_t), 0, 1))  # 1: little ∇s, 0: plain dots
        if lead:
            disc = min(disc, m.smooth(np.clip(1 + t / (lead * _F), 0, 1)))
        outline = disc * 0.075 * triangle + (1 - disc) * DOT_RADIUS * DOT  # the triangle rounds off into the dot
        size = np.where(extra, disc, 1)                                     # the extra ones vanish, the others become the dots
        c, s = (size * np.cos(turn))[:, None], (size * np.sin(turn))[:, None]
        x, y = outline[None, :, 0], outline[None, :, 1]
        points = (P + disc * offset)[:, None, :] + np.stack([c * x - s * y, s * x + c * y], axis=-1)
        light = np.ceil(disc * np.clip(np.maximum(ring, wake), 0, 1) * len(lights) - 0.5).astype(int)
        layer = np.where(light > 0, DOT_BANDS + light - 1, band)
        return [chain(points[layer == i]) for i in range(len(layers))]
    return layers, shapes


def play_intro(scene):
    """The dots of the background grow into little ∇s and the logo's ∇ grows out of one of them (so the intro can
    open a video or follow a short introduction). The ∇ stands still, slides right while "Nabla" slides out to the left from behind it, and holds. Then the
    logo undoes its entrance: the word slides back under the ∇, the ∇ returns to the middle and shrinks to one of
    the little ∇s of the background. 6.0 s. In a Lesson the background is intro_field for as long as the intro lasts."""
    word, nabla = intro()
    middle = [*nabla.core(), 0]
    tiny = 0.075 * 1.5 / (204 * _px())  # as tall as a ∇ of intro_field (the logo's ∇ is 204 px tall)
    nabla.scale(tiny, about_point=middle)
    field = None
    if hasattr(scene, "backdrop"):
        scene.remove(scene.dots)
        field = scene.backdrop(*intro_field(word, nabla, scene.dots.t, _LEAD), t=scene.dots.t)
    scene.wait((_LEAD - _GROW) * _F)
    _fix(scene, word, nabla)  # only now: the tiny ∇ would show as a speck while the dots still grow
    scene.play(nabla.animate(rate_func=m.ease_out_back).scale(1 / tiny, about_point=middle), run_time=_GROW * _F)
    clock = m.ValueTracker(0)  # frames

    def slide(img, dx, start, duration, ease):
        x0 = img.get_x()

        def place(mob):
            out = ease(np.clip((clock.get_value() - _SPLIT - start) / duration, 0, 1))
            back = m.smooth(np.clip((clock.get_value() - _BACK) / (_HOME - _BACK), 0, 1))
            mob.set_x(x0 + dx * _px() * out * (1 - back))
        img.add_updater(place)

    # easings fitted to the frames of Intro.mov
    slide(nabla, 324, 0, 53, lambda t: m.ease_in_out_quart(t ** 0.5))
    slide(word, -435, 6, 39, lambda t: m.ease_in_out_cubic(t ** 0.4))
    word.add_updater(word.mask)  # after the slides, so the cut follows this frame's positions
    scene.play(clock.animate(rate_func=m.linear).set_value(_HOME), run_time=_HOME * _F)
    scene.remove(word)  # under the ∇ again: hidden
    nabla.clear_updaters()
    scene.play(nabla.animate(rate_func=m.rush_into).scale(tiny, about_point=middle), run_time=(_GONE - _HOME) * _F)
    scene.remove(nabla)
    scene.wait((_END - _GONE) * _F)
    if field is not None:  # the ∇s are dots again: hand over to the plain background, at the same moment of its drift
        scene.remove(field)
        scene.dots.t = field.t
        scene.add(scene.dots)


# ── Transition ─────────────────────────────────────────────────────────────
_RIPPLE_WIDTH = 2.2                                                # the ripple's half width
_RIPPLE_AHEAD = np.array([np.cos(np.pi / 6), -np.sin(np.pi / 6)])  # the front leans 30° clockwise: it runs this way
_GRAIN = 0.18                                                     # wipe: one particle per this much outline


def _ripple_front(u):
    """Where the front is (along _RIPPLE_AHEAD, in frame units) at progress u (0…1): off frame at both ends."""
    a = _RIPPLE_AHEAD
    edge = m.config.frame_width / 2 * abs(a[0]) + m.config.frame_height / 2 * abs(a[1]) + _RIPPLE_WIDTH
    return -edge + 2 * edge * m.smooth(float(np.clip(u, 0, 1)))


def transition_field(start, duration, sources=()):
    """A ripple through the background, as (layers, shapes) for Lesson.backdrop: a front runs from the left edge
    to the right in `duration` seconds; where it passes, the dots (and the extra ones between them, as in the intro)
    grow into the intro's little ∇s, lit, nudged to the right and turned a third of a turn, and settle back into
    the plain dots behind it. start: the time of the background's drift at which it begins.
    sources: points in frame coordinates (n, 2) where a particle breaks loose when the front comes: a little ∇ that
    travels with the wave to a ∇ of the field a little ahead and, once there, is that ∇ (same place, turn, light)."""
    half = DOT_STEP / 2
    grid = np.concatenate([dots_grid() + o for o in ([0, 0], [half, 0], [0, half], [half, half])])
    extra = np.arange(len(grid)) >= len(grid) // 4
    a, b, c = np.array([0.866, 0.5]), np.array([-0.866, 0.5]), np.array([0.0, -1.0])
    triangle = np.concatenate([np.linspace(p, q, 4) for p, q in ((a, (a + b) / 2), ((a + b) / 2, b), (b, c), (c, a))])
    lights = (0.2, 0.32, 0.44, 0.56)
    layers = m.VGroup(*dots_layers(), *(m.VMobject().set_fill(C_TEXT, o).set_stroke(width=0) for o in lights))
    width, ahead = _RIPPLE_WIDTH, _RIPPLE_AHEAD
    src = np.asarray(sources, float).reshape(-1, 2)
    P0, _ = dots_at(grid, start)
    # each particle's ∇ in the field: the nearest to a point a little ahead of it (rows: memory stays small)
    target = np.array([np.argmin(((P0 - q) ** 2).sum(1)) for q in src + 0.35 * ahead], int)
    src_along = src @ ahead

    def shapes(drift):
        P, band = dots_at(grid, drift)
        front = _ripple_front((drift - start) / duration)
        behind = (front - P @ ahead) / width  # > 0: the front has passed
        disc = np.exp(-behind ** 2)  # 1 on the front: a little ∇; 0 away from it: a dot
        u = np.clip(0.5 + behind / 2, 0, 1)
        turn = -2 * np.pi / 3 * u * u * (3 - 2 * u)  # rolled clockwise with the wave, a third of a turn: point down again
        outline = disc[:, None, None] * 0.075 * triangle + (1 - disc)[:, None, None] * DOT_RADIUS * DOT
        size = np.where(extra, disc, 1)[:, None]
        cs, sn = size * np.cos(turn)[:, None], size * np.sin(turn)[:, None]
        x, y = outline[..., 0], outline[..., 1]
        at = P + 0.25 * (disc * behind * np.exp(0.5))[:, None] * ahead  # pushed ahead, then back: a wave
        points = at[:, None, :] + np.stack([cs * x - sn * y, sn * x + cs * y], axis=-1)
        light = np.ceil(disc * len(lights) - 0.5).astype(int)
        layer = np.where(light > 0, DOT_BANDS + light - 1, band)
        layer = np.where(extra & (disc < 0.05), -1, layer)  # the extra ones only exist on the ripple
        if len(src):
            b = (front - src_along) / width
            grow = np.clip((b + 0.5) / 0.2, 0, 1)        # breaks loose half a width before the front
            s = np.clip((b + 0.4) / 0.45, 0, 1)
            s = 1 - (1 - s) ** 2 * (1 - s) * (1 - s)      # the way to its ∇ (0 at the source, 1 there): quick, then settles
            go = (grow > 0) & (s < 1)                     # once there it is the field's own ∇: no need to draw it
            t = target[go]
            whole = 0.075 * triangle @ np.array([[np.cos(turn[t]), np.sin(turn[t])],
                                                 [-np.sin(turn[t]), np.cos(turn[t])]]).transpose(2, 0, 1)
            there = points[t] - at[t][:, None, :]         # the shape of its ∇ right now
            k = s[go][:, None, None]
            flying = (src[go] + (at[t] - src[go]) * k[:, 0])[:, None, :] + grow[go][:, None, None] * (
                (1 - k) * whole + k * there)
            bright = DOT_BANDS + len(lights) - 1
            flying_layer = np.where((s[go] > 0.5) & (layer[t] >= 0), layer[t], bright)
            points = np.concatenate([points, flying])
            layer = np.concatenate([layer, flying_layer])
        return [chain(points[layer == i]) for i in range(len(layers))]
    return layers, shapes


def play_transition(scene, duration=T_SLOW, wipe=True):
    """A ripple of little ∇s runs through the background from left to right (transition_field), e.g. before a
    chapter card. wipe: everything in frame (not the subtitle) merges into the background: as the front comes,
    each piece (a letter, a line, a symbol) breaks into little ∇s along its outline that travel with the wave
    into the ∇s of the field, while the piece itself fades out. Afterwards the frame is empty and the pieces are
    back in their old shape, so they can be shown again. In a scene without the Lesson background it only fades."""
    keep = {getattr(scene, "dots", None), getattr(scene, "_subtitle", None)}
    gone = [mob for mob in scene.mobjects if mob not in keep] if wipe else []
    fixed = scene.camera.fixed_in_frame_mobjects if isinstance(scene, m.ThreeDScene) else set()
    cam = scene.camera
    if isinstance(scene, m.ThreeDScene):  # the frame's right and up in the scene, per unit on screen
        phi, theta, zoom = cam.get_phi(), cam.get_theta(), cam.get_zoom()
        to_camera = np.array([np.sin(phi) * np.cos(theta), np.sin(phi) * np.sin(theta), np.cos(phi)])
        right = np.array([-np.sin(theta), np.cos(theta), 0])
        axes, centre = np.array([right, np.cross(to_camera, right)]) / zoom, np.asarray(cam.frame_center, float)
    else:
        axes, centre = np.eye(3)[:2], np.zeros(3)
    pieces, sources = [], []
    for mob in gone:
        for p in mob.get_family():
            if p.submobjects or not len(p.get_points()):
                continue
            # shortcut: where a piece lies on screen ignores perspective, fine for CAM_TOP; a tilted 3D view is off a bit
            pts = p.get_points()
            on_screen = pts[:, :2] if p in fixed else (pts - centre) @ axes.T / (axes ** 2).sum(1)
            if isinstance(p, m.VMobject):  # particles every _GRAIN along the outline
                step = np.r_[0, np.cumsum(np.linalg.norm(np.diff(on_screen, axis=0), axis=1))]
                at = np.arange(0, step[-1], _GRAIN) + _GRAIN / 2 if step[-1] > _GRAIN else [step[-1] / 2]
                grains = np.stack([np.interp(at, step, on_screen[:, i]) for i in (0, 1)], axis=1)
                look = (p.get_fill_opacity(), p.get_stroke_opacity())
            else:  # an image: particles on a grid over it
                (x0, y0), (x1, y1) = on_screen.min(0), on_screen.max(0)
                gx, gy = np.meshgrid(np.arange(x0, x1, 2 * _GRAIN), np.arange(y0, y1, 2 * _GRAIN))
                grains, look = np.stack([gx.ravel(), gy.ravel()], axis=1), None
            if not len(grains):  # too small for the grid: one particle in the middle
                grains = on_screen.mean(0, keepdims=True)
            sources.append(grains)
            along = grains @ _RIPPLE_AHEAD
            pieces.append((p, look, along.min(), along.max()))
    field = None
    if hasattr(scene, "backdrop"):
        scene.remove(scene.dots)
        field = scene.backdrop(*transition_field(scene.dots.t, duration, np.concatenate(sources or [np.zeros((0, 2))])),
                               t=scene.dots.t)
    clock = m.ValueTracker(0)

    def dissolve(_):
        front = _ripple_front(clock.get_value())
        for p, look, lead, trail in pieces:
            # fades while its particles break loose: from the front reaching its first part to its last
            u = np.clip((front - lead + 0.5 * _RIPPLE_WIDTH) / (trail - lead + 0.4 * _RIPPLE_WIDTH), 0, 1)
            e = u * u * (3 - 2 * u)
            if look is not None:
                p.set_fill(opacity=look[0] * (1 - e), family=False).set_stroke(opacity=look[1] * (1 - e), family=False)
            elif hasattr(p, "set_opacity"):
                p.set_opacity(1 - e)
    carrier = m.Mobject().add_updater(dissolve)
    scene.add(carrier)
    scene.play(clock.animate(rate_func=m.linear).set_value(1), run_time=duration)
    scene.remove(carrier, *gone)
    for p, look, *_ in pieces:
        if look is not None:
            p.set_fill(opacity=look[0], family=False).set_stroke(opacity=look[1], family=False)
        elif hasattr(p, "set_opacity"):
            p.set_opacity(1)
    if field is not None:
        scene.remove(field)
        scene.dots.t = field.t
        scene.add(scene.dots)


# ── Chapter card ───────────────────────────────────────────────────────────
def chapter_card(number, title, word="Hoofdstuk"):
    words = m.VGroup(text(f"{word} {number}", FS_HEADING, C_MUTED), text(title, FS_TITLE, weight="BOLD"))
    return words.arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.25)


def play_chapter_card(scene, number, title, hold=T_SLOW):
    card = chapter_card(number, title)
    _fix(scene, card)
    scene.remove(card)
    scene.play(m.FadeIn(card, shift=0.2 * m.LEFT), run_time=T_NORMAL)
    scene.wait(hold)
    scene.play(m.FadeOut(card), run_time=T_FAST)


# ── Formula card (Binas style) ─────────────────────────────────────────────
def formula_card(tex, legend, name=None):
    """The formula large, under it a table of its symbols: [("U", "spanning", "V"), ...], as in Binas.
    Returns VGroup(plate, content), like a panel: place it with to_corner or show it in the middle."""
    rows = [[formula(sym, FS_FORMULA_STEP), text(meaning), text(f"({unit})", color=C_MUTED)]
            for sym, meaning, unit in legend]
    x = 0.0
    for j in range(3):  # three left-aligned columns
        for i, row in enumerate(rows):
            row[j].move_to([x, -0.55 * i, 0], aligned_edge=m.LEFT)
        x += max(row[j].width for row in rows) + 0.4
    table = m.VGroup(*(m.VGroup(*row) for row in rows))
    key = formula(tex, FS_FORMULA_KEY)
    rule = m.Line(m.ORIGIN, max(table.width, key.width) * m.RIGHT).set_stroke(C_MUTED, SW_THIN)
    content = m.VGroup(*([text(name, FS_LABEL, C_MUTED)] if name else []), key, rule, table)
    content.arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.3)
    return m.VGroup(frame_plate(content, buff=0.35), content)


# ── End screen ─────────────────────────────────────────────────────────────
def end_screen(thanks="Bedankt voor het kijken!", next_video="volgende video", subscribe="abonneren"):
    """Thanks, and outlines where YouTube's end-screen elements go (two videos, subscribe)."""
    head = text(thanks, FS_TITLE, weight="BOLD")
    slots = m.VGroup(*(m.VGroup(r := m.Rectangle(width=4.4, height=4.4 * 9 / 16).set_stroke(C_MUTED, SW_THIN),
                                text(next_video, FS_SMALL, C_MUTED).move_to(r)) for _ in range(2)),
                     m.VGroup(c := m.Circle(radius=1.0).set_stroke(C_MUTED, SW_THIN),
                              text(subscribe, FS_SMALL, C_MUTED).move_to(c)))
    slots.arrange(m.RIGHT, buff=0.6)
    return m.VGroup(head, slots).arrange(m.DOWN, buff=0.8)


def play_end_screen(scene, hold=T_END_SCREEN):
    screen = end_screen()
    _fix(scene, screen)
    scene.remove(screen)
    scene.play(m.FadeIn(screen[0], shift=0.2 * m.UP), run_time=T_NORMAL)
    scene.play(m.FadeIn(screen[1]), run_time=T_FAST)
    scene.wait(hold)

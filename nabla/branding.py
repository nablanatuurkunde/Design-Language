"""Brand moments: the intro, a chapter card, a formula card in Binas style and the end screen.

This is the only place where the five brand colours appear together (BRAND_STRIPES). Each moment comes as a
builder (a mobject to place yourself) and a play_... function that shows it the standard way:

    play_intro(self)                         stripes grow in, the word mark appears
    play_chapter_card(self, 3, "Stroom")     between two parts of a video
    self.play(*self.show(formula_card(r"U = I \\cdot R", [("U", "spanning", "V"), ...], "Wet van Ohm")))
    play_end_screen(self)                    with room for YouTube's end-screen elements
"""
import manimgx as m

from .style import *


def _fix(scene, *mobs):
    """Fixed in frame in a 3D scene (Lesson), plainly added in a 2D one."""
    if isinstance(scene, m.ThreeDScene):
        scene.add_fixed_in_frame_mobjects(*mobs)
    else:
        scene.add(*mobs)


def stripes(width=4.0, bar=0.22, gap=0.08, slant=0.35):
    """The five stripes of the logo: slanted bars, red at the top, blue at the bottom.
    shortcut: drawn after the logo's colours, not traced from the logo file; swap for assets/ once it is there."""
    bars = [m.Polygon([0, 0, 0], [width, 0, 0], [width + slant, bar, 0], [slant, bar, 0])
            .set_stroke(width=0).set_fill(c, 1) for c in BRAND_STRIPES]
    return m.VGroup(*bars).arrange(m.DOWN, buff=gap)


def _grow(bars, run_time=T_SLOW):
    return m.LaggedStart(*(m.GrowFromEdge(b, m.LEFT) for b in bars), lag_ratio=0.15, run_time=run_time)


# ── Intro ──────────────────────────────────────────────────────────────────
def intro():
    s = stripes()
    word = text("Nabla", FS_BRAND, weight="BOLD")
    return m.VGroup(s, word).arrange(m.DOWN, buff=0.6)


def play_intro(scene):
    logo = intro()
    _fix(scene, logo)
    scene.remove(logo)
    scene.play(_grow(logo[0]))
    scene.play(m.FadeIn(logo[1], shift=0.2 * m.UP), run_time=T_NORMAL)
    scene.wait(T_PAUSE)
    scene.play(m.FadeOut(logo), run_time=T_FAST)


# ── Chapter card ───────────────────────────────────────────────────────────
def chapter_card(number, title, word="Hoofdstuk"):
    s = stripes(width=1.4, bar=0.16, gap=0.06, slant=0.2)
    words = m.VGroup(text(f"{word} {number}", FS_HEADING, C_MUTED), text(title, FS_TITLE, weight="BOLD"))
    words.arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.25)
    s.match_height(words)
    return m.VGroup(s, words).arrange(m.RIGHT, buff=0.5)


def play_chapter_card(scene, number, title, hold=T_SLOW):
    card = chapter_card(number, title)
    _fix(scene, card)
    scene.remove(card)
    scene.play(_grow(card[0], T_NORMAL), m.FadeIn(card[1], shift=0.2 * m.LEFT), run_time=T_NORMAL)
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
    plate = m.SurroundingRectangle(content, buff=0.35, corner_radius=0.12).set_stroke(C_MUTED, SW_THIN)
    plate.set_fill(C_BG, PANEL_OPACITY)
    return m.VGroup(plate, content)


# ── End screen ─────────────────────────────────────────────────────────────
def end_screen(thanks="Bedankt voor het kijken!", next_video="volgende video", subscribe="abonneren"):
    """Thanks, the stripes, and outlines where YouTube's end-screen elements go (two videos, subscribe)."""
    head = m.VGroup(text(thanks, FS_TITLE, weight="BOLD"), stripes(width=3.0, bar=0.1, gap=0.05, slant=0.15))
    head.arrange(m.DOWN, buff=0.35)
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
    scene.play(m.FadeIn(screen[0][0], shift=0.2 * m.UP), _grow(screen[0][1], T_NORMAL), run_time=T_NORMAL)
    scene.play(m.FadeIn(screen[1]), run_time=T_FAST)
    scene.wait(hold)

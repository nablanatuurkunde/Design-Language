"""Reference scene: every colour, type size, component, animation and brand moment of nabla-design side by side.
Its storyboard (the frame at the end of each play) gives the stills in docs/img.

Run from the repo root:  python -m manimgx render examples/StyleSheet.py -o videos/StyleSheet.mp4
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # use this checkout, also when not installed
import numpy as np
import manimgx as m
from nabla import *

COLORS = [("C_VOLTAGE", C_VOLTAGE, "U spanning"), ("C_ENERGY", C_ENERGY, "E energie"),
          ("C_CURRENT", C_CURRENT, "I stroom"), ("C_RESISTANCE", C_RESISTANCE, "R weerstand"),
          ("C_POWER", C_POWER, "P vermogen"), ("C_CHARGE", C_CHARGE, "Q lading"),
          ("C_ACCENT", C_ACCENT, "let op, gevaar"), ("C_LIGHT", C_LIGHT, "lamp aan"),
          ("C_ELECTRON", C_ELECTRON, "elektronen"), ("C_WATER", C_WATER, "water"),
          ("C_COPPER", C_COPPER, "koper"), ("C_USEFUL", C_USEFUL, "nuttige energie"),
          ("C_LOSS", C_LOSS, "verlies, warmte"), ("C_TEXT", C_TEXT, "tekst, draden, stroompijltjes"),
          ("C_MUTED", C_MUTED, "bijzaken, randen")]


class StyleSheet(Lesson):
    def construct(self):
        self.set_camera_orientation(**CAM_TOP, zoom=1.0, frame_center=m.ORIGIN)
        play_intro(self)
        for page in (self.colors, self.type, self.components, self.current, self.patterns):
            page()
            self.play(*vanish(*(x for x in self.mobjects if x is not self._bg)), run_time=T_FAST)
        play_chapter_card(self, 3, "Stroom")
        play_end_screen(self, hold=T_END_HOLD)

    def background(self, distance=0.35):
        self._bg = super().background(distance)
        return self._bg

    def page(self, heading, *mobs, fixed=()):
        """Title and fixed panels in frame (hud); mobs in the scene, where the current arrows move too."""
        self.play(*self.show(title(heading), *fixed), *appear(*mobs), run_time=T_NORMAL)
        self.wait(T_PAUSE)

    def colors(self):
        cells = m.VGroup(*(m.VGroup(m.Square(0.4).set_stroke(width=0).set_fill(c, 1),
                                    m.VGroup(text(name, FS_SMALL), text(meaning, FS_SMALL, C_MUTED))
                                    .arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.06)).arrange(m.RIGHT, buff=0.2)
                           for name, c, meaning in COLORS))
        cells.arrange_in_grid(rows=5, buff=(0.6, 0.3), flow_order="dr").move_to(0.4 * m.DOWN)
        self.page("Kleuren", cells)

    def type(self):
        sizes = m.VGroup(*(text(f"{name} {size}", size) for name, size in
                           [("FS_TITLE", FS_TITLE), ("FS_HEADING", FS_HEADING), ("FS_LABEL", FS_LABEL),
                            ("FS_SUBTITLE", FS_SUBTITLE), ("FS_SMALL", FS_SMALL)]))
        sizes.arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.3)
        forms = m.VGroup(formula(r"U = I \cdot R", FS_FORMULA_KEY), formula(r"P = U \cdot I", FS_FORMULA),
                         formula(comma(r"E = Q \cdot U = 4 \cdot 3,7 = 14,8\ \mathrm{J}"), FS_FORMULA_STEP),
                         value("I", 0.25, "A", 2))
        forms.arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.35)
        self.page("Letters en formules", m.VGroup(sizes, forms).arrange(m.RIGHT, buff=1.2, aligned_edge=m.UP)
                  .move_to(0.3 * m.DOWN))

    def components(self):
        parts = [("Battery", Battery()), ("AcSource", AcSource()), ("Resistor", Resistor()),
                 ("VariableResistor", VariableResistor()), ("LDR", LDR()), ("NTC", NTC()), ("PTC", PTC()),
                 ("Lamp", Lamp()), ("Lamp(1)", Lamp(1)), ("Switch", Switch()), ("Switch(0)", Switch(0)),
                 ("Diode", Diode()), ("LED", LED()), ("Fuse", Fuse()), ("Fuse(True)", Fuse(True)),
                 ("Ammeter", Ammeter()), ("Voltmeter", Voltmeter()), ("Motor", Motor())]
        cols = 6
        for k, (n, c) in enumerate(parts):  # a fixed grid on the terminals, so every name sits on the same line
            at = np.array([-5.0 + 2.0 * (k % cols), 1.6 - 2.0 * (k // cols), 0])
            c.place(at - 0.6 * m.RIGHT, at + 0.6 * m.RIGHT)
        cells = m.VGroup(*(m.VGroup(c, text(n, FS_SMALL, C_MUTED).move_to((c.a + c.b) / 2 + 0.75 * m.DOWN))
                           for n, c in parts))
        glow = parts[8][1].glow()
        self.page("Schakelsymbolen", glow, cells)

    def current(self):
        # a loop with a battery (left, + at the top), a lamp and an ammeter; wires attach to the terminals
        L, R, T, B = -4.0, 1.0, 1.6, -2.4
        bat = Battery().place([L, 0.6, 0], [L, -0.6, 0])  # terminal a (+) at the top
        lamp = Lamp(1).place([R, 0.6, 0], [R, -0.6, 0])
        meter = Ammeter().place([-1.0, B, 0], [-2.2, B, 0])
        wires = m.VGroup(Wire(bat.a, [L, T, 0], [R, T, 0], lamp.a), Wire(lamp.b, [R, B, 0], meter.a),
                         Wire(meter.b, [L, B, 0], bat.b))
        loop = [bat.a, [L, T, 0], [R, T, 0], [R, B, 0], [L, B, 0], bat.b]
        I = m.ValueTracker(1.5)
        arrows = current_by_density(loop, I, max_current=3)
        info = panel(value("I", 1.5, "A"), "dichtheid = stroom", corner=m.UR)
        self.page("Stroom en elektronen", lamp.glow(), wires, bat, lamp, meter, fixed=[info])
        self.add(arrows)
        self.wait(2)
        self.play(I.animate.set_value(3), swap_value(info[1][0], value("I", 3, "A")),
                  run_time=T_NORMAL)
        self.wait(2)
        speed = m.ValueTracker(1.0)
        by_speed = current_by_speed(loop, speed)
        self.play(I.animate.set_value(0), swap_value(info[1][1], text("snelheid = stroom")), run_time=T_FAST)
        self.remove(arrows)
        self.add(by_speed)
        self.wait(2)
        self.play(speed.animate.set_value(2), run_time=T_NORMAL)
        self.wait(1)
        electrons = electron_flow(loop, m.ValueTracker(1.0))
        self.remove(by_speed)
        self.add(electrons)
        self.play(swap_value(info[1][1], text("elektronen: − → +", color=C_ELECTRON)), run_time=T_FAST)
        self.wait(2)
        self.remove(electrons)

    def patterns(self):
        res = Resistor()
        circuit = branch([-6, -2, 0], [-2, -2, 0], res)
        card = formula_card(r"U = I \cdot R", [("U", "spanning", "V"), ("I", "stroomsterkte", "A"),
                                               ("R", "weerstand", "Ω")], "Wet van Ohm").to_corner(m.DR, buff=MARGIN)
        self.page("Animaties", fixed=[card])
        self.play(draw(circuit), run_time=T_NORMAL)
        self.play(point_at(res, C_RESISTANCE), run_time=T_NORMAL)
        summary = panel("samenvatting: regels één voor één", formula(r"U = I \cdot R"),
                        formula(r"P = U \cdot I"), corner=m.UL).shift(1.0 * m.DOWN)
        self.hud(summary[0])
        self.one_by_one(summary[1], 1.5, m.FadeIn(summary[0]))
        brd = board(formula(r"R = \frac{U}{I}"), formula(comma(r"R = \frac{6,0}{0,5} = 12\ \Omega")))
        self.play(*vanish(card, summary), run_time=T_FAST)
        self.board_in(brd)
        self.play(*self.show(*brd[1]), run_time=T_NORMAL)
        self.wait(T_PAUSE)
        self.board_out(brd)
        d = say(self, "Zo ziet een ondertitel eruit: onderaan, op een donkere achtergrond.")
        self.wait(d)
        say(self, "")

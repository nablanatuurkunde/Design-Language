"""Telling the story (nabla.scene): subtitle, panel, formula card and the white calculation board."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # use this checkout, also when not installed
import manimgx as m
from nabla import *


class Story(Lesson):
    def construct(self):
        self.set_camera_orientation(**CAM_TOP, zoom=1.0, frame_center=m.ORIGIN)
        circuit = branch([-3, 1, 0], [3, 1, 0], Resistor())  # above the formula card
        self.play(draw(circuit), run_time=T_NORMAL)

        self.wait(say(self, "Dit is een ondertitel: onderaan, op een donkere achtergrond."))
        say(self, "")

        info = panel("panel()", value("I", 0.5, "A"), corner=m.UL)
        card = formula_card(r"U = I \cdot R", [("U", "spanning", "V"), ("I", "stroomsterkte", "A"),
                                               ("R", "weerstand", "Ω")], "Wet van Ohm").to_corner(m.DR, buff=MARGIN)
        self.play(*self.show(info, card), run_time=T_NORMAL)
        self.wait(T_END_HOLD)
        self.play(*vanish(info, card), run_time=T_FAST)

        brd = board(formula(r"U = I \cdot R"), formula(r"I = \frac{U}{R}"),
                    formula(comma(r"I = \frac{6,0}{12} = 0,50\ \mathrm{A}")))
        self.board_in(brd)
        self.one_by_one(brd[1], T_NORMAL * len(brd[1]))
        self.wait(T_END_HOLD)
        self.board_out(brd)
        self.end()

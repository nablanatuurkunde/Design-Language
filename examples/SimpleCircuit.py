"""Example: a battery and a resistor, current flowing, then Ohm's law worked out on the white board.

Run from the repo root:  python -m manimgx preview examples/SimpleCircuit.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # use this checkout, also when not installed
import manimgx as m
from nabla import *


class SimpleCircuit(Lesson):
    def construct(self):
        self.set_camera_orientation(**CAM_TOP, zoom=1.0, frame_center=m.ORIGIN)

        # loop: battery on the left (+ at the top), resistor on the right
        L, R, T, B = -2.5, 2.5, 1.5, -1.5
        bat = Battery().place([L, 0.6, 0], [L, -0.6, 0])
        res = Resistor().place([R, 0.6, 0], [R, -0.6, 0])
        wires = m.VGroup(Wire(bat.a, [L, T, 0], [R, T, 0], res.a), Wire(res.b, [R, B, 0], [L, B, 0], bat.b))
        loop = [bat.a, [L, T, 0], [R, T, 0], [R, B, 0], [L, B, 0], bat.b]

        d = say(self, "Een batterij van 6 volt met een weerstand van 12 ohm.")
        self.do(d, draw(m.VGroup(wires, bat, res)))

        I = m.ValueTracker(0)
        self.add(current_by_density(loop, I, max_current=1))
        d = say(self, "Er loopt een stroom, van plus naar min. Hoe groot is die stroom?")
        self.do(d, I.animate.set_value(0.5), point_at(res, C_RESISTANCE))

        brd = board(formula(r"U = I \cdot R"), formula(r"I = \frac{U}{R}"),
                    formula(comma(r"I = \frac{6,0}{12} = 0,50\ \mathrm{A}")))
        self.wait(say(self, "Met de wet van Ohm rekenen we het uit."))
        say(self, "")  # the subtitle plate is dark: it would cover the white board
        self.board_in(brd)
        self.one_by_one(brd[1], T_NORMAL * len(brd[1]))
        self.wait(T_PAUSE)

        self.board_out(brd)
        self.end()

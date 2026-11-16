"""The fixed ways to enter, change and leave: draw, appear, point_at, swap_value, vanish."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # use this checkout, also when not installed
import manimgx as m
from nabla import *


class Animations(Lesson):
    def construct(self):
        self.set_camera_orientation(**CAM_TOP, zoom=1.0, frame_center=m.ORIGIN)
        self.play(*self.show(title("Animaties")), run_time=T_FAST)
        res = Resistor()
        circuit = branch([-3, 0, 0], [3, 0, 0], res)
        name = text("draw()", FS_LABEL, C_MUTED).to_edge(m.DOWN, buff=1.5)
        self.add(name)
        self.play(draw(circuit), run_time=T_NORMAL)
        self.wait(T_PAUSE)

        r = value("R", 12, "Ω", 0).next_to(res, m.UP, buff=0.4)
        self.play(*appear(r), swap_value(name, text("appear()", FS_LABEL, C_MUTED)), run_time=T_NORMAL)
        self.wait(T_PAUSE)
        self.play(point_at(res, C_RESISTANCE), swap_value(name, text("point_at()", FS_LABEL, C_MUTED)),
                  run_time=T_NORMAL)
        self.wait(T_PAUSE)
        self.play(swap_value(r, value("R", 24, "Ω", 0)), swap_value(name, text("swap_value()", FS_LABEL, C_MUTED)),
                  run_time=T_NORMAL)
        self.wait(T_PAUSE)
        self.play(*vanish(circuit, r), swap_value(name, text("vanish()", FS_LABEL, C_MUTED)), run_time=T_NORMAL)
        self.wait(T_END_HOLD)

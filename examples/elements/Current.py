"""The three ways to show charge moving: current_by_density, current_by_speed and electron_flow."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # use this checkout, also when not installed
import manimgx as m
from nabla import *


class Current(Lesson):
    def construct(self):
        self.set_camera_orientation(**CAM_TOP, zoom=1.0, frame_center=m.ORIGIN)
        L, R, T, B = -4.0, 1.0, 1.6, -2.4
        bat = Battery().place([L, 0.6, 0], [L, -0.6, 0])  # terminal a (+) at the top
        lamp = Lamp(1).place([R, 0.6, 0], [R, -0.6, 0])
        wires = m.VGroup(Wire(bat.a, [L, T, 0], [R, T, 0], lamp.a), Wire(lamp.b, [R, B, 0], [L, B, 0], bat.b))
        loop = [bat.a, [L, T, 0], [R, T, 0], [R, B, 0], [L, B, 0], bat.b]
        info = panel(value("I", 1.5, "A"), "current_by_density", corner=m.UR)
        self.play(*self.show(title("Stroom en elektronen"), info), *appear(lamp.glow(), wires, bat, lamp),
                  run_time=T_NORMAL)

        I = m.ValueTracker(1.5)
        flow = current_by_density(loop, I, max_current=3)
        self.add(flow)
        self.wait(2)
        self.play(I.animate.set_value(3), swap_value(info[1][0], value("I", 3, "A")), run_time=T_NORMAL)
        self.wait(2)
        self.remove(flow)

        speed = m.ValueTracker(1.0)
        flow = current_by_speed(loop, speed)
        self.add(flow)
        self.play(swap_value(info[1][1], text("current_by_speed")), run_time=T_FAST)
        self.wait(1)
        self.play(speed.animate.set_value(2), run_time=T_NORMAL)
        self.wait(1)
        self.remove(flow)

        self.add(electron_flow(loop, m.ValueTracker(1.0)))
        self.play(swap_value(info[1][1], text("electron_flow: − → +", color=C_ELECTRON)), run_time=T_FAST)
        self.wait(T_END_HOLD)

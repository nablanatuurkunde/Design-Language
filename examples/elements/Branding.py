"""The brand moments (nabla.branding): intro, chapter card and end screen."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # use this checkout, also when not installed
import manimgx as m
from nabla import *


class Branding(Lesson):
    def construct(self):
        self.set_camera_orientation(**CAM_TOP, zoom=1.0, frame_center=m.ORIGIN)
        play_chapter_card(self, 1, "Intro")
        play_intro(self)
        circuit = branch([-3, -1, 0], [3, -1, 0], Resistor())  # something in frame for the transition to wipe out
        self.play(*self.show(title("Overgang"), panel(value("I", 0.5, "A"), corner=m.UR)), draw(circuit),
                  run_time=T_NORMAL)
        self.wait(T_PAUSE)
        play_transition(self)
        play_chapter_card(self, 2, "Titel")
        play_end_screen(self, hold=T_END_HOLD)

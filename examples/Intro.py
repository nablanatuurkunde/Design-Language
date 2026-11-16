"""The intro on its own: play_intro, the logo animation of assets/Intro.mov rebuilt in nabla.branding."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # use this checkout, also when not installed
import manimgx as m
from nabla import *


class Intro(Lesson):
    def construct(self):
        self.set_camera_orientation(**CAM_TOP, zoom=1.0, frame_center=m.ORIGIN)
        play_intro(self)

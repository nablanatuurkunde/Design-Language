"""Type sizes, formulas and the text helpers of nabla.style: title, label, box, formula, value, comma."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # use this checkout, also when not installed
import manimgx as m
from nabla import *


class Text(Lesson):
    def construct(self):
        self.set_camera_orientation(**CAM_TOP, zoom=1.0, frame_center=m.ORIGIN)
        sizes = m.VGroup(*(text(f"{name} {size}", size) for name, size in
                           [("FS_TITLE", FS_TITLE), ("FS_HEADING", FS_HEADING), ("FS_LABEL", FS_LABEL),
                            ("FS_SUBTITLE", FS_SUBTITLE), ("FS_SMALL", FS_SMALL)]))
        sizes.arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.3)
        forms = m.VGroup(formula(r"U = I \cdot R", FS_FORMULA_KEY), formula(r"P = U \cdot I", FS_FORMULA),
                         formula(comma(r"E = Q \cdot U = 4 \cdot 3,7 = 14,8\ \mathrm{J}"), FS_FORMULA_STEP),
                         value("I", 0.25, "A", 2))
        forms.arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.35)
        m.VGroup(sizes, forms).arrange(m.RIGHT, buff=1.2, aligned_edge=m.UP).move_to(0.6 * m.UP)

        lamp = Lamp().place([-1.6, -2.4, 0], [-0.4, -2.4, 0])
        warning = formula(r"R = 0\ \Omega").move_to([2.5, -2.4, 0])
        boxed = box(warning)
        helpers = m.VGroup(lamp, label("label()", lamp), boxed, label("box()", boxed, m.DOWN))
        self.play(*self.show(title("Letters en formules")), *appear(sizes, forms, helpers), run_time=T_NORMAL)
        self.wait(T_END_HOLD)

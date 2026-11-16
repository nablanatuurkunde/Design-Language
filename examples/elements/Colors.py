"""Every colour of nabla.style with its meaning (the five brand colours together only appear in the logo: Branding.py)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # use this checkout, also when not installed
import manimgx as m
from nabla import *

COLORS = [("C_VOLTAGE", C_VOLTAGE, "U spanning"), ("C_ENERGY", C_ENERGY, "E energie"),
          ("C_CURRENT", C_CURRENT, "I stroom"), ("C_RESISTANCE", C_RESISTANCE, "R weerstand"),
          ("C_POWER", C_POWER, "P vermogen"), ("C_CHARGE", C_CHARGE, "Q lading"),
          ("C_ACCENT", C_ACCENT, "let op, gevaar"), ("C_CURRENT_ARROW", C_CURRENT_ARROW, "stroompijltjes"),
          ("C_ELECTRON", C_ELECTRON, "elektronen"), ("C_JOULE", C_JOULE, "joules uit een lamp"),
          ("C_LIGHT", C_LIGHT, "lamp aan"), ("C_WATER", C_WATER, "water (analogie)"),
          ("C_FIELD", C_FIELD, "magnetisch veld"), ("C_COPPER", C_COPPER, "koper"),
          ("C_HOT", C_HOT, "gloeiend"), ("C_USEFUL", C_USEFUL, "nuttige energie"),
          ("C_LOSS", C_LOSS, "verlies, warmte"), ("C_TEXT", C_TEXT, "tekst, draden"),
          ("C_MUTED", C_MUTED, "bijzaken, randen"), ("LED_COLORS", LED_COLORS[0], "LED's (uitzondering)")]


class Colors(Lesson):
    def construct(self):
        self.set_camera_orientation(**CAM_TOP, zoom=1.0, frame_center=m.ORIGIN)
        cells = m.VGroup(*(m.VGroup(m.Square(0.4).set_stroke(width=0).set_fill(c, 1),
                                    m.VGroup(text(name, FS_SMALL), text(meaning, FS_SMALL, C_MUTED))
                                    .arrange(m.DOWN, aligned_edge=m.LEFT, buff=0.06)).arrange(m.RIGHT, buff=0.2)
                           for name, c, meaning in COLORS))
        cells.arrange_in_grid(rows=7, buff=(0.8, 0.25), flow_order="dr").move_to(0.6 * m.DOWN)
        self.play(*self.show(title("Kleuren")), *appear(cells), run_time=T_NORMAL)
        self.wait(T_END_HOLD)

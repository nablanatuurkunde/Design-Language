"""Every circuit symbol of nabla.circuits, plus Wire, Node, Ground and the lamp glow."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # use this checkout, also when not installed
import numpy as np
import manimgx as m
from nabla import *


class Components(Lesson):
    def construct(self):
        self.set_camera_orientation(**CAM_TOP, zoom=1.0, frame_center=m.ORIGIN)
        parts = [("Battery", Battery()), ("AcSource", AcSource()), ("Resistor", Resistor()),
                 ("VariableResistor", VariableResistor()), ("LDR", LDR()), ("NTC", NTC()), ("PTC", PTC()),
                 ("Lamp", Lamp()), ("Lamp(1)", Lamp(1)), ("Switch", Switch()), ("Switch(0)", Switch(0)),
                 ("Diode", Diode()), ("LED", LED()), ("Fuse", Fuse()), ("Fuse(True)", Fuse(True)),
                 ("Ammeter", Ammeter()), ("Voltmeter", Voltmeter()), ("Motor", Motor())]
        cols = 6
        for k, (n, c) in enumerate(parts):  # a fixed grid on the terminals, so every name sits on the same line
            at = np.array([-5.0 + 2.0 * (k % cols), 1.9 - 1.7 * (k // cols), 0])
            c.place(at - 0.6 * m.RIGHT, at + 0.6 * m.RIGHT)
        cells = m.VGroup(*(m.VGroup(c, text(n, FS_SMALL, C_MUTED).move_to((c.a + c.b) / 2 + 0.7 * m.DOWN))
                           for n, c in parts))

        # wiring: Wire with a corner, a Node where it branches, Ground hanging from it
        y = -3.0
        wiring = m.VGroup(Wire([-5.6, y + 0.6, 0], [-5.6, y, 0], [-3.4, y, 0]), Node([-4.5, y, 0]),
                          Ground([-4.5, y, 0]))
        names = text("Wire, Node, Ground", FS_SMALL, C_MUTED).next_to(wiring, m.RIGHT, buff=0.3)
        self.play(*self.show(title("Schakelsymbolen")), *appear(parts[8][1].glow(), cells, wiring, names),
                  run_time=T_NORMAL)
        self.wait(T_END_HOLD)

"""nabla-design: the look of every Nabla video. A scene does `from nabla import *`.

style.py       brand and semantic colours, type sizes, strokes, timing, layout; text and formula helpers
circuits.py    circuit symbols as classes (Binas), wires and nodes
animations.py  fixed ways to enter, leave and change; current arrows and electrons
branding.py    intro, chapter card, formula card, end screen
scene.py       Lesson (the base of every video), subtitles, panels, the calculation board
"""
__version__ = "0.2.0"

from .style import *
from .circuits import *
from .animations import *
from .scene import *
from .branding import *

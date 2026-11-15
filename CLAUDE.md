# nabla-design

The design language of the Nabla physics videos (HAVO/VWO, Dutch, made with **manimgx**, not ManimGL). Every video
repo installs this package at a fixed version tag and does `from nabla import *`. See `docs/STYLEGUIDE.md`.

## Hard rules (here and in every video repo)

1. **No hard-coded style values in scenes.** No hex colours, no `m.BLUE` etc., no loose numbers for `font_size`,
   `stroke_width`, `run_time` or layout positions that belong to the style. Use the names in `nabla/style.py`
   (`C_CURRENT`, `FS_LABEL`, `SW_WIRE`, `T_FAST`, ...). A deliberate exception gets a comment saying why.
2. **Circuit symbols only from `nabla.circuits`.** IEC/NEN as in Binas: a resistor is a rectangle, never a zigzag.
   Wires attach to `component.a` / `component.b`. Do not draw a symbol by hand in a video repo; add it here.
3. **Style changes only in this repo, with a new version tag.** A video pins a tag; changing the look means a new
   release here (bump `__version__` in `nabla/__init__.py`, tag `vX.Y.Z`) and then bumping the pin in the video.
   Never patch style in a video repo.
4. **The five brand colours together (`BRAND_STRIPES`) only for brand moments**: intro, chapter cards, end screen,
   all in `nabla/branding.py`. The single exception is `LED_COLORS`.

## Colour meanings (fixed)

U and E yellow · I blue · R orange · P green · Q red · current arrows white (+ → −) · electrons yellow (− → +) ·
C_ACCENT red = danger/attention · everything else white or grey on black.

## Working here

- Layout: `nabla/style.py` (constants and text/formula helpers), `circuits.py`, `animations.py`, `scene.py`
  (`Lesson`, subtitles, panels, board), `branding.py`. Render settings in `custom_config.yml`.
- After a change, render the reference scene and look at it:
  `python -m manimgx render examples/StyleSheet.py -o videos/StyleSheet.mp4`
  then update the stills in `docs/img/` (frames from that video) if the look changed.
- Only render when the user asks, except to verify a change to this package.
- Decimal comma: `comma()` / `value()`. Never `{,}` (manimgx puts a space after it).
- Code is English; on-screen text and docs are Dutch.
- Binaries in `assets/` go through Git LFS (see `.gitattributes`).

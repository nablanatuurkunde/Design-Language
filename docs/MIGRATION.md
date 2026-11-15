# Het elektriciteit-project overzetten naar nabla-design

Dit document beschrijft hoe [Elektriciteit](https://github.com/nablanatuurkunde/Elektriciteit) overgaat van
zijn eigen `bouwstenen/` naar `nabla-design` v0.1.0. De regelnummers horen bij de werkversie van
16-11-2026, inclusief de wijzigingen die toen nog niet gecommit waren. Controleer ze voordat je begint.

## 1. Installeren en vastzetten

Zet in het videoproject een `requirements.txt` neer:

```
nabla-design @ git+https://github.com/nablanatuurkunde/Design-Language@v0.1.0
```

Installeer met `pip install -r requirements.txt`. Werk je tegelijk aan de stijl, gebruik dan
`pip install -e ../Design-Language`.

**`film.py`, regel 36–41 (`vingerafdruk`):** neem ook de versie van nabla-design op in de hash. Anders rendert een
nieuwe stijlversie niets opnieuw:

```python
import nabla
h.update(nabla.__version__.encode())
```

## 2. Wat er met `bouwstenen/` gebeurt

| Bestand | Wordt |
|---|---|
| `stijl.py` | **weg**: alles staat in `nabla.style` |
| `symbolen.py` | **weg**: `nabla.circuits` en `nabla.animations`. Alleen `zon()` (r. 216–232) is videospecifiek: verhuis die naar `kring.py` of naar `08_sensoren.py` (de intro gebruikt hem ook) |
| `verhaal.py` | **weg**: `nabla.scene` |
| `kring.py`, `schakeling.py`, `modellen.py` | **blijven** (natuurkunde en 3D-modellen van deze video), maar met `from nabla import *` in plaats van `from .stijl import *` / `from .symbolen import *`. Hernoem de namen volgens de tabel hieronder |
| `__init__.py` | importeert `nabla` en de drie overgebleven modules |

Een scène doet daarna `from bouwstenen import *`. Dat werkt nog steeds, omdat `bouwstenen` op zijn beurt nabla doorgeeft.

## 3. Vertaaltabel oud → nieuw

### Stijl (`stijl.py` → `nabla.style`)

| Oud | Nieuw | Let op |
|---|---|---|
| `BG`, `TEKST`, `DRAAD`, `GEDEMPT`, `ACCENT` | `C_BG`, `C_TEXT`, `C_WIRE`, `C_MUTED`, `C_ACCENT` | |
| `U_KLEUR`, `I_KLEUR`, `R_KLEUR`, `P_KLEUR` | `C_VOLTAGE`, `C_CURRENT`, `C_RESISTANCE`, `C_POWER` | |
| `E_KLEUR` | `C_ENERGY` | **was rood, nu geel** |
| `Q_KLEUR` | `C_CHARGE` | **was blauw, nu rood** |
| `LICHT`, `ELEKTRON_KLEUR`, `WATER_KLEUR` | `C_LIGHT`, `C_ELECTRON`, `C_WATER` | |
| `PIJL_KLEUR` | `C_CURRENT_ARROW` | wit |
| `ROOD`, `ORANJE`, `GEEL`, `GROEN`, `BLAUW`, `WIT`, `ZWART` | `N_RED`, … , `WHITE`, `BLACK` | alleen voor branding en `LED_COLORS`; in scenes een semantische naam kiezen |
| koper `ORANJE` | `C_COPPER` | |
| `GROOTHEDEN` | `QUANTITY_COLORS` | |
| `TITEL`, `KOP`, `LABEL`, `KLEIN` | `FS_TITLE`, `FS_HEADING`, `FS_LABEL`, `FS_SMALL` | |
| `FORMULE` | `FS_FORMULA` | |
| `STREEP`, `MAATLAT_DIKTE` | `SW_SYMBOL` | |
| `DRAAD_DIKTE` | `SW_WIRE` | |
| `RAND_DIKTE` | `SW_THIN` | |
| `LENGTE` | `SYMBOL_LENGTH` | |
| `PIJL_VOOR`, `PIJL_ACHTER`, `PIJL_BREED` | `ARROW_FRONT`, `ARROW_BACK`, `ARROW_HALF_WIDTH` | |
| `DEELTJE_STRAAL` | `ELECTRON_R_WIRE` | |
| `GLOED_STRAAL/RINGEN/DEKKING` | `GLOW_RADII/RINGS/OPACITY` | |
| `HALO_STRAAL/LAGEN/DEKKING`, `LAMPLICHT` | `HALO_RADII/LAYERS/OPACITY`, `LAMP_LIGHT` | |
| `PANEEL_DEKKING` | `PANEL_OPACITY` | |
| `MAT_DOORZICHT`, `MAT_RUW` | `MAT_OPACITY`, `MAT_ROUGHNESS` | |
| `SNEL`, `NORMAAL`, `TRAAG`, `PAUZE` | `T_FAST`, `T_NORMAL`, `T_SLOW`, `T_PAUSE` | |
| `SCHAKELING`, `FORMULES` | `ZONE_CIRCUIT`, `ZONE_FORMULAS` | |
| `mat()` | `material()` | |
| `tekst(s, size, kleur)` | `text(s, size, color)` | |
| `titel()`, `kader()` | `title()`, `box()` | |
| `label(s, doel, richting, size=, kleur=)` | `label(s, target, direction)` | standaard is nu `FS_LABEL` en wit; `size=LABEL, kleur=TEKST` kan weg |
| `formule()`, `komma()`, `waarde()` | `formula()`, `comma()`, `value()` | |
| `pijlhoeken()`, `lampgloed()` | `arrow_corners()`, `lamp_glow()` | |
| `m.config.background_color = BG` | vervalt | `custom_config.yml` regelt het |

### Symbolen (`symbolen.py` → `nabla.circuits`)

| Oud | Nieuw |
|---|---|
| `bron()` | `Battery()` (ook `Source()`) |
| `wisselbron()` | `AcSource()` |
| `weerstand()` | `Resistor()` |
| `weerstand_zigzag()` | **vervalt** (zie 05_weerstand) |
| `variabele_weerstand()`, `ntc()`, `ptc()`, `ldr()` | `VariableResistor()`, `NTC()`, `PTC()`, `LDR()` |
| `lamp()` + `s[2].set_fill(LICHT, …)` | `Lamp(brightness)`, `lamp.set_brightness(h)`, `lamp.glow()` |
| `diode()`, `led()` | `Diode()`, `LED()` |
| `schakelaar(open=True)` | `Switch()` (open), `Switch(0)` (dicht) |
| `schakelaar_stand(hoek)` | `Switch(hoek)` |
| `zekering(doorgebrand)` | `Fuse(blown)` |
| `meter("A")`, `meter("V")`, `motor()` | `Ammeter()`, `Voltmeter()`, `Motor()` (of `Meter("X")`) |
| `aarde(p)` | `Ground(p)` |
| `plaats(sym, p, q)` | `sym.place(p, q)` |
| `pool_a(sym)`, `pool_b(sym)` | `sym.a`, `sym.b` |
| `draad(*punten)` | `Wire(*punten)` |
| `tak(p, q, sym)`, `knoop(p)` | `branch(p, q, sym)`, `Node(p)` |
| `pijltjes_langs(punten)` | `current_by_speed(punten, speed)` of `current_by_density(punten, I, I_max)` |
| `elektronen_langs(punten)` | `electron_flow(punten, speed)` |

Let op bij indexeren: de onderdelen van `Lamp` staan nog op dezelfde plek (`[2]` is de cirkel), maar
**de dikke minplaat van `Battery` staat nu op `[4]`**. Op `[2]` staat een vlakje in de achtergrondkleur, zodat de pijltjes tussen de platen verdwijnen.

### Vertellen (`verhaal.py` → `nabla.scene`)

| Oud | Nieuw |
|---|---|
| `Les` | `Lesson` |
| `zeg(self, s)`, `spreektijd(s)` | `say(self, s)`, `speaking_time(s)` |
| `ONDERTITEL_IN_BEELD`, `WOORDEN_PER_SEC` | `SUBTITLES_IN_FRAME`, `WORDS_PER_SEC` |
| `paneel(*r, hoek=)`, `kaart(*r, hoek=, size=)` | `panel(*r, corner=, size=)`: één stijl, strings mogen direct |
| `paneel_delen(*r, hoek=)` | `panel_parts(*r, corner=)` |
| `rekenbord()`, `op_bord()` | `board()`, `on_board()` |
| `links(cam)` | `figure_left(cam)` |
| `SCHEIDING_X`, `BORD_BOVEN` | `BOARD_LEFT_X`, `BOARD_TOP_Y` |
| `stippen_patroon()`, `RONDJE` | `dots_pattern()`, `DOT` |
| `self.toon()`, `self.na_elkaar()`, `self.doe(d, …, duur=)` | `self.show()`, `self.one_by_one()`, `self.do(d, …, duration=)` |
| `self.camerabaan(…, begin="zacht"/"door")` | `self.camera_path(…, start="soft"/"through")` |
| `self.camerastand()` | `self.camera_state()` |
| `self.bord_in/bord_uit/bord_wissel(…, duur=)` | `self.board_in/board_out/board_swap(…, duration=)` |
| `self.achtergrond()` | `self.background()` |
| `zeg(self, ""); self.wait(2 of 3)` | `self.end()` |
| `self.wait(d + 2)` na "pauzeer de video" | `self.think(d)` |

`panel()` met een hoek onderaan (`DL`, `DR`) schuift nu zelf boven de ondertitels. Haal de handmatige `shift(1.1 * m.UP)` dus weg.

### `schakeling.py`

| Regel | Wijziging |
|---|---|
| 18–19 | `V_PIJL` → `CURRENT_SPEED`, `Q_PIJL` → `CHARGE_PER_ARROW` |
| 92 | `{"bron": bron, "lamp": lamp, "weerstand": weerstand, "wissel": wisselbron}` → `{"bron": Battery, "lamp": Lamp, "weerstand": Resistor, "wissel": AcSource}` |
| 93 | `plaats(maak(), P, Q)` → `maak().place(P, Q)` |
| 96–99 | lampvulling met de hand → `sym.set_brightness(hl)` |
| 107 | `set_stroke(ACCENT, 7, …)` → `set_stroke(C_ACCENT, SW_HEAVY, …)` |
| 109 | `ORANJE` → `C_HOT` |
| 119, 121 | `draad(…)`, `knoop(…)` → `Wire(…)`, `Node(…)` |
| 206 | `PIJL_KLEUR` → `C_CURRENT_ARROW` |
| 229 | `pijlhoeken` → `arrow_corners` |
| 247–248 | `U_KLEUR`, `MAATLAT_DIKTE` → `C_VOLTAGE`, `SW_SYMBOL` |
| 298 | `m.Dot(radius=0.05, color=LICHT)` → `m.Dot(radius=JOULE_R, color=C_JOULE)` |

### `kring.py`

| Regel | Wijziging |
|---|---|
| 22, 157–168 | `draad` → `Wire` |
| 27–28, 161 | `plaats(bron(), …)` → `Battery().place(…)`, idem `Lamp`, `Ammeter` |
| 34 | `lampgloed` → `lamp_glow` (of `lamp_s.glow()`) |
| 84 | `DEELTJE_STRAAL` → `ELECTRON_R_WIRE` |
| 142 | `PIJL_KLEUR` → `C_CURRENT_ARROW`; `lus_pijltjes` blijft (snelheidsmodus in 3D, met maskers) |
| 147 | `pijlhoeken` → `arrow_corners` |
| 155 | `lamp_s[2].set_fill(LICHT, 1)` → `lamp_s.set_brightness(1)` |
| 158–164 | `label(…, size=LABEL, kleur=TEKST)` → `label(…)` |
| 207 | `MAATLAT_DIKTE` → `SW_SYMBOL` |

### `modellen.py`

| Regel | Wijziging |
|---|---|
| 28, 36, 78, 89, 129, 145 | `set_stroke(WIT, RAND_DIKTE)` → `set_stroke(C_EDGE, SW_THIN)` |
| 159 | koperionen `ORANJE` → `C_COPPER` |
| 166 | `radius=0.06` → `ELECTRON_R_FREE` (0,07) |
| 181 | `PROTON, NEUTRON = ROOD, GEDEMPT` → `C_PROTON`, `C_NEUTRON` |
| 205 | `GEDEMPT` → `C_MUTED` |
| 214 | `radius=0.08` → `ELECTRON_R_FREE` (0,07) |

## 4. Per scène

### Overal
- `import manimgx as m` en `from bouwstenen import *` blijven staan. Hernoem volgens de tabellen.
- Het einde `zeg(self, ""); self.wait(2)` / `wait(3)` wordt `self.end()`. Dat geldt voor 01:140–141, 02:184–185,
  03:177–178, 04:114–115, 05:253–254, 06:245–246, 07:271–272, 08:264–265, 09:245–246 en extra/transformator:190–191.
  **Video's die op 2 s eindigden, worden 1 s langer.**
- De helper `rij()`/`f()` met `FORMULE - 6` wordt `formula(comma(tex), FS_FORMULA_STEP)`. Hij staat op 01:27, 06:49 en
  06:138 (twee keer in hetzelfde bestand), 07:73, 09:75 en transformator:71. Zet hem één keer in `bouwstenen/__init__.py`,
  of gebruik hem direct.
- Groottes: `FORMULE + 4/6/8` → `FS_FORMULA_KEY`, `FORMULE - 2/8` → `FS_FORMULA_STEP`, `KLEIN + 2` → `FS_SMALL`,
  `KLEIN + 4` → `FS_SUBTITLE`, `KOP + 4` → `FS_HEADING`.
- Een losse `run_time=3` / `2,5` bij een camerawissel (boven ↔ schuin, kring optillen) wordt `T_CAMERA`.
- **Q wordt rood en E wordt geel** in elke formule (`formula()` doet dat zelf). Kijk alle rekenborden even na.

### 00_intro.py
| Regel | Wijziging |
|---|---|
| 31 | `("lading", ELEKTRON_KLEUR)` → `C_CHARGE` (rood); `("de waterkring", WATER_KLEUR)` blijft blauw |
| 117–123 | `schakelaar(…).scale(0.6)`, `lamp().scale(0.6)`, `l[2].set_fill` → `Switch(…)`, `Lamp(1)`, `.scale(SYMBOL_SMALL)` |
| 118 | `m.Line(…, color=DRAAD, stroke_width=DRAAD_DIKTE)` → `Wire(…)` |
| 179, 253 | `set_stroke(WIT, 3)` / `(WIT, 4)` → `set_stroke(C_EDGE, SW_FRAME)` / `SW_SYMBOL` |
| 185 | `run_time=0.12`: de klik van het knopje, bewust snel. Mag blijven, met een opmerking |
| 285 | `KOP + 4` → `FS_HEADING` |
| 445–447 | kWh-kast `set_stroke(TEKST, 3)` / `(TEKST, 2)` → `SW_FRAME` / `SW_THIN` |
| 495–496 | `run_time=NORMAAL`, `wait(0.5)` → `T_NORMAL`, `T_FAST` |
| — | Overweeg `play_intro(self)` of de logo-animatie in plaats van `assets/Intro.mov` (film.py:21) |

### 01_lading.py
| Regel | Wijziging |
|---|---|
| 16 | `PROTON`, `NEUTRON`, `ELEKTRON_KLEUR` → `C_PROTON`, `C_NEUTRON`, `C_ELECTRON` |
| 52, 100 | `KLEIN + 4` → `FS_SUBTITLE` (of `FS_SMALL`) |
| 61–62, 69 | `paneel(…, hoek=m.DR).shift(1.1 * m.UP)` → `panel(…, corner=m.DR)` zonder shift |
| 73–94 | `Q = …`-panelen worden nu rood (`C_CHARGE`) |
| 88 | `naam_min` in `ELEKTRON_KLEUR`: blijft geel (elektronen) |

### 02_waterkring.py
| Regel | Wijziging |
|---|---|
| 18 | `plat_label`: `KOP` → `FS_HEADING` |
| 59, 86, 139 | `kaart(…)` → `panel(…)` (nu met dekkend vlak) |
| 63 | `wait(d - SNEL + 2)` → `think(d - T_FAST)` |
| 105 | `run_time=0.3`: de pomp springt aan, bewust. Mag blijven, met een opmerking |
| 141 | `size=KLEIN + 2` → `size=FS_SMALL` |
| 173, 177 | `label(…, size=LABEL, kleur=TEKST)` → `label(…)` |
| 179 | `lamp_s[2].animate.set_fill(LICHT, 1)` → `lamp_s.animate.set_brightness(1)` (of de vulling via een ValueTracker) |

### 03_stroom.py
| Regel | Wijziging |
|---|---|
| 19–20 | `RAND_DIKTE` → `SW_THIN`; `tekst("A").scale(0.6)` → `text("A", FS_SMALL)` |
| 26 | `set_stroke(WIT, RAND_DIKTE)` → `set_stroke(C_EDGE, SW_THIN)` |
| 135 | `run_time=0.5` → `T_FAST` |
| 141 | `FORMULE - 8` → `FS_FORMULA_STEP` |
| 141–151 | `I = Q / t`: **Q wordt rood** |
| 165 | `run_time=3` → `T_CAMERA` |

### 04_spanning.py
| Regel | Wijziging |
|---|---|
| 76, 95 | `meter("V") … .scale(0.7)` → `Voltmeter() … .scale(SYMBOL_SMALL)` |
| 78–80, 97 | `draad`, `knoop`, `pool_a/b` → `Wire`, `Node`, `.a/.b` |
| 98 | `set_stroke(U_KLEUR, 6)` → `set_stroke(C_VOLTAGE, SW_HEAVY)` |

### 05_weerstand.py: de grootste wijziging
| Regel | Wijziging |
|---|---|
| 1–8 | docstring: zigzag → rechthoek |
| 102 | `meter("V") … .scale(0.7)` → `Voltmeter() … .scale(SYMBOL_SMALL)` |
| 149 | `FORMULE + 6` → `FS_FORMULA_KEY` |
| 196–209 | `weerstand_zigzag()` → `Resistor()`. Voice-over 208: *"In een schema tekenen we hem als een rechthoek. Deze weerstand heeft 3 ohm."* |
| 205 | `stijf` naar 0 laten gaan blijft nodig: de helling wordt bij 2 × H hoger dan het symbool lang is. De rechthoek **rekt dan mee tot een parallellogram**, waar de zigzag uitrekte. Render en beoordeel of dat goed oogt; anders `h` maximaal `SYMBOL_LENGTH` houden |
| 229–236 | `weerstand_zigzag(tanden=12)` als "twee keer zo grote weerstand" **heeft geen rechthoekversie**. Mijn voorstel: dezelfde `Resistor()` met een label "6 Ω" erbij, of een tweede `Resistor` in serie. **Open keuze** |
| 239 | `FORMULE + 8` → `FS_FORMULA_KEY`; `"3{,}0 = 0{,}5 \cdot 6"` → `comma("3,0 = 0,5 \cdot 6")`. **`{,}` geeft onder manimgx een spatie na de komma ("3, 0").** |

### 06_serie_parallel.py
| Regel | Wijziging |
|---|---|
| 42–47 | `boven()`, `schuin()` → `dict(CAM_TOP, zoom=1.0, frame_center=[0, 0, Z])`, `dict(CAM_TILTED, zoom=0.95, frame_center=[0, 0, 0.5])` |
| 49–50, 138–139 | dubbele `rij()` → één keer, `FS_FORMULA_STEP` |
| 76 | `run_time=3` → `T_CAMERA` |
| 93, 132, 150, 207, 215 | `duur=2.5` / `duur=3` → `duration=T_CAMERA` |
| 187 | `wait(d + 2)` → `think(d)` |
| 227 | `set_stroke(ACCENT, DRAAD_DIKTE + 1)` → `set_stroke(C_ACCENT, SW_SYMBOL)` |

### 07_vermogen.py
| Regel | Wijziging |
|---|---|
| 62–63 | accumeter: `set_stroke(WIT, 2)` → `SW_THIN`; vulling `GROEN` → `C_CHARGE` (rood: het balkje toont lading Q; **open keuze**, groen betekent nu vermogen). Ook `op_bord(…).shift(1.1 * m.UP)` (67) houden: die staat op het bord, niet in een paneel |
| 73 | `f(tex, size=FORMULE - 6)` → `FS_FORMULA_STEP` |
| 80–85 | `boven()`, `schuin()` → `CAM_TOP`, `CAM_TILTED` |
| 108 | `run_time=3` → `T_CAMERA` |
| 121, 159, 217 | `FORMULE + 4` → `FS_FORMULA_KEY` |
| 135 | `run_time=2.5` → `T_CAMERA` |
| 184 | `d - SNEL + 2` → `d - T_FAST + T_THINK` |
| 231 | `d - SNEL + 1.5` → `d - T_FAST + T_THINK` (wordt 0,5 s langer) |
| 243 | `run_time=5`: het leeglopen van de accu ("10 uur in 5 seconden"). Mag blijven, met een opmerking |
| 159–168, 217–257 | **E is nu geel en Q rood**: kijk de borden met `E = Q · U` na |

### 08_sensoren.py
| Regel | Wijziging |
|---|---|
| 19 | `LED_KLEUREN = [ROOD, …, WIT]` → `LED_COLORS` (de toegestane uitzondering) |
| 27–55 | `stroom_variabel` → `current_by_density(punten, I, I_max=1.5, visible=pijl_zicht)` uit `nabla.animations`. Let op: het oude systeem vervaagt de pijltjes bij de aansluitdraadjes via `Route.plek`; het nieuwe verbergt ze achter de symbolen. Bij de schakelaar (geen gevuld lichaam) lopen ze dan zichtbaar door |
| 68–71 | thermometer: `set_stroke(WIT, 2, a)` → `C_EDGE, SW_THIN`; `ROOD` → `C_HOT` of `C_ACCENT` (**open keuze**: de rode kolom is een thermometer, geen grootheid) |
| 88 | `schakelaar_stand(hoek)` → `Switch(hoek)` |
| 170 | `wait(d + 1.5)` → `think(d)` (wordt 0,5 s langer) |
| 172–198 | `duur=3` → `duration=T_CAMERA` (een langzame verandering, geen camera; of een eigen `T_SLOW`-variant) |
| 225–230 | LED-gloed: `ROOD` → `LED_COLORS[0]` |

### 09_thuis.py
| Regel | Wijziging |
|---|---|
| 76 | `rij()` → `FS_FORMULA_STEP` |
| 118, 199 | `set_stroke(TEKST, 3)` → `SW_FRAME` |
| 121–122 | `set_stroke(ACCENT, 3)` → `C_ACCENT, SW_FRAME` |
| 148–150 | stroomdiagram: `P_KLEUR` (beweging) → `C_USEFUL` (**nu geel**), `ACCENT` (warmte) → `C_LOSS` |
| 149–150, 173–174, 220–223 | `KLEIN + 2` → `FS_SMALL` |
| 170 | `.scale(0.6)` → `.scale(SYMBOL_SMALL)` |
| 171 | lampbalken: `LICHT` → `C_USEFUL` (beide geel), `ACCENT` → `C_LOSS` |
| 201 | `set_stroke(TEKST, 2)` → `SW_THIN` |
| 212 | `run_time=3` (kWh-teller loopt): mag blijven, met een opmerking |
| 219–223 | opwekking: `P_KLEUR` → `C_USEFUL` (**nu geel**), `ACCENT` → `C_LOSS` |

### extra/
- `stijl_demo.py`: vervalt. `examples/StyleSheet.py` in nabla-design neemt zijn plaats in.
- `kring_3d_naar_2d.py`: losse `run_time=2/2.5/3` → `T_SLOW` / `T_CAMERA`; `lamp_s[2].set_fill` → `set_brightness`.
- `transformator.py`: `spoel` `set_stroke(ORANJE, 4)` → `C_COPPER, SW_SYMBOL`; `Indicate(…, color=GEEL)` (102–103) →
  `point_at(…, C_COPPER)`; kern `BLAUW` → `C_FIELD`; `transformator_symbool` blijft in deze scène (komt in geen andere video voor).

## 5. Na het overzetten

1. Render elke video en vergelijk hem met de vorige render. Let vooral op de kleuren van Q en E, de rechthoek in 05 en
   de lengte van de video's (eindwacht en denkpauzes).
2. Zoek naar restanten: `grep -nE "#[0-9A-Fa-f]{6}|FORMULE|KLEIN|stroke_width=[0-9]|run_time=[0-9]" scenes/`.
   Wat overblijft, krijgt een opmerking waarom het bewust zo is.

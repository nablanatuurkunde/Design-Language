# assets

Merkbestanden. Binaire bestanden gaan via **Git LFS** (zie `.gitattributes`); doe één keer `git lfs install`.

Hier horen (nog aan te leveren):

| Bestand | Wat | Gebruikt door |
|---|---|---|
| `logo/nabla-logo.svg` | het logo als vector (strepen + woordmerk) | thumbnails (de intro gebruikt `nabla/brand/logo.png`) |
| `logo/nabla-logo.png` | het logo, transparante achtergrond, minstens 2000 px breed | thumbnails, social |
| `logo/nabla-logo-wit.png` | het logo in wit, voor op foto's | thumbnails |
| `logo/nabla-icon.png` | vierkant icoon (∇), 800 × 800 | YouTube-kanaalfoto |
| `video/intro.mov` | de bestaande logo-animatie met geluid (nu `Elektriciteit/assets/Intro.mov`) | film.py van elke video |
| `fonts/` | de fonts van het logo en de thumbnails (`.otf`/`.ttf`), als ze afwijken van New Computer Modern | thumbnails |
| `thumbnail/template.psd` (of `.afdesign`, `.fig`) | thumbnailsjabloon, 1280 × 720 | elke video |
| `banner/youtube-banner.png` | kanaalbanner, 2560 × 1440 | YouTube |

Kleuren in deze bestanden: precies de merkkleuren uit `nabla/style.py`
(`#FF0020`, `#FF601C`, `#FFB31F`, `#15CD36`, `#008EFE`; zwart `#000000`, wit `#FFFFFF`).

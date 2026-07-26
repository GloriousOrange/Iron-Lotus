# Level Backgrounds & Platforms (PixelLab, overnight batch)

Generated art for the six planned level environments. Everything is
programmer-directed placeholder-quality concept art meant for you to pick
favorites from — not yet wired into any scene.

## How to review
Open each level's **`_sheet.png`** — it shows the 3 background variants side by
side plus the themed jump-platforms on a checker (transparent) background.

## Levels
| Folder | Environment |
|---|---|
| `euro_exterior`   | European approach — colossal gothic castle looming in the distance |
| `castle_interior` | Inside the castle — great hall, columns, torchlight |
| `japan_town`      | Feudal Japan village street with a great pagoda temple behind |
| `temple_interior` | Inside the temple — golden statues, lacquered columns |
| `norse_beach`     | Scandinavian storm-battered rocky shore |
| `viking_ship`     | The longship seen from the side (establishing / parallax) |
| `viking_ship_deck`| ON the ship's deck, looking down toward the dragon prow (playable POV) |

## Files per level
- `backgrounds/<level>/bg_1.png … bg_6.png` — 400×224 parallax backdrops (6 seed variants).
- `backgrounds/<level>/_sheet.png` — review contact sheet (all variants + platforms).
- `platforms/<level>/*.png` — themed jump platforms, transparent background.
- `backgrounds/_overview.png` — one-look grid of a pick from every level.

## Notes / next steps
- Backgrounds are single-image backdrops. For true parallax we can later split
  or regenerate far/mid/near layers, or just scroll these slower than the
  foreground (the Abathor look in the design doc).
- Platforms are quick passes — some may need a cleaner side-on silhouette or
  tiling seams fixed. Tell me which per-level favorites you want and I'll
  refine + wire them into the levels.
- Tone target was dark/gritty to match Kageharu; say if any level should be
  moodier/brighter.
- Generator: `tools/bg_gen.py` (per-level prompts live there; easy to re-roll
  seeds or adjust a prompt and regenerate one level).

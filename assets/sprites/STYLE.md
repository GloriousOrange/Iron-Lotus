# Iron Lotus — Sprite Style Guide (PixelLab)

The locked style so the whole cast reads as one game. Generated with the PixelLab
Python SDK via `tools/pixellab_gen.py`. **Side-view side-scroller sprites only — never
top-down / directional generation.**

## Global rules (every generation)
- **View:** `view="side"`, `direction="east"` (facing right). The engine flips for
  facing-left; we never generate left/other directions.
- **Tone:** dark, gritty, muted palette; heavy black outline; readable at small size.
- **Negatives (always):** `top-down, 3/4 view, isometric, front-facing, back view,
  turnaround sheet, multiple characters, blurry, anti-aliased, white background`.
- **Background:** `no_background=True` (transparent) so sprites drop onto the level.
- **Base size:** 64×64 for the hero body (bump to 96 only if detail is lost).

## Kageharu (Ninja) — reference: `Ninja Concept1.jpg`
Style anchor is the concept art in this folder. Key traits to preserve:
- Dark **teal/forest-green** shinobi outfit (gi top + loose trousers).
- **Red** accents: forearm wraps, waist sash, shin/ankle wraps.
- **Black** face mask + matching headband; spiky dark hair.
- Muscular build; a **second sword sheathed on the back**.
- Signature weapon: **katana with a green energy/ki charge** along the blade.

Prompt seed: `"dark ninja warrior, teal green outfit, red arm and leg wraps, black
mask and headband, spiky black hair, katana"` + global rules above. The concept jpg is
passed as the bitforge **style reference** (and/or pixflux `init_image`) so output
matches this Kageharu rather than a generic ninja.

## Consistency method
1. Lock the hero from the concept (bitforge style-transfer / init_image).
2. Reuse the same `text_guidance_scale`, palette words, size, and outline/shading
   settings for every later character; carry a color reference where it helps.
3. One base frame → review → animate. Never blind-batch (credits).

#!/usr/bin/env python3
"""Level background + jump-platform asset generator for Iron Lotus (PixelLab).

Generates, per level:
  - assets/backgrounds/<level>/bg_<seed>.png   (wide parallax backdrops, variants)
  - assets/platforms/<level>/<name>_<seed>.png (themed jump platforms, transparent)
and a contact sheet assets/backgrounds/<level>/_sheet.png for review.

Dark, gritty tone to match the game. Run:  python tools/bg_gen.py <level|all>
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from PIL import Image, ImageDraw

_spec = importlib.util.spec_from_file_location("g", Path(__file__).with_name("pixellab_gen.py"))
g = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(g)

ASSETS = g.REPO / "assets"
BG_W, BG_H = 400, 224          # wide parallax backdrop
BG_SEEDS = [1, 2, 3]           # variants per background
PLAT_SIZE = 96
TONE = "dark gritty muted colors, moody atmosphere, pixel art, side-scroller game background"
BG_NEG = ("text, watermark, character, person, ui, frame, border, blurry, "
          "top-down, isometric, modern, bright cartoon")
PLAT_NEG = ("background, scenery, character, person, text, blurry, top-down, "
            "isometric, 3d perspective, angled view, drop shadow")

# level -> (background prompt, [ (platform_name, platform_prompt) ... ])
LEVELS = {
    "euro_exterior": (
        "sweeping dark medieval European landscape at dusk, a colossal gothic "
        "castle looming on a distant crag, rolling misty hills, dead trees, "
        "ravens, heavy overcast sky, multi-layer parallax depth",
        [("stone_block", "a weathered grey stone platform block, moss on edges"),
         ("broken_pillar", "a broken stone pillar segment platform"),
         ("wood_beam", "an old wooden beam platform, iron brackets"),
         ("ruined_arch", "a crumbling stone archway ledge platform")],
    ),
    "castle_interior": (
        "grand gothic castle great-hall interior, towering stone columns, "
        "tattered banners, iron chandeliers, flickering torchlight, long "
        "shadows, stained-glass windows far behind, gloomy",
        [("stone_ledge", "a carved stone ledge platform with railing"),
         ("wood_scaffold", "a wooden scaffold plank platform"),
         ("chandelier", "a hanging iron chandelier platform"),
         ("stone_stair", "a broken stone staircase block platform")],
    ),
    "japan_town": (
        "feudal Japanese village street at dusk, wooden machiya houses with "
        "tiled roofs, paper lanterns glowing, a great multi-tier pagoda temple "
        "rising in the background, cherry blossom trees, distant mountains",
        [("tiled_roof", "a curved tiled Japanese roof platform section"),
         ("wood_deck", "a wooden engawa deck platform"),
         ("stone_lantern", "a stone toro lantern platform pedestal"),
         ("torii_beam", "a red torii gate crossbeam platform")],
    ),
    "temple_interior": (
        "interior of a vast Japanese temple hall, towering golden Buddha "
        "statues, red lacquered wooden columns, dim candlelight, incense haze, "
        "ornate coffered ceiling, sacred solemn atmosphere",
        [("wood_beam", "a lacquered red wooden beam platform"),
         ("statue_base", "a stone statue pedestal platform"),
         ("altar_step", "a golden altar step platform"),
         ("hanging_lantern", "a hanging paper temple lantern platform")],
    ),
    "norse_beach": (
        "cold windswept Scandinavian rocky shore, grey storm waves crashing on "
        "black rocks, jagged sea cliffs, driftwood and kelp, low heavy clouds, "
        "distant longship silhouettes, bleak northern light",
        [("sea_rock", "a wet black sea rock platform outcropping"),
         ("driftwood", "a bleached driftwood log platform"),
         ("ice_slab", "a cracked ice slab platform"),
         ("wreck_hull", "a broken shipwreck hull plank platform")],
    ),
    "viking_ship": (
        "aboard a massive viking longship in a storm at sea, planked deck, "
        "carved dragon-head prow, tall mast and torn sail, rows of round "
        "shields on the gunwale, grey towering waves, dark tempest sky",
        [("deck_plank", "a wooden ship deck plank platform"),
         ("crates", "a stack of wooden cargo crates platform"),
         ("barrel", "a wooden barrel platform"),
         ("mast_beam", "a ship mast crossbeam platform with rope")],
    ),
}


def gen_bg(level: str, prompt: str) -> list[Path]:
    c = g.client()
    out = ASSETS / "backgrounds" / level
    out.mkdir(parents=True, exist_ok=True)
    paths = []
    for seed in BG_SEEDS:
        d = g.post(c, "generate-image-pixflux", {
            "description": f"{prompt}, {TONE}",
            "negative_description": BG_NEG,
            "image_size": {"width": BG_W, "height": BG_H},
            "text_guidance_scale": 8.0,
            "seed": seed,
        })
        p = out / f"bg_{seed}.png"
        g.save_b64(d["image"], p)
        paths.append(p)
        print(f"  bg {level} seed {seed} -> {p.name}")
    return paths


def gen_platforms(level: str, plats: list) -> None:
    c = g.client()
    out = ASSETS / "platforms" / level
    out.mkdir(parents=True, exist_ok=True)
    for name, prompt in plats:
        d = g.post(c, "generate-image-pixflux", {
            "description": f"{prompt}, flat side-on horizontal platform seen from "
                           f"the side, front elevation, single object centered, "
                           f"dark gritty muted pixel art game asset",
            "negative_description": PLAT_NEG,
            "image_size": {"width": PLAT_SIZE, "height": PLAT_SIZE // 2},
            "text_guidance_scale": 8.0,
            "no_background": True,
            "seed": 1,
        })
        p = out / f"{name}.png"
        g.save_b64(d["image"], p)
        print(f"  plat {level} -> {p.name}")


def sheet(level: str) -> None:
    bgs = sorted((ASSETS / "backgrounds" / level).glob("bg_*.png"))
    plats = sorted((ASSETS / "platforms" / level).glob("*.png"))
    pad = 10
    rowh = BG_H + pad
    W = max(BG_W * len(bgs) + pad * (len(bgs) + 1), PLAT_SIZE * len(plats) + pad * (len(plats) + 1), 600)
    H = rowh + PLAT_SIZE + pad * 3 + 20
    img = Image.new("RGBA", (W, H), (24, 24, 28, 255))
    d = ImageDraw.Draw(img)
    d.text((pad, 4), f"{level}  —  backgrounds (400x224 variants) + platforms", fill=(230, 230, 235, 255))
    x = pad
    for b in bgs:
        img.paste(Image.open(b).convert("RGBA"), (x, 20))
        x += BG_W + pad
    x, y = pad, 20 + rowh
    for pl in plats:
        im = Image.open(pl).convert("RGBA")
        # checker behind transparent platforms
        for yy in range(0, PLAT_SIZE, 8):
            for xx in range(0, im.width, 8):
                d.rectangle([x + xx, y + yy, x + xx + 8, y + yy + 8],
                            fill=(60, 60, 66, 255) if (xx // 8 + yy // 8) % 2 else (44, 44, 50, 255))
        img.paste(im, (x, y), im)
        d.text((x, y + PLAT_SIZE + 2), pl.stem, fill=(200, 200, 205, 255))
        x += max(im.width, 80) + pad
    out = ASSETS / "backgrounds" / level / "_sheet.png"
    img.save(out)
    print(f"  sheet -> {out}")


def do_level(level: str) -> None:
    prompt, plats = LEVELS[level]
    print(f"== {level} ==")
    gen_bg(level, prompt)
    gen_platforms(level, plats)
    sheet(level)


def main() -> None:
    arg = sys.argv[1] if len(sys.argv) > 1 else "all"
    levels = list(LEVELS) if arg == "all" else [arg]
    for lv in levels:
        do_level(lv)
    print("DONE", levels)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Iron Lotus art generator (PixelLab).

Side-view side-scroller sprites ONLY. This tool never calls rotate() or any
directional / top-down generator -- that is the credit trap we are avoiding.
Every call forces view="side", direction="east" (facing right); the Godot
engine flips the sprite for facing-left.

Secret: reads PIXELLAB_SECRET from tools/.pixellab.secrets (gitignored).

Usage:
    python tools/pixellab_gen.py balance
    python tools/pixellab_gen.py base   [--size 64] [--seed 0]
    python tools/pixellab_gen.py anim ACTION [--frames 4] [--size 64] [--seed 0]

`base` uses the Ninja Concept1 art as a bitforge style reference so output
matches our Kageharu. `anim` animates the approved base (assets/sprites/ninja/
base.png) for one action (idle/run/jump/attack/dodge/hit).
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from PIL import Image
import pixellab

REPO = Path(__file__).resolve().parent.parent
SECRETS = REPO / "tools" / ".pixellab.secrets"
NINJA_DIR = REPO / "assets" / "sprites" / "ninja"
CONCEPT = REPO / "assets" / "sprites" / "Ninja Concept1.jpg"
BASE = NINJA_DIR / "base.png"

# --- Locked style (see assets/sprites/STYLE.md) -------------------------------
KAGEHARU = (
    "dark ninja warrior, teal green outfit, red arm and leg wraps, "
    "black mask and headband, spiky black hair, katana, muscular"
)
NEGATIVE = (
    "top-down, 3/4 view, isometric, front-facing, back view, turnaround sheet, "
    "multiple characters, blurry, anti-aliased, white background"
)


def client() -> pixellab.Client:
    if not SECRETS.exists():
        sys.exit(
            f"Missing {SECRETS}. Create it with a single line:\n"
            f"    PIXELLAB_SECRET=<your token>\n"
            f"(it is gitignored -- never commit it)."
        )
    return pixellab.Client.from_env_file(str(SECRETS))


def show_balance(c: pixellab.Client, label: str) -> None:
    try:
        bal = c.get_balance()
        usd = getattr(bal, "usd", bal)
        print(f"[balance {label}] {usd}")
    except Exception as e:  # balance is informational, never fatal
        print(f"[balance {label}] unavailable: {e}")


def cmd_balance(args) -> None:
    show_balance(client(), "now")


def cmd_base(args) -> None:
    c = client()
    show_balance(c, "before")
    style = Image.open(CONCEPT).convert("RGBA")
    print(f"Generating base sprite ({args.size}px, seed {args.seed}) from concept ref...")
    resp = c.generate_image_bitforge(
        description=KAGEHARU + ", standing idle, full body",
        negative_description=NEGATIVE,
        image_size={"width": args.size, "height": args.size},
        view="side",
        direction="east",
        no_background=True,
        style_image=style,
        style_strength=50.0,
        seed=args.seed,
    )
    NINJA_DIR.mkdir(parents=True, exist_ok=True)
    out = NINJA_DIR / "base.png"
    resp.image.pil_image().save(out)
    show_balance(c, "after")
    print(f"Saved {out}  -- review before animating.")


def cmd_anim(args) -> None:
    if not BASE.exists():
        sys.exit(f"No approved base at {BASE}. Run `base` and approve it first.")
    c = client()
    show_balance(c, "before")
    ref = Image.open(BASE).convert("RGBA")
    print(f"Animating '{args.action}' ({args.frames} frames)...")
    resp = c.animate_with_text(
        description=KAGEHARU,
        action=args.action,
        image_size={"width": args.size, "height": args.size},
        reference_image=ref,
        view="side",
        direction="east",
        negative_description=NEGATIVE,
        n_frames=args.frames,
        seed=args.seed,
    )
    out_dir = NINJA_DIR / args.action
    out_dir.mkdir(parents=True, exist_ok=True)
    images = getattr(resp, "images", None) or [resp.image]
    for i, im in enumerate(images):
        im.pil_image().save(out_dir / f"{args.action}_{i}.png")
    show_balance(c, "after")
    print(f"Saved {len(images)} frames to {out_dir}")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("balance")

    pb = sub.add_parser("base")
    pb.add_argument("--size", type=int, default=64)
    pb.add_argument("--seed", type=int, default=0)

    pa = sub.add_parser("anim")
    pa.add_argument("action", help="idle|run|jump|attack|dodge|hit")
    pa.add_argument("--frames", type=int, default=4)
    pa.add_argument("--size", type=int, default=64)
    pa.add_argument("--seed", type=int, default=0)

    args = p.parse_args()
    {"balance": cmd_balance, "base": cmd_base, "anim": cmd_anim}[args.cmd](args)


if __name__ == "__main__":
    main()

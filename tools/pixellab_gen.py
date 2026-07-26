#!/usr/bin/env python3
"""Iron Lotus art generator (PixelLab).

Side-view side-scroller sprites ONLY. This tool never calls rotate() or any
directional / top-down generator -- that is the credit trap we are avoiding.
Every call forces view="side", direction="east" (facing right); the Godot
engine flips the sprite for facing-left.

We POST to the PixelLab REST API directly (not the SDK response models): the
installed SDK rejects the API's newer `usage` metadata, but the requests work.
We use the SDK only for auth headers + balance.

Secret: reads PIXELLAB_SECRET from tools/.pixellab.secrets (gitignored).

Usage:
    python tools/pixellab_gen.py balance
    python tools/pixellab_gen.py base   [--size 128] [--seed 0] [--style-strength 50]
    python tools/pixellab_gen.py anim ACTION [--frames 4] [--size 128] [--seed 0]
"""
from __future__ import annotations

import argparse
import base64
import io
import sys
from pathlib import Path

import requests
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
    "full black head mask covering face and ears, spiky black hair on top, "
    "cloth-wrapped hands, wrapped tabi boots covering the feet, katana, "
    "lean athletic build, toned but not bulky"
)
NEGATIVE = (
    "top-down, 3/4 view, isometric, front-facing, back view, turnaround sheet, "
    "multiple characters, blurry, anti-aliased, white background, "
    "trailing ribbons, loose hair behind head, sword on back, back scabbard, "
    "clutter behind head, huge bulky muscles, bodybuilder, "
    "bare hands, bare feet, exposed ears, uncovered face"
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
        print(f"[balance {label}] ${c.get_balance().usd:.4f}")
    except Exception as e:  # informational, never fatal
        print(f"[balance {label}] unavailable: {e}")


def post(c: pixellab.Client, path: str, payload: dict) -> dict:
    """Raw POST that tolerates the newer `usage` schema the SDK rejects."""
    r = requests.post(f"{c.base_url}/{path}", headers=c.headers(), json=payload)
    if not r.ok:
        detail = ""
        try:
            detail = r.json().get("detail", "")
        except Exception:
            detail = r.text[:400]
        sys.exit(f"API error {r.status_code} on /{path}: {detail}")
    return r.json()


def b64_of(img: Image.Image) -> dict:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return {"type": "base64", "base64": base64.b64encode(buf.getvalue()).decode(), "format": "png"}


def save_b64(d: dict, out: Path) -> None:
    out.write_bytes(base64.b64decode(d["base64"]))


def square_resize(img: Image.Image, size: int) -> Image.Image:
    """Letterbox to a square (preserve aspect, no distortion) then resize --
    bitforge requires the style_image to match the output size."""
    img = img.convert("RGBA")
    side = max(img.size)
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    canvas.paste(img, ((side - img.width) // 2, (side - img.height) // 2))
    return canvas.resize((size, size), Image.LANCZOS)


def cmd_balance(args) -> None:
    show_balance(client(), "now")


def cmd_base(args) -> None:
    c = client()
    show_balance(c, "before")
    style = square_resize(Image.open(CONCEPT), args.size)
    print(f"Generating base sprite ({args.size}px, seed {args.seed}) from concept ref...")
    data = post(c, "generate-image-bitforge", {
        "description": KAGEHARU + ", standing idle, full body",
        "negative_description": NEGATIVE,
        "image_size": {"width": args.size, "height": args.size},
        "view": "side",
        "direction": "east",
        "no_background": True,
        "style_image": b64_of(style),
        "style_strength": args.style_strength,
        "seed": args.seed,
    })
    NINJA_DIR.mkdir(parents=True, exist_ok=True)
    save_b64(data["image"], BASE)
    show_balance(c, "after")
    print(f"Saved {BASE}  -- review before animating.")


def cmd_anim(args) -> None:
    if not BASE.exists():
        sys.exit(f"No approved base at {BASE}. Run `base` and approve it first.")
    c = client()
    show_balance(c, "before")
    # animate-with-text caps output at 64px; the reference must match that size.
    ref = square_resize(Image.open(BASE), args.size)
    print(f"Animating '{args.action}' ({args.frames} frames, {args.size}px)...")
    data = post(c, "animate-with-text", {
        "image_size": {"width": args.size, "height": args.size},
        "description": KAGEHARU,
        "action": args.action,
        "negative_description": NEGATIVE,
        "n_frames": args.frames,
        "view": "side",
        "direction": "east",
        "reference_image": b64_of(ref),
        "seed": args.seed,
    })
    out_dir = NINJA_DIR / args.action
    out_dir.mkdir(parents=True, exist_ok=True)
    frames = data["images"]
    for i, im in enumerate(frames):
        save_b64(im, out_dir / f"{args.action}_{i}.png")
    show_balance(c, "after")
    print(f"Saved {len(frames)} frames to {out_dir}")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("balance")

    pb = sub.add_parser("base")
    pb.add_argument("--size", type=int, default=128)
    pb.add_argument("--seed", type=int, default=0)
    pb.add_argument("--style-strength", type=float, default=50.0)

    pa = sub.add_parser("anim")
    pa.add_argument("action", help="idle|run|jump|attack|dodge|hit")
    pa.add_argument("--frames", type=int, default=4)
    pa.add_argument("--size", type=int, default=128)
    pa.add_argument("--seed", type=int, default=0)

    args = p.parse_args()
    {"balance": cmd_balance, "base": cmd_base, "anim": cmd_anim}[args.cmd](args)


if __name__ == "__main__":
    main()

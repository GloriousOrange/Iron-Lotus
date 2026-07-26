#!/usr/bin/env python3
"""Emit a Godot 4 SpriteFrames .tres for the Ninja from the generated frames.

Scans assets/sprites/ninja/<action>/<action>_<n>.png and writes
scenes/player/NinjaFrames.tres with one animation per action.
"""
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
NINJA = REPO / "assets" / "sprites" / "ninja"
OUT = REPO / "scenes" / "player" / "NinjaFrames.tres"

# action -> (fps, loop)
ACTIONS = {
    "idle":   (6.0, True),
    "run":    (12.0, True),
    "jump":   (10.0, False),
    "attack": (14.0, False),
    "dodge":  (14.0, False),
    "hit":    (10.0, False),
}


def main() -> None:
    ext, frame_ids = [], {}
    idx = 1
    for action in ACTIONS:
        frames = sorted((NINJA / action).glob(f"{action}_*.png"),
                        key=lambda p: int(p.stem.split("_")[-1]))
        frame_ids[action] = []
        for f in frames:
            rid = f"{idx}_{action}{f.stem.split('_')[-1]}"
            res_path = "res://" + str(f.relative_to(REPO)).replace("\\", "/")
            ext.append(f'[ext_resource type="Texture2D" path="{res_path}" id="{rid}"]')
            frame_ids[action].append(rid)
            idx += 1

    anims = []
    for action, (fps, loop) in ACTIONS.items():
        fr = ",".join(
            f'{{"duration":1.0,"texture":ExtResource("{rid}")}}' for rid in frame_ids[action]
        )
        anims.append(
            f'{{\n"frames": [{fr}],\n"loop": {str(loop).lower()},\n'
            f'"name": &"{action}",\n"speed": {fps}\n}}'
        )

    tres = (
        f'[gd_resource type="SpriteFrames" load_steps={len(ext) + 1} format=3]\n\n'
        + "\n".join(ext)
        + "\n\n[resource]\nanimations = ["
        + ", ".join(anims)
        + "]\n"
    )
    OUT.write_text(tres)
    print(f"Wrote {OUT} ({len(ext)} frames, {len(ACTIONS)} animations)")


if __name__ == "__main__":
    main()

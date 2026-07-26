#!/usr/bin/env python3
"""Skeleton-keyframe authoring for Iron Lotus sprites (PixelLab).

Text-to-animation drifts the character; skeleton animation poses the EXACT base
sprite along stick-figure keyframes, so identity holds. We estimate the base's
rest pose once, then synthesize per-action keyframes (2-bone IK on the legs so
knees bend naturally) and feed them to animate-with-skeleton.

Side view, facing +x (east). Coordinates are normalized 0..1, y down.

    python tools/skeleton_anim.py estimate          # refresh base_skel.json
    python tools/skeleton_anim.py run   [--frames 6]
    python tools/skeleton_anim.py idle  [--frames 4]
    python tools/skeleton_anim.py jump
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import os
from pathlib import Path

from PIL import Image

# Load the sibling generator module for its client/post/b64 helpers.
_spec = importlib.util.spec_from_file_location("g", Path(__file__).with_name("pixellab_gen.py"))
g = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(g)

SKEL_JSON = Path("/tmp") / "base_skel.json"  # overwritten by `estimate`; also cached below
CACHE = g.NINJA_DIR / "base_skel.json"
LIMBS = ("LEFT", "RIGHT")


def estimate() -> list[dict]:
    c = g.client()
    ref = Image.open(g.NINJA_DIR / "base64.png").convert("RGBA")
    d = g.post(c, "estimate-skeleton", {"image": g.b64_of(ref)})
    CACHE.write_text(json.dumps(d["keypoints"], indent=2))
    print(f"Saved rest skeleton -> {CACHE}")
    return d["keypoints"]


def rest_pose() -> dict[str, dict]:
    if not CACHE.exists():
        estimate()
    kps = json.loads(CACHE.read_text())
    return {k["label"]: dict(k) for k in kps}


# --- kinematics ---------------------------------------------------------------
def _dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def ik2(hip, target, l1, l2, bend_sign):
    """2-bone IK: return the joint (knee/elbow) placing the limb from `hip` to
    `target` with bone lengths l1,l2. bend_sign picks which way the joint bows."""
    hx, hy = hip
    tx, ty = target
    d = max(1e-4, _dist(hip, target))
    d = min(d, l1 + l2 - 1e-3)  # keep reachable
    a = (l1 * l1 - l2 * l2 + d * d) / (2 * d)
    h = math.sqrt(max(0.0, l1 * l1 - a * a))
    ux, uy = (tx - hx) / d, (ty - hy) / d           # unit hip->target
    mx, my = hx + a * ux, hy + a * uy               # foot of the perpendicular
    px, py = -uy, ux                                 # perpendicular
    return (mx + bend_sign * h * px, my + bend_sign * h * py)


def _seglens(rest):
    L = {}
    for s in LIMBS:
        L[(s, "thigh")] = _dist((rest[f"{s} HIP"]["x"], rest[f"{s} HIP"]["y"]),
                                (rest[f"{s} KNEE"]["x"], rest[f"{s} KNEE"]["y"]))
        L[(s, "shank")] = _dist((rest[f"{s} KNEE"]["x"], rest[f"{s} KNEE"]["y"]),
                                (rest[f"{s} LEG"]["x"], rest[f"{s} LEG"]["y"]))
        L[(s, "uarm")] = _dist((rest[f"{s} SHOULDER"]["x"], rest[f"{s} SHOULDER"]["y"]),
                               (rest[f"{s} ELBOW"]["x"], rest[f"{s} ELBOW"]["y"]))
        L[(s, "farm")] = _dist((rest[f"{s} ELBOW"]["x"], rest[f"{s} ELBOW"]["y"]),
                               (rest[f"{s} ARM"]["x"], rest[f"{s} ARM"]["y"]))
    return L


def frame_from(rest, overrides, dy=0.0):
    """Build a SkeletonFrame: start from rest, apply {label:(x,y)} overrides,
    add a global vertical bob dy. Preserves z_index and untouched joints."""
    kps = []
    for label, k in rest.items():
        x, y = k["x"], k["y"]
        if label in overrides:
            x, y = overrides[label]
        kps.append({"x": round(x, 4), "y": round(y + dy, 4),
                    "label": label, "z_index": k.get("z_index", 0.0)})
    return {"keypoints": kps}


# --- shared stance ------------------------------------------------------------
# Aggressive forward lean: the whole upper body tilts toward +x (facing dir),
# with the leading (near/LEFT) shoulder pushed forward and the head dipped.
_UPPER = ("NOSE", "LEFT EYE", "RIGHT EYE", "LEFT EAR", "RIGHT EAR", "NECK",
          "LEFT SHOULDER", "RIGHT SHOULDER", "LEFT ELBOW", "RIGHT ELBOW",
          "LEFT ARM", "RIGHT ARM")


def apply_lean(rest, ov, lean_x=0.06, head_dip=0.015):
    for lbl in _UPPER:
        bx, by = ov.get(lbl, (rest[lbl]["x"], rest[lbl]["y"]))
        extra = 0.035 if lbl == "LEFT SHOULDER" else (0.02 if lbl == "LEFT ELBOW" else 0.0)
        dip = head_dip if lbl in ("NOSE", "LEFT EYE", "RIGHT EYE", "LEFT EAR", "RIGHT EAR") else 0.0
        ov[lbl] = (bx + lean_x + extra, by + dip)


def hand_on_hilt(rest, ov, shoulder_dip=0.03):
    # Left hand rests on the sheathed katana's handle at the waist, the left
    # elbow leading forward (+x), and the left shoulder dipped down. The right
    # (far) arm stays at rest. This is the imposing "ready to draw" carry.
    ov["LEFT SHOULDER"] = (0.55, 0.25 + shoulder_dip)
    ov["LEFT ELBOW"] = (0.67, 0.42)      # elbow juts forward
    ov["LEFT ARM"] = (0.60, 0.49)        # hand on the hilt at the waist


# --- actions ------------------------------------------------------------------
def run_frames(rest, n=6, stride=0.10, lift=0.05):
    # Legs only, 6-frame cycle for a smooth natural gait (arms stay at rest so
    # the hand keeps resting on the sheathed weapon). Small stride + low lift.
    L = _seglens(rest)
    frames = []
    for i in range(n):
        t = i / n
        ov = {}
        dy = -0.018 * abs(math.sin(2 * math.pi * t))   # gentle body bob
        for s, phase0 in (("LEFT", 0.0), ("RIGHT", 0.5)):
            phi = t + phase0
            hip = (rest[f"{s} HIP"]["x"], rest[f"{s} HIP"]["y"])
            # -cos so the PLANTED foot travels backward (pushes body forward);
            # +cos moon-walked. Foot lifts during the swing half (sin>0).
            foot_x = hip[0] - stride * math.cos(2 * math.pi * phi)
            foot_y = rest[f"{s} LEG"]["y"] - lift * max(0.0, math.sin(2 * math.pi * phi))
            ov[f"{s} KNEE"] = ik2(hip, (foot_x, foot_y), L[(s, "thigh")], L[(s, "shank")], bend_sign=-1)
            ov[f"{s} LEG"] = (foot_x, foot_y)
        # Left hand on the hilt; left shoulder dips rhythmically as he walks.
        hand_on_hilt(rest, ov, shoulder_dip=0.03 + 0.025 * (0.5 + 0.5 * math.sin(2 * math.pi * t)))
        frames.append(frame_from(rest, ov, dy=dy))
    return frames


def idle_frames(rest, n=3):
    # Standing: upright and imposing, left hand on the sheathed hilt, ready to
    # draw. No forward lean -- that's for walking.
    frames = []
    for i in range(n):
        dy = -0.02 * math.sin(2 * math.pi * i / n)   # gentle breathing bob
        ov = {}
        hand_on_hilt(rest, ov, shoulder_dip=0.02)
        frames.append(frame_from(rest, ov, dy=dy))
    return frames


def jump_frames(rest, n=3):
    L = _seglens(rest)
    # crouch -> launch/extend -> rising tuck  (a jump is not a loop)
    poses = [0.06, -0.06, -0.03]      # body dy per frame
    tuck = [0.01, 0.02, 0.10]         # how much the feet pull up
    frames = []
    for i in range(n):
        ov = {}
        for s in LIMBS:
            hip = (rest[f"{s} HIP"]["x"], rest[f"{s} HIP"]["y"])
            foot_y = rest[f"{s} LEG"]["y"] - tuck[i]
            foot_x = hip[0] + 0.02
            knee = ik2(hip, (foot_x, foot_y), L[(s, "thigh")], L[(s, "shank")], bend_sign=-1)
            ov[f"{s} KNEE"] = knee
            ov[f"{s} LEG"] = (foot_x, foot_y)
        frames.append(frame_from(rest, ov, dy=poses[i]))
    return frames


def _set_arm(rest, ov, side, ang, bend=0.35):
    """Pose one arm: shoulder->elbow at angle `ang` (radians, 0=+x, +y down),
    forearm bent by `bend`."""
    L = _seglens(rest)
    sh = (rest[f"{side} SHOULDER"]["x"], rest[f"{side} SHOULDER"]["y"])
    elbow = (sh[0] + L[(side, "uarm")] * math.cos(ang), sh[1] + L[(side, "uarm")] * math.sin(ang))
    wa = ang + bend
    wrist = (elbow[0] + L[(side, "farm")] * math.cos(wa), elbow[1] + L[(side, "farm")] * math.sin(wa))
    ov[f"{side} ELBOW"] = elbow
    ov[f"{side} ARM"] = wrist


def attack_frames(rest, n=3):
    # IAIJUTSU draw-cut with the LEFT (near) hand, animated from the drawn-katana
    # base. The sword hand stays FORWARD of the body the whole time (never
    # crosses back through him -- that read as self-harm). It sweeps from a
    # retracted-forward guard out to full forward extension toward the enemy.
    ext = (rest["LEFT ARM"]["x"], rest["LEFT ARM"]["y"])       # extended (base)
    ext_el = (rest["LEFT ELBOW"]["x"], rest["LEFT ELBOW"]["y"])
    ext_sh = (rest["LEFT SHOULDER"]["x"], rest["LEFT SHOULDER"]["y"])
    # per-frame LEFT (shoulder, elbow, wrist) + body-forward dx. All wrist x >
    # hip x (~0.53) so the blade always points forward/right, in front of him.
    poses = [
        ((0.58, 0.34), (0.60, 0.40), (0.63, 0.38), -0.01),    # drawn, high guard (forward)
        ((0.59, 0.34), (0.64, 0.42), (0.72, 0.44),  0.02),    # cutting down-forward
        (ext_sh,        ext_el,       ext,          0.04),    # full forward extension
    ]
    frames = []
    for sh, el, wr, dx in poses:
        ov = {"LEFT SHOULDER": sh, "LEFT ELBOW": el, "LEFT ARM": wr}
        for lbl in ("NOSE", "LEFT EYE", "RIGHT EYE", "LEFT EAR", "RIGHT EAR", "NECK"):
            ov[lbl] = (rest[lbl]["x"] + dx, rest[lbl]["y"])
        frames.append(frame_from(rest, ov))
    return frames


def dodge_frames(rest, n=3):
    # Dodge-roll: crouch -> deep forward tuck -> rise. Body drops and leans,
    # legs pull up under the hips, head ducks.
    L = _seglens(rest)
    body_dy = [0.05, 0.14, 0.05]
    foot_up = [0.06, 0.16, 0.06]
    lean = [0.02, 0.06, 0.03]
    frames = []
    for i in range(n):
        ov = {}
        for s in LIMBS:
            hip = (rest[f"{s} HIP"]["x"], rest[f"{s} HIP"]["y"])
            foot = (hip[0] + 0.04, rest[f"{s} LEG"]["y"] - foot_up[i])
            ov[f"{s} KNEE"] = ik2(hip, foot, L[(s, "thigh")], L[(s, "shank")], bend_sign=-1)
            ov[f"{s} LEG"] = foot
            # arms left at rest -- hand stays on the sheathed weapon
        for lbl in ("NOSE", "LEFT EYE", "RIGHT EYE", "LEFT EAR", "RIGHT EAR", "NECK"):
            ov[lbl] = (rest[lbl]["x"] + lean[i], rest[lbl]["y"] + 0.04)
        frames.append(frame_from(rest, ov, dy=body_dy[i]))
    return frames


def hit_frames(rest, n=3):
    # Flinch: recoil the upper body backward (-x) and up, then settle.
    recoil = [0.0, -0.06, -0.02]
    up = [0.0, -0.02, 0.0]
    frames = []
    for i in range(n):
        ov = {}
        for lbl in ("NOSE", "LEFT EYE", "RIGHT EYE", "LEFT EAR", "RIGHT EAR",
                    "NECK", "LEFT SHOULDER", "RIGHT SHOULDER"):
            ov[lbl] = (rest[lbl]["x"] + recoil[i], rest[lbl]["y"] + up[i])
        _set_arm(rest, ov, "LEFT", -0.6, bend=0.6)   # arms fly up defensively
        _set_arm(rest, ov, "RIGHT", -0.9, bend=0.6)
        frames.append(frame_from(rest, ov))
    return frames


ACTIONS = {
    "run": run_frames, "idle": idle_frames, "jump": jump_frames,
    "attack": attack_frames, "dodge": dodge_frames, "hit": hit_frames,
}


# Actions that animate from their own base sprite (skeleton + appearance)
# instead of the default sheathed base -- e.g. attack draws a katana.
ACTION_BASE = {"attack": "attack_base.png"}


def skel_for(base_file: str) -> dict[str, dict]:
    """Estimate (and cache) the rest skeleton for a given base sprite."""
    stem = Path(base_file).stem
    cache = CACHE if stem == "base64" else g.NINJA_DIR / f"{stem}_skel.json"
    if not cache.exists():
        c = g.client()
        ref = Image.open(g.NINJA_DIR / base_file).convert("RGBA")
        d = g.post(c, "estimate-skeleton", {"image": g.b64_of(ref)})
        cache.write_text(json.dumps(d["keypoints"], indent=2))
    kps = json.loads(cache.read_text())
    return {k["label"]: dict(k) for k in kps}


def generate(action: str, n: int | None):
    base_file = ACTION_BASE.get(action, "base64.png")
    rest = skel_for(base_file)
    fn = ACTIONS[action]
    frames = fn(rest, n) if n else fn(rest)
    if len(frames) % 3 != 0:
        raise SystemExit(f"{action}: {len(frames)} frames; must be a multiple of 3 "
                         f"(the model is a 3-frame window).")
    c = g.client()
    g.show_balance(c, "before")
    ref = Image.open(g.NINJA_DIR / base_file).convert("RGBA")
    out = g.NINJA_DIR / action
    out.mkdir(parents=True, exist_ok=True)
    for f in out.glob(f"{action}_*.png"):
        f.unlink()
    # Actions with big pose deltas (a sword draw-cut) need stronger pose
    # guidance so the skeleton wins over the reference image's fixed stance.
    pose_gs = 7.0 if action == "attack" else 3.0
    print(f"Skeleton-animating '{action}' ({len(frames)} frames "
          f"= {len(frames)//3} window(s) of 3, pose_gs={pose_gs})...")
    idx = 0
    for w0 in range(0, len(frames), 3):        # chain 3-frame windows
        window = frames[w0:w0 + 3]
        d = g.post(c, "animate-with-skeleton", {
            "image_size": {"width": 64, "height": 64},
            # REST wants each frame as a bare list of keypoints (not {"keypoints":[...]}).
            "skeleton_keypoints": [f["keypoints"] for f in window],
            "view": "side",
            "direction": "east",
            "reference_image": g.b64_of(ref),
            "reference_guidance_scale": 1.1,
            "pose_guidance_scale": pose_gs,
            "seed": 0,
        })
        for im in d["images"]:
            p = out / f"{action}_{idx}.png"
            g.save_b64(im, p)
            strip_bg(p)
            idx += 1
    g.show_balance(c, "after")
    print(f"Saved {idx} frames (bg removed) -> {out}")


def strip_bg(path: Path) -> None:
    """animate-with-skeleton returns sprites on a white bg. Flood-fill the
    connected white region inward from the 4 corners -> transparent, so
    interior near-white pixels (a sword glint) are preserved."""
    im = Image.open(path).convert("RGBA")
    w, h = im.size
    px = im.load()
    def is_bg(p):
        return p[0] > 238 and p[1] > 238 and p[2] > 238
    seen = [[False] * w for _ in range(h)]
    stack = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    while stack:
        x, y = stack.pop()
        if x < 0 or y < 0 or x >= w or y >= h or seen[y][x]:
            continue
        seen[y][x] = True
        if not is_bg(px[x, y]):
            continue
        px[x, y] = (0, 0, 0, 0)
        stack += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    im.save(path)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("estimate")
    for a in ACTIONS:
        sp = sub.add_parser(a)
        sp.add_argument("--frames", type=int, default=None)
    args = p.parse_args()
    if args.cmd == "estimate":
        estimate()
    else:
        generate(args.cmd, getattr(args, "frames", None))


if __name__ == "__main__":
    main()

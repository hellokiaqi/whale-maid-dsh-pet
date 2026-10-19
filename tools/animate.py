"""Generate the whale-maid idle loop and hop from one transparent illustration.

The source (source/base.png) is a single 1022 x 1550 cutout. The animation is a
mesh warp: breathing (scale about the feet), a slow tail/hair sway, a small
ahoge wiggle and a head tilt. The hop lifts the body with squash-and-stretch.
All frames share one canvas so the pet box never jumps.

Usage:
    python -m pip install pillow numpy
    python tools/animate.py
    node scripts/verify.mjs

The constants below are the tuning entry points. Coordinates are in the
1022 x 1550 source space; TOP_PAD/SIDE_PAD add transparent room for the hop
and the sway so a frame never clips at the cell border.
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "source" / "base.png"
OUT_IDLE = ROOT / "pet" / "idle"
OUT_HOP = ROOT / "pet" / "hop"
OUT_PREVIEW = ROOT / "pet" / "previews"

TOP_PAD = 64
SIDE_PAD = 24
OUT_W, OUT_H = 586, 884
IDLE_FRAMES = 24
IDLE_MS = 100
HOP_FRAMES = 11
HOP_MS = 70
GLOBAL_SHRINK = 0.97
PREVIEW_BG = (13, 20, 36)

for directory in (OUT_IDLE, OUT_HOP, OUT_PREVIEW):
    directory.mkdir(parents=True, exist_ok=True)

source_image = Image.open(SRC).convert("RGBA")
if source_image.size != (1022, 1550):
    raise SystemExit(
        f"source/base.png must be 1022 x 1550 (got {source_image.width} x {source_image.height}); "
        "the warp weights are authored for that canvas."
    )

base = Image.new("RGBA", (1022 + SIDE_PAD * 2, 1550 + TOP_PAD), (0, 0, 0, 0))
base.paste(source_image, (SIDE_PAD, TOP_PAD))
W, H = base.size
CX = 480.0
PIVOT = (445.0, 520.0)

src = np.asarray(base, dtype=np.float32) / 255.0
src[..., :3] *= src[..., 3:4]
FLAT = src.reshape(-1, 4)
X, Y = np.meshgrid(np.arange(W, dtype=np.float32), np.arange(H, dtype=np.float32))
XS = X - SIDE_PAD


def smoothstep(edge0: float, edge1: float, value: np.ndarray) -> np.ndarray:
    t = np.clip((value - edge0) / (edge1 - edge0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


# Region weights. Tail: right side, fading in from x=720 and out below y=980.
# Left hair: outer left mass. Ahoge: small gaussian at the top. Head: fades
# out down the neck so the rotation never shears the collar.
W_TAIL = smoothstep(720, 900, XS) * smoothstep(980, 720, Y)
W_LEFT = smoothstep(380, 80, XS) * smoothstep(280, 460, Y)
W_AHOGE = np.exp(-(((XS - 520) / 50) ** 2 + ((Y - 99) / 70) ** 2))
W_HEAD = 1.0 - smoothstep(450, 580, Y)


def warp(breath: float, sway: float, bob: float, head_angle: float, hop: float, sy: float, sx: float) -> Image.Image:
    # Inverse scale about the bottom edge plus the hop offset.
    y1 = H + (Y - hop - H) / sy
    x1 = CX + (XS - CX) / sx

    # Inverse head rotation (weighted, so the neck does not shear).
    angle = -head_angle * W_HEAD
    dy = y1 - PIVOT[1]
    dx = x1 - PIVOT[0]
    cos_a = np.cos(angle)
    sin_a = np.sin(angle)
    x2 = PIVOT[0] + dx * cos_a - dy * sin_a
    y2 = PIVOT[1] + dx * sin_a + dy * cos_a

    # Inverse of the local sway field.
    ddx = (16.0 * sway) * W_TAIL - (10.0 * sway) * W_LEFT + (8.0 * sway) * W_AHOGE
    ddy = (6.0 * bob) * W_TAIL - (4.0 * bob) * W_LEFT + (5.0 * bob) * W_AHOGE
    x2 = x2 - ddx
    y2 = y2 - ddy

    # A small global shrink leaves room for the sway at both silhouette edges.
    x2 = CX + (x2 - CX) / GLOBAL_SHRINK
    y2 = 864.0 + (y2 - 864.0) / GLOBAL_SHRINK

    x0 = np.floor(x2).astype(np.int32)
    y0 = np.floor(y2).astype(np.int32)
    fx = (x2 - x0)[..., None]
    fy = (y2 - y0)[..., None]
    x0 = np.clip(x0, 0, W - 2)
    y0 = np.clip(y0, 0, H - 2)
    x1i = x0 + 1
    y1i = y0 + 1

    i00 = y0 * W + x0
    i10 = y0 * W + x1i
    i01 = y1i * W + x0
    i11 = y1i * W + x1i
    c00 = FLAT[i00]
    c10 = FLAT[i10]
    c01 = FLAT[i01]
    c11 = FLAT[i11]
    out = c00 * (1 - fx) * (1 - fy) + c10 * fx * (1 - fy) + c01 * (1 - fx) * fy + c11 * fx * fy

    alpha = out[..., 3:4]
    rgb = out[..., :3] / np.maximum(alpha, 1e-6)
    rgba = np.concatenate([np.clip(rgb, 0, 1), alpha], axis=2)
    image = Image.fromarray((rgba * 255.0).round().astype(np.uint8), "RGBA")
    return image.resize((OUT_W, OUT_H), Image.LANCZOS)


idle_frames = []
for index in range(IDLE_FRAMES):
    t = 2.0 * math.pi * index / IDLE_FRAMES
    frame = warp(
        breath=math.sin(t),
        sway=math.sin(t),
        bob=math.sin(2.0 * t),
        head_angle=0.006 * math.sin(t),
        hop=0.0,
        sy=1.0 + 0.008 * math.sin(t),
        sx=1.0 - 0.004 * math.sin(t),
    )
    idle_frames.append(frame)
    frame.save(OUT_IDLE / f"{index + 1:02d}.webp", "WEBP", quality=95, method=6)

hop_spec = [
    (0.0, 1.000, 1.000),
    (0.0, 0.980, 1.006),
    (0.0, 0.965, 1.010),
    (-22.0, 1.012, 0.995),
    (-44.0, 1.006, 0.997),
    (-52.0, 1.000, 1.000),
    (-40.0, 1.004, 0.998),
    (-12.0, 0.985, 1.007),
    (0.0, 0.972, 1.010),
    (0.0, 0.990, 1.004),
    (0.0, 1.000, 1.000),
]
hop_frames = []
for index, (hop, sy, sx) in enumerate(hop_spec):
    phase = 2.0 * math.pi * index / (HOP_FRAMES - 1)
    frame = warp(
        breath=0.0,
        sway=0.55 * math.sin(phase),
        bob=0.4 * math.sin(2.0 * phase),
        head_angle=0.0,
        hop=hop,
        sy=sy,
        sx=sx,
    )
    hop_frames.append(frame)
    frame.save(OUT_HOP / f"{index + 1:02d}.webp", "WEBP", quality=95, method=6)


def preview(frames: list[Image.Image], path: Path, size: tuple[int, int], ms: int) -> None:
    flats = []
    for frame in frames:
        canvas = Image.new("RGB", frame.size, PREVIEW_BG)
        canvas.paste(frame, (0, 0), frame)
        flats.append(canvas.resize(size, Image.LANCZOS))
    flats[0].save(path, "GIF", save_all=True, append_images=flats[1:], duration=ms, loop=0, optimize=True)


preview(idle_frames, OUT_PREVIEW / "idle.gif", (300, 452), IDLE_MS)
preview(hop_frames, OUT_PREVIEW / "hop.gif", (300, 452), HOP_MS)

print(f"wrote {len(idle_frames)} idle frames to {OUT_IDLE}")
print(f"wrote {len(hop_frames)} hop frames to {OUT_HOP}")
print(f"frame size: {idle_frames[0].size}")

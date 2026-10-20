"""Generate the whale-maid tracks and pet.json from one transparent illustration.

The source (source/base.png) is a single 1022 x 1550 cutout. Every track is a
mesh warp of that image: breathing, tail/hair sway, head tilt, lean, sink,
squash/stretch and a hop. The tracks are authored for the frames2d renderer,
where each track is <track>/<frame>.webp plus the metadata in pet.json.

Usage:
    python -m pip install pillow numpy
    python tools/animate.py
    node scripts/verify.mjs

The constants below are the tuning entry points. Coordinates are in the
1022 x 1550 source space; TOP_PAD/SIDE_PAD add transparent room for the hop
and the sway so a frame never clips at the cell border.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "source" / "base.png"
PET = ROOT / "pet"
OUT_PREVIEW = PET / "previews"

TOP_PAD = 64
SIDE_PAD = 24
RIGHT_PAD = 36
OUT_H = 724
GLOBAL_SHRINK = 0.97
PREVIEW_BG = (13, 20, 36)
PREVIEW_H = 350

for directory in (PET, OUT_PREVIEW):
    directory.mkdir(parents=True, exist_ok=True)

source_image = Image.open(SRC).convert("RGBA")
if source_image.size != (1022, 1550):
    raise SystemExit(
        f"source/base.png must be 1022 x 1550 (got {source_image.width} x {source_image.height}); "
        "the warp weights are authored for that canvas."
    )

base = Image.new("RGBA", (1022 + SIDE_PAD * 2 + RIGHT_PAD, 1550 + TOP_PAD), (0, 0, 0, 0))
base.paste(source_image, (SIDE_PAD, TOP_PAD))
W, H = base.size
OUT_W = round(OUT_H * W / H)
PREVIEW_SIZE = (round(PREVIEW_H * W / H), PREVIEW_H)
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
# out down the neck. Upper body: fades out toward the feet, so lean/sink move
# the torso without sliding the shoes.
W_TAIL = smoothstep(720, 900, XS) * smoothstep(980, 720, Y)
W_LEFT = smoothstep(380, 80, XS) * smoothstep(280, 460, Y)
W_AHOGE = np.exp(-(((XS - 520) / 50) ** 2 + ((Y - 99) / 70) ** 2))
W_HEAD = 1.0 - smoothstep(450, 580, Y)
W_UPPER = 1.0 - smoothstep(0.55 * H, 0.95 * H, Y)


def warp(
    breath: float = 0.0,
    sway: float = 0.0,
    bob: float = 0.0,
    head_angle: float = 0.0,
    hop: float = 0.0,
    sy: float = 1.0,
    sx: float = 1.0,
    head_dx: float = 0.0,
    lean: float = 0.0,
    sink: float = 0.0,
    shake: float = 0.0,
    tail_dy: float = 0.0,
    tail_amp: float = 16.0,
    hair_amp: float = 10.0,
    ahoge_amp: float = 8.0,
) -> Image.Image:
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

    # Inverse of the local sway field and the extra body shifts.
    ddx = tail_amp * sway * W_TAIL - hair_amp * sway * W_LEFT + ahoge_amp * sway * W_AHOGE
    ddy = 6.0 * bob * W_TAIL - 4.0 * bob * W_LEFT + 5.0 * bob * W_AHOGE
    x2 = x2 - ddx - head_dx * W_HEAD - (lean + shake) * W_UPPER
    y2 = y2 - ddy - sink * W_UPPER - tail_dy * W_TAIL

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


def idle_params(i: int, n: int) -> dict:
    t = 2.0 * math.pi * i / n
    return dict(
        breath=math.sin(t),
        sway=math.sin(t),
        bob=math.sin(2.0 * t),
        head_angle=0.006 * math.sin(t),
        sy=1.0 + 0.008 * math.sin(t),
        sx=1.0 - 0.004 * math.sin(t),
    )


def tail_wag_params(i: int, n: int) -> dict:
    u = 2.0 * math.pi * i / (n - 1)
    return dict(sway=1.7 * math.sin(u), bob=0.4 * math.sin(2.0 * u), tail_amp=24.0, hair_amp=6.0, ahoge_amp=5.0)


def head_tilt_params(i: int, n: int) -> dict:
    u = 2.0 * math.pi * i / (n - 1)
    return dict(
        head_dx=12.0 * math.sin(u),
        head_angle=0.026 * math.sin(u),
        sway=-0.6 * math.sin(u),
        bob=0.3 * math.sin(2.0 * u),
        tail_amp=10.0,
        hair_amp=8.0,
    )


def bounce_params(i: int, n: int) -> dict:
    p = math.sin(math.pi * i / (n - 1))
    u = 2.0 * math.pi * i / (n - 1)
    return dict(hop=-26.0 * p, sy=1.0 + 0.01 * p, sx=1.0 - 0.005 * p, sway=0.8 * math.sin(u), head_angle=-0.006 * p)


def think_params(i: int, n: int) -> dict:
    t = 2.0 * math.pi * i / n
    return dict(
        head_angle=0.024 + 0.005 * math.sin(t),
        head_dx=4.0 * math.sin(t + math.pi / 2.0),
        sway=0.4 * math.sin(t),
        breath=0.3 * math.sin(t),
        bob=0.25 * math.sin(2.0 * t),
        tail_amp=12.0,
        hair_amp=8.0,
    )


def droop_params(i: int, n: int) -> dict:
    p = math.sin(math.pi * i / (n - 1))
    u = 2.0 * math.pi * i / (n - 1)
    return dict(
        sink=16.0 * p,
        head_angle=-0.04 * p,
        tail_dy=22.0 * p,
        sy=1.0 - 0.006 * p,
        sway=0.15 * math.sin(u),
        tail_amp=12.0,
    )


def pat_head_params(i: int, n: int) -> dict:
    u = 2.0 * math.pi * i / (n - 1)
    return dict(
        head_angle=0.026 * math.sin(u),
        head_dx=6.0 * math.sin(u),
        sway=1.0 * math.sin(u),
        bob=0.5 * math.sin(2.0 * u),
        breath=0.5 * math.sin(u),
        sy=1.0 - 0.004 * math.sin(u) ** 2,
    )


def poke_body_params(i: int, n: int) -> dict:
    p = math.sin(math.pi * i / (n - 1))
    u = 2.0 * math.pi * 1.5 * i / (n - 1)
    return dict(
        hop=-26.0 * p,
        sy=1.0 + 0.01 * p,
        sx=1.0 - 0.005 * p,
        head_angle=-0.01 * p,
        sway=1.3 * math.sin(u),
        bob=0.6 * math.sin(u),
    )


def shiver_params(i: int, n: int) -> dict:
    u = 2.0 * math.pi * 3.0 * i / (n - 1)
    v = 2.0 * math.pi * 1.5 * i / (n - 1)
    return dict(shake=9.0 * math.sin(u), head_dx=4.0 * math.sin(u), sway=0.4 * math.sin(v), head_angle=0.004 * math.sin(u))


def hop_params(i: int, n: int) -> dict:
    spec = [
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
    hop, sy, sx = spec[i]
    phase = 2.0 * math.pi * i / (n - 1)
    return dict(hop=hop, sy=sy, sx=sx, sway=0.55 * math.sin(phase), bob=0.4 * math.sin(2.0 * phase))


TRACKS = [
    dict(name="idle", count=24, ms=100, loop=True, params=idle_params),
    dict(name="hop", count=11, ms=70, loop=False, params=hop_params),
    dict(name="tail-wag", count=12, ms=60, loop=False, params=tail_wag_params),
    dict(name="head-tilt", count=18, ms=80, loop=False, params=head_tilt_params),
    dict(name="bounce", count=12, ms=60, loop=False, params=bounce_params),
    dict(name="think", count=24, ms=120, loop=True, params=think_params),
    dict(name="droop", count=14, ms=90, loop=False, params=droop_params),
    dict(name="pat-head", count=14, ms=60, loop=False, params=pat_head_params),
    dict(name="poke-body", count=12, ms=50, loop=False, params=poke_body_params),
    dict(name="shiver", count=12, ms=40, loop=False, params=shiver_params),
]

FRAMES: dict[str, list[Image.Image]] = {}


def render_track(track: dict) -> None:
    name = track["name"]
    count = track["count"]
    target = PET / name
    target.mkdir(parents=True, exist_ok=True)
    for old in target.glob("*.webp"):
        old.unlink()
    frames: list[Image.Image] = []
    for index in range(count):
        frame = warp(**track["params"](index, count))
        bbox = frame.getchannel("A").getbbox()
        if bbox is None:
            raise SystemExit(f"{name}/{index + 1}: empty alpha")
        if bbox[0] <= 0 or bbox[1] <= 0 or bbox[2] >= OUT_W or bbox[3] >= OUT_H:
            raise SystemExit(f"{name}/{index + 1}: frame clips the cell: {bbox} (cell {OUT_W}x{OUT_H})")
        frames.append(frame)
        frame.save(target / f"{index + 1:02d}.webp", "WEBP", quality=95, method=6)
    FRAMES[name] = frames
    print(f"{name}: {count} frames, {count * track['ms']} ms")


for track in TRACKS:
    render_track(track)


def manifest() -> dict:
    tracks = {}
    for track in TRACKS:
        entry = {
            "frames": [f"{i + 1:02d}.webp" for i in range(track["count"])],
            "frameMs": [track["ms"]] * track["count"],
            "loop": track["loop"],
        }
        if not track["loop"]:
            entry["fallback"] = "idle"
        tracks[track["name"]] = entry

    return {
        "$schema": "https://schemas.linxin666.org/dsh-pet/pet-manifest-v2.schema.json",
        "petManifestVersion": 2,
        "id": "whale-maid",
        "displayName": "蓝白鲸尾女仆",
        "description": "蓝白配色的鲸尾女仆少女。有呼吸、摇尾、歪头、小跳和摸头反应。",
        "version": "1.2.0",
        "license": "personal-use",
        "renderer": "frames2d",
        "frames2d": {
            "tracks": tracks,
            "phases": {
                "idle": "idle",
                "waiting": "idle",
                "thinking": "think",
                "tool": "think",
                "review": "think",
                "done": "hop",
                "failed": "droop",
            },
        },
        "gameplay": {
            "stats": {
                "mood": {"max": 100, "initial": 60, "decayPerMinute": 0},
            },
            "hitBox": {"x0": 0.05, "y0": 0.03, "x1": 0.99, "y1": 0.99},
            "idleDirector": {
                "intervalMs": 18000,
                "maxMiss": 2,
                "idleWeight": 5,
                "acts": [
                    {"track": "tail-wag", "weight": 3, "phrases": ["尾巴摇摇～", "今天也很开心～"]},
                    {"track": "head-tilt", "weight": 2, "phrases": ["在看什么呀？", "嗯？"]},
                    {"track": "bounce", "weight": 2, "phrases": ["嘿嘿～", "跳一下！"]},
                ],
            },
            "touch": {
                "zones": [
                    {
                        "name": "head",
                        "y0": 0,
                        "y1": 0.30,
                        "branches": [{
                            "probability": 1,
                            "state": "pat-head",
                            "stateMs": 840,
                            "effects": [{"stat": "mood", "amount": 3}],
                            "phrases": ["摸摸头～", "好舒服～", "再摸一下～"],
                        }],
                    },
                    {
                        "name": "body",
                        "y0": 0.30,
                        "y1": 0.72,
                        "branches": [{
                            "probability": 1,
                            "state": "poke-body",
                            "stateMs": 600,
                            "effects": [{"stat": "mood", "amount": 2}],
                            "phrases": ["呀！", "别戳啦～", "尾巴被看到啦～"],
                        }],
                    },
                    {
                        "name": "legs",
                        "y0": 0.72,
                        "y1": 1,
                        "branches": [{
                            "probability": 1,
                            "state": "shiver",
                            "stateMs": 480,
                            "effects": [{"stat": "mood", "amount": 2}],
                            "phrases": ["痒痒的～", "咯咯～", "别挠啦～"],
                        }],
                    },
                ],
            },
        },
        "remarks": {
            "pet": ["摸摸头～", "鲸尾摇摇，开心～"],
            "feed": ["小鱼干真香！", "再来一条～"],
            "noTreats": ["没有小鱼干了……陪我工作一会儿吧～"],
        },
    }


manifest_path = PET / "pet.json"
manifest_path.write_text(json.dumps(manifest(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"wrote {manifest_path}")


try:
    LABEL_FONT = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 14)
except OSError:
    LABEL_FONT = ImageFont.load_default()


def flatten(frame: Image.Image, label: str | None = None) -> Image.Image:
    canvas = Image.new("RGB", frame.size, PREVIEW_BG)
    canvas.paste(frame, (0, 0), frame)
    canvas = canvas.resize(PREVIEW_SIZE, Image.LANCZOS)
    if label is not None:
        draw = ImageDraw.Draw(canvas)
        width = int(draw.textlength(label, font=LABEL_FONT))
        draw.rounded_rectangle((10, canvas.height - 32, 10 + width + 16, canvas.height - 8), 8, fill=(12, 20, 36))
        draw.text((18, canvas.height - 28), label, font=LABEL_FONT, fill=(186, 215, 255))
    return canvas


def gif(frames: list[Image.Image], path: Path, durations: int | list[int], label: str | None = None) -> None:
    flats = [flatten(frame, label) for frame in frames]
    flats[0].save(
        path, "GIF", save_all=True, append_images=flats[1:],
        duration=durations, loop=0, optimize=True,
    )
    print(f"{path.name}: {len(flats)} frames, {round(path.stat().st_size / 1024 / 1024, 2)} MB")


gif(FRAMES["idle"], OUT_PREVIEW / "idle.gif", 100)
gif(FRAMES["hop"], OUT_PREVIEW / "hop.gif", 70)

showreel: list[Image.Image] = []
showreel_ms: list[int] = []
clips = [
    ("idle", FRAMES["idle"][:8], 100),
    ("tail wag", FRAMES["tail-wag"][:8], 60),
    ("head tilt", FRAMES["head-tilt"][:8], 80),
    ("bounce", FRAMES["bounce"][:8], 60),
    ("head pat", FRAMES["pat-head"][:8], 60),
    ("poke", FRAMES["poke-body"][:8], 50),
    ("shiver", FRAMES["shiver"][:8], 40),
    ("think", FRAMES["think"][:8], 120),
    ("droop", FRAMES["droop"][:8], 90),
    ("hop", FRAMES["hop"][:8], 70),
]
for label, frames, ms in clips:
    for frame in frames:
        showreel.append(flatten(frame, label))
        showreel_ms.append(ms)
showreel[0].save(
    OUT_PREVIEW / "showreel.gif", "GIF", save_all=True, append_images=showreel[1:],
    duration=showreel_ms, loop=0, optimize=True,
)
print(f"showreel.gif: {len(showreel)} frames, {round((OUT_PREVIEW / 'showreel.gif').stat().st_size / 1024 / 1024, 2)} MB")
print("done")

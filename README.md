**English** | [简体中文](README.zh-CN.md)

# Whale-Maid · DSH Desktop Pet

An animated custom pet for the DeepSeek Harness [`@linxin666/dsh-pet`](https://github.com/zhu1090093659/dsh-pet) plugin.
Built from a single illustration: a 24-frame idle loop plus an 11-frame celebration hop.

![Idle loop](pet/previews/idle.gif)

![Celebration hop](pet/previews/hop.gif)

## What it is

- Pet id: `whale-maid`
- Display name: 蓝白鲸尾女仆 (Blue-White Whale-Tail Maid)
- Manifest: `pet/pet.json` (manifest v2, `renderer: frames2d`)
- Idle: `pet/idle/01..24.webp`, 100 ms per frame, 2.4 s loop
- Celebration: `pet/hop/01..11.webp`, 70 ms per frame, 0.77 s, plays once and falls back to idle
- Frames: 586 × 884 transparent WebP, 35 frames total
- Default display size: 210 px tall (adjustable in Settings → Pet)

## Quick install

Requirements: DSH Desktop (or a `dsh web` host) with the `@linxin666/dsh-pet` plugin installed.
On Windows, both Windows PowerShell 5.1 and PowerShell 7+ work.

```powershell
git clone https://github.com/hellokiaqi/whale-maid-dsh-pet.git
powershell -NoProfile -ExecutionPolicy Bypass -File .\whale-maid-dsh-pet\scripts\install.ps1
```

The installer:

1. Finds `$env:DSH_HOME`, then falls back to `%USERPROFILE%\.dsh-beta` or `%USERPROFILE%\.dsh`.
2. Copies `pet/` to `$DSH_HOME\pets\whale-maid\`.
3. Prints the frame counts, destination, and the next step.

Then **restart DSH Desktop** (tray icon → Restart DSH Desktop) and choose
“蓝白鲸尾女仆” in **Settings → Pet**.

To make it the default pet in one go:

```powershell
cd whale-maid-dsh-pet
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\install.ps1 -Select
```

`-Select` only edits the `petId` field inside an existing `- id: pet` block in
`profiles\desktop\cordis.patch.yml`. If that block is not found, it skips the edit and
you can still select the pet in Settings.

macOS / Linux (DSH home is usually `~/.dsh`):

```bash
git clone https://github.com/hellokiaqi/whale-maid-dsh-pet.git
bash whale-maid-dsh-pet/scripts/install.sh
```

## Updating

```powershell
cd whale-maid-dsh-pet
git pull
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\install.ps1
```

Restart DSH Desktop afterwards. The pet id never changes, so your selection and
affinity are preserved.

## Manual install

No script needed: copy the whole `pet/` directory to
`%DSH_HOME%\pets\whale-maid\`.

```
%DSH_HOME%\pets\whale-maid\
  pet.json
  idle\01..24.webp
  hop\01..11.webp
```

`pet/previews/` is only for the README and previews; the plugin never treats it as
animation frames. It is optional for a manual install.

## Repository layout

```
whale-maid-dsh-pet/
├── pet/                 # the pet package (copy this to $DSH_HOME/pets/whale-maid)
│   ├── pet.json
│   ├── idle/            # 24-frame idle loop
│   ├── hop/             # 11-frame celebration hop
│   └── previews/        # README / preview GIFs
├── source/
│   └── base.png         # 1022×1550 transparent base image
├── tools/
│   └── animate.py       # regenerates idle/hop with a mesh warp (Python + Pillow + numpy)
├── scripts/
│   ├── install.ps1
│   ├── install.sh
│   └── verify.mjs       # manifest/frame checks without plugin internals
├── docs/
│   └── ANIMATION.md     # tracks, timing, phases, and tuning (Chinese)
├── .github/workflows/
│   └── verify.yml       # runs the verifier on push
├── README.md            # English
├── README.zh-CN.md      # 简体中文
├── NOTICE.md            # artwork provenance and licensing
└── LICENSE              # MIT for scripts/docs (artwork excluded)
```

## Compatibility

- Manifest version: `petManifestVersion: 2`
- Renderer: `frames2d`
- Verified with `@linxin666/dsh-pet` 0.4.7 and DSH Desktop Beta 2.0.18
- If the plugin contract changes: update `pet/pet.json`, then run
  `node scripts/verify.mjs`

## Customization

- **Change speed**: edit `frameMs` for the `idle` track in `pet/pet.json`
  (16–5000 ms per frame).
- **Change the motion**: replace the frames in `pet/idle/` or `pet/hop/` and keep
  the file names/counts, or edit the `frames` arrays.
- **Add a state**: map `waiting` / `thinking` / `review` / `done` / `failed` to an
  existing track in `frames2d.phases`.
- **Regenerate**: edit the amplitudes, frame counts, and durations at the top of
  `tools/animate.py`, then:

```bash
python -m pip install pillow numpy
python tools/animate.py
node scripts/verify.mjs
```

See [docs/ANIMATION.md](docs/ANIMATION.md) for the track/phase details (Chinese).

## License

- Scripts, manifest, and documentation: MIT (see [LICENSE](LICENSE)).
- Pet artwork (`pet/idle`, `pet/hop`, `pet/previews`, `source/base.png`):
  **personal use only** (`"personal-use"` in `pet/pet.json`). See
  [NOTICE.md](NOTICE.md) and the provenance notice below.

## Provenance and fan-work notice

This pet is an **unofficial fan work**. The artwork was generated with an AI image
tool from a reference image supplied by the repository owner: a Chinese-language
meme titled **“当各家 LLM 做道德题时”** (“When LLMs take moral questions”), which
depicts Claude, GPT, Llama, and DeepSeek mascots seated around a table. The
blue-haired, whale-tailed maid labeled **“DeepSeek”** in that meme is the visual
basis for this pet.

The reference image is **not** included in this repository. Its original artist and
source are unknown; it may itself be an AI-generated or fan-made work. It contains
third-party characters and marks (Claude, GPT, Llama, DeepSeek); all rights in those
remain with their respective owners.

This project is **not affiliated with, sponsored by, or endorsed by** DeepSeek,
Anthropic, OpenAI, Meta, or any other rights holder. The pet artwork is provided for
**personal, non-commercial use only**; no license is granted to redistribute it.
If you are a rights holder and believe this repository infringes your rights, please
open an issue and the material will be removed.

AI-generated output may not be protected by copyright and may be subject to the
terms of the tool that produced it. If you intend to publish or use this work
commercially, verify the rights with a qualified lawyer.

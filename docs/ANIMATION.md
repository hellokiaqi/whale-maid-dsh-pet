# 动画说明

这份宠物使用 `frames2d` 渲染器：没有图集，每个动作是 `<track>/<frame>` 目录下的一组图，
按 `pet/pet.json` 里的 `frames` / `frameMs` 顺序播放。

## 当前轨道

| 轨道 | 帧数 | 单帧时长 | 总时长 | 循环 | 映射相位 |
|---|---:|---:|---:|---|---|
| `idle` | 24 | 100 ms | 2.40 s | 是 | `idle`（以及所有未映射相位） |
| `hop` | 11 | 70 ms | 0.77 s | 否 | `done` |

- 所有帧：586 × 884，透明 WebP。
- `hop` 的 `fallback` 是 `idle`：播完自动回待机。
- 注册表用 `idle` 的第一帧尺寸作为宠物框的宽高比，所以换帧时保持图片比例一致，
  否则宠物框和气泡的位置会变。

## 相位与动作

```json
"phases": {
  "idle": "idle",
  "done": "hop"
}
```

未声明的相位（`waiting` / `thinking` / `tool` / `review` / `failed`）都会回落到 `idle`。
想给思考或失败单独做动作，加轨道再映射即可：

```json
"tracks": {
  "think": { "frames": ["01.webp", "02.webp"], "frameMs": [300, 300], "loop": true }
},
"phases": { "idle": "idle", "thinking": "think", "done": "hop" }
```

## 调速

- 整体变慢：把 `frameMs` 等比调大（例如 idle 从 100 改成 130）。
- 整体变快：调小，最低 16 ms。
- 单个轨道可以有自己的节奏；`hop` 用 70 ms 是为了让起跳更利落。

改完跑一次：

```bash
node scripts/verify.mjs
```

然后重启 DSH Desktop。

## 动作是怎么生成的

`tools/animate.py` 从 `source/base.png`（1022 × 1550 透明底图）生成所有帧。它做的是
**网格变形**，不是逐帧重绘：

- 呼吸：以脚为锚点的纵向缩放（约 0.8%），横向轻微反向补偿；
- 尾巴：从尾根到尾尖权重渐增的左右摆 + `sin(2t)` 的上下 8 字；
- 头发：左右两束以相反相位轻摆，权重从发根到发梢渐大；
- 呆毛：一个高斯权重的小幅抖动；
- 歪头：以脖子为轴，权重向下衰减，避免脖子被剪切；
- 小跳：下蹲压扁 → 起跳拉长上移 → 落地压扁 → 回正；
- 所有帧共用一张画布（586 × 884），并留出透明边距，防止尾巴/头发摆出边界。

运行：

```bash
python -m pip install pillow numpy
python tools/animate.py
node scripts/verify.mjs
```

脚本顶部的常量就是调参入口：

```python
TOP_PAD = 64        # 顶部留白，给起跳用
SIDE_PAD = 24       # 两侧留白
OUT_W, OUT_H = 586, 884
IDLE_FRAMES = 24
IDLE_MS = 100
HOP_FRAMES = 11
HOP_MS = 70
```

`smoothstep` 权重里的坐标、`warp()` 里的振幅（16 / 10 / 8 / 6 等）可以按喜好调整；
改大之前先确认帧不会被裁掉（脚本生成的 bbox 应该始终大于 0、小于画布宽高）。

## 单张立绘的局限

这种形变适合呼吸、摇尾、轻微歪头和小跳。要做挥手、走路、换表情，最好有对应的
多张原画，或者做 Live2D 模型；单张图硬扭会出现关节/衣褶拉伸。

## 预览

`pet/previews/idle.gif` 和 `pet/previews/hop.gif` 只用于 README 和 GitHub 展示；
插件不会把它们当作动画帧。

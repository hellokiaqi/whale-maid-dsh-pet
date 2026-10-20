# 动画说明

这份宠物使用 `frames2d` 渲染器：没有图集，每个动作是 `<track>/<frame>` 目录下的一组图，
按 `pet/pet.json` 里的 `frames` / `frameMs` 顺序播放。

## 当前轨道

| 轨道 | 帧数 | 单帧 | 总时长 | 循环 | 用途 |
|---|---:|---:|---:|---|---|
| `idle` | 24 | 100 ms | 2.40 s | 是 | 默认待机 |
| `hop` | 11 | 70 ms | 0.77 s | 否 | `done` 完成小跳 |
| `tail-wag` | 12 | 60 ms | 0.72 s | 否 | 空闲导演：摇尾 |
| `head-tilt` | 18 | 80 ms | 1.44 s | 否 | 空闲导演：歪头看 |
| `bounce` | 12 | 60 ms | 0.72 s | 否 | 空闲导演：小跳 |
| `think` | 24 | 120 ms | 2.88 s | 是 | `thinking` / `tool` / `review` |
| `droop` | 14 | 90 ms | 1.26 s | 否 | `failed` 沮丧 |
| `pat-head` | 14 | 60 ms | 0.84 s | 否 | 点头部 |
| `poke-body` | 12 | 50 ms | 0.60 s | 否 | 点身体/尾巴 |
| `shiver` | 12 | 40 ms | 0.48 s | 否 | 点腿 |

- 所有帧：496 × 724，透明 WebP；总计 153 帧。
- 非循环轨道的 `fallback` 都是 `idle`：播完自动回待机。
- 注册表用 `idle` 的第一帧尺寸作为宠物框的宽高比，所以换帧时保持图片比例一致，
  否则宠物框和气泡的位置会变。

## 相位映射

```json
"phases": {
  "idle": "idle",
  "waiting": "idle",
  "thinking": "think",
  "tool": "think",
  "review": "think",
  "done": "hop",
  "failed": "droop"
}
```

未声明的相位会回落到 `idle`。

## 空闲导演

`gameplay.idleDirector` 每 `intervalMs`（18 秒）掷一次骰：

- `idleWeight`：5（什么都不做）
- `tail-wag`：3
- `head-tilt`：2
- `bounce`：2
- `maxMiss`：2，连续两次没抽中动作后强制演一个

每个 act 可以带 `phrases`，播动作时宠物会说一句；动作期间不会和拖拽、点击反应、
漫游或已有动作抢同一帧。

## 点击反应

`gameplay.touch.zones` 是按**纵向**切的三个区域（`hitBox` 内 0–1）：

| 区域 | y 范围 | 轨道 | `stateMs` | 心情 |
|---|---|---:|---:|---:|
| 头 | 0.00–0.30 | `pat-head` | 840 | +3 |
| 身体/尾巴 | 0.30–0.72 | `poke-body` | 600 | +2 |
| 腿 | 0.72–1.00 | `shiver` | 480 | +2 |

点击本身仍会计入摸头亲密度。`gameplay.stats.mood` 是 `max 100 / initial 60`、
不衰减的心情条，打开「玩法」可以看到；区域效果会把心情加上去。

## 调速

- 整体变慢：把对应轨道的 `frameMs` 等比调大（例如 idle 从 100 改成 130）。
- 整体变快：调小，最低 16 ms。
- 单轨可以有自己的节奏；`hop` 用 70 ms 让起跳更利落，`shiver` 用 40 ms 做快速抖动。

改完跑一次：

```bash
node scripts/verify.mjs
```

然后重启 DSH Desktop。

## 动作是怎么生成的

`tools/animate.py` 从 `source/base.png`（1022 × 1550 透明底图）生成所有帧和
`pet/pet.json`。它做的是**网格变形**，不是逐帧重绘：

- 呼吸：以脚为锚点的纵向缩放，横向轻微反向补偿；
- 尾巴：从尾根到尾尖权重渐增的左右摆 + 上下 8 字；
- 头发：左右两束以相反相位轻摆，权重从发根到发梢渐大；
- 呆毛：一个高斯权重的小幅抖动；
- 歪头：以脖子为轴，权重向下衰减；`head_dx` 让头左右移动；
- 前倾/下沉：上身躯干的水平/垂直位移，权重到脚踝衰减为 0；
- 小跳：下蹲压扁 → 起跳拉长上移 → 落地压扁 → 回正；
- 所有帧共用 496 × 724 画布，左右/顶部留透明边距，右侧额外留 36 px 给摇尾。

运行：

```bash
python -m pip install pillow numpy
python tools/animate.py
node scripts/verify.mjs
```

脚本顶部的常量就是调参入口：

```python
TOP_PAD = 64        # 顶部留白，给起跳用
SIDE_PAD = 24       # 左侧/基础留白
RIGHT_PAD = 36      # 右侧额外留白，给摇尾用
OUT_H = 724         # 输出高度，宽度按底图比例算
PREVIEW_H = 350     # 预览 GIF 高度
```

轨道表在 `TRACKS` 里：每项有 `name`、`count`、`ms`、`loop` 和一个 `params(i, n)`
函数；函数返回 `warp()` 的参数。`render_track` 每帧都会检查 alpha bbox，碰到画布
边界会直接报错，所以改大振幅后先本地跑一遍。

## 单张立绘的局限

这种形变适合呼吸、摇尾、歪头、下沉和小跳。要做挥手、走路、换表情，最好有对应的
多张原画，或者做 Live2D 模型；单张图硬扭会出现关节/衣褶拉伸。

## 预览

`pet/previews/idle.gif`、`hop.gif` 和 `showreel.gif` 只用于 README 和 GitHub 展示；
插件不会把它们当作动画帧。

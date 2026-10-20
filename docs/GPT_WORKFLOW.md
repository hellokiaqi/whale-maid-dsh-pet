# 用 GPT 生成复杂动作素材：执行方案

目标：给「蹲下画圈圈」「转圈跳舞」这类动作补图。GPT（ChatGPT 图像 / GPT Image）
适合出**单张关键姿势**和**特效层**，不适合一次出完整动画。推荐流程是：

> GPT 出角色设定 + 每个动作 6–8 张关键姿势 → 我们后期抠图/对齐/插帧 → 接进插件。

如果你只用 GPT，也能做，但动作会是「关键帧 + 少量中间帧」的有限动画；要顺滑的
12–24 帧循环，最好补一个 AI 视频或 RIFE/FILM 插帧步骤（见阶段 4）。

## 最小可行版本（建议先跑这个）

1. 角色四视图（阶段 0）。
2. 蹲下画圈 6 张关键姿势（阶段 1）。
3. 正面 twirl 6 张（阶段 2 方案 A）。
4. 圈圈特效 1 张（阶段 3）。

先做成 6 + 6 帧、120 ms/帧，接进插件看效果；跑通后再挑战 360° 和插帧。
这样即使 GPT 的一致性一般，也能先得到一个可用的「蹲下画圈 + 原地转圈」。

> 眨眼是另一套素材：见 [BLINK_WORKFLOW.md](BLINK_WORKFLOW.md)。核心是先生成一张
> **睁眼版**，让睁眼成为默认，闭眼只用于眨眼帧。

---

## 准备

1. **参考图**：用现在的 `source/base.png`（透明底）或它的白底版。
2. **一个固定会话**：一个动作一个 ChatGPT 会话，先把角色参考图上传，之后一直用
   “Edit the attached image”，不要每次新开会话重新生成。
3. **画布**：1024 × 1536（2:3），全身、四周留 5% 边距、脚底同一条线。可以上传
   [`frame-guide.png`](templates/frame-guide.png) 当构图参考，并要求
   “不要画出辅助线”。
4. **统一命名**：`assets/ref/`、`assets/draw-circle/`、`assets/dance/`、`assets/effects/`。

---

## 阶段 0：角色四视图（最重要）

先生成一张 2×2 的四视图，锁住正面、3/4、侧面、背面。360° 转圈必须要有背面，
否则 GPT 每帧都会重新编后背和尾巴。

### 提示词

```text
Use the attached image as the exact character reference. Create a character model sheet
on a plain white background: a 2x2 grid with four full-body views of the same chibi
whale-maid — front, 3/4 front, side, back. Keep the same face, closed happy eyes,
long wavy deep-blue hair with light-blue tips, ahoge, blue whale-fin ear ornaments,
white frilled maid headdress, blue ribbon bows, navy-blue and white frilled maid dress,
white ruffled apron, blue bows, white thigh-high stockings with blue bows, navy Mary Jane
platform shoes, and the large blue whale tail with a pale underside. Same proportions
and colors. Neutral standing pose, arms at the sides. No text, no labels, no watermark,
no shadow, no floor.
```

拿到图后裁成四张，保存 `ref/front.png`、`ref/side.png`、`ref/back.png`。如果背面不一致，
用正面当参考单独重画：

```text
Using the front view as the exact reference, draw the back view of the same character:
seen from behind, same scale and height, long blue hair covering the back, back of the
navy maid dress with white apron ties and blue bows, large blue whale tail attached at
the lower back, plain white background, full body, no shadow, no text.
```

**检查**：尾巴、蓝色鱼鳍耳饰、白围裙、蓝蝴蝶结、过膝袜、玛丽珍鞋。缺一个就重画。

---

## 阶段 1：蹲下画圈（6 张关键姿势）

每个动作都从**同一张 canonical 正面图**开始，用编辑而不是重新生成。

### 通用编辑模板

```text
Edit the attached image. Keep the character, face, hair, ahoge, blue whale-fin ear
ornaments, white frilled headdress, navy and white maid dress, white apron, blue bows,
white thigh-high stockings, navy Mary Jane shoes, blue whale tail, proportions, colors,
camera angle, scale, and plain white background exactly the same. Only change the pose
to: [POSE]. Keep the full body in frame and the feet on the same ground line.
Do not add a floor, cast shadow, magic circle, sparkles, floor markings, guide lines,
grid, text, or watermark.
```

### 六张的 `[POSE]`

1. `standing, looking down at the floor, hands at her sides, tail hanging behind`
2. `crouching down, heels together, knees bent, skirt spread around her, feet visible, one hand reaching toward the floor with the index finger extended, the other hand on her knee, tail curled to the side`
3. `crouching low, heels together, knees bent, skirt spread, feet visible, index finger drawing an arc on the floor to the left, head following the finger, tail swishing to the right`
4. `crouching, index finger at the right end of the arc, looking at the floor, tail lifted`
5. `crouching, looking up at the viewer, happy smile, index finger still touching the floor`
6. `standing up, hands clasped in front, happy smile`

保存 `draw-circle/01.png .. 06.png`。**角色图里不要圈**，圈用阶段 3 单独做。

---

## 阶段 2：转圈跳舞

### 方案 A：正面 twirl（推荐先做，不需要背面）

6 张关键姿势：

1. `standing, arms slightly out, tail behind`
2. `arms out, body tilted to the left, skirt starting to flare, tail swinging to the right`
3. `arms out, body tilted further left, skirt flaring outward, tail swinging right`
4. `arms raised, body upright, skirt fully flared, tail lifted`
5. `arms out, body tilted to the right, skirt flaring, tail swinging to the left`
6. `back to front, arms down, skirt settling`

提示词仍用阶段 1 的编辑模板，`[POSE]` 换成上面六句，再加：

```text
front-facing twirl dance, same camera, same center, no motion blur
```

### 方案 B：完整 360°（需要背面）

用 `ref/front.png`、`ref/side.png`、`ref/back.png` 当参考，一帧一帧生成，不要一次要 8 张。

```text
Using the attached character reference, draw the same character rotated [ANGLE] degrees
clockwise in a spin. Same character, outfit, colors, proportions, scale, center, and
camera height. Arms out, skirt flaring, blue whale tail visible and swinging. Full body,
plain white background, no shadow, no motion blur, no text, no watermark.
```

角度：0°（正面）、45°（右前）、90°（右侧）、135°（右后）、180°（背面）、
225°（左后）、270°（左侧）、315°（左前）。保存 `dance/01.png .. 08.png`。

**如果 GPT 每次背面都不一致**：只做方案 A，或者用 3D 人偶/SD 的 ControlNet 先定姿势。
也可以只做 0°、90°、180°、270° 四个角度，中间帧靠视频插帧，但会有轻微跳变。

---

## 阶段 3：圈圈 / 星星特效

角色图里不要画圈，单独出一张发光特效，后期叠在脚下。

```text
Create a separate image: a glowing blue magic circle on the floor, matching a front 3/4
camera angle, flat on the ground, thin luminous lines, soft blue glow, on a pure black
background, no character, no text, high quality.
```

- 黑色背景适合**滤色（Screen）**叠加；白色背景适合正片叠底/抠图。
- 星星/粒子：

```text
Create a separate image: a trail of small glowing blue sparkles and stars, pure black
background, no character, no text, soft glow, high quality.
```

保存 `effects/circle.png`、`effects/sparkles.png`。需要逐帧动画时，让 GPT 生成 4–6 个
不同形状的圆/星星，或后期做旋转/缩放。

---

## 阶段 4：中间帧与节奏

### 只用 GPT（有限动画）

- 直接用 6–8 张关键姿势，`frameMs` 设 120–160 ms，动作会像动画的“关键帧 + 停顿”，
  但可读、可爱。
- 想要更顺，让 GPT 在相邻姿势之间再生成 1–2 张中间姿势（仍是编辑同一张参考图），
  做到 12–16 帧，`frameMs` 90–110 ms。

### GPT + AI 视频 / 插帧（更顺）

- 用首帧姿势做 **image-to-video**（Kling / Runway / Veo / Pika / 即梦），锁相机、白底、
  全身，生成 3–5 秒，导出 12–24 fps，再抽 12–16 帧。
- 或对关键姿势用 **RIFE / FILM** 插帧（ComfyUI 或独立工具）。
- 插帧只适合相邻姿势差别小的情况；跨度太大（比如 0°→90°）会糊手/尾巴，改用 AI 视频
  或再加中间关键姿势。
- 视频提示词：

```text
Locked camera, full body, same character as the reference image, the chibi anime
whale-maid crouches down and draws a glowing blue circle on the floor with her index
finger, then stands up and smiles at the viewer. Smooth 2D anime animation, plain pure
white background, no camera movement, no cuts, no text, seamless loop.
```

转圈版把动作换成：

```text
the chibi anime whale-maid spins in place 360 degrees, arms out, skirt and whale tail
flaring, happy smile
```

---

## 阶段 5：交付给我

放到仓库的 `assets/` 下，按下面命名：

```
assets/
  ref/front.png  side.png  back.png
  draw-circle/01.png .. 06.png
  dance/01.png .. 08.png
  effects/circle.png  sparkles.png
```

要求：

- 1024 × 1536 或 1024 × 1494，全身、白底、无阴影、无文字；
- 同一动作的所有帧角色高度/脚底线一致；
- 不要裁掉尾巴、脚、手指；
- 文件按顺序编号，不缺帧。

我拿到后会：抠图 → 对齐/统一比例 → 压成 496 × 724 WebP → 加 `draw-circle` /
`dance` 轨道 → 生成预览 → 更新 `pet.json`。

---

## ChatGPT 操作技巧

- **一个动作一个会话**，先上传参考图，之后一直用 “Edit the attached image”。
- 每次强调 **“keep everything exactly the same, only change the pose”**。
- 要 **一张图**，不要让它画多格 sprite sheet；多格之间会换衣服/换比例。
- 它加了地板/阴影/圈圈就说 “remove the floor/shadow/circle, keep the character only”。
- 它改了尾巴/围裙/蝴蝶结就说 “restore the reference tail/outfit exactly”。
- 画布比例：让它出 1024×1536；如果只有方形，留白也行，后期裁/补。
- 透明底：ChatGPT 一般给白底，没关系，我们抠；如果用 API，可以请求透明背景。
- 手：明确 “one index finger extended, the other fingers curled, no extra fingers”。
- 表情：整段统一闭眼笑；要睁眼就整段都睁眼，不要一半闭一半睁。
- **GPT 不肯蹲/转身**：再上传一张火柴人或 3D 人偶的姿势参考，说
  “match the body pose in the second image, keep the character and outfit from the first image”。
- **减少漂移**：每接受一张，就用「上一张 + canonical 正面」一起当下一张的参考；
  不要每次都只用最初那张，也不要连续十几张只参考上一张。
- **白底**：要 “plain solid white background, not a checkerboard, not a transparent grid”；
   checkerboard 会被画进图里。
- **它拒绝/改角色**：把描述改成 “original chibi whale-maid”，不要提具体作品名或 IP；
  参考图仍然可以上传。
- **用 API**：如果走 OpenAI 图像 API，优先请求 1024×1536、高质量、透明背景（如果当前模型支持）；
  编辑时仍然要传参考图，并保留同样的 “keep everything, only change the pose” 指令。

---

## 什么时候换别的 AI

| 需求 | 工具 | 原因 |
|---|---|---|
| 精确姿势/四肢 | Stable Diffusion / ComfyUI + ControlNet OpenPose / DW Pose | 用骨架直接控制，比文字描述准 |
| 多帧角色一致性 | Midjourney `--cref`、SD IP-Adapter | 身份锁定更强 |
| 360° 背面/侧面 | 3D 人偶 / Blender / SD + 三视图参考 | GPT 容易每帧重编背面 |
| 中间帧/动画 | Kling / Runway / Veo / Pika / 即梦；RIFE / FILM | GPT 不做时间连续 |
| 抠图/透明 | rembg / 我们现有的抠图脚本 | 稳定 |
| 放大/修细节 | Topaz / Real-ESRGAN | 提高分辨率 |

**建议**：GPT 负责角色设定、关键姿势和特效；如果姿势总是不准，再用 SD + ControlNet
补那几张；中间帧交给视频模型或 RIFE。这样不需要换掉整个工作流。

---

## 接进插件

具体 manifest 片段和触摸区/模式示例见
[ASSET_PROMPTS.md](ASSET_PROMPTS.md) 的「接入插件」一节。要点：

- `draw-circle`：非循环，`fallback: "idle"`，用 `gameplay.touch` 最下面的 `floor` 区域触发，
  `stateMs` ≤ 10000 ms。
- `dance`：循环轨道，加到 `gameplay.modes.dance`，玩法卡片里出现「跳舞」按钮，
  点宠物退出。
- 触摸区只有 y 轴切片；要做「点尾巴 vs 点身体」需要改插件。
- 每条轨道最多 64 帧，单帧 16–5000 ms。

## 版权

新素材仍然是对同一个参考图/角色的衍生，[NOTICE.md](../NOTICE.md) 和 README 末尾的
来源声明同样适用；公开或商用前请确认上游权利。

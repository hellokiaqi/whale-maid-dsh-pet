# 复杂动作的素材与提示词

这份文档给「蹲下画圈圈」「转圈跳舞」这类**超出单张立绘形变能力**的动作准备素材。
现有 10 条轨道都是把同一张图做网格变形，能做呼吸、摇尾、歪头、下沉、小跳；
蹲下、手指画圈、360° 转圈会改变四肢/视角/背面，必须有新图。

> 提示词用英文写，主流图像模型对英文更稳；中文是说明和检查清单。
>
> **主用 GPT / ChatGPT 的话，先看 [GPT_WORKFLOW.md](GPT_WORKFLOW.md)**：
> 按阶段给了可直接复制的编辑提示词、关键姿势表和交付清单。

## 一、先做一张角色设定图

所有动作都靠它锁角色。先生成 **front / 3/4 / side / back** 四视图，挑最一致的一张，
后面每个姿势都把它当**角色参考图**（Midjourney `--cref`、SD 的 IP-Adapter / 角色参考、
即梦/Seedream 的角色参考、Nano Banana 的多图参考等）。

### 角色锁定块（每条提示词都带上）

```text
masterpiece, best quality, chibi anime style, 2.5 heads tall, cute chibi whale-maid girl,
same character as the reference image, long wavy deep-blue hair with light-blue gradient tips,
ahoge, large blue eyes, happy closed-eye smile (eyes closed in a happy arc), soft blush,
white frilled maid headdress, blue ribbon bows, blue whale-fin ear ornaments,
navy-blue and white frilled maid dress, white ruffled apron, blue bows on the chest and waist,
white thigh-high stockings with blue bows, navy-blue Mary Jane platform shoes,
large blue whale tail with a pale underside, tail always visible,
soft cel shading, clean lineart, high detail, full body, front 3/4 view, standing,
plain pure white background, no shadow, no text, no watermark
```

### 负面提示词

```text
extra characters, multiple tails, missing whale tail, human ears, wrong hair color,
wrong outfit, realistic, 3D render, photorealistic, complex background, floor,
cast shadow, cropped, out of frame, text, watermark, signature, logo, low quality,
blurry, deformed hands, extra fingers, extra limbs, bad anatomy,
inconsistent proportions, motion blur
```

> 画圈动作的角色帧再加：`magic circle, sparkles, floor markings`（圈圈用单独特效层，见下）。

### 四视图设定图

```text
character model sheet of the same chibi whale-maid, four views in a row:
front view, 3/4 front view, side view, back view, neutral standing pose,
arms relaxed at the sides, same scale, full body, plain pure white background,
no shadow, no text, no labels, no watermark, clean lineart, soft cel shading
```

背面单独补一张（360° 转圈必须用）：

```text
back view of the same chibi whale-maid, seen from behind, long blue hair covering the back,
back of the navy maid dress with white apron ties and blue bows, large blue whale tail
attached at the lower back, standing, full body, plain pure white background, no shadow
```

**检查点**：尾巴、蓝色鱼鳍耳饰、白色围裙、蓝色蝴蝶结、过膝袜、玛丽珍鞋都要在；
背面要有尾巴和围裙系带。AI 很容易漏尾巴，逐张检查。

> 当前立绘是**闭眼笑**。新动作建议整段保持闭眼笑；如果某个动作需要睁眼
> （比如低头看地面、惊讶），先用参考图单独定一张睁眼脸，整段统一使用，不要一半闭一半睁。

## 二、动作 A：蹲下画圈圈

### 需要的关键姿势（6–8 张）

1. 站立，低头看地面，手自然下垂，尾巴在身后。
2. 蹲下，膝盖弯曲，一只手伸向地面，食指快要碰到地面，另一只手扶膝，裙摆铺开，尾巴卷向一侧。
3. 蹲低，食指在地面画弧线，手臂伸展，头低着看地面，闭眼笑，尾巴摆动。
4. 蹲着，手指到弧线另一端，看着地面，尾巴抬起。
5. 蹲着，抬头看镜头，笑，手指还停在地面。
6. 站起来，双手在身前交握，开心。

每条提示词 = **角色锁定块 + 下面这句姿势 + 镜头/背景约束**：

```text
same character as the reference image, same proportions and outfit, [POSE],
front 3/4 view, same camera height, same ground line, same scale, full body,
plain pure white background, no shadow, no magic circle, no sparkles,
no floor markings, no text, no watermark
```

把 `[POSE]` 换成：

```text
standing, looking down at the floor, hands at her sides, tail hanging behind
```

```text
crouching down, heels together, knees bent, skirt spread around her, feet visible,
one hand reaching toward the floor, index finger about to touch the floor,
other hand on her knee, tail curled to the side
```

```text
crouching low, heels together, knees bent, skirt spread, feet visible,
drawing an arc on the floor with her index finger, one index finger
extended and the other fingers curled, arm extended, head tilted down,
happy closed-eye smile, tail swishing
```

```text
crouching, finger at the other side of the arc, looking at the floor, tail up
```

```text
crouching, looking up at the viewer, happy smile, finger still touching the floor
```

```text
standing back up, hands clasped in front, happy smile
```

### 圈圈特效

不要在角色图里让 AI 画圈，否则每帧形状都不一样。单独生成一张/一组发光圈，
后期叠在角色脚下：

```text
a glowing blue magic circle on the floor, matching a front 3/4 camera angle,
flat on the ground, thin luminous lines, soft blue glow, transparent background,
no character, no text, high quality
```

或者用蓝色星星/粒子拖尾：

```text
a trail of small glowing blue sparkles and stars, transparent background,
no character, no text, soft glow
```

## 三、动作 B：转圈跳舞

### 方案 1：正面原地转圈（不需要背面，先做这个）

角色始终面向镜头，只做身体倾斜 + 裙摆/尾巴甩动 + 手臂展开。6–8 个关键姿势：

1. 站立，手臂微张。
2. 手臂展开，身体向左倾，裙摆开始外扩，尾巴向右甩。
3. 身体向左转约 15°，裙摆继续外扩，尾巴甩到右侧。
4. 手臂上举，身体回正，裙摆完全展开，尾巴向上。
5. 身体向右倾，裙摆外扩，尾巴向左甩。
6. 回到正面，手臂放下，裙摆收拢。

提示词：

```text
[POSE], front-facing twirl dance, arms outstretched, skirt flaring outward,
whale tail swinging, happy closed-eye smile, full body, same camera, same center,
pure white background, no shadow, no motion blur, no text
```

`[POSE]` 示例：

```text
body tilted to the left, arms out, skirt flaring, tail swinging to the right
```

```text
body upright, arms raised, skirt fully flared, tail lifted
```

```text
body tilted to the right, arms out, skirt flaring, tail swinging to the left
```

### 方案 2：完整 360° 转圈（需要背面）

需要 8 个角度：正面 0° → 右前 45° → 右侧 90° → 右后 135° → 背面 180° →
左后 225° → 左侧 270° → 左前 315° → 回到正面 360°。

每帧提示词：

```text
frame [N] of 8 of a clockwise 360-degree spin, body rotated [X] degrees,
arms out, skirt flaring, whale tail swinging, same character, same center,
same height, full body, plain pure white background, no shadow, no motion blur,
no text, no watermark
```

- 0°/360°：正面
- 45°：右前 3/4
- 90°：右侧
- 135°：右后 3/4
- 180°：背面
- 225°：左后 3/4
- 270°：左侧
- 315°：左前 3/4

**必须用四视图里的背面/侧面做参考图**，否则每帧的后背和尾巴都会乱编。

### 方案 3：用 AI 视频补中间帧

图像模型只出关键姿势，中间帧用 AI 视频（Kling / Runway / Veo / Sora / Pika / 即梦）
或 RIFE / FILM 插帧。视频提示词：

```text
locked camera, full body, same character as the reference image,
the chibi anime whale-maid crouches down and draws a glowing blue circle on the floor
with her index finger, then stands up and smiles at the viewer, smooth 2D anime animation,
plain pure white background, no camera movement, no cuts, no text, seamless loop
```

转圈版：

```text
locked camera, full body, same character as the reference image,
the chibi anime whale-maid spins in place 360 degrees, arms out, skirt and whale tail
flaring, happy smile, plain pure white background, smooth 2D anime animation,
seamless loop
```

导出 12–24 fps，隔帧抽取；检查每帧的尾巴、手、裙摆是否连贯。

## 四、其他可选动作

| 动作 | 关键姿势 | 备注 |
|---|---|---:|
| 挥手 | 6–8 | 手部最容易崩，建议单独练一张手 |
| 伸懒腰 | 8 | 手臂上举、身体拉长 |
| 睡觉 | 8 | 低头、尾巴卷起；Zzz 用特效层 |
| 打字/工作 | 8 | 需要桌子/电脑道具，建议单独一套 |
| 害羞捂脸 | 8 | 双手贴脸，手部难度高 |

## 五、一致性与交付规格

### 工作流

1. 生成四视图设定图，选最一致的一张；抠成透明底。
2. 每个动作先用**角色参考图 + 姿势参考**（OpenPose / DW Pose / 3D 人偶）生成关键姿势；
   同 seed、同比例、同镜头。
3. 不要直接让模型画整张 sprite sheet——格子之间很容易换衣服/换比例。
4. 关键姿势用 RIFE / FILM 或 AI 视频补中间帧。
5. 逐帧检查：尾巴、鱼鳍耳饰、围裙、蝴蝶结、鞋、手指。
6. 纯白/纯绿背景出图，后期抠图；不要地板和投影，阴影单独加。
7. 对齐脚底线和头高；缩放到 **496 × 724**，透明 WebP。

### 画布

- 建议 1024 × 1536（2:3）或 1024 × 1494（接近最终 496×724 的比例）。
- 全身完整、四周留 5% 边距；脚底在同一条水平线上；不要裁切。
- 角色高度保持一致：头顶约在画面 5%，脚底约在 95%。

### 交付目录

```
assets/
  character-sheet.png
  draw-circle/01.png .. 06.png
  dance/01.png .. 08.png
  effect/circle-01.png .. 08.png   # 可选
```

### 交付前检查

- [ ] 四视图有正面、3/4、侧面、背面；尾巴和鱼鳍耳饰都在
- [ ] 所有帧同一画布、同一角色高度、同一脚底线
- [ ] 每帧都有鲸鱼尾巴、白围裙、蓝蝴蝶结、过膝袜
- [ ] 角色帧里没有画圈/星星/地面痕迹（特效单独一层）
- [ ] 背景是纯白/纯绿，没有地板和投影
- [ ] 手指数对、手指没有粘在一起、尾巴没有断
- [ ] 文件命名连续（01、02…），没有缺帧

## 六、接入插件

在 `pet/pet.json` 里加轨道：

```json
"tracks": {
  "draw-circle": {
    "frames": ["01.png", "02.png", "03.png", "04.png", "05.png", "06.png"],
    "frameMs": [90, 90, 90, 90, 90, 90],
    "loop": false,
    "fallback": "idle"
  },
  "dance": {
    "frames": ["01.png", "02.png", "03.png", "04.png", "05.png", "06.png"],
    "frameMs": [80, 80, 80, 80, 80, 80],
    "loop": true
  }
}
```

触发方式：

- **蹲下画圈**：加到 `gameplay.touch.zones` 最下面的区域（脚/地面），
  `state: "draw-circle"`，`stateMs` 设为整段时长（≤10000 ms）。触摸区只有纵向切片，
  所以地面动作放最下面最自然。例如把原来的 `legs` 区域拆成两段：

```json
"zones": [
  { "name": "legs", "y0": 0.72, "y1": 0.85, "branches": [ ... ] },
  { "name": "floor", "y0": 0.85, "y1": 1, "branches": [
    { "probability": 1, "state": "draw-circle", "stateMs": 900,
      "phrases": ["画个圈圈～", "看，是鲸鱼圈！"] }
  ] }
]
```
- **转圈跳舞**：加到 `gameplay.modes`，玩法卡片里会多一个「跳舞」按钮：

```json
"modes": {
  "dance": { "state": "dance", "label": "跳舞", "activeLabel": "跳舞中" }
}
```

  模式会一直保持，点宠物或再点按钮退出。比 `stateMs` 更适合长循环。

限制提醒：

- 每条轨道最多 64 帧，单帧 16–5000 ms；`stateMs` 最大 10000 ms。
- 触摸区只按 y 轴切；要做「点尾巴 vs 点身体」的 x 轴区分，需要改插件。
- 圈圈/星星/汗滴这类特效建议单独一层合成，不要依赖每帧 AI 画对。

## 七、版权

新素材仍然是对同一个参考图/角色的衍生，[NOTICE.md](../NOTICE.md) 和 README 末尾的
来源声明同样适用；公开或商用前请确认上游权利。

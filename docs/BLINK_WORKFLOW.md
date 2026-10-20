# 眨眼动画：睁眼版素材与接入方案

## 先理解一个关键点

现在这张立绘是**闭眼笑**。眨眼不是“加一个闭眼动作”，而是：

> 大部分时间**睁眼**，每 4–6 秒快速闭一下。

所以不能只做一条 `blink` 轨道在闭眼默认上播；否则宠物平时闭眼，眨眼时反而“睁眼”，
而且整帧切换会让身体/头发/衣服闪一下。

推荐做法：

1. 生成一张**睁眼版** `base-open.png`，姿势、画布、服装、光线和现在完全一样；
2. 让睁眼版成为新的默认底图，所有轨道都用它；
3. 原来的闭眼版只保留给眨眼的 1–2 帧；
4. 眨眼烘焙进待机循环（48 帧 / 4.8 秒），而不是单独一条随机轨道。

如果只想要“偶尔眨一下”的简单版，也可以做一条 `blink` 轨道，但身体姿势要刚好在
neutral 待机帧，否则会跳；详见最后。

---

## 需要生成的图

| 文件 | 用途 | 必需 |
|---|---|---|
| `source/base-open.png` | 睁眼默认底图 | 是 |
| `source/base-half.png` | 半闭眼，眨眼中间帧 | 推荐 |
| `source/base-wink.png` | 单眼 wink，交互动作 | 可选 |

统一 1024 × 1536、纯白底、全身、同一姿势/同一画布。可以用
[`templates/frame-guide.png`](templates/frame-guide.png) 当构图参考。

---

## 提示词：睁眼版

```text
Edit the attached image. Keep the pose, body, hair, ahoge, white frilled headdress,
blue whale-fin ear ornaments, navy and white maid dress, white apron, blue bows,
white thigh-high stockings, navy Mary Jane shoes, blue whale tail, colors, lighting,
camera angle, scale, crop, and plain white background exactly the same.
Only change the eyes: from the closed happy arcs to large open anime eyes.
Blue iris with a darker blue upper gradient and a lighter lower rim, dark upper lash line,
two white catchlights, soft lower lid, same friendly happy expression.
Keep the open-mouth smile, blush, eyebrows, face shape, hair, and outfit unchanged.
Do not restyle, do not make it realistic. No text, no watermark, no shadow, no floor.
```

负面：

```text
different pose, different outfit, different hair, changed mouth, changed face shape,
changed blush, realistic eyes, 3D render, extra eyelashes, text, watermark, shadow,
floor, cropped, different art style
```

- 想要金色/红色眼睛，把 `Blue iris...` 换成对应颜色；整段保持一致。
- 如果 GPT 把脸/嘴也改了：追加
  `Keep the mouth, blush, face outline, hair, and body pixel-identical; only change the eye area.`
- 如果它把眼睛画得太写实：追加 `anime eyes, flat cel shading, no realistic iris texture`。
- 如果它把闭眼弧线留了一半：追加 `remove the closed-eye arcs completely; the eyes are fully open`。

保存 `source/base-open.png`，并保留原来的 `source/base.png`（闭眼版）。

---

## 提示词：半闭眼（眨眼中间帧）

用**睁眼版**当参考图，不要用闭眼版：

```text
Edit the attached open-eye image. Keep the pose, body, hair, outfit, smile, blush,
face shape, colors, camera, scale, crop, and plain white background exactly the same.
Only lower the upper eyelids halfway so the eyes are half-closed; the irises are
partially visible, the lower eyelids and lashes stay the same.
Do not close the eyes completely. Do not change the mouth or face shape.
No text, no watermark, no shadow, no floor.
```

保存 `source/base-half.png`。如果 GPT 画不好半闭，也可以只做“睁眼 → 闭眼 → 睁眼”
两帧，眨眼会更快、更干脆。

---

## 提示词：单眼 wink（可选）

```text
Edit the attached open-eye image. Keep the pose, body, hair, outfit, smile, blush,
face shape, colors, camera, scale, crop, and plain white background exactly the same.
Only close the character's right eye (viewer's left) in a happy arc and keep the left eye
open, as a playful wink. Do not change the mouth or the rest of the face.
No text, no watermark, no shadow, no floor.
```

左右反了就让 GPT 换另一只眼，或后期水平翻转眼睛区域。

---

## 怎么接成眨眼

### 方案 A：烘焙进待机（推荐）

把 idle 从 24 帧扩成 **48 帧 / 4.8 秒**：

- 第 1–31 帧：睁眼，100 ms/帧（3.1 秒）
- 第 32 帧：半闭，40 ms
- 第 33 帧：闭眼，60–80 ms
- 第 34 帧：半闭，40 ms
- 第 35–48 帧：睁眼，100 ms（1.4 秒）

生成时对 `base-open`、`base-half`、`base` 用**同一组 warp 参数**逐帧变形，所以身体、
头发、衣服完全对齐，只有眼睛状态不同。眨眼发生在待机循环的固定位置，不需要额外轨道。

- 4.8 秒眨一次对卡通宠物刚好；人类大约 4–6 秒一次。
- 如果觉得太频繁，用 60 帧 / 6 秒或 72 帧 / 7.2 秒，眨眼点放在 2/3 处。
- 帧数增加后 idle 文件会变大（48 帧约 4–5 MB），但仍在插件预算内。

### 方案 B：单独 `blink` 轨道（简单但不推荐）

5 帧：睁眼 → 半闭 → 闭眼 → 半闭 → 睁眼，每帧 40–80 ms，非循环，fallback `idle`。
挂到 `gameplay.idleDirector.acts`，让它偶尔播。

问题：触发时待机可能停在呼吸/摇尾的任意相位，而 blink 轨道从 neutral 开始，身体会跳一下；
如果身体差异明显，看起来像闪帧。只有在待机是 neutral 静止时才自然。

**结论**：认真做眨眼就用方案 A；只想试一下可以先用 B。

---

## 为什么不能直接“睁眼帧/闭眼帧”整帧切换

如果睁眼版和闭眼版是两次独立生成，身体、头发、衣服会有细微差异；整帧切换会闪。
正确做法是**只取眼睛区域**：

1. 把 `base-open` 对齐到 `base`（同画布、同头位；必要时平移/微缩放）。
2. 在眼睛周围做一个柔边椭圆 mask（覆盖双眼、眉毛下方，不碰鼻子/嘴）。
3. 把 `base-open` 的眼睛区域贴回 `base`，得到“身体完全不动、只有眼睛睁开”的底图。
4. 半闭帧同理（用 `base-half` 的眼睛区域）。
5. 再对这三张底图做同一组 warp，生成 48 帧 idle。

这样身体像素完全一致，眨眼不会跳。眼睛区域的 mask 和颜色匹配我来做。

---

## 交付给我

```
source/base.png        # 现有闭眼版
source/base-open.png   # 睁眼版
source/base-half.png   # 半闭（可选）
source/base-wink.png   # wink（可选）
```

要求：1024 × 1536、纯白底、全身、同姿势/同画布/同头位；不要裁切；不要阴影/文字。
我拿到后会：对齐 → 眼睛 mask 合成 → 重生成全部轨道（睁眼为默认）→ 做 48 帧眨眼 idle
→ 预览 GIF → 更新 `pet.json`。

## 注意

- 睁眼版会成为**新默认**，所有动作轨道都会重生成；先确认眼睛颜色/形状/大小满意，再批量做。
- GPT 很难做到像素级一致，所以“只取眼睛区域”是必须的，不要整帧切换。
- 新素材仍然是对同一参考图/角色的衍生，[NOTICE.md](../NOTICE.md) 同样适用。

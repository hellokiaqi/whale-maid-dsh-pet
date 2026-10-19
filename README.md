# 蓝白鲸尾女仆 · DSH 桌宠

一只给 [DeepSeek Harness](https://github.com/deepseek-ai) 的 `@linxin666/dsh-pet` 插件用的自定义宠物。
单张立绘做成的 `frames2d` 动画桌宠：24 帧待机循环 + 11 帧完成小跳。

![待机循环](pet/previews/idle.gif)

![完成小跳](pet/previews/hop.gif)

## 这是什么

- 宠物 id：`whale-maid`
- 清单：`pet/pet.json`（manifest v2，`renderer: frames2d`）
- 待机：`pet/idle/01..24.webp`，100 ms/帧，2.4 秒循环
- 完成：`pet/hop/01..11.webp`，70 ms/帧，0.77 秒，播放一次后回到待机
- 帧规格：586 × 884 透明 WebP，共 35 帧
- 默认显示：210 px 高（可在 设置 → 宠物 调整）

## 一键导入

要求：已安装 DSH Desktop（或 `dsh web`）并装有 `@linxin666/dsh-pet` 插件。
Windows 上用 Windows PowerShell 5.1 或 PowerShell 7+ 都可以。

```powershell
git clone <this-repo-url> whale-maid-dsh-pet
powershell -NoProfile -ExecutionPolicy Bypass -File .\whale-maid-dsh-pet\scripts\install.ps1
```

脚本会：

1. 自动找 `$env:DSH_HOME`，找不到再找 `%USERPROFILE%\.dsh-beta` / `%USERPROFILE%\.dsh`；
2. 把 `pet/` 复制到 `$DSH_HOME\pets\whale-maid\`；
3. 打印帧数、目标路径和下一步。

然后 **重启 DSH Desktop**（右键托盘图标 → 重启 DSH Desktop），在 **设置 → 宠物** 里选择「蓝白鲸尾女仆」。

想顺便把默认宠物改成它：

```powershell
cd whale-maid-dsh-pet
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\install.ps1 -Select
```

`-Select` 只会改 `profiles\desktop\cordis.patch.yml` 里 `- id: pet` 这一段的 `petId`；如果找不到这一段，就跳过，仍然可以在设置里手动选。

macOS / Linux（DSH 的 home 一般是 `~/.dsh`）：

```bash
git clone <this-repo-url> whale-maid-dsh-pet
bash whale-maid-dsh-pet/scripts/install.sh
```

## 更新

```powershell
cd whale-maid-dsh-pet
git pull
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\install.ps1
```

重启 DSH Desktop 即可。宠物 id 不变，之前的选择和亲密度都会保留。

## 传到 GitHub

这是一个普通文件夹，没有内嵌 `.git`。在仓库目录里初始化后推上去即可：

```bash
cd whale-maid-dsh-pet
git init
git add .
git commit -m "Add whale-maid DSH animated pet"
git branch -M main
git remote add origin https://github.com/<you>/<repo>.git
git push -u origin main
```

推送后 `.github/workflows/verify.yml` 会自动在 GitHub Actions 里跑一次清单/帧校验。
公开前请先看 [NOTICE.md](NOTICE.md) 里的素材授权说明。

## 手动导入

不跑脚本也可以，直接把仓库的 `pet/` 目录整个复制过去：

```
%DSH_HOME%\pets\whale-maid\
  pet.json
  idle\01..24.webp
  hop\01..11.webp
```

`pet/previews/` 只是给仓库和设置页看的，插件不会把它当作动画帧；手动导入时可以不要。

## 目录结构

```
whale-maid-dsh-pet/
├── pet/                 # 宠物包本体（复制这一层到 $DSH_HOME/pets/whale-maid）
│   ├── pet.json
│   ├── idle/            # 24 帧待机
│   ├── hop/             # 11 帧完成小跳
│   └── previews/        # README / 预览用 GIF
├── source/
│   └── base.png         # 1022×1550 透明底图，可替换后重新生成
├── tools/
│   └── animate.py       # 生成 idle / hop 的网格变形脚本（Python + Pillow + numpy）
├── scripts/
│   ├── install.ps1
│   ├── install.sh
│   └── verify.mjs       # 不依赖插件内部代码的清单/帧校验
├── docs/
│   └── ANIMATION.md     # 帧、轨道、速度、相位的说明
├── .github/workflows/
│   └── verify.yml       # push 时跑一次 verify
├── NOTICE.md            # 素材来源与授权说明
└── LICENSE              # 脚本/文档 MIT（素材不含）
```

## 兼容性

- 清单版本：`petManifestVersion: 2`
- 渲染器：`frames2d`
- 在 `@linxin666/dsh-pet` 0.4.7 + DSH Desktop Beta 2.0.18 上验证
- 插件契约变化时：改 `pet/pet.json`，然后跑 `node scripts/verify.mjs`

## 自定义

- **换速度**：改 `pet/pet.json` 里 `idle` 的 `frameMs`（16–5000 ms）。
- **换动作**：替换 `pet/idle/` 或 `pet/hop/` 的帧，保持文件名和数量，或在 `frames` 列表里改。
- **加状态**：在 `frames2d.phases` 里把 `waiting` / `thinking` / `review` / `done` / `failed` 映射到已有轨道。
- **改幅度/重新生成**：改 `tools/animate.py` 顶部的振幅、帧数、时长，然后：

```bash
python tools/animate.py
node scripts/verify.mjs
```

更多说明见 [docs/ANIMATION.md](docs/ANIMATION.md)。

## 授权

- 脚本、文档：MIT（见 [LICENSE](LICENSE)）
- 宠物图像（`pet/idle`、`pet/hop`、`source/base.png`、`pet/previews`）：个人使用（`personal-use`），来源与再分发限制见 [NOTICE.md](NOTICE.md)。**如果要公开这个仓库，请先确认你对原立绘拥有再分发权利，或把素材换成你有权的图。**

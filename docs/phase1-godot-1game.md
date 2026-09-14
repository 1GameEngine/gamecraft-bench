# GameCraft-Bench 第一期：Godot × 1Game 分数对比方案

状态：设计冻结（尚未改评测代码）。  
依据：仓库现状 + 已安装并通读的 `@1game/skill@1.21.0`（hub / create / core / debug / api / physics / e2e）。  
目标：在**同一批玩法规格、同一套 hidden rubric、同一套 VLM judge** 下，产出 Godot vs 1Game 的可比分数表。不是把 140 题全部引擎无关化。

本文综合四路并行设计（verifier 运行时、任务/rubric 信封、sandbox 实验协议、家族能力偏差），并收口冲突点。

---

## 1. 读完 1Game skill 之后，和本仓库真正对得上的点

1Game **不是**「另一个 Godot」。它是：

| 层 | 事实（skill 真值） | 对评测的含义 |
|---|---|---|
| 运行时 | `@1game/engine-bundle`：Worker 内 JSX DSL + `createGameStore` / `renderGame` / `bindStore`；禁止 `window`/`document` | 产物是 `src/game.tsx` 工程，不是 `project.godot` |
| 绘制 | 公开路径只有 Canvas 2D；不支持 3D / Three.js / 未公开 WebGL 包 | 与 GameCraft「2D」主张对齐；开放世界光影/假 3D 任务不要进主表 |
| 构建 | `1game init` / `1game build`（默认 `out/index.html` single-file）；cli 与 engine-bundle **版本字符串必须一致** | BUILD 门闩是 bundle + 能跑，不是 tsc |
| 无头 | `1gameplay create/step/query`；`frame screenshot` 走 Node `@napi-rs/canvas`，**不需要 Chromium** | 第一期 **不要** 用 Xvfb 去抓 HTML 回放页 |
| 输入 | `--click` / `keypress` / `pointer.*` / `keyboard`；坐标是 **scene 空间**（含 `viewportX/Y`），不是截图像素 | 与 xdotool 像素点击不是同一物理；应用约定把 scene 做成 1280×720 且无镜头偏移的标题屏，使 JSON 坐标两边同义 |
| 命中 | 须先 `hit:point`；`<scene clickable>` ≠ 空白可点 | instruction 要求可点底板；verifier **不**自动改坐标（与 Godot 点空仍送达保持同语义） |
| 回放 | 权威时间线是确定性 tick + `.1gamerecord`；默认单分支 | Agent **仍交** `demo_outputs/*.json`；`.1gamerecord` 只作内部产物 |
| 场景启动 | **没有** `godot -- --scenario` | 每条 demo 由 verifier 生成 `src/gamecraft-scenario.ts`（`GAMECRAFT_SCENARIO`），游戏启动时读入 store |
| 技能 | `@1game/skill` 是流程文档，**不是** API | Agent 沙箱要全量 activate；judge 不得依赖 skill |
| 物理 | Rapier 可选，从 `runtime/physics` 按需 import | 平台跳跃/竞速可做，但是 Godot 主场，只作附录压力题 |
| 模板尺寸 | 官方模板 scene 常为 320×180 | **禁止**原样送审；第一期强制根 `<scene width={1280} height={720}>` |
| 回放页 HUD | `?mode=userplay` 时视口右上有暂停 DOM | 评分不走回放 HTML；试玩页用 `1game build` 的 `out/index.html` |

本仓库已经相对引擎无关的部分：`score.py` 的 BUILD → 回放 → 抽帧 → VLM → `score_formula`。  
仍然绑死 Godot 的部分：`replay.py`、judge 文案里的 “Godot 2D game”、140 份 instruction 样板、`rubric.json` 的 `build_check` 与 ColorRect 措辞、Dashboard 的 Godot+VNC。

---

## 2. 第一期成功标准

能发表一张表，且表头诚实：

- 行：冻结的任务子集（slug 对齐）
- 列：Godot 4.6.2 vs 1Game（钉死的 `@1game/*` semver，与 skill 同批）
- 单元格：Overall（官方公式）、M/D/V/A、`BUILD_rate`、replay 失败率、token
- 标注：`skill_policy = ecological`（见 §7）

**不算成功：** 只改 instruction 里的引擎名；用 13 道 1Game 均分去对 README 里 140 题 65.7%；A 类美术分被当成引擎画质排名。

Godot 默认 CLI / 现有 140 题路径 **byte-compatible**：不加 `--engine` 时产物路径、`ReplayResult` 字段名、`reward.txt` 形状不变。

---

## 3. 架构收口（运行时）

### 3.1 `EngineRuntime`

```
EngineRuntime.detect / replay_trace
  GodotRuntime   ← 现 replay.py 整段搬迁，行为不变
  OneGameRuntime ← 1gameplay 同源 Node 会话 + napi 截图 + ffmpeg 合成 mp4
```

`score_project` 只换 `engine.replay_trace`；`_sample_frames` 与 judge 请求形状不动。  
`resolve_engine`：`project.godot` 优先 Godot；否则 `src/game.tsx` / `@1game/engine-bundle` → 1Game；CLI `--engine auto|godot|1game`，默认 auto。

`ReplayResult.godot_returncode` **第一期不改名**（1Game 写入 create/step 退出码），避免 breakdown 调用方破裂。`breakdown.json` **追加** `engine` 字段。

### 3.2 1Game 画面路径（唯一）

**只用** `1gameplay` / `@1game/test` 同源 canvas 截图，再 ffmpeg 合成 30fps mp4（854×480），再走现有 `_sample_frames`。

明确禁止：Xvfb 抓 `replay.html`、Chromium/Playwright、agent 提交 `.1gamerecord` 当 demo、对每帧 fork 一次 CLI（用常驻 Node 会话）。

热路径：JSON trace → 瞬时 `pointer.down/move/up` 与 `keydown/keyup`（**不用** `--click` 默认 200ms / `keypress` 默认 16ms 宏，以免吃掉逻辑帧）→ 每逻辑帧截 PNG → `libx264`。

几何：

1. Instruction 强制 scene **1280×720**，标题屏 `viewport` = 全 scene（无镜头平移）。此时 GameCraft JSON 的 x/y 与 scene 坐标同义。
2. 截图 `--width 1280 --height 720`（等于 scene），再 lanczos 降到 854×480，与 Godot「1280 抓屏再降 480p」同一 judge 像素预算。
3. **不做** 320↔1280 自动缩放。Agent 若交 320 模板，视为规格失败（A/V 会低，这是正确信号）。

`duration_seconds` 继续用 trace 逻辑时长，不用 Node 墙钟。不要给 1Game 人为加 1.5s Godot settle 黑帧。

### 3.3 BUILD

语义对齐 Godot 的「能加载 + 主循环跑约 5 帧」：

```bash
cd /workspace/game && pnpm install && pnpm exec 1game build \
  && pnpm exec 1gameplay create --entry src/game.tsx --out /tmp/gamecraft-build.1gamerecord \
  && pnpm exec 1gameplay step /tmp/gamecraft-build.1gamerecord --ms 16 --repeat 5
```

- 不要用 `--typecheck` 当门闩。
- 不要只用 `1game build`（会漏运行时挂死，和 Godot BUILD=0 不对齐）。
- `pnpm install` 必须走离线 store；store 未命中记 **`INFRA`**，不进「游戏不会做」的 BUILD=0 统计。
- 1Game rubric `timeout_seconds` 建议 300；Godot 保持 60。
- `_run_build_check` 增加 `cwd=project_dir`。

### 3.4 Scenario

Verifier 在每条 demo 的 `create` 前写入（gitignore 生成物）：

```ts
// src/gamecraft-scenario.ts
export const GAMECRAFT_SCENARIO: string | null = "near_victory"; // 或 null
```

游戏 `import { GAMECRAFT_SCENARIO } from './gamecraft-scenario'`，非 null 则跳菜单、装入命名局面。Dashboard / 省略 scenario 时写 `null`。  
禁止：伪造 CLI `--scenario`、用 KV 传场景、多 entry 文件。

### 3.5 Trace

Agent **只交** `demo_outputs/*.json`（现有 8 种 type）。keycode 仅在 1Game 侧映射（`LEFT`→`ArrowLeft` 等）。`hit:false` 仍注入事件，由画面体现「没点到」。

### 3.6 Dashboard

Godot：现有 VNC 不动。  
1Game：snapshot 后 `1game build`，本机静态服 + iframe `out/index.html`（不要 replay HTML）。`has_game`：`project.godot` **或** `src/game.tsx`。

### 3.7 环境

Host 预装：Node 20 钉 patch、pnpm 9、预编译 `better-sqlite3` / `esbuild` / `@napi-rs/canvas`、字体（无字体则缺字，A/V 不可比）。  
Sandbox：`HOME` / `PNPM_STORE_DIR` / sqlite 与 canvas 帧走 `/tmp`（FUSE 上 sqlite 易挂）。Watchdog 扩 `1gameplay`，不要杀所有 `node`。

Judge 文案去掉 Godot 专指（否则 1Game 会被模型先验压分）：

- `gamecraft_bench/verifier/judges/_common.py`：`Godot 2D game` → `2D game`
- `openai_gpt.py` 同样改

---

## 4. 任务与文件布局

Harbor 第一期 **分目录**，不用 `--engine` run flag（避免一次改 LocalSubprocessEnvironment + 全套脚本）。

```
tasks/<slug>/                     # 现有 140 题 Godot 真源；全集 instruction 不改
tasks-1game/<slug>/               # 仅子集：已展开的 1Game 任务
  instruction.md                  # 信封 + 共享 spec
  tests/rubric.json               # 共享 requirements + 1Game build_check
  task.toml                       # name = gamecraft-bench/<slug>-1game
                                  # metadata.engine = "1game"
shared/gamecraft/
  specs/<slug>.md                 # Core Vision / Player Experiences（去 Godot 句）
  rubrics/<slug>.requirements.json
  envelopes/1game.md              # 信封真源
```

跑法：

```bash
./scripts/run.sh -p tasks/<slug> --agent …
./scripts/run.sh -p tasks-1game/<slug> --agent …
```

对比键：去掉 `-1game` 后缀对齐 slug。报告 **subset overall**，禁止对 140 题历史总分。

### 4.1 1Game 信封要点

- 必须用 1Game；禁止改 Phaser / 纯 Canvas / Godot（skill「平台冲突」）。
- `/workspace/game` + `src/game.tsx` + `demo_outputs/`。
- `createGameStore` + `bindStore` + `<For>`，禁止 JSX `.map`、禁止 `@1game/engine`。
- 资产：从只读 Kenney/OGA **拷贝**到 `src/assets/` 再 `import`；Worker 不能扫 `/workspace/assets/library`；单文件建议 ≤1MB。
- 调试：`1gameplay`，不用 `screenshot.sh`。
- HUD 可点控件避开视口右上（试玩若将来用回放页）。
- `Math.random()` 默认可；不要为调试全局 seed；仅 named scenario 内 seed。

### 4.2 Rubric

- 同一 `score_formula`、同一 requirement id / 权重 / `agg`。
- **仅子集**的 Godot `rubric.json` 也换成中性 cap（两边正文逐字相同）。140 题全集不动。
- 替换：`ColorRect` → programmatic shapes / solid fills；`default Godot widgets` → unstyled default engine controls；`Godot grey` → unthemed engine-default background。
- 不在共享 rubric 出现 `project.godot` / `Main.tscn` / ColorRect。

---

## 5. 任务子集（主表 vs 附录）

能力结论：1Game 对 **离散规则 + UI 列表 + 经营/卡牌/VN** 公平；对 **连续物理、音频时钟、氛围光、大世界工具链** 系统性利 Godot。

### 主表（9 题，进 Overall）

| slug | 家族 | 备注 |
|---|---|---|
| `puzzle-sokoban-dungeon` | Puzzle | 网格规则 |
| `puzzle-pipe-crisis` | Puzzle | 空间连接 |
| `strategy-kingdom-cards` | Strategy | 卡+策略 |
| `cardgame-autobattler` | Card | 旗舰对照；烟测 oracle 候选 |
| `cardgame-gwent-war` | Card | 第二套卡牌 |
| `idle-dungeon-guild` | Idle | 面板/编制 |
| `tycoon-potion-shop` | Tycoon | 配方库存 |
| `simulation-kitchen-rush` | Simulation | 多工位流程 |
| `visualnovel-detective-noir` | VN | 证据板；避开 split-screen 的 `visualnovel-time-paradox` |

Roguelike / Shooter 可进 **主表扩容**（战术向 `roguelike-breach-tactics`、`shooter-void-patrol`），但第一期最小闭环先 9 题。

### 附录压力题（单独报，不进主 Overall）

| slug | 预期偏差 |
|---|---|
| `platformer-knight-quest` | Godot（TileMap / 手感） |
| `racing-drift-circuit` | Godot（车辆物理） |

### 明确延后

Rhythm（音频时钟；skill：Worker 无 AudioContext 作判定真值）、Horror 光影特效向、Open-world 大地图流水线、任何 3D/真分屏/`<webview>` 当验收的任务。

### Oracle

- Godot 140 题 `solution/` 不动。
- 1Game 只做 **2 道烟测**（`cardgame-autobattler`、`visualnovel-lastsignal` 或 detective-noir）：证明 BUILD+回放，不当分数上限。
- 禁止用 Godot `solve.sh` 跑 1Game 任务。无 oracle 的格子标 `oracle=n/a`。
- `--agent nop` 仍应 0.0。

---

## 6. Agent 沙箱

| 项 | 决策 |
|---|---|
| 项目根 | 两边都是 `/workspace/game`（根目录有 assets bind，不能 `1game init .` 在 `/workspace`） |
| 资产 | 共用只读 Kenney/OGA |
| 1Game 工具链 | `/opt/1game` 钉 Node20 + pnpm9 + 离线 store + 预编译 native + **全量 skill 树** |
| Init | `1game init .` → `pnpm install`（offline）→ `1game-skill activate --cursor --force` |
| 网络 | Judge/Agent API 开；**禁止**公网 npm 作为成功路径 |
| 泄漏 | 宿主机 repo 的 `.cursor/skills` 不得被 trial 当成技能源；只从 pin 副本 activate |

Godot 侧仍给现有 `/tools/godot_command_line.md` + `screenshot.sh`。第一期 **不** 为对称去写一套 Godot mega-skill。

---

## 7. 实验协议

冻结：同一 harness、同一模型与 reasoning 档、同一 judge 后端/模型、viewport 1280×720、record 854×480、fps 30、frame_interval 0.5s、max_demos 10、max_demo_seconds 20、agent 7200s、verifier 1800s。中途换 judge = 实验作废。

### 主矩阵

`9 tasks × 2 engines × 1 agent/model × 3 seeds = 54 trials`

报告：subset overall + family 均值；单任务 n=3 只作附录。拆 `BUILD_rate`、`replay_fail`、`no_trace`、`INFRA`。  
`Overall | BUILD` 作为解读列，官方 Overall 仍含 BUILD 乘子。

### Skill 政策

- **主表 `ecological`**：Godot = 现状文档+截图脚本；1Game = 官方全 skill。问题是「各自推荐工具链下的成品分数」，不是控制文档 token 后的纯引擎差。
- **消融（不上主表）**：6 题 × 1Game × (全 skill vs 仅 CLI 一页) × 3 seeds，估计 skill 抬分。
- 表头必须写 `skill_policy`。训练数据偏 Godot 与 1Game 官方 skill 是两类 confound，不要互相「补文档」假装抵消。

### 会使对比作废的条件

不同模型/harness；主表混 skill 条件；judge 未冻结；INFRA 计成游戏失败；1Game 公网装包；项目不在 `/workspace/game`；rubric 仍写 Godot grey；scene 不是 1280×720；宿主机 skill 泄漏；把附录压力题灌进主 Overall；用 README 历史表当本次 Godot 基线；一边 oracle 一边真 agent；`--click` 宏撑歪时间轴却当画面差。

A 类（美术）跨引擎绝对值 **不宣称可比**（GLES vs Canvas 2D）。主结论放 M/D 与 BUILD/replay 结构指标。

---

## 8. 实现顺序

1. **Verifier 垂直切片**：`EngineRuntime` + Godot 搬迁（行为不变）+ 最小 1Game fixture（`src/game.tsx` + 一条 JSON）跑通 mp4/frames/`reward.txt`。
2. Judge 去 Godot 字样；`build_check` cwd；breakdown.engine。
3. 环境：Node/pnpm/offline store/native/字体；watchdog；`/tmp` sqlite。
4. `shared/gamecraft` + 9 个 `tasks-1game/<slug>`；子集 Godot rubric 中性化。
5. Dashboard iframe（可后于第一次表）。
6. 两道 1Game 烟测 oracle + nop。
7. 跑 54 trial；再决定 skill 消融与附录压力题。

文件级（代码阶段，本文不落地）：

- 新增 `gamecraft_bench/verifier/runtime/{base,godot,onegame}.py` + `onegame_replay.mjs`
- 改 `replay.py`（facade）、`score.py`、`cli.py`、`config.py`、`local_env.py`
- 改 `judges/_common.py`、`judges/openai_gpt.py`
- 改 `dashboard/manager.py`、`server.py`
- 新增 `docs/` 本文件；`shared/gamecraft/`；`tasks-1game/`

第一期明确 **不做**：改 Godot replay 时序；140 题 instruction 全改；vitest/`store:state` 替代 VLM；双协议 demo；hit 自动校准；强制全局 RNG seed；Chromium 对照轨；宣称 A 分跨引擎排名。

---

## 9. 与四路草案的分歧如何裁定

| 分歧 | 裁定 |
|---|---|
| 子集 9 vs 13 vs 15 族全上 | **主表 9**；平台跳跃/竞速进附录；不做 15 族硬凑 |
| 截图 320 上采样 vs 强制 1280 scene | **强制 1280×720 scene**，再降到 854×480 |
| BUILD 只 `1game build` vs create+step | **build + create + step×5** |
| `--engine` vs 分目录 | **分目录 `tasks-1game/`** |
| 主表 skill 对齐 vs 生态默认 | **生态默认 + 标注 + 可选消融** |
| Agent 交 `.1gamerecord` | **否**，只交 JSON |

---

## 10. 技能包在本仓库的位置

本设计过程已将 `@1game/skill@1.21.0` 激活到工作区 `.cursor/skills/`（`.gitignore` 忽略 `.cursor/`）。评测镜像应 pin npm 包，由 `1game-skill activate` 注入 **trial sandbox**，不要把开发机 skill 树当评测依赖。

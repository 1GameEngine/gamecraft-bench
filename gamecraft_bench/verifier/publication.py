"""Option-0 publication of a frozen ``engine_toolchain_effect`` ledger.

Reads cells and ``analyze.report`` only. Does not rescore, does not spawn, and
refuses to write into ``host_excerpt_ledger/``.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Sequence

from gamecraft_bench.verifier.analyze import load_cells, report
from gamecraft_bench.verifier.host_paths import LEDGER_DIRNAME

EXPERIMENT_ID = "h-20260918t061615z-36781d69"
ARM_ORDER = ("godot", "1game_eco", "1game_bare")
ARM_LABEL = {
    "godot": "Godot 臂",
    "1game_eco": "eco 臂（含 `@1game/skill`）",
    "1game_bare": "bare 臂（无该技能；仅本矩阵）",
}


class PublicationError(ValueError):
    """Refuse a write that would look like ledger promotion or rescoring."""


def refuse_ledger_write(path: Path) -> None:
    resolved = path.resolve()
    if resolved.parent.name == LEDGER_DIRNAME:
        raise PublicationError(
            f"refusing to write {path} inside {LEDGER_DIRNAME}/ "
            "(ledger records stay O_EXCL and are never rewritten)"
        )


def _arm_cells(cells: Sequence[dict[str, Any]], arm: str) -> list[dict[str, Any]]:
    return [c for c in cells if c.get("arm") == arm]


def arm_tally(cells: Sequence[dict[str, Any]], arm: str) -> dict[str, Any]:
    rows = _arm_cells(cells, arm)
    n = len(rows)
    void_k = sum(bool(c.get("void")) for c in rows)
    launch_k = sum(bool(c.get("launch_ok")) for c in rows)
    build_k = sum(bool(c.get("build_ok")) for c in rows)
    reasons = Counter(
        (c.get("void_reason") or "unspecified") for c in rows if c.get("void")
    )
    return {
        "arm": arm,
        "n": n,
        "void_k": void_k,
        "launch_k": launch_k,
        "build_k": build_k,
        "void_reasons": dict(reasons),
    }


def _fmt_interval(interval: list[float] | None) -> str:
    if not interval or len(interval) != 2:
        return "—"
    lo, hi = interval
    return f"[{lo}, {hi}]"


def _fmt_delta(block: dict[str, Any]) -> str:
    diff = block.get("difference")
    if diff is None:
        return "—"
    return f"{diff} {_fmt_interval(block.get('interval'))}"


def _per_slug_rows(block: dict[str, Any]) -> str:
    per = block.get("per_slug") or {}
    if not per:
        return "（`report()` 无 `per_slug`，本表从缺，不改分析器。）"
    lines = [
        "| slug | 差（Godot 臂 − eco 臂） |",
        "| --- | ---: |",
    ]
    for slug in sorted(per):
        lines.append(f"| `{slug}` | {per[slug]} |")
    return "\n".join(lines)


def _ablation_per_slug(block: dict[str, Any]) -> str:
    per = block.get("per_slug") or {}
    lines = [
        "| slug | 差（eco 臂 − bare 臂） |",
        "| --- | ---: |",
    ]
    for slug in sorted(per):
        lines.append(f"| `{slug}` | {per[slug]} |")
    return "\n".join(lines)


def render_publication(cells: Sequence[dict[str, Any]]) -> str:
    """Fill the option-0 publication from frozen cells + ``report()``."""
    out = report(cells)
    primary = out["primary"]
    reach = out["reach_primary"]
    ablation = out.get("ablation")
    tallies = {arm: arm_tally(cells, arm) for arm in ARM_ORDER}
    contaminated_field = sum(bool(c.get("contaminated")) for c in cells)

    rate_rows = []
    for arm in ARM_ORDER:
        t = tallies[arm]
        rate_rows.append(
            f"| {ARM_LABEL[arm]} | {t['n']} | "
            f"{t['build_k']}/{t['n']}（跨臂不可比） | "
            f"{t['launch_k']}/{t['n']} | "
            f"{t['void_k']}/{t['n']} |"
        )

    void_notes = []
    for arm in ARM_ORDER:
        t = tallies[arm]
        if t["void_k"] == 0:
            continue
        reasons = ", ".join(
            f"{reason} × {k}" for reason, k in sorted(t["void_reasons"].items())
        )
        void_notes.append(f"- {ARM_LABEL[arm]}：{t['void_k']}/{t['n']}（{reasons}）")
    if not void_notes:
        void_notes.append("- 无 void 格。")

    dropped_state = ", ".join(primary.get("dropped_slugs") or []) or "无"
    dropped_reach = ", ".join(reach.get("dropped_slugs") or []) or "无"

    ablation_section = "本记录无 `ablation` 键；不补做第三臂。"
    if ablation is not None:
        ablation_section = f"""角色：技能文档贡献的**描述性上界**，不是纯技能因果，也不是引擎核。
减法方向：`1game_eco − 1game_bare`。必须带区间；禁止单独点估计讲 skill 方向。

| 量 | 点估计与区间 | n_slug | dropped_slugs |
| --- | --- | ---: | --- |
| STATE 消融（非确认性） | {_fmt_delta(ablation)} | {ablation.get("slugs")} | {", ".join(ablation.get("dropped_slugs") or []) or "无"} |

{_ablation_per_slug(ablation)}
"""

    return f"""# 八个短演示任务上、固定智能体配置的宿主出码门控分项记录（已冻结三臂矩阵）

**效力：** 本文只发表已冻结的 72 格。不改计分器、不重打细胞、不 spawn、不开 P1、不新实验。仓库 `protocol-v2.md` 里的 Phase **不因本文启动**。

**主张类（仅账本字段，不得当标题）：** `engine_toolchain_effect`＝本冻结矩阵里，臂标签对应的整条宿主出码链路（运行时、系统附录、eco 侧 `@1game/skill`、预训练/语料、探针自报、BUILD 操作化）上的**分项比率记录**。此处 `engine` 是历史字段名，不是已识别的引擎内核因果。

**运行：** `{EXPERIMENT_ID}`（只读）。
**数字来源：** 冻结模块 `python -m gamecraft_bench.verifier.analyze`（`seed={primary.get("seed")}`，`resamples={primary.get("resamples")}`）。推断单位是共享 slug，不是 72 格。预注册写过「slug 随机效应」，实现是 slug 均值差的百分位 bootstrap；本文按代码报告，不把区间写成混合模型。

**计分规则（当时，不是修复项）：** 超过演示条数上限的 traces 按截断后的集合计 REACH；空覆盖 STATE 记 0。

---

## 摘要

在固定一种智能体配置、固定 USER 字节、八个短演示任务上，并置三条宿主出码链路——Godot 附录臂、含 `@1game/skill` 的 1Game 生态臂、以及仅本矩阵存在的无该技能臂——分项记录机器可检查的门控比率；不估计纯引擎质量，不产出单一分数或排行。

预注册主对照为 STATE（Godot 臂 − 生态臂）。slug 均值差 Δ = {primary["difference"]}（百分位 bootstrap 区间 {_fmt_interval(primary.get("interval"))}；n_slug = {primary["slugs"]}）。该区间包含 0。预注册分析已完成，结果为未检出 STATE 差。本设计没有无差异界，不得写成等价、打平、可互换，也不得写成「无差异故维持现状」。

入账 STATE 在未触及任何预登记节拍时记 0，故主终点混合了覆盖与条件通过。该缠结削弱「差／无差」的含义，不授权改换主终点，不授权把 STATE_cond 回打本矩阵当作真正主结论。

REACH 为预注册分项，见 T0 第二区；不是确认性对照。本摘要不给出 REACH 的点估计、区间或是否盖住 0。LAUNCH 与 void 见主表。

可识别对象是整条宿主出码链路。生态臂含技能文档；Godot 臂无补偿技能；无技能臂只提供技能文档贡献的描述性上界。BUILD 跨臂不可比。主路径无多模态裁判、无像素分。

Harbor 上的百分制量规评价的是同一 Godot 运行时上的智能体可玩性任务；本冻结宿主矩阵既不复现该量规，也不与其 Overall 通分，不能读成该论文的跨运行时续篇。

---

## T0 预注册终点（分区；禁止共用「主结果」表头）

减法方向：Godot 臂 − eco 臂。无星号、不按是否盖住 0 排序。

### 确认性（预注册 STATE）

| 量 | 点估计与区间 | n_slug | dropped_slugs |
| --- | --- | ---: | --- |
| STATE | {_fmt_delta(primary)} | {primary.get("slugs")} | {dropped_state} |

区间包含 0。不能排除无差，也不能声称等价。

### 次终点（描述，非确认）

| 量 | 点估计与区间 | n_slug | dropped_slugs |
| --- | --- | ---: | --- |
| REACH | {_fmt_delta(reach)} | {reach.get("slugs")} | {dropped_reach} |

次终点；n_slug={reach.get("slugs")}；未做多重校正；区间排除 0 不构成确认，亦不修正主对照。同一套 slug 差上，该次终点对单个任务敏感，不作为确认性发现，也不用来替换 STATE 结论。

### 分臂率（分母＝该臂全部已生成格，含 void）

| 臂 | n | BUILD | LAUNCH | void |
| --- | ---: | --- | --- | --- |
{chr(10).join(rate_rows)}

BUILD 跨臂不可比：Godot 无头检查是一次调用，1Game 可分编译与装配启动。void ≠ 0 ≠ fail；void 格不把 REACH/STATE 记成 0 再进均值。

---

## T1 样本与排除

- 计划 72 格；`report().cells` = {out["cells"]}。
- 污染字段合计为 {contaminated_field}。检测器当时未跑：记 **未标**，不得写成已证明 0 污染，也不得事后扫描后改本矩阵对比。
- STATE dropped_slugs：{dropped_state}。
- REACH dropped_slugs：{dropped_reach}。

void：

{chr(10).join(void_notes)}

---

## T2 slug 构件（抄 `per_slug`；不产生发布动作）

STATE：

{_per_slug_rows(primary)}

REACH（只说明是否单任务撑住「不穿 0」；不升级为迁栈令）：

{_per_slug_rows(reach)}

---

## T3 消融（仅因本账本含 `1game_bare`）

{ablation_section}

---

## 读数卡（决策锁，不是仪表）

**Q1.** STATE 主估计在场：`difference` 与 `interval` 均非空。入账 0 可能是没碰到拍、没编过或断言失败，须与 REACH、LAUNCH、void 同读。

**Q2. 迁栈吗？** 不迁栈。这不是两栈等价，也不是出码无差。未检出差、且空覆盖入账为 0，解释已被削弱。不迁是不确定下的运营选择，不是检验结论。本问不把 REACH 当键。

**Q3. 下线吗？** 不下线。LAUNCH：Godot 臂 {tallies['godot']['launch_k']}/{tallies['godot']['n']}，eco 臂 {tallies['1game_eco']['launch_k']}/{tallies['1game_eco']['n']}。void 量级不构成弃用。

**Q4. 作榜或按 REACH 采购吗？** 不作榜。REACH 不是采购键。消融见 T3；无键则不补第三臂。

**发布默认：**

1. 不迁默认运行时（≠ 两臂一样好）。
2. 1Game 生态臂不下线。
3. STATE 是已完成的预注册对照（未检出差）。REACH 列在 T0 以免漏报，但不产生发布动作。

---

## 允许 / 禁止

**允许：** 只读分项；STATE 与 0 相容；LAUNCH/void/REACH 并列不加总；void 用 k/n。

**禁止：** 更好引擎；等价/打平；排行/百分制；用 REACH 指导选栈；STATE_cond 回打本矩阵；新格验证本表；void 记 0 填进 STATE。

---

选项 1 不在效力范围内：不开新格、不改分析器、不把 REACH 写成正赛；若未来另立新实验，须另文并在第一格前自行预注册，不得更新本稿就地开启。
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m gamecraft_bench.verifier.publication",
        description="Render option-0 publication from a frozen ledger (read-only).",
    )
    parser.add_argument("record", type=Path)
    parser.add_argument("--md-out", type=Path)
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args(argv)

    for dest in (args.md_out, args.json_out):
        if dest is not None:
            refuse_ledger_write(dest)

    cells = load_cells([args.record])
    payload = report(cells)
    markdown = render_publication(cells)
    if not markdown.endswith("\n"):
        markdown += "\n"

    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(payload, indent=2) + "\n")
    if args.md_out:
        args.md_out.parent.mkdir(parents=True, exist_ok=True)
        args.md_out.write_text(markdown if markdown.endswith("\n") else markdown + "\n")
    if args.md_out is None:
        print(markdown, end="" if markdown.endswith("\n") else "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

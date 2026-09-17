"""Diagnostic table assembler — not a paper ranking."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from gamecraft_bench.verifier.compare import main, merge_pair


def _bd(*, engine: str, name: str, model: str, comparable: bool, media: str | None = None) -> dict:
    reqs = [
        {"id": "M3", "aggregated": 0.8 if engine == "godot" else 0.4},
        {"id": "M4", "aggregated": 0.7 if engine == "godot" else 0.3},
        {"id": "D3", "aggregated": 1.0},
        {"id": "D2", "aggregated": 0.6 if engine == "godot" else 0.2},
        {"id": "V1", "aggregated": 0.9},
        {"id": "A4", "aggregated": 0.1},
    ]
    out = {
        "reward": 0.55,
        "engine": engine,
        "judge": {"name": name, "model": model},
        "comparable": comparable,
        "build_ok": True,
        "requirements": reqs,
        "media": media or ("slideshow" if engine == "1game" else "x11grab"),
    }
    return out


def test_merge_rejects_stub() -> None:
    table = merge_pair(
        _bd(engine="godot", name="StubJudge", model="1.0", comparable=False),
        _bd(engine="1game", name="StubJudge", model="1.0", comparable=False),
    )
    assert table["publishable"] is False
    assert table["not_a_paper_ranking"] is True
    assert "unpublished" in table
    assert "V1" not in table["diagnostic_columns"]
    assert "A4" not in table["diagnostic_columns"]
    assert "D3" not in table["diagnostic_columns"]


def test_merge_accepts_matching_real_judge() -> None:
    table = merge_pair(
        _bd(engine="godot", name="OpenAIJudge", model="gpt-4o", comparable=True),
        _bd(engine="1game", name="OpenAIJudge", model="gpt-4o", comparable=True),
    )
    assert table["publishable"] is True
    assert table["success_gate"] is False
    assert table["cite_columns"] is False
    assert table["not_a_paper_ranking"] is True
    assert table["diagnostic_columns"]["M3"]["godot"] == 0.8
    assert "D3" in table["unpublished_ids"]
    assert table["judge"]["model"] == "gpt-4o"


def test_merge_rejects_model_mismatch() -> None:
    table = merge_pair(
        _bd(engine="godot", name="OpenAIJudge", model="gpt-4o", comparable=True),
        _bd(engine="1game", name="OpenAIJudge", model="gpt-5.5", comparable=True),
    )
    assert table["publishable"] is False
    assert any("model" in b for b in table["blockers"])


def test_merge_rejects_auto_engine_on_1game_arm() -> None:
    g = _bd(engine="godot", name="OpenAIJudge", model="gpt-4o", comparable=True)
    o = _bd(engine="godot", name="OpenAIJudge", model="gpt-4o", comparable=True)
    table = merge_pair(g, o)
    assert table["publishable"] is False


def test_keepsake_prompts_omit_rubric_ids() -> None:
    root = Path(__file__).resolve().parents[2]
    skill = root / "skills/gamecraft-host-dual-run"
    assert (skill / "appendix-godot.md").is_file()
    assert (skill / "score-excerpt.md").is_file()
    assert not (skill / "plumbing.md").is_file()
    env = (skill / "keepsake-1game-brief.md").read_text()
    assert "(M3)" not in env
    assert "(M4)" not in env
    assert "project.godot" not in env
    assert "instruction.md" not in env
    assert "HARD-no-spawn" not in env
    assert "src/game.tsx" in env
    assert "two" in env.lower() and "logic frames" in env.lower()
    main_text = (skill / "keepsake-main.md").read_text()
    assert "M3" not in main_text
    assert "M4" not in main_text
    assert "1280" in main_text
    assert "/workspace/assets/library/" in main_text
    assert "scenario" in main_text
    lower = main_text.lower()
    assert "memory board" in lower
    assert "grows" in lower
    assert "gating" in lower
    assert "separate traces" in lower
    assert "both arms" not in lower
    assert "engine ranking" not in lower
    assert "engine-neutral" not in lower
    godot = (skill / "appendix-godot.md").read_text()
    assert "project.godot" in godot
    assert "1game" not in godot.lower()
    assert "instruction.md" not in godot
    skill_md = (skill / "SKILL.md").read_text()
    assert "HARD-no-spawn" not in skill_md
    assert "phase-1-run-once-keepsake" in skill_md
    assert "1+1-only" in skill_md
    assert "score-godot" in skill_md
    assert "score-1game" in skill_md
    assert "consumed" in skill_md
    assert "新录再打" in skill_md
    assert "child_raw" in skill_md
    assert "protocol_cap" in skill_md
    excerpt = (skill / "score-excerpt.md").read_text()
    assert "child_raw" in excerpt
    assert "protocol_cap" in excerpt
    assert "Same USER bytes" in excerpt


def test_compare_main_exits_zero_when_not_publishable(tmp_path: Path) -> None:
    godot_dir = tmp_path / "godot"
    onegame_dir = tmp_path / "onegame"
    godot_dir.mkdir()
    onegame_dir.mkdir()
    (godot_dir / "breakdown.json").write_text(
        json.dumps(_bd(engine="godot", name="StubJudge", model="1.0", comparable=False))
    )
    (onegame_dir / "breakdown.json").write_text(
        json.dumps(_bd(engine="1game", name="StubJudge", model="1.0", comparable=False))
    )
    out = tmp_path / "table.json"
    rc = main(
        ["--godot", str(godot_dir), "--onegame", str(onegame_dir), "--out", str(out)]
    )
    assert rc == 0
    assert out.is_file()
    dumped = json.loads(out.read_text())
    assert dumped["publishable"] is False
    assert dumped["success_gate"] is False
    assert dumped["cite_columns"] is False

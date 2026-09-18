"""Engine dispatch: Godot Harbor identity vs 1Game skip-rubric BUILD."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from gamecraft_bench.config import env_for_subprocess
from gamecraft_bench.verifier.score import (
    InfraError,
    _run_1game_build_check,
    detect_engine,
    judge_hard_failed,
    score_project,
)


def test_project_godot_wins_over_tsx(tmp_path: Path) -> None:
    (tmp_path / "project.godot").write_text("[application]\n")
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "game.tsx").write_text("x")
    assert detect_engine(tmp_path) == "godot"
    assert detect_engine(tmp_path, "1game") == "1game"


def test_auto_never_selects_1game(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "game.tsx").write_text("x")
    (tmp_path / "1game.config.ts").write_text("export default {}\n")
    assert detect_engine(tmp_path) == "godot"
    assert detect_engine(tmp_path, None) == "godot"
    assert detect_engine(tmp_path, "") == "godot"
    assert detect_engine(tmp_path, "auto") == "godot"
    assert detect_engine(tmp_path, "1game") == "1game"


def test_detect_engine_ignores_environ(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("GAMECRAFT_BENCH_ENGINE", "1game")
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "game.tsx").write_text("x")
    assert detect_engine(tmp_path) == "godot"


def test_empty_tree_is_godot(tmp_path: Path) -> None:
    assert detect_engine(tmp_path) == "godot"


def test_config_without_tsx_stays_godot_on_auto(tmp_path: Path) -> None:
    (tmp_path / "1game.config.ts").write_text("export default {}\n")
    assert detect_engine(tmp_path) == "godot"


def test_godot_tree_does_not_require_1gameplay(tmp_path: Path) -> None:
    (tmp_path / "project.godot").write_text("[application]\n")
    rubric = {
        "score_formula": "BUILD",
        "build_check": {
            "id": "BUILD",
            "cmd": "godot --headless --path /workspace/game --quit-after 5",
        },
        "requirements": [],
    }
    rubric_path = tmp_path / "rubric.json"
    rubric_path.write_text(json.dumps(rubric))
    out = tmp_path / "out"
    proc = MagicMock(returncode=1, stdout="", stderr="fail\n")
    from gamecraft_bench.verifier.judges.stub import StubJudge
    with patch("gamecraft_bench.config.ONEGAMEPLAY_BIN", None), \
         patch("gamecraft_bench.config.ONEGAME_BIN", None), \
         patch("gamecraft_bench.verifier.score.subprocess.run", return_value=proc) as mock_run:
        result = score_project(
            project_dir=tmp_path,
            rubric_path=rubric_path,
            output_dir=out,
            judge=StubJudge(),
        )
    assert result.engine == "godot"
    assert result.build_ok is False
    assert mock_run.called
    cmd = mock_run.call_args[0][0]
    assert "godot" in cmd


def test_engine_godot_exclusive_on_tsx_tree(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "game.tsx").write_text("x")
    rubric = {
        "score_formula": "BUILD",
        "build_check": {
            "id": "BUILD",
            "cmd": "godot --headless --path /workspace/game --quit-after 5",
        },
        "requirements": [],
    }
    rubric_path = tmp_path / "rubric.json"
    rubric_path.write_text(json.dumps(rubric))
    proc = MagicMock(returncode=1, stdout="", stderr="fail\n")
    from gamecraft_bench.verifier.judges.stub import StubJudge
    with patch("gamecraft_bench.verifier.score.subprocess.run", return_value=proc) as mock_run:
        result = score_project(
            project_dir=tmp_path,
            rubric_path=rubric_path,
            output_dir=tmp_path / "out",
            judge=StubJudge(),
            engine="godot",
        )
    assert result.engine == "godot"
    cmd = mock_run.call_args[0][0]
    assert isinstance(cmd, str) and "godot" in cmd


def test_cli_godot_judge_hard_fail_writes_reward(tmp_path: Path) -> None:
    (tmp_path / "project.godot").write_text("[application]\n")
    rubric_path = tmp_path / "rubric.json"
    rubric_path.write_text(json.dumps({
        "score_formula": "BUILD",
        "build_check": {"id": "BUILD", "cmd": "true"},
        "requirements": [],
    }))
    out = tmp_path / "out"
    from gamecraft_bench.verifier.cli import main
    from gamecraft_bench.verifier.score import ScoreResult

    fake = ScoreResult(
        reward=0.0,
        build_ok=True,
        build_log="",
        formula="BUILD",
        requirements=[],
        demos=[],
        judge_name="OpenAIJudge",
        judge_model="gpt-5.5",
        errors=["judge failed on 01_click: none of OPENAI_API_KEY set"],
        engine="godot",
    )
    with patch("gamecraft_bench.verifier.cli.score_project", return_value=fake):
        rc = main([
            "--project", str(tmp_path),
            "--rubric", str(rubric_path),
            "--output", str(out),
            "--judge", "stub",
        ])
    assert rc == 1
    assert (out / "reward.txt").exists()
    extra = json.loads((out / "ctrf.json").read_text())["results"]["extra"]
    assert extra["comparable"] is False


def test_cli_1game_judge_hard_fail_skips_reward(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "game.tsx").write_text("x")
    rubric_path = tmp_path / "rubric.json"
    rubric_path.write_text(json.dumps({
        "score_formula": "BUILD",
        "build_check": {"id": "BUILD", "cmd": "true"},
        "requirements": [],
    }))
    out = tmp_path / "out"
    from gamecraft_bench.verifier.cli import main
    from gamecraft_bench.verifier.score import ScoreResult

    fake = ScoreResult(
        reward=0.0,
        build_ok=True,
        build_log="",
        formula="BUILD",
        requirements=[],
        demos=[],
        judge_name="OpenAIJudge",
        judge_model="gpt-5.5",
        errors=["judge failed on 01_click: none of OPENAI_API_KEY set"],
        engine="1game",
    )
    with patch("gamecraft_bench.verifier.cli.score_project", return_value=fake), \
         patch("gamecraft_bench.verifier.cli.detect_engine", return_value="1game"):
        rc = main([
            "--project", str(tmp_path),
            "--rubric", str(rubric_path),
            "--output", str(out),
            "--judge", "stub",
            "--engine", "1game",
        ])
    assert rc == 2
    assert not (out / "reward.txt").exists()


def test_cli_infra_exit_2_skips_reward(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "game.tsx").write_text("x")
    rubric_path = tmp_path / "rubric.json"
    rubric_path.write_text(json.dumps({
        "score_formula": "BUILD",
        "build_check": {"id": "BUILD", "cmd": "true"},
        "requirements": [],
    }))
    out = tmp_path / "out"
    from gamecraft_bench.verifier.cli import main
    with patch("gamecraft_bench.verifier.cli.cfg.ONEGAMEPLAY_BIN", None):
        rc = main([
            "--project", str(tmp_path),
            "--rubric", str(rubric_path),
            "--output", str(out),
            "--judge", "stub",
            "--engine", "1game",
        ])
    assert rc == 2
    assert not (out / "reward.txt").exists()


def test_1game_build_never_invokes_godot(tmp_path: Path) -> None:
    project = tmp_path / "game"
    project.mkdir()
    (project / "src").mkdir()
    (project / "src" / "game.tsx").write_text("x")
    out = tmp_path / "out"
    out.mkdir()
    proc = MagicMock(returncode=0, stdout="ok\n", stderr="")
    with patch("gamecraft_bench.verifier.score.subprocess.run", return_value=proc) as mock_run:
        ok, log = _run_1game_build_check(out, project)
    assert ok
    assert "godot" not in log.lower() or "skipped rubric godot" in log
    joined = " ".join(
        " ".join(args[0]) if isinstance(args[0], list) else str(args[0])
        for args, _ in mock_run.call_args_list
    )
    assert "--surface display" in joined or "--surface" in joined
    assert "--flush" in joined
    for args, _kwargs in mock_run.call_args_list:
        argv = args[0]
        assert argv[0] != "godot"
        assert "godot" not in argv


def test_missing_1gameplay_is_infra_not_build_zero(tmp_path: Path) -> None:
    project = tmp_path / "game"
    project.mkdir()
    (project / "src").mkdir()
    (project / "src" / "game.tsx").write_text("x")
    rubric = {
        "score_formula": "BUILD * M1",
        "build_check": {
            "id": "BUILD",
            "cmd": "godot --headless --path /workspace/game --quit-after 5",
        },
        "requirements": [{"id": "M1", "description": "x", "agg": "max"}],
    }
    rubric_path = tmp_path / "rubric.json"
    rubric_path.write_text(json.dumps(rubric))
    out = tmp_path / "out"
    from gamecraft_bench.verifier.judges.stub import StubJudge

    with patch("gamecraft_bench.config.ONEGAMEPLAY_BIN", None):
        try:
            score_project(
                project_dir=project,
                rubric_path=rubric_path,
                output_dir=out,
                judge=StubJudge(),
                engine="1game",
            )
        except InfraError as exc:
            assert "1gameplay" in str(exc).lower()
        else:
            raise AssertionError("expected InfraError")
    assert not (out / "reward.txt").exists()


def test_judge_hard_failed_detects_prefix() -> None:
    assert judge_hard_failed(["judge failed on d: missing key"])
    assert not judge_hard_failed(["replay failed for d: boom"])


def test_env_for_subprocess_omits_engine() -> None:
    env = env_for_subprocess()
    assert "GAMECRAFT_BENCH_ENGINE" not in env
    assert "engine" not in {k.lower() for k in env if "ENGINE" in k}

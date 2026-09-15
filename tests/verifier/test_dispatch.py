"""Engine dispatch: Godot Harbor identity vs 1Game skip-rubric BUILD."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from gamecraft_bench.verifier.score import (
    InfraError,
    _run_1game_build_check,
    detect_engine,
    score_project,
)


def test_project_godot_wins_over_tsx(tmp_path: Path) -> None:
    (tmp_path / "project.godot").write_text("[application]\n")
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "game.tsx").write_text("x")
    assert detect_engine(tmp_path) == "godot"
    assert detect_engine(tmp_path, "1game") == "1game"


def test_empty_tree_is_godot(tmp_path: Path) -> None:
    assert detect_engine(tmp_path) == "godot"


def test_tsx_is_1game(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "game.tsx").write_text("x")
    assert detect_engine(tmp_path) == "1game"


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
            )
        except InfraError as exc:
            assert "1gameplay" in str(exc).lower()
        else:
            raise AssertionError("expected InfraError")
    assert not (out / "reward.txt").exists()

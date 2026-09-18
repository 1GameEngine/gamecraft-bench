"""Contract tests for replay_1game.replay_trace (no live 1gameplay)."""

from __future__ import annotations

import inspect
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from gamecraft_bench.verifier.replay import ReplayError, ReplayResult, replay_trace as godot_replay
from gamecraft_bench.verifier.replay_1game import replay_trace as onegame_replay


def test_replay_1game_accepts_score_kwargs() -> None:
    godot = inspect.signature(godot_replay)
    one = inspect.signature(onegame_replay)
    for name in (
        "project_dir", "trace_path", "output_mp4", "viewport",
        "record_size", "fps", "log_dir",
    ):
        assert name in godot.parameters
        assert name in one.parameters


def test_replay_1game_returns_replay_result() -> None:
    hints = inspect.signature(onegame_replay).return_annotation
    assert hints is ReplayResult or "ReplayResult" in str(hints)


def test_missing_1gameplay_raises_replay_error(tmp_path: Path) -> None:
    proj = tmp_path / "g"
    proj.mkdir()
    (proj / "src").mkdir()
    (proj / "src" / "game.tsx").write_text("x")
    trace = tmp_path / "t.json"
    trace.write_text('{"duration_frames": 30, "events": []}')
    with patch("gamecraft_bench.verifier.replay_1game.cfg.ONEGAMEPLAY_BIN", None):
        try:
            onegame_replay(
                project_dir=proj,
                trace_path=trace,
                output_mp4=tmp_path / "out.mp4",
            )
        except ReplayError as e:
            assert "1gameplay" in str(e).lower()
        else:
            raise AssertionError("expected ReplayError")

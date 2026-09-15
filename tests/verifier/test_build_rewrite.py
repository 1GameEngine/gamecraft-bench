"""Unit tests for host BUILD cmd rewriting in ``_run_build_check``.

subprocess.run is mocked: no Godot, Harbor, or score_project.
"""

from __future__ import annotations

import sys
from pathlib import Path

# The pytest console script does not put the repo root on sys.path, so a
# non-editable site-packages install would otherwise shadow local score.py.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import shlex
import subprocess
from unittest.mock import patch

from gamecraft_bench.verifier.score import _run_build_check

HARBOR_GAME = Path("/workspace/game")
RUBRIC_CMD = "godot --headless --path /workspace/game --quit-after 5"


def _ok_proc(cmd: str = "") -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess(
        args=cmd, returncode=0, stdout="ok\n", stderr="",
    )


def _run(spec: dict, output_dir: Path, project_dir: Path, mock_run):
    mock_run.return_value = _ok_proc()
    return _run_build_check(spec, output_dir, project_dir)


def _call(mock_run):
    assert mock_run.called
    args, kwargs = mock_run.call_args
    return args, kwargs


def test_identity_keeps_original_cmd_string(tmp_path: Path) -> None:
    spec = {"cmd": RUBRIC_CMD, "timeout_seconds": 5}
    with patch("gamecraft_bench.verifier.score.subprocess.run") as mock_run:
        ok, log = _run(spec, tmp_path, HARBOR_GAME, mock_run)

    args, kwargs = _call(mock_run)
    assert ok
    assert isinstance(args[0], str)
    assert args[0] == RUBRIC_CMD
    assert kwargs["shell"] is True
    assert Path(kwargs["cwd"]).resolve() == HARBOR_GAME.resolve()
    assert "env" not in kwargs
    assert "# cmd (raw): " + RUBRIC_CMD in log
    assert "# cmd (rewritten): " + RUBRIC_CMD in log
    assert f"# cwd: {HARBOR_GAME.resolve()}" in log
    assert (tmp_path / "build.log").read_text() == log


def test_non_identity_rewrites_path_token_with_space(tmp_path: Path) -> None:
    project_dir = tmp_path / "my game"
    project_dir.mkdir()
    output_dir = tmp_path / "out"
    output_dir.mkdir()
    spec = {"cmd": RUBRIC_CMD, "timeout_seconds": 5}
    resolved = str(project_dir.resolve())

    with patch("gamecraft_bench.verifier.score.subprocess.run") as mock_run:
        ok, log = _run(spec, output_dir, project_dir, mock_run)

    args, kwargs = _call(mock_run)
    assert ok
    assert isinstance(args[0], str)
    tokens = shlex.split(args[0], posix=True)
    assert kwargs["shell"] is True
    assert Path(kwargs["cwd"]).resolve() == project_dir.resolve()
    assert "--path" in tokens
    path_val = tokens[tokens.index("--path") + 1]
    assert path_val == resolved
    assert "/workspace/game" not in tokens
    assert "# cmd (raw): " + RUBRIC_CMD in log
    assert "# cmd (rewritten): " + args[0] in log
    assert f"# cwd: {project_dir.resolve()}" in log


def test_gameplay_and_games_tokens_are_not_rewritten(tmp_path: Path) -> None:
    project_dir = tmp_path / "proj"
    project_dir.mkdir()
    cmd = (
        "godot --headless --path /workspace/gameplay "
        "/workspace/games --path=/workspace/gameplay --quit-after 5"
    )
    spec = {"cmd": cmd, "timeout_seconds": 5}

    with patch("gamecraft_bench.verifier.score.subprocess.run") as mock_run:
        _run(spec, tmp_path, project_dir, mock_run)

    args, _kwargs = _call(mock_run)
    tokens = shlex.split(args[0], posix=True)
    assert "/workspace/gameplay" in tokens
    assert "/workspace/games" in tokens
    assert "--path=/workspace/gameplay" in tokens
    assert str(project_dir.resolve()) not in tokens
    assert "/workspace/game" not in tokens


def test_env_var_tokens_rewritten_when_not_identity(tmp_path: Path) -> None:
    project_dir = tmp_path / "host-game"
    project_dir.mkdir()
    resolved = str(project_dir.resolve())
    cmd = (
        "godot --headless --path $GAME_PROJECT_PATH "
        "${GAME_PROJECT_PATH} --quit-after 5"
    )
    spec = {"cmd": cmd, "timeout_seconds": 5}

    with patch("gamecraft_bench.verifier.score.subprocess.run") as mock_run:
        _run(spec, tmp_path, project_dir, mock_run)

    args, kwargs = _call(mock_run)
    tokens = shlex.split(args[0], posix=True)
    assert tokens.count(resolved) == 2
    assert "$GAME_PROJECT_PATH" not in tokens
    assert "${GAME_PROJECT_PATH}" not in tokens
    assert Path(kwargs["cwd"]).resolve() == project_dir.resolve()


def test_glued_path_flag_rewritten(tmp_path: Path) -> None:
    project_dir = tmp_path / "host-game"
    project_dir.mkdir()
    resolved = str(project_dir.resolve())
    cmd = "godot --headless --path=/workspace/game --quit-after 5"
    spec = {"cmd": cmd, "timeout_seconds": 5}

    with patch("gamecraft_bench.verifier.score.subprocess.run") as mock_run:
        _run(spec, tmp_path, project_dir, mock_run)

    args, _kwargs = _call(mock_run)
    tokens = shlex.split(args[0], posix=True)
    assert "--path=" + resolved in tokens
    assert "/workspace/game" not in tokens
    assert not any(t == "--path=/workspace/game" for t in tokens)


def test_glued_path_child_and_standalone_child(tmp_path: Path) -> None:
    project_dir = tmp_path / "host-game"
    project_dir.mkdir()
    resolved = str(project_dir.resolve())
    cmd = "godot --path=/workspace/game/foo /workspace/game/bar"
    spec = {"cmd": cmd, "timeout_seconds": 5}

    with patch("gamecraft_bench.verifier.score.subprocess.run") as mock_run:
        _run(spec, tmp_path, project_dir, mock_run)

    args, _kwargs = _call(mock_run)
    tokens = shlex.split(args[0], posix=True)
    assert "--path=" + resolved + "/foo" in tokens
    assert resolved + "/bar" in tokens
    assert not any("/workspace/game" in t for t in tokens)


def test_empty_project_dir_still_runs(tmp_path: Path) -> None:
    """Empty dirs must still invoke the cmd (no project.godot short-circuit)."""
    project_dir = tmp_path / "empty"
    project_dir.mkdir()
    assert not (project_dir / "project.godot").exists()
    spec = {"cmd": RUBRIC_CMD, "timeout_seconds": 5}

    with patch("gamecraft_bench.verifier.score.subprocess.run") as mock_run:
        _run(spec, tmp_path, project_dir, mock_run)

    assert mock_run.call_count == 1
    args, kwargs = _call(mock_run)
    assert kwargs["shell"] is True
    assert Path(kwargs["cwd"]).resolve() == project_dir.resolve()
    tokens = shlex.split(args[0], posix=True)
    assert tokens[tokens.index("--path") + 1] == str(project_dir.resolve())

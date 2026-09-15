"""Replay a demo trace against a 1Game project and encode an mp4.

Host path only: system ``1gameplay`` (not ``pnpm exec``), napi
``frame screenshot`` (not Xvfb / replay.html). Event injection uses
instantaneous ``pointer.*`` / ``keydown`` / ``keyup`` macros — never
the multi-frame ``--click`` / ``keypress`` helpers.

Godot ``replay.py`` is untouched. This module is imported lazily from
``score.py`` only after the project is classified as 1Game.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from .. import config as cfg
from .replay import ReplayError, ReplayResult

_KEYCODES: dict[str, str] = {
    "ESCAPE": "Escape",
    "ENTER": "Enter",
    "SPACE": "Space",
    "TAB": "Tab",
    "BACKSPACE": "Backspace",
    "DELETE": "Delete",
    "UP": "ArrowUp",
    "DOWN": "ArrowDown",
    "LEFT": "ArrowLeft",
    "RIGHT": "ArrowRight",
    "SHIFT": "ShiftLeft",
    "CTRL": "ControlLeft",
    "ALT": "AltLeft",
    **{c: f"Key{c}" for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"},
    **{str(d): f"Digit{d}" for d in range(10)},
}


def replay_trace(
    *,
    project_dir: Path,
    trace_path: Path,
    output_mp4: Path,
    viewport: tuple[int, int] = (1280, 720),
    record_size: tuple[int, int] | None = (854, 480),
    fps: int = 30,
    godot_bin: str | None = None,
    settle_seconds: float = 1.5,
    log_dir: Path | None = None,
    max_replay_seconds: float = 90.0,
) -> ReplayResult:
    """Run a single Godot-shaped JSON trace through 1gameplay.

    ``godot_bin`` and ``settle_seconds`` are accepted so ``score_project``
    can pass the same kwargs as Godot ``replay_trace``; they are ignored.
    """
    del godot_bin, settle_seconds
    project_dir = Path(project_dir).resolve()
    trace_path = Path(trace_path).resolve()
    output_mp4 = Path(output_mp4).resolve()
    output_mp4.parent.mkdir(parents=True, exist_ok=True)
    if log_dir is not None:
        log_dir = Path(log_dir).resolve()
        log_dir.mkdir(parents=True, exist_ok=True)

    play = _require_1gameplay()
    if shutil.which("ffmpeg") is None:
        raise ReplayError("required tool not on PATH: ffmpeg")

    trace = json.loads(trace_path.read_text())
    events = list(trace.get("events", []))
    duration_frames = int(trace.get("duration_frames", 0))
    replay_frames = max(
        duration_frames,
        *(int(ev["frame"]) for ev in events),
    ) if events else duration_frames
    if replay_frames < 0:
        raise ReplayError(f"negative trace duration/frame in {trace_path}")
    trace_seconds = replay_frames / fps
    if trace_seconds <= 0:
        raise ReplayError(f"trace duration_seconds must be > 0 in {trace_path}")
    if trace_seconds > max_replay_seconds:
        raise ReplayError(
            f"trace lasts {trace_seconds:.2f}s, exceeding "
            f"max_replay_seconds={max_replay_seconds}s"
        )

    w, h = viewport
    env = _onegame_env()
    entry = _entry_path(project_dir)

    with tempfile.TemporaryDirectory(prefix="gc1game-replay-", dir="/tmp") as tmp:
        archive = Path(tmp) / "demo.1gamerecord"
        _run_cli(
            [play, "create", "--entry", str(entry), "--out", str(archive)],
            cwd=project_dir,
            env=env,
            timeout=300,
            log_path=(log_dir / "1gameplay.log") if log_dir else None,
        )
        _apply_events(
            play, archive, events, fps=fps, duration_frames=replay_frames,
            cwd=project_dir, env=env,
            log_path=(log_dir / "1gameplay.log") if log_dir else None,
        )
        png = Path(tmp) / "last.png"
        _run_cli(
            [
                play, "frame", "screenshot", str(archive),
                "--at", "last",
                "--out", str(png),
                "--width", str(w),
                "--height", str(h),
            ],
            cwd=project_dir,
            env=env,
            timeout=120,
            log_path=(log_dir / "1gameplay.log") if log_dir else None,
        )
        if not png.is_file() or png.stat().st_size <= 0:
            raise ReplayError("1gameplay frame screenshot produced an empty PNG")
        rw, rh = record_size if record_size is not None else viewport
        _encode_still_mp4(
            png, output_mp4, duration_seconds=trace_seconds, fps=fps,
            record_size=(rw, rh),
            log_path=(log_dir / "ffmpeg.log") if log_dir else None,
        )

    if not output_mp4.is_file() or output_mp4.stat().st_size <= 0:
        raise ReplayError(f"ffmpeg did not write {output_mp4}")
    return ReplayResult(
        output_mp4=output_mp4,
        duration_seconds=trace_seconds,
        godot_returncode=0,
    )


def _require_1gameplay() -> str:
    play = cfg.ONEGAMEPLAY_BIN
    if not play:
        raise ReplayError(
            "no 1gameplay binary configured "
            "(set GAMECRAFT_BENCH_ONEGAMEPLAY_BIN)"
        )
    return play


def _onegame_env() -> dict[str, str]:
    env = dict(os.environ)
    node_modules = cfg.ONEGAME_NODE_MODULES
    existing = env.get("NODE_PATH", "")
    if node_modules:
        env["NODE_PATH"] = (
            node_modules if not existing else f"{node_modules}:{existing}"
        )
    return env


def _entry_path(project_dir: Path) -> Path:
    entry = project_dir / "src" / "game.tsx"
    if not entry.is_file():
        raise ReplayError(f"1Game entry not found: {entry}")
    return entry


def _run_cli(
    argv: list[str],
    *,
    cwd: Path,
    env: dict[str, str],
    timeout: float,
    log_path: Path | None,
) -> str:
    try:
        proc = subprocess.run(
            argv,
            cwd=str(cwd),
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as e:
        raise ReplayError(f"{argv[0]} timed out: {argv}") from e
    text = (proc.stdout or "") + (proc.stderr or "")
    if log_path is not None:
        with log_path.open("a", encoding="utf-8") as fh:
            fh.write(f"$ {' '.join(argv)}\n{text}\n")
    if proc.returncode != 0:
        raise ReplayError(
            f"{argv[0]} exited {proc.returncode}: {text[-2000:]}"
        )
    return proc.stdout or ""


def _ms_per_frame(fps: int) -> int:
    return max(1, int(round(1000 / fps)))


def _apply_events(
    play: str,
    archive: Path,
    events: list[dict],
    *,
    fps: int,
    duration_frames: int,
    cwd: Path,
    env: dict[str, str],
    log_path: Path | None,
) -> None:
    ordered = sorted(events, key=lambda ev: int(ev.get("frame", 0)))
    cursor = 0
    ms_frame = _ms_per_frame(fps)
    for ev in ordered:
        frame = int(ev.get("frame", 0))
        if frame > cursor:
            _tick(play, archive, (frame - cursor) * ms_frame, cwd, env, log_path)
            cursor = frame
        for payload in _event_payloads(ev):
            _run_cli(
                [
                    play, "step", str(archive),
                    "--ms", "16", "--repeat", "1",
                    "--event", json.dumps(payload, separators=(",", ":")),
                ],
                cwd=cwd, env=env, timeout=120, log_path=log_path,
            )
            cursor += 1
    if duration_frames > cursor:
        _tick(
            play, archive, (duration_frames - cursor) * ms_frame,
            cwd, env, log_path,
        )


def _tick(
    play: str,
    archive: Path,
    ms: int,
    cwd: Path,
    env: dict[str, str],
    log_path: Path | None,
) -> None:
    if ms <= 0:
        return
    _run_cli(
        [play, "step", str(archive), "--ms", str(ms), "--repeat", "1"],
        cwd=cwd, env=env, timeout=120, log_path=log_path,
    )


def _event_payloads(ev: dict) -> list[dict]:
    kind = str(ev.get("type", ""))
    if kind in ("wait",):
        return []
    if kind == "mouse_move":
        return [_pointer("pointer.move", ev)]
    if kind == "mouse_down":
        return [_pointer("pointer.down", ev)]
    if kind == "mouse_up":
        return [_pointer("pointer.up", ev)]
    if kind == "mouse_click":
        return [_pointer("pointer.down", ev), _pointer("pointer.up", ev)]
    if kind == "key_down":
        return [_key("keydown", ev)]
    if kind == "key_up":
        return [_key("keyup", ev)]
    if kind == "key_press":
        return [_key("keydown", ev), _key("keyup", ev)]
    raise ReplayError(f"unsupported 1Game replay event type: {kind!r}")


def _pointer(kind: str, ev: dict) -> dict:
    return {
        "type": kind,
        "data": {"id": 1, "x": int(ev["x"]), "y": int(ev["y"])},
    }


def _key(kind: str, ev: dict) -> dict:
    code = str(ev.get("keycode", ""))
    mapped = _KEYCODES.get(code.upper(), code)
    return {"type": kind, "data": {"code": mapped}}


def _encode_still_mp4(
    png: Path,
    output_mp4: Path,
    *,
    duration_seconds: float,
    fps: int,
    record_size: tuple[int, int],
    log_path: Path | None,
) -> None:
    rw, rh = record_size
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-loop", "1", "-i", str(png),
        "-t", f"{duration_seconds:.3f}",
        "-r", str(fps),
        "-vf", f"scale={rw}:{rh}:flags=lanczos",
        "-pix_fmt", "yuv420p",
        str(output_mp4),
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    except subprocess.TimeoutExpired as e:
        raise ReplayError("ffmpeg timed out encoding 1Game mp4") from e
    if log_path is not None:
        log_path.write_text((proc.stdout or "") + (proc.stderr or ""))
    if proc.returncode != 0:
        raise ReplayError(f"ffmpeg failed: {(proc.stderr or proc.stdout)[-2000:]}")

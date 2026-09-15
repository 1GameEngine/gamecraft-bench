"""Replay a demo trace against a 1Game project and encode an mp4.

Host path only: system ``1gameplay`` (not ``pnpm exec``), napi
``frame screenshot`` (not Xvfb / replay.html). Event injection uses
instantaneous ``pointer.*`` / ``keydown`` / ``keyup`` macros — never
the multi-frame ``--click`` / ``keypress`` helpers.

The mp4 is a **timeline slideshow**: ``frames list`` + screenshots at
~0.5s engine-time cadence, then ffmpeg concat. Do **not** loop the
last PNG for the whole trace (``-loop 1``).

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

# Judge-facing cadence. Not per logic frame — sparse seq screenshots.
SCREENSHOT_CADENCE_SECONDS = 0.5

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
    screenshot_cadence_seconds: float = SCREENSHOT_CADENCE_SECONDS,
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
    cadence_s = max(0.1, float(screenshot_cadence_seconds))
    rw, rh = record_size if record_size is not None else viewport

    with tempfile.TemporaryDirectory(prefix="gc1game-replay-", dir="/tmp") as tmp:
        tmp_path = Path(tmp)
        archive = tmp_path / "demo.1gamerecord"
        shots_dir = tmp_path / "shots"
        shots_dir.mkdir()
        play_log = (log_dir / "1gameplay.log") if log_dir else None
        _run_cli(
            [play, "create", "--entry", str(entry), "--out", str(archive)],
            cwd=project_dir,
            env=env,
            timeout=300,
            log_path=play_log,
        )
        _apply_events(
            play, archive, events, fps=fps, duration_frames=replay_frames,
            cwd=project_dir, env=env, log_path=play_log,
        )
        list_out = _run_cli(
            [play, "frames", "list", str(archive)],
            cwd=project_dir,
            env=env,
            timeout=120,
            log_path=play_log,
        )
        rows = parse_frames_list(list_out)
        seqs = sample_timeline_seqs(
            rows, interval_ms=int(round(cadence_s * 1000)),
        )
        pngs: list[Path] = []
        for i, seq in enumerate(seqs):
            png = shots_dir / f"shot_{i:04d}_seq{seq}.png"
            _run_cli(
                [
                    play, "frame", "screenshot", str(archive),
                    "--at", str(seq),
                    "--out", str(png),
                    "--width", str(w),
                    "--height", str(h),
                ],
                cwd=project_dir,
                env=env,
                timeout=120,
                log_path=play_log,
            )
            if not png.is_file() or png.stat().st_size <= 0:
                raise ReplayError(
                    f"1gameplay frame screenshot --at {seq} produced an empty PNG"
                )
            pngs.append(png)
        durations = slide_durations(
            seqs, rows, total_seconds=trace_seconds, cadence_seconds=cadence_s,
        )
        encode_slideshow_mp4(
            pngs,
            output_mp4,
            durations_seconds=durations,
            fps=fps,
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


def parse_frames_list(stdout: str) -> list[tuple[int, int]]:
    """Return ``(seq, tickedTimeMs)`` from ``1gameplay frames list`` JSON."""
    try:
        data = json.loads(stdout)
    except json.JSONDecodeError as e:
        raise ReplayError(f"frames list was not JSON: {e}") from e
    result = data.get("result") if isinstance(data, dict) else None
    rows = (result or {}).get("rows") if isinstance(result, dict) else None
    if not isinstance(rows, list) or not rows:
        raise ReplayError("frames list returned no rows")
    out: list[tuple[int, int]] = []
    for row in rows:
        if isinstance(row, dict):
            seq = int(row["seq"])
            ticked = int(row.get("tickedTimeMs") or 0)
        elif isinstance(row, (list, tuple)) and len(row) >= 3:
            seq = int(row[0])
            ticked = int(row[2])
        else:
            raise ReplayError(f"unrecognized frames list row: {row!r}")
        out.append((seq, ticked))
    out.sort(key=lambda item: item[0])
    return out


def sample_timeline_seqs(
    rows: list[tuple[int, int]],
    *,
    interval_ms: int = 500,
) -> list[int]:
    """First frame, then ~interval_ms of engine time, then last — not every seq."""
    if not rows:
        raise ReplayError("cannot sample an empty frames list")
    interval_ms = max(1, int(interval_ms))
    picked: list[int] = [rows[0][0]]
    last_t = rows[0][1]
    for seq, ticked in rows[1:]:
        if ticked - last_t >= interval_ms:
            picked.append(seq)
            last_t = ticked
    last_seq = rows[-1][0]
    if picked[-1] != last_seq:
        picked.append(last_seq)
    return picked


def slide_durations(
    seqs: list[int],
    rows: list[tuple[int, int]],
    *,
    total_seconds: float,
    cadence_seconds: float,
) -> list[float]:
    """Per-PNG hold times summing to ``total_seconds``."""
    if not seqs:
        raise ReplayError("no screenshot seqs")
    t_by_seq = {seq: ticked for seq, ticked in rows}
    times = [t_by_seq.get(seq, 0) / 1000.0 for seq in seqs]
    n = len(seqs)
    if n == 1:
        return [max(total_seconds, cadence_seconds)]
    durs: list[float] = []
    for i in range(n - 1):
        gap = times[i + 1] - times[i]
        durs.append(max(cadence_seconds / 2.0, gap if gap > 0 else cadence_seconds))
    used = sum(durs)
    last = max(cadence_seconds / 2.0, total_seconds - used)
    durs.append(last)
    return durs


def encode_slideshow_mp4(
    pngs: list[Path],
    output_mp4: Path,
    *,
    durations_seconds: list[float],
    fps: int,
    record_size: tuple[int, int],
    log_path: Path | None,
) -> None:
    """Concat stills with per-slide duration. Never ``ffmpeg -loop 1``."""
    if not pngs:
        raise ReplayError("no PNGs to encode")
    if len(pngs) != len(durations_seconds):
        raise ReplayError("png count must match slide durations")
    rw, rh = record_size
    list_path = pngs[0].parent / "concat.txt"
    lines: list[str] = []
    for png, dur in zip(pngs, durations_seconds):
        lines.append(f"file '{png.resolve()}'")
        lines.append(f"duration {max(0.05, float(dur)):.3f}")
    # concat demuxer needs the last file repeated.
    lines.append(f"file '{pngs[-1].resolve()}'")
    list_path.write_text("\n".join(lines) + "\n")
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "concat", "-safe", "0", "-i", str(list_path),
        "-vf", f"scale={rw}:{rh}:flags=lanczos,fps={fps}",
        "-pix_fmt", "yuv420p",
        str(output_mp4),
    ]
    if any(part == "-loop" for part in cmd):
        raise ReplayError("internal error: still-loop ffmpeg argv is forbidden")
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    except subprocess.TimeoutExpired as e:
        raise ReplayError("ffmpeg timed out encoding 1Game mp4") from e
    if log_path is not None:
        log_path.write_text((proc.stdout or "") + (proc.stderr or ""))
    if proc.returncode != 0:
        raise ReplayError(f"ffmpeg failed: {(proc.stderr or proc.stdout)[-2000:]}")


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
                    "--surface", "display",
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
        [
            play, "step", str(archive),
            "--surface", "display",
            "--ms", str(ms), "--repeat", "1",
        ],
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

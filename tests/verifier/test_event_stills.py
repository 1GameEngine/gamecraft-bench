"""Event stills: Godot x11grab PNG, 1Game post-click +2 ticks, score skips mp4 sample."""

from __future__ import annotations

import inspect
import json
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from gamecraft_bench.verifier import replay as replay_godot
from gamecraft_bench.verifier import replay_1game as r1
from gamecraft_bench.verifier.replay import ReplayResult
from gamecraft_bench.verifier.score import _copy_event_stills, _judge_stills, stills_for_judge


def test_grab_x11_still_is_single_frame() -> None:
    src = inspect.getsource(replay_godot._grab_x11_still)
    assert "-frames:v" in src
    assert "x11grab" in src
    assert "1" in src


def test_godot_replay_writes_event_png_names() -> None:
    src = inspect.getsource(replay_godot.replay_trace)
    assert "event_{len(stills):04d}.png" in src or 'f"event_{len(stills):04d}.png"' in src
    assert "x11_post_event" in src
    assert "_grab_x11_still" in src


def test_apply_events_settles_two_empty_ticks_then_still() -> None:
    calls: list[list[str]] = []
    stills: list[int] = []

    def fake_run(argv, **kwargs):
        calls.append(list(argv))
        return json.dumps({"meta": {"statePointer": {"lastTickedTimeMs": 16 * len(calls)}}})

    def on_event(ticked_ms):
        stills.append(int(ticked_ms))

    with patch.object(r1, "_run_cli", side_effect=fake_run):
        r1._apply_events(
            "1gameplay",
            Path("/tmp/demo.1gamerecord"),
            [{"frame": 0, "type": "mouse_click", "x": 1, "y": 2}],
            fps=30,
            duration_frames=4,
            cwd=Path("/tmp"),
            env={},
            log_path=None,
            on_event_still=on_event,
        )
    event_steps = [c for c in calls if "--event" in c]
    empty_steps = [c for c in calls if c[1] == "step" and "--event" not in c]
    assert len(event_steps) == 2
    assert len(empty_steps) >= 2
    assert len(stills) == 1
    last_event_idx = max(i for i, c in enumerate(calls) if "--event" in c)
    first_empty_after = next(
        i for i, c in enumerate(calls)
        if i > last_event_idx and c[1] == "step" and "--event" not in c
    )
    assert first_empty_after > last_event_idx
    assert stills


def test_judge_stills_never_samples_1game_mp4(tmp_path: Path) -> None:
    mp4 = tmp_path / "demo.mp4"
    mp4.write_bytes(b"not-a-video")
    still = tmp_path / "event_0000.png"
    still.write_bytes(b"\x89PNG\r\n\x1a\n" + b"x" * 32)
    rr = ReplayResult(
        output_mp4=mp4,
        duration_seconds=1.0,
        godot_returncode=0,
        still_paths=(still,),
        still_source="1game_post_event_plus2",
    )
    with patch("gamecraft_bench.verifier.score._sample_frames") as sample:
        frames, source = _judge_stills(
            rr,
            tmp_path / "frames",
            engine="1game",
            duration_seconds=1.0,
            interval_seconds=0.5,
            max_window_seconds=20.0,
            seed="01",
        )
    sample.assert_not_called()
    assert source == "1game_post_event_plus2"
    assert len(frames) == 1
    assert frames[0].name == "event_0000.png"


def test_judge_stills_1game_without_paths_skips_sample(tmp_path: Path) -> None:
    rr = ReplayResult(
        output_mp4=tmp_path / "demo.mp4",
        duration_seconds=1.0,
        godot_returncode=0,
    )
    with patch("gamecraft_bench.verifier.score._sample_frames") as sample:
        frames, source = _judge_stills(
            rr,
            tmp_path / "frames",
            engine="1game",
            duration_seconds=1.0,
            interval_seconds=0.5,
            max_window_seconds=20.0,
            seed="01",
        )
    sample.assert_not_called()
    assert frames == []
    assert source == "missing_event_stills"


def test_copy_event_stills_keeps_event_names(tmp_path: Path) -> None:
    src = tmp_path / "event_0001.png"
    src.write_bytes(b"\x89PNG\r\n\x1a\n" + b"y" * 16)
    copied = _copy_event_stills((src,), tmp_path / "frames")
    assert copied[0].name == "event_0001.png"


def test_score_project_source_routes_1game_off_mp4() -> None:
    from gamecraft_bench.verifier import score as score_mod

    src = inspect.getsource(score_mod._judge_stills)
    assert "engine == \"1game\"" in src
    assert "_sample_frames" in src
    assert "still_paths" in src


def _empty_godot_rr(tmp_path: Path) -> ReplayResult:
    return ReplayResult(
        output_mp4=tmp_path / "demo.mp4",
        duration_seconds=1.0,
        godot_returncode=0,
    )


def test_host_godot_without_stills_skips_mp4_sample(tmp_path: Path) -> None:
    rr = _empty_godot_rr(tmp_path)
    with patch("gamecraft_bench.verifier.score._judge_stills") as inner:
        with patch("gamecraft_bench.verifier.score._sample_frames") as sample:
            frames, source = stills_for_judge(
                rr,
                tmp_path / "frames",
                requested_engine="godot",
                resolved_engine="godot",
                duration_seconds=1.0,
                interval_seconds=0.5,
                max_window_seconds=20.0,
                seed="01",
            )
    inner.assert_not_called()
    sample.assert_not_called()
    assert frames == []
    assert source == "missing_event_stills"


def test_harbor_auto_godot_without_stills_still_samples(tmp_path: Path) -> None:
    rr = _empty_godot_rr(tmp_path)
    (tmp_path / "demo.mp4").write_bytes(b"not-a-video")
    with patch(
        "gamecraft_bench.verifier.score._sample_frames",
        return_value=[tmp_path / "frame.png"],
    ) as sample:
        frames, source = stills_for_judge(
            rr,
            tmp_path / "frames",
            requested_engine=None,
            resolved_engine="godot",
            duration_seconds=1.0,
            interval_seconds=0.5,
            max_window_seconds=20.0,
            seed="01",
        )
    sample.assert_called_once()
    assert source == "mp4_sample"
    assert frames == [tmp_path / "frame.png"]


def test_every_1game_step_captures_console() -> None:
    """The probe contract rides on worker console output, which defaults to warn."""
    calls: list[list[str]] = []

    def fake_run(argv, **kwargs):
        calls.append(list(argv))
        return json.dumps({"meta": {"statePointer": {"lastTickedTimeMs": 16 * len(calls)}}})

    with patch.object(r1, "_run_cli", side_effect=fake_run):
        r1._apply_events(
            "1gameplay",
            Path("demo.1gamerecord"),
            [{"frame": 3, "type": "mouse_click", "x": 10, "y": 20}],
            fps=30,
            duration_frames=12,
            cwd=Path("."),
            env={},
            log_path=None,
        )

    steps = [c for c in calls if "step" in c]
    assert steps
    for call in steps:
        assert "--capture-console" in call
        assert call[call.index("--capture-console") + 1] == "log"

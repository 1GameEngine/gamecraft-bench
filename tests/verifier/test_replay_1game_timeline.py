"""Timeline 1Game replay: no still-loop; sparse seq sampling; slideshow mp4."""

from __future__ import annotations

import hashlib
import inspect
import shutil
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from gamecraft_bench.verifier import replay_1game as r1


def test_encode_still_mp4_removed() -> None:
    assert not hasattr(r1, "_encode_still_mp4")
    replay_src = inspect.getsource(r1.replay_trace)
    assert "--at\", \"last\"" not in replay_src
    encode_src = inspect.getsource(r1.encode_slideshow_mp4)
    assert '"-f", "concat"' in encode_src


def test_parse_and_sample_timeline_skips_dense_seqs() -> None:
    stdout = """
    {"schema":"1gameplay.frames.list.v1","ok":true,
     "result":{"columns":["seq","deltaMs","tickedTimeMs","events","storeCursor"],
               "rows":[
                 {"seq":0,"deltaMs":0,"tickedTimeMs":0},
                 {"seq":1,"deltaMs":16,"tickedTimeMs":16},
                 {"seq":2,"deltaMs":16,"tickedTimeMs":32},
                 {"seq":10,"deltaMs":500,"tickedTimeMs":500},
                 {"seq":11,"deltaMs":16,"tickedTimeMs":516},
                 {"seq":20,"deltaMs":500,"tickedTimeMs":1000}
               ]}}
    """
    rows = r1.parse_frames_list(stdout)
    seqs = r1.sample_timeline_seqs(rows, interval_ms=500)
    assert seqs == [0, 10, 20]
    assert seqs != [s for s, _ in rows]


def test_parse_frames_list_array_rows() -> None:
    stdout = '{"result":{"rows":[[3,16,48],[4,16,64]]}}'
    rows = r1.parse_frames_list(stdout)
    assert rows == [(3, 48), (4, 64)]
    assert r1.sample_timeline_seqs(rows, interval_ms=500) == [3, 4]


def test_slideshow_ffmpeg_has_no_loop(tmp_path: Path) -> None:
    a = tmp_path / "a.png"
    b = tmp_path / "b.png"
    _color_png(a, "0x2563eb")
    _color_png(b, "0xf97316")
    out = tmp_path / "out.mp4"
    r1.encode_slideshow_mp4(
        [a, b],
        out,
        durations_seconds=[0.5, 0.5],
        fps=30,
        record_size=(64, 64),
        log_path=None,
    )
    assert out.is_file() and out.stat().st_size > 0
    extracted = tmp_path / "extracted"
    extracted.mkdir()
    subprocess.run(
        [
            "ffmpeg", "-y", "-loglevel", "error",
            "-i", str(out),
            "-vf", "fps=2",
            "-frames:v", "2",
            str(extracted / "f%02d.png"),
        ],
        check=True,
        capture_output=True,
    )
    frames = sorted(extracted.glob("f*.png"))
    assert len(frames) >= 2
    hashes = [_sha(p) for p in frames]
    assert hashes[0] != hashes[-1]


def test_replay_trace_mock_uses_seq_screenshots_not_last_loop(
    tmp_path: Path,
) -> None:
    proj = tmp_path / "g"
    (proj / "src").mkdir(parents=True)
    (proj / "src" / "game.tsx").write_text("x")
    trace = tmp_path / "t.json"
    trace.write_text('{"duration_frames": 45, "events": []}')
    out = tmp_path / "out.mp4"
    calls: list[list[str]] = []

    def fake_run(argv, **kwargs):
        calls.append(list(argv))
        if argv[1] == "frames" and argv[2] == "list":
            return (
                '{"result":{"rows":['
                '{"seq":0,"tickedTimeMs":0},'
                '{"seq":5,"tickedTimeMs":500},'
                '{"seq":10,"tickedTimeMs":1000}'
                "]}}"
            )
        if argv[1] == "frame" and argv[2] == "screenshot":
            dest = Path(argv[argv.index("--out") + 1])
            color = "0x2563eb" if argv[argv.index("--at") + 1] == "0" else "0xf97316"
            _color_png(dest, color)
            return ""
        return ""

    with patch.object(r1, "_require_1gameplay", return_value="1gameplay"), \
         patch.object(r1, "_run_cli", side_effect=fake_run):
        result = r1.replay_trace(
            project_dir=proj,
            trace_path=trace,
            output_mp4=out,
            record_size=(64, 64),
        )
    assert result.output_mp4 == out
    shot_calls = [c for c in calls if c[1:3] == ["frame", "screenshot"]]
    assert shot_calls
    ats = [c[c.index("--at") + 1] for c in shot_calls]
    assert "last" not in ats
    assert ats == ["0", "5", "10"]
    assert out.is_file() and out.stat().st_size > 0


def _color_png(path: Path, color: str) -> None:
    if shutil.which("ffmpeg") is None:
        pytest.skip("ffmpeg required")
    subprocess.run(
        [
            "ffmpeg", "-y", "-loglevel", "error",
            "-f", "lavfi", "-i", f"color=c={color}:s=64x64:d=0.1",
            "-frames:v", "1",
            str(path),
        ],
        check=True,
        capture_output=True,
    )


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

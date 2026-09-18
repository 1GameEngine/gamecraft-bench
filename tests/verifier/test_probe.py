"""Engine-neutral probe oracle: parsing, beat assertions, void semantics."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from gamecraft_bench.verifier.probe import (
    ProbeError,
    evaluate_demo,
    evaluate_output_dir,
    evaluate_run,
    load_probe_schema,
    parse_probe_lines,
    read_demo_logs,
)

_SCHEMA = {
    "probe_schema_version": 1,
    "slug": "demo",
    "beats": [
        {"id": "title", "assert": {"collected": {"eq": 0}}},
        {"id": "examine_first", "assert": {"collected": {"min": 1}}},
        {"id": "ending", "assert": {"ending": {"not_null": True}}},
    ],
}


def _log(*records: dict) -> str:
    lines = ["Godot Engine v4.6.2 - https://godotengine.org"]
    for rec in records:
        lines.append(json.dumps(rec))
    lines.append("WARNING: unrelated engine chatter")
    return "\n".join(lines)


def test_parse_ignores_noise_and_bad_json() -> None:
    text = "\n".join(
        [
            "boot line",
            '{"probe": 1, "beat": "title", "flags": {"collected": 0}}',
            '{"probe": 1, "beat":',
            '{"probe": 0, "beat": "ignored"}',
            'prefix {"probe": 1, "beat": "ending", "flags": {"ending": "kept"}} suffix',
        ]
    )
    events = parse_probe_lines(text)
    assert [e.beat for e in events] == ["title", "ending"]
    assert events[1].flags == {"ending": "kept"}


def test_full_pass_run() -> None:
    log = _log(
        {"probe": 1, "beat": "title", "flags": {"collected": 0}},
        {"probe": 1, "beat": "examine_first", "flags": {"collected": 1}},
        {"probe": 1, "beat": "ending", "flags": {"ending": "kept"}},
    )
    outcome = evaluate_run(schema=_SCHEMA, build_ok=True, demo_logs={"01": log})
    assert outcome.void is False
    assert outcome.reach == 1.0
    assert outcome.state == 1.0


def test_missing_beat_is_unseen_not_failed_assertion() -> None:
    log = _log({"probe": 1, "beat": "title", "flags": {"collected": 0}})
    demo = evaluate_demo("01", _SCHEMA, log)
    by_id = {b.beat_id: b for b in demo.beats}
    assert by_id["ending"].seen is False
    assert by_id["ending"].failures == ()
    assert demo.reach == pytest.approx(1 / 3)
    assert demo.state == pytest.approx(1 / 3)


def test_failed_assertion_reports_reason() -> None:
    log = _log(
        {"probe": 1, "beat": "title", "flags": {"collected": 3}},
        {"probe": 1, "beat": "examine_first", "flags": {"collected": 0}},
        {"probe": 1, "beat": "ending", "flags": {"ending": None}},
    )
    demo = evaluate_demo("01", _SCHEMA, log)
    assert demo.reach == 1.0
    assert demo.state == 0.0
    joined = " ".join(f for b in demo.beats for f in b.failures)
    assert "collected=3" in joined
    assert "ending is null/missing" in joined


def test_last_record_per_beat_wins() -> None:
    log = _log(
        {"probe": 1, "beat": "examine_first", "flags": {"collected": 0}},
        {"probe": 1, "beat": "examine_first", "flags": {"collected": 2}},
    )
    demo = evaluate_demo("01", _SCHEMA, log)
    by_id = {b.beat_id: b for b in demo.beats}
    assert by_id["examine_first"].passed is True


def test_no_probe_output_is_void_not_zero() -> None:
    outcome = evaluate_run(
        schema=_SCHEMA, build_ok=True, demo_logs={"01": "engine boot only"}
    )
    assert outcome.void is True
    assert outcome.state is None
    assert outcome.reach is None
    assert "no probe output" in outcome.void_reason


def test_build_failure_is_not_void() -> None:
    outcome = evaluate_run(schema=_SCHEMA, build_ok=False, demo_logs={})
    assert outcome.build_ok is False
    assert outcome.void is False
    assert outcome.state == 0.0


def test_partial_void_demo_is_dropped_not_scored_zero() -> None:
    good = _log(
        {"probe": 1, "beat": "title", "flags": {"collected": 0}},
        {"probe": 1, "beat": "examine_first", "flags": {"collected": 1}},
        {"probe": 1, "beat": "ending", "flags": {"ending": "left"}},
    )
    outcome = evaluate_run(
        schema=_SCHEMA, build_ok=True, demo_logs={"01": good, "02": "nothing"}
    )
    assert outcome.void is False
    assert [d.demo_id for d in outcome.demos] == ["01"]
    assert outcome.state == 1.0


def test_schema_validation_rejects_bad_operators(tmp_path: Path) -> None:
    bad = dict(_SCHEMA)
    bad["beats"] = [{"id": "title", "assert": {"collected": {"gt": 1}}}]
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(bad))
    with pytest.raises(ProbeError, match="unknown operators"):
        load_probe_schema(path)


def test_shipped_keepsake_schema_loads() -> None:
    root = Path(__file__).resolve().parents[2]
    schema = load_probe_schema(root / "host_probes" / "visualnovel-keepsake.json")
    assert schema["slug"] == "visualnovel-keepsake"
    assert [b["id"] for b in schema["beats"]][0] == "title"


def test_evaluate_output_dir_builds_v2_cell(tmp_path: Path) -> None:
    schema_path = tmp_path / "schema.json"
    schema_path.write_text(json.dumps(_SCHEMA))
    logs = tmp_path / "demos" / "01" / "logs"
    logs.mkdir(parents=True)
    (logs / "godot.log").write_text(
        _log(
            {"probe": 1, "beat": "title", "flags": {"collected": 0}},
            {"probe": 1, "beat": "examine_first", "flags": {"collected": 2}},
            {"probe": 1, "beat": "ending", "flags": {"ending": "kept"}},
        )
    )
    (tmp_path / "breakdown.json").write_text(
        json.dumps({"build_ok": True, "still_source": "x11_post_event"})
    )
    cell = evaluate_output_dir(tmp_path, schema_path)
    assert cell["void"] is False
    assert cell["state"] == 1.0
    assert cell["still_source"] == "x11_post_event"
    assert cell["trace_author"] == "generator"


def test_evaluate_output_dir_drops_mp4_sample_still_source(tmp_path: Path) -> None:
    schema_path = tmp_path / "schema.json"
    schema_path.write_text(json.dumps(_SCHEMA))
    logs = tmp_path / "demos" / "01" / "logs"
    logs.mkdir(parents=True)
    (logs / "godot.log").write_text(
        _log({"probe": 1, "beat": "title", "flags": {"collected": 0}})
    )
    (tmp_path / "breakdown.json").write_text(
        json.dumps({"build_ok": True, "still_source": "mp4_sample"})
    )
    cell = evaluate_output_dir(tmp_path, schema_path)
    assert "still_source" not in cell


def test_read_demo_logs_merges_engine_logs(tmp_path: Path) -> None:
    logs = tmp_path / "demos" / "01" / "logs"
    logs.mkdir(parents=True)
    (logs / "godot.log").write_text('{"probe": 1, "beat": "title", "flags": {}}')
    (logs / "1gameplay.log").write_text("1game chatter")
    collected = read_demo_logs(tmp_path)
    assert "01" in collected
    assert "title" in collected["01"]
    assert "1game chatter" in collected["01"]


_MULTIPATH = {
    "probe_schema_version": 1,
    "slug": "t",
    "beats": [
        {"id": "title", "assert": {}},
        {"id": "gate_locked", "assert": {"gate": {"eq": "locked"}}},
        {"id": "ending", "assert": {"ending": {"not_null": True}}},
    ],
}


def _line(beat: str, **flags) -> str:
    return json.dumps({"probe": 1, "beat": beat, "flags": flags})


def test_beats_are_task_requirements_not_per_trace() -> None:
    """A locked-gate trace is not supposed to reach the ending."""
    outcome = evaluate_run(
        schema=_MULTIPATH,
        build_ok=True,
        demo_logs={
            "locked": "\n".join([_line("title"), _line("gate_locked", gate="locked")]),
            "ending": "\n".join([_line("title"), _line("ending", ending="kept")]),
        },
    )
    assert outcome.reach == 1.0
    assert outcome.state == 1.0


def test_state_counts_a_beat_failed_wherever_it_failed() -> None:
    outcome = evaluate_run(
        schema=_MULTIPATH,
        build_ok=True,
        demo_logs={
            "good": "\n".join([_line("title"), _line("gate_locked", gate="locked")]),
            "bad": "\n".join([_line("title"), _line("gate_locked", gate="open")]),
        },
    )
    assert outcome.reach == 2 / 3
    assert outcome.state == 0.5


def test_unreached_beats_do_not_dilute_state() -> None:
    outcome = evaluate_run(
        schema=_MULTIPATH,
        build_ok=True,
        demo_logs={"only": _line("title")},
    )
    assert outcome.reach == 1 / 3
    assert outcome.state == 1.0

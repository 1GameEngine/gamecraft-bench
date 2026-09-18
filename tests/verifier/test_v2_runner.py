"""v2 cell scoring and ledger assembly (no engines involved)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from gamecraft_bench.verifier.host_paths import HostPathError
from gamecraft_bench.verifier.host_record import validate_record
from gamecraft_bench.verifier.v2_runner import assemble, cell_path, score_cell

_EID = "h-20260918t031808z-27f3940d"
_SCHEMA = {
    "probe_schema_version": 1,
    "slug": "visualnovel-keepsake",
    "beats": [
        {"id": "title", "assert": {"collected": {"eq": 0}}},
        {"id": "ending", "assert": {"ending": {"not_null": True}}},
    ],
}


def _run_dir(tmp_path: Path) -> Path:
    run = tmp_path / _EID
    (run / "cells").mkdir(parents=True)
    return run


def _write_record(run: Path, arm: str, lines: list[dict], build_ok: bool = True) -> Path:
    logs = run / "record" / "visualnovel-keepsake" / arm / "r1" / "demos" / "01" / "logs"
    logs.mkdir(parents=True)
    (logs / "godot.log").write_text("\n".join(json.dumps(x) for x in lines))
    (run / "record" / "visualnovel-keepsake" / arm / "r1" / "breakdown.json").write_text(
        json.dumps({"build_ok": build_ok, "still_source": "x11_post_event"})
    )
    return run / "record" / "visualnovel-keepsake" / arm / "r1"


def test_score_cell_writes_named_file(tmp_path: Path) -> None:
    run = _run_dir(tmp_path)
    _write_record(
        run,
        "godot",
        [
            {"probe": 1, "beat": "title", "flags": {"collected": 0}},
            {"probe": 1, "beat": "ending", "flags": {"ending": "kept"}},
        ],
    )
    schema_path = tmp_path / "schema.json"
    schema_path.write_text(json.dumps(_SCHEMA))
    cell = score_cell(
        run_dir=run, arm="godot", repeat=1, model="agent-x", probe_schema=schema_path
    )
    assert cell["state"] == 1.0
    assert cell["arm"] == "godot"
    assert cell_path(run, "godot", 1, "agent-x", slug="visualnovel-keepsake").is_file()


def test_assemble_produces_promotable_payload(tmp_path: Path) -> None:
    run = _run_dir(tmp_path)
    schema_path = tmp_path / "schema.json"
    schema_path.write_text(json.dumps(_SCHEMA))
    for arm in ("godot", "1game_eco", "1game_bare"):
        _write_record(
            run,
            arm,
            [
                {"probe": 1, "beat": "title", "flags": {"collected": 0}},
                {"probe": 1, "beat": "ending", "flags": {"ending": "kept"}},
            ],
        )
        score_cell(
            run_dir=run, arm=arm, repeat=1, model="agent-x", probe_schema=schema_path
        )
    payload = assemble(
        run_dir=run, slug="visualnovel-keepsake", prereg_frozen_at="deadbeef"
    )
    assert {c["arm"] for c in payload["cells"]} == {"godot", "1game_eco", "1game_bare"}
    assert validate_record(payload)


def test_assemble_strips_numbers_from_void_cells(tmp_path: Path) -> None:
    run = _run_dir(tmp_path)
    schema_path = tmp_path / "schema.json"
    schema_path.write_text(json.dumps(_SCHEMA))
    _write_record(run, "godot", [{"note": "no probe output at all"}])
    cell = score_cell(
        run_dir=run, arm="godot", repeat=1, model="agent-x", probe_schema=schema_path
    )
    assert cell["void"] is True
    payload = assemble(
        run_dir=run, slug="visualnovel-keepsake", prereg_frozen_at="deadbeef"
    )
    assert payload["cells"][0]["state"] is None
    assert validate_record(payload)


def test_assemble_requires_cells(tmp_path: Path) -> None:
    run = _run_dir(tmp_path)
    with pytest.raises(HostPathError, match="no cells"):
        assemble(run_dir=run, slug="s", prereg_frozen_at="x")

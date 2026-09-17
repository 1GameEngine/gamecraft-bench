"""Host path gates, ledger O_EXCL writer, dashboard $HOME refuse."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from gamecraft_bench.dashboard.manager import SessionManager
from gamecraft_bench.verifier import compare as compare_mod
from gamecraft_bench.verifier.host_paths import (
    HostPathError,
    assert_not_ledger_write,
    resolve_jobs_root,
)
from gamecraft_bench.verifier.host_record import validate_record, write_ledger

_EID = "h-20260917t134612z-k4n9xq2p"
_USER = "a" * 64


def _ok_payload(**arm_over: dict) -> dict:
    godot = {
        "void": False,
        "still_source": "x11_post_event",
        "trace_author": "generator",
        "M3": 1,
    }
    onegame = {
        "void": False,
        "still_source": "1game_post_event_plus2",
        "trace_author": "generator",
        "M3": 1,
    }
    godot.update(arm_over.get("godot") or {})
    onegame.update(arm_over.get("onegame") or {})
    return {
        "experiment_id": _EID,
        "claim_class": "host_product_stack_diagnostic",
        "slug": "visualnovel-keepsake",
        "protocol": "cursor-subagent-png-excerpt",
        "cite_columns": False,
        "not_an_engine_ranking": True,
        "user_sha256": _USER,
        "parent_surface": {"ids": ["M3"], "layout": "split_cards"},
        "arms": {"godot": godot, "1game": onegame},
    }


def test_jobs_root_refuses_home_equality_not_prefix(tmp_path: Path) -> None:
    home = Path.home().resolve()
    with pytest.raises(HostPathError):
        resolve_jobs_root(home)
    with pytest.raises(HostPathError):
        resolve_jobs_root(home / ".")
    ok = resolve_jobs_root(tmp_path / "gamecraft-bench-jobs")
    assert ok == (tmp_path / "gamecraft-bench-jobs").resolve()


def test_list_trials_home_is_empty() -> None:
    assert SessionManager.list_trials(Path.home()) == []


def test_refuse_ledger_write(tmp_path: Path) -> None:
    dest = tmp_path / "host_excerpt_ledger" / "table.json"
    dest.parent.mkdir()
    with pytest.raises(HostPathError):
        assert_not_ledger_write(dest)


def test_compare_out_ledger_exits_two(tmp_path: Path) -> None:
    godot_dir = tmp_path / "godot"
    onegame_dir = tmp_path / "onegame"
    godot_dir.mkdir()
    onegame_dir.mkdir()
    stub = {
        "reward": 0.0,
        "engine": "godot",
        "judge": {"name": "StubJudge", "model": "1.0"},
        "comparable": False,
        "build_ok": True,
        "requirements": [{"id": "M3", "aggregated": 0.0}],
        "media": "x11grab",
    }
    (godot_dir / "breakdown.json").write_text(json.dumps(stub))
    stub_1g = dict(stub, engine="1game", media="slideshow")
    (onegame_dir / "breakdown.json").write_text(json.dumps(stub_1g))
    out = tmp_path / "host_excerpt_ledger" / "table.json"
    rc = compare_mod.main(
        ["--godot", str(godot_dir), "--onegame", str(onegame_dir), "--out", str(out)]
    )
    assert rc == 2
    assert not out.exists()


def test_write_ledger_excl_and_void(tmp_path: Path) -> None:
    dest = tmp_path / "host_excerpt_ledger" / f"{_EID}.json"
    write_ledger(dest, _ok_payload())
    assert dest.is_file()
    with pytest.raises(HostPathError):
        write_ledger(dest, _ok_payload())
    bad = tmp_path / "host_excerpt_ledger" / "h-20260917t134612z-zzzzzzzz.json"
    payload = _ok_payload(godot={"void": True})
    payload["experiment_id"] = bad.stem
    with pytest.raises(HostPathError, match="void"):
        validate_record(payload)


def test_mp4_sample_not_promotable() -> None:
    payload = _ok_payload(godot={"still_source": "mp4_sample"})
    with pytest.raises(HostPathError, match="still_source"):
        validate_record(payload)

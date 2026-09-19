"""Option-0 publication: frozen 72-cell ledger, no rescoring, no ranking."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from gamecraft_bench.verifier.analyze import load_cells, main as analyze_main, report
from gamecraft_bench.verifier.publication import (
    PublicationError,
    refuse_ledger_write,
    render_publication,
)

_ROOT = Path(__file__).resolve().parents[2]
_LEDGER = _ROOT / "host_excerpt_ledger" / "h-20260918t061615z-36781d69.json"
_SNAPSHOT = (
    _ROOT / "skills" / "gamecraft-host-dual-run" / "publication" / "72cell-analyze.json"
)
_MD = _ROOT / "skills" / "gamecraft-host-dual-run" / "publication" / "72cell.md"


def test_frozen_report_matches_committed_snapshot() -> None:
    cells = load_cells([_LEDGER])
    assert len(cells) == 72
    assert report(cells) == json.loads(_SNAPSHOT.read_text())


def test_publication_markdown_is_regenerated_from_report() -> None:
    cells = load_cells([_LEDGER])
    rendered = render_publication(cells)
    if not rendered.endswith("\n"):
        rendered += "\n"
    assert _MD.read_text() == rendered


def test_abstract_has_state_interval_not_reach_delta() -> None:
    abstract = _MD.read_text().split("## T0")[0]
    assert "0.0079" in abstract
    assert "[-0.0208, 0.0446]" in abstract
    assert "0.135" not in abstract
    assert "0.0052" not in abstract
    assert "两引擎" not in abstract
    assert "winner" not in abstract


def test_tables_are_partitioned_and_unranked() -> None:
    text = _MD.read_text()
    assert "## T0" in text
    assert "确认性（预注册 STATE）" in text
    assert "次终点（描述，非确认）" in text
    assert "不迁栈" in text
    assert "不作榜" in text
    assert "winner" not in text
    assert "STATE_cond" in text  # only as a prohibition
    t0 = text.split("## T0", 1)[1].split("## T1", 1)[0]
    assert t0.index("确认性") < t0.index("次终点")
    assert t0.index("| STATE |") < t0.index("| REACH |")


def test_refuses_writes_into_ledger_dir() -> None:
    with pytest.raises(PublicationError, match="host_excerpt_ledger"):
        refuse_ledger_write(_LEDGER)


def test_analyze_refuses_to_overwrite_ledger() -> None:
    with pytest.raises(SystemExit) as exc:
        analyze_main([str(_LEDGER), "--out", str(_LEDGER)])
    assert exc.value.code == 2


def test_publication_cli_writes_outside_ledger(tmp_path: Path) -> None:
    md = tmp_path / "out.md"
    js = tmp_path / "out.json"
    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "gamecraft_bench.verifier.publication",
            str(_LEDGER),
            "--md-out",
            str(md),
            "--json-out",
            str(js),
        ],
        cwd=_ROOT,
    )
    assert "未检出 STATE 差" in md.read_text()
    assert json.loads(js.read_text())["primary"]["difference"] == 0.0079

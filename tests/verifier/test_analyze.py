"""Analysis behaviour, verified on synthetic cells before any matrix data exists."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from gamecraft_bench.verifier.analyze import (
    paired_contrast,
    rates,
    report,
    slug_means,
)


def _cell(slug: str, arm: str, state: float | None, **over) -> dict:
    cell = {
        "slug": slug,
        "arm": arm,
        "repeat": over.pop("repeat", 1),
        "model": "m",
        "build_ok": True,
        "launch_ok": True,
        "void": False,
        "state": state,
        "reach": state,
    }
    cell.update(over)
    return cell


def test_void_cells_are_not_zeros() -> None:
    """A cell that failed to be measured is not a cell that scored nothing."""
    cells = [
        _cell("a", "godot", 1.0),
        _cell("a", "1game_eco", None, void=True, void_reason="no probe output"),
        _cell("a", "1game_eco", 1.0, repeat=2),
    ]
    assert slug_means(cells, "1game_eco", "state") == {"a": 1.0}
    assert rates(cells, "1game_eco")["void_rate"] == 0.5


def test_contaminated_cells_are_excluded_from_the_metric() -> None:
    cells = [
        _cell("a", "godot", 0.2, contaminated=True),
        _cell("a", "godot", 0.8, repeat=2),
    ]
    assert slug_means(cells, "godot", "state") == {"a": 0.8}
    assert rates(cells, "godot")["contaminated_rate"] == 0.5


def test_pairing_is_per_slug_not_pooled() -> None:
    """A slug with more surviving cells must not dominate the contrast."""
    cells = [
        _cell("easy", "godot", 1.0),
        _cell("easy", "godot", 1.0, repeat=2),
        _cell("easy", "godot", 1.0, repeat=3),
        _cell("easy", "1game_eco", 1.0),
        _cell("hard", "godot", 0.0),
        _cell("hard", "1game_eco", 1.0),
    ]
    result = paired_contrast(cells, arm_a="godot", arm_b="1game_eco")
    assert result["slugs"] == 2
    assert result["difference"] == -0.5
    assert result["per_slug"] == {"easy": 0.0, "hard": -1.0}


def test_slug_missing_from_one_arm_is_dropped_and_reported() -> None:
    cells = [
        _cell("a", "godot", 1.0),
        _cell("a", "1game_eco", 0.5),
        _cell("b", "godot", 1.0),
    ]
    result = paired_contrast(cells, arm_a="godot", arm_b="1game_eco")
    assert result["slugs"] == 1
    assert result["dropped_slugs"] == ["b"]


def test_interval_brackets_the_point_estimate() -> None:
    cells = []
    for i, (g, o) in enumerate([(1.0, 0.5), (0.9, 0.4), (0.8, 0.6), (1.0, 0.3)]):
        cells.append(_cell(f"s{i}", "godot", g))
        cells.append(_cell(f"s{i}", "1game_eco", o))
    result = paired_contrast(cells, arm_a="godot", arm_b="1game_eco")
    lo, hi = result["interval"]
    assert lo <= result["difference"] <= hi
    assert lo > 0


def test_interval_is_deterministic() -> None:
    cells = [
        _cell("a", "godot", 1.0), _cell("a", "1game_eco", 0.4),
        _cell("b", "godot", 0.7), _cell("b", "1game_eco", 0.9),
        _cell("c", "godot", 0.6), _cell("c", "1game_eco", 0.2),
    ]
    first = paired_contrast(cells, arm_a="godot", arm_b="1game_eco")
    second = paired_contrast(cells, arm_a="godot", arm_b="1game_eco")
    assert first["interval"] == second["interval"]


def test_no_shared_slug_reports_no_number() -> None:
    cells = [_cell("a", "godot", 1.0), _cell("b", "1game_eco", 1.0)]
    result = paired_contrast(cells, arm_a="godot", arm_b="1game_eco")
    assert result["difference"] is None
    assert result["interval"] is None


def test_report_has_no_ranking_or_single_number() -> None:
    cells = [
        _cell("a", "godot", 1.0),
        _cell("a", "1game_eco", 0.5),
    ]
    out = report(cells)
    assert set(out) == {
        "cells", "rates", "primary", "reach_primary"
    }
    assert "winner" not in out and "score" not in out
    assert "ablation" not in out


def test_report_keeps_ablation_when_bare_cells_exist() -> None:
    cells = [
        _cell("a", "godot", 1.0),
        _cell("a", "1game_eco", 0.5),
        _cell("a", "1game_bare", 0.0),
    ]
    out = report(cells)
    assert out["ablation"]["difference"] == 0.5
    assert "reach_ablation" in out


def test_build_and_launch_are_rates_not_folded_into_state() -> None:
    cells = [
        _cell("a", "godot", None, build_ok=True, launch_ok=False, void=False),
        _cell("a", "godot", 1.0, repeat=2),
    ]
    r = rates(cells, "godot")
    assert r["build_ok_rate"] == 1.0
    assert r["launch_ok_rate"] == 0.5
    assert slug_means(cells, "godot", "state") == {"a": 1.0}

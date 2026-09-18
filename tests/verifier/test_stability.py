"""Stability comparison logic (no engines involved)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from gamecraft_bench.verifier.stability import compare


def _sig(reach: float, state: float, **demos) -> dict:
    return {
        "void": False,
        "void_reason": "",
        "reach": reach,
        "state": state,
        "demos": {k: sorted(v) for k, v in demos.items()},
    }


_RUN = {"01": [("title", True, True), ("ending", True, True)]}


def test_identical_replays_are_stable() -> None:
    report = compare([_sig(1.0, 1.0, **_RUN)] * 3)
    assert report["stable"] is True
    assert report["unstable_demos"] == []


def test_a_flipped_beat_is_unstable() -> None:
    flipped = {"01": [("title", True, True), ("ending", False, False)]}
    report = compare([_sig(1.0, 1.0, **_RUN), _sig(0.5, 1.0, **flipped)])
    assert report["stable"] is False
    assert report["unstable_demos"] == ["01"]


def test_a_missing_demo_is_unstable() -> None:
    report = compare([_sig(1.0, 1.0, **_RUN), _sig(1.0, 1.0)])
    assert report["stable"] is False
    assert report["unstable_demos"] == ["01"]


def test_same_beats_but_different_metrics_is_unstable() -> None:
    """Catches a scoring path that drifts even when beats agree."""
    report = compare([_sig(1.0, 1.0, **_RUN), _sig(1.0, 0.5, **_RUN)])
    assert report["stable"] is False


def test_no_replays_is_not_stable() -> None:
    assert compare([])["stable"] is False

"""Relative traces get absolute frames; Harbor-shaped traces stay untouched."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from gamecraft_bench.verifier.trace_format import scheduled_events


def test_absolute_frames_are_left_alone() -> None:
    events, last = scheduled_events({
        "duration_frames": 40,
        "events": [
            {"frame": 10, "type": "wait"},
            {"frame": 20, "type": "mouse_click", "x": 1, "y": 2},
        ],
    })
    assert [e["frame"] for e in events] == [10, 20]
    assert last == 40


def test_relative_wait_and_click_accumulate() -> None:
    events, last = scheduled_events({
        "events": [
            {"type": "wait", "frames": 20},
            {"type": "mouse_click", "x": 640, "y": 360},
            {"type": "wait", "frames": 12},
        ],
    })
    assert [e["frame"] for e in events] == [0, 20, 21]
    assert last >= 33


def test_actions_alias_is_accepted() -> None:
    events, last = scheduled_events({
        "actions": [
            {"type": "mouse_click", "x": 1, "y": 2},
            {"type": "wait", "frames": 4},
        ],
    })
    assert events[0]["frame"] == 0
    assert last > 0


def test_empty_trace_is_zero_length() -> None:
    events, last = scheduled_events({})
    assert events == []
    assert last == 0

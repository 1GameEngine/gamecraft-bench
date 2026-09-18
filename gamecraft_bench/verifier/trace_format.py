"""Normalize generator traces so replay can schedule them.

Harbor traces stamp every event with an absolute ``frame``. Agents writing
from the v2 brief often emit a sequence instead: ``wait`` carries a relative
``frames`` count, and clicks have no ``frame`` at all. Requiring the Harbor
shape then ``KeyError``s before any demo log exists, which voids the cell as
an instrument failure even when the game built. Absolute stamps stay the
preferred form; this only fills ``frame`` when it is missing.
"""

from __future__ import annotations

from typing import Any


def scheduled_events(trace: dict[str, Any]) -> tuple[list[dict[str, Any]], int]:
    """Return events with a ``frame`` key, plus the last frame to hold until."""
    raw = trace.get("events")
    if not isinstance(raw, list) or not raw:
        raw = trace.get("actions")
    if not isinstance(raw, list):
        raw = []

    duration = int(trace.get("duration_frames") or 0)
    if all(isinstance(ev, dict) and "frame" in ev for ev in raw) and raw:
        events = [dict(ev) for ev in raw if isinstance(ev, dict)]
        last = max(int(ev["frame"]) for ev in events)
        return events, max(duration, last)

    events: list[dict[str, Any]] = []
    cursor = 0
    for item in raw:
        if not isinstance(item, dict):
            continue
        ev = dict(item)
        kind = str(ev.get("type", ""))
        wait = int(ev.get("frames") or 0)
        ev["frame"] = cursor
        events.append(ev)
        if kind == "wait":
            cursor += max(wait, 1)
        else:
            cursor += 1
    last = events[-1]["frame"] if events else 0
    return events, max(duration, last, cursor)

"""Engine-neutral behaviour oracle for the v2 engine-toolchain comparison.

Both arms emit the same contract from inside the game: after each input is
handled, one line of JSON on stdout (Godot ``print``) or in the 1gameplay log::

    {"probe": 1, "beat": "examine_first", "flags": {"collected": 1}}

The verifier reads those lines out of whatever log the replay captured, so the
primary metric never depends on pixels, camera timing, or a multimodal judge.
Missing output is ``void`` (instrument failure), not a game-quality zero.
"""

from __future__ import annotations

import dataclasses
import json
import re
from pathlib import Path
from typing import Any, Iterable

PROBE_SCHEMA_VERSION = 1
_LINE_RE = re.compile(r"\{.*?\"probe\"\s*:\s*1.*\}")


class ProbeError(ValueError):
    """Malformed probe schema."""


@dataclasses.dataclass(frozen=True)
class ProbeEvent:
    beat: str
    flags: dict[str, Any]


@dataclasses.dataclass(frozen=True)
class BeatOutcome:
    beat_id: str
    seen: bool
    passed: bool
    failures: tuple[str, ...] = ()


@dataclasses.dataclass(frozen=True)
class DemoOutcome:
    demo_id: str
    void: bool
    void_reason: str
    beats: tuple[BeatOutcome, ...]

    @property
    def reach(self) -> float:
        if not self.beats:
            return 0.0
        return sum(1 for b in self.beats if b.seen) / len(self.beats)

    @property
    def state(self) -> float:
        """Assertion pass rate over the whole expected beat list."""
        if not self.beats:
            return 0.0
        return sum(1 for b in self.beats if b.passed) / len(self.beats)


@dataclasses.dataclass(frozen=True)
class RunOutcome:
    """One (task, arm, repeat) cell. ``void`` cells never publish a number."""

    build_ok: bool
    launch_ok: bool
    void: bool
    void_reason: str
    demos: tuple[DemoOutcome, ...]

    @property
    def reach(self) -> float | None:
        return None if self.void else _mean(d.reach for d in self.demos)

    @property
    def state(self) -> float | None:
        return None if self.void else _mean(d.state for d in self.demos)


def _mean(values: Iterable[float]) -> float:
    items = list(values)
    return sum(items) / len(items) if items else 0.0


def parse_probe_lines(text: str) -> list[ProbeEvent]:
    """Pull probe records out of a mixed engine log. Bad lines are skipped."""
    events: list[ProbeEvent] = []
    for raw in text.splitlines():
        match = _LINE_RE.search(raw)
        if not match:
            continue
        try:
            payload = json.loads(match.group(0))
        except json.JSONDecodeError:
            continue
        beat = payload.get("beat")
        if not isinstance(beat, str) or not beat:
            continue
        flags = payload.get("flags")
        events.append(ProbeEvent(beat=beat, flags=flags if isinstance(flags, dict) else {}))
    return events


def load_probe_schema(path: Path) -> dict[str, Any]:
    schema = json.loads(Path(path).read_text())
    version = schema.get("probe_schema_version")
    if version != PROBE_SCHEMA_VERSION:
        raise ProbeError(f"probe_schema_version must be {PROBE_SCHEMA_VERSION}, got {version!r}")
    beats = schema.get("beats")
    if not isinstance(beats, list) or not beats:
        raise ProbeError("probe schema needs a non-empty beats list")
    seen: set[str] = set()
    for beat in beats:
        beat_id = beat.get("id") if isinstance(beat, dict) else None
        if not isinstance(beat_id, str) or not beat_id:
            raise ProbeError("every beat needs a string id")
        if beat_id in seen:
            raise ProbeError(f"duplicate beat id {beat_id!r}")
        seen.add(beat_id)
        checks = beat.get("assert", {})
        if not isinstance(checks, dict):
            raise ProbeError(f"beat {beat_id!r} assert must be an object")
        for flag, spec in checks.items():
            if not isinstance(spec, dict) or not spec:
                raise ProbeError(f"beat {beat_id!r} flag {flag!r} needs an operator object")
            unknown = set(spec) - {"eq", "min", "max", "in", "not_null"}
            if unknown:
                raise ProbeError(f"beat {beat_id!r} flag {flag!r} unknown operators {sorted(unknown)}")
    return schema


def _check_flag(flag: str, spec: dict[str, Any], flags: dict[str, Any]) -> str | None:
    present = flag in flags
    value = flags.get(flag)
    if "not_null" in spec:
        want_present = bool(spec["not_null"])
        if want_present and (not present or value is None):
            return f"{flag} is null/missing"
        if not want_present and present and value is not None:
            return f"{flag} should be null, got {value!r}"
    if "eq" in spec and value != spec["eq"]:
        return f"{flag}={value!r} != {spec['eq']!r}"
    if "in" in spec and value not in spec["in"]:
        return f"{flag}={value!r} not in {spec['in']!r}"
    for op, cmp in (("min", lambda v, b: v >= b), ("max", lambda v, b: v <= b)):
        if op in spec:
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                return f"{flag}={value!r} is not numeric for {op}"
            if not cmp(value, spec[op]):
                return f"{flag}={value!r} fails {op}={spec[op]!r}"
    return None


def evaluate_demo(demo_id: str, schema: dict[str, Any], log_text: str) -> DemoOutcome:
    events = parse_probe_lines(log_text)
    if not events:
        return DemoOutcome(
            demo_id=demo_id, void=True, void_reason="no probe output", beats=()
        )
    latest: dict[str, dict[str, Any]] = {}
    for event in events:
        latest[event.beat] = event.flags
    outcomes: list[BeatOutcome] = []
    for beat in schema["beats"]:
        beat_id = beat["id"]
        if beat_id not in latest:
            outcomes.append(BeatOutcome(beat_id=beat_id, seen=False, passed=False))
            continue
        flags = latest[beat_id]
        failures = [
            msg
            for flag, spec in (beat.get("assert") or {}).items()
            if (msg := _check_flag(flag, spec, flags)) is not None
        ]
        outcomes.append(
            BeatOutcome(
                beat_id=beat_id,
                seen=True,
                passed=not failures,
                failures=tuple(failures),
            )
        )
    return DemoOutcome(demo_id=demo_id, void=False, void_reason="", beats=tuple(outcomes))


def evaluate_run(
    *,
    schema: dict[str, Any],
    build_ok: bool,
    demo_logs: dict[str, str],
) -> RunOutcome:
    """BUILD/LAUNCH gate first; then REACH/STATE over the expected beats."""
    if not build_ok:
        return RunOutcome(
            build_ok=False, launch_ok=False, void=False,
            void_reason="", demos=(),
        )
    if not demo_logs:
        return RunOutcome(
            build_ok=True, launch_ok=False, void=True,
            void_reason="no demo logs captured", demos=(),
        )
    demos = tuple(
        evaluate_demo(demo_id, schema, text)
        for demo_id, text in sorted(demo_logs.items())
    )
    if all(d.void for d in demos):
        return RunOutcome(
            build_ok=True, launch_ok=True, void=True,
            void_reason="no probe output in any demo", demos=demos,
        )
    scored = tuple(d for d in demos if not d.void)
    return RunOutcome(
        build_ok=True, launch_ok=True, void=False, void_reason="", demos=scored,
    )


def evaluate_output_dir(run_output_dir: Path, schema_path: Path) -> dict[str, Any]:
    """Score one verifier output dir without a judge. Returns a v2 cell body."""
    run_output_dir = Path(run_output_dir)
    schema = load_probe_schema(schema_path)
    breakdown_path = run_output_dir / "breakdown.json"
    build_ok = True
    still_source = ""
    if breakdown_path.is_file():
        breakdown = json.loads(breakdown_path.read_text())
        build_ok = bool(breakdown.get("build_ok", True))
        still_source = breakdown.get("still_source") or ""
    outcome = evaluate_run(
        schema=schema,
        build_ok=build_ok,
        demo_logs=read_demo_logs(run_output_dir),
    )
    cell: dict[str, Any] = {
        "build_ok": outcome.build_ok,
        "launch_ok": outcome.launch_ok,
        "void": outcome.void,
        "void_reason": outcome.void_reason,
        "reach": outcome.reach,
        "state": outcome.state,
        "trace_author": "generator",
        "beats": [
            {
                "demo_id": demo.demo_id,
                "results": [
                    {
                        "beat": beat.beat_id,
                        "seen": beat.seen,
                        "passed": beat.passed,
                        "failures": list(beat.failures),
                    }
                    for beat in demo.beats
                ],
            }
            for demo in outcome.demos
        ],
    }
    if still_source in ("x11_post_event", "1game_post_event_plus2"):
        cell["still_source"] = still_source
    return cell


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        prog="python -m gamecraft_bench.verifier.probe",
        description="Machine-checked v2 metrics from probe logs (no judge).",
    )
    parser.add_argument("--output", type=Path, required=True,
                        help="Verifier output dir for one (task, arm, repeat) cell")
    parser.add_argument("--probe", type=Path, required=True,
                        help="host_probes/<slug>.json")
    args = parser.parse_args(argv)
    try:
        cell = evaluate_output_dir(args.output, args.probe)
    except ProbeError as exc:
        print(str(exc))
        return 2
    print(json.dumps(cell, indent=2))
    return 0


def read_demo_logs(run_output_dir: Path) -> dict[str, str]:
    """Collect engine logs per demo from a verifier output directory."""
    logs: dict[str, str] = {}
    demos_dir = Path(run_output_dir) / "demos"
    if not demos_dir.is_dir():
        return logs
    for demo_dir in sorted(p for p in demos_dir.iterdir() if p.is_dir()):
        chunks: list[str] = []
        for name in ("godot.log", "1gameplay.log", "probe.log"):
            candidate = demo_dir / "logs" / name
            if candidate.is_file():
                chunks.append(candidate.read_text(errors="replace"))
        if chunks:
            logs[demo_dir.name] = "\n".join(chunks)
    return logs


if __name__ == "__main__":
    raise SystemExit(main())

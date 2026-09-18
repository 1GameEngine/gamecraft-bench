"""Replay one project repeatedly and report whether the probe stream is stable.

This measures the instrument, not a game. If replaying identical inputs into
identical code yields different beat outcomes, then some of the STATE spread
between arms is replay noise, and the matrix cannot tell that apart from a
toolchain effect. Run this once per arm before the matrix, not per cell.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .probe import evaluate_run, load_probe_schema, read_demo_logs
from .v2_runner import ARMS, record_cell


def beat_signature(run_output_dir: Path, schema: dict[str, Any]) -> dict[str, Any]:
    """Per-demo (beat, seen, passed) triples, order-independent."""
    outcome = evaluate_run(
        schema=schema,
        build_ok=True,
        demo_logs=read_demo_logs(run_output_dir),
    )
    return {
        "void": outcome.void,
        "void_reason": outcome.void_reason,
        "reach": outcome.reach,
        "state": outcome.state,
        "demos": {
            demo.demo_id: sorted(
                (b.beat_id, b.seen, b.passed) for b in demo.beats
            )
            for demo in outcome.demos
        },
    }


def compare(signatures: list[dict[str, Any]]) -> dict[str, Any]:
    """Stable when every replay produced the same beat outcomes."""
    if not signatures:
        return {"stable": False, "reason": "no replays"}
    first = signatures[0]
    unstable_demos = sorted({
        demo_id
        for sig in signatures[1:]
        for demo_id in set(first["demos"]) | set(sig["demos"])
        if first["demos"].get(demo_id) != sig["demos"].get(demo_id)
    })
    metrics = {(sig["reach"], sig["state"]) for sig in signatures}
    return {
        "stable": not unstable_demos and len(metrics) == 1,
        "replays": len(signatures),
        "unstable_demos": unstable_demos,
        "distinct_metric_pairs": sorted(
            [list(m) for m in metrics], key=lambda m: (m[0] is None, m)
        ),
    }


def run(
    *,
    run_dir: Path,
    arm: str,
    rubric: Path,
    probe_schema: Path,
    repeats: int = 3,
    slug: str = "visualnovel-keepsake",
) -> dict[str, Any]:
    schema = load_probe_schema(probe_schema)
    signatures = []
    for i in range(repeats):
        output = record_cell(
            run_dir=run_dir, arm=arm, rubric=rubric,
            slug=slug, repeat=1,
        )
        signatures.append(beat_signature(output, schema))
        keep = Path(run_dir) / "stability" / arm
        keep.mkdir(parents=True, exist_ok=True)
        (keep / f"replay{i + 1}.json").write_text(
            json.dumps(signatures[-1], indent=2, default=str) + "\n"
        )
    report = compare(signatures)
    report["arm"] = arm
    dest = Path(run_dir) / "stability" / arm / "report.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(report, indent=2, default=str) + "\n")
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m gamecraft_bench.verifier.stability",
        description="Replay one arm repeatedly and report probe-stream stability.",
    )
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--arm", choices=sorted(ARMS), required=True)
    parser.add_argument("--rubric", type=Path, required=True)
    parser.add_argument("--probe", type=Path, required=True)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--slug", default="visualnovel-keepsake")
    args = parser.parse_args(argv)

    report = run(
        run_dir=args.run_dir,
        arm=args.arm,
        rubric=args.rubric,
        probe_schema=args.probe,
        repeats=args.repeats,
        slug=args.slug,
    )
    print(json.dumps(report, indent=2, default=str))
    return 0 if report["stable"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

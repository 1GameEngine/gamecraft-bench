"""Pre-registered analysis for `engine_toolchain_effect` ledger records.

Written before any matrix cell exists, so the model cannot be tuned to the
data. Deliberately plain: a paired slug-level contrast with a bootstrap
interval, no library dependency, no p-value, no leaderboard.

Slug is the unit of pairing because task difficulty dominates arm difference;
comparing pooled cells would let a slug with more surviving cells dominate the
contrast. Void and contaminated cells are dropped from the metric and reported
as rates, never as zeros: a cell that failed to be measured is not a cell that
scored nothing.
"""

from __future__ import annotations

import argparse
import json
import random
import statistics
from pathlib import Path
from typing import Any, Iterable, Sequence

BOOTSTRAP_RESAMPLES = 10000
BOOTSTRAP_SEED = 20260918


def load_cells(paths: Iterable[Path]) -> list[dict[str, Any]]:
    """Read cells out of one or more ledger-v2 records."""
    cells: list[dict[str, Any]] = []
    for path in paths:
        record = json.loads(Path(path).read_text())
        slug = record.get("slug")
        for cell in record.get("cells", []):
            cells.append({**cell, "slug": cell.get("slug", slug)})
    return cells


def rates(cells: Sequence[dict[str, Any]], arm: str) -> dict[str, Any]:
    """BUILD / LAUNCH / void / contaminated rates for one arm."""
    arm_cells = [c for c in cells if c.get("arm") == arm]
    if not arm_cells:
        return {"arm": arm, "cells": 0}
    n = len(arm_cells)
    return {
        "arm": arm,
        "cells": n,
        "build_ok_rate": sum(bool(c.get("build_ok")) for c in arm_cells) / n,
        "launch_ok_rate": sum(bool(c.get("launch_ok")) for c in arm_cells) / n,
        "void_rate": sum(bool(c.get("void")) for c in arm_cells) / n,
        "contaminated_rate": sum(bool(c.get("contaminated")) for c in arm_cells) / n,
    }


def scorable(cells: Sequence[dict[str, Any]], arm: str, metric: str) -> list[dict]:
    return [
        c for c in cells
        if c.get("arm") == arm
        and not c.get("void")
        and not c.get("contaminated")
        and isinstance(c.get(metric), (int, float))
    ]


def slug_means(
    cells: Sequence[dict[str, Any]], arm: str, metric: str
) -> dict[str, float]:
    per_slug: dict[str, list[float]] = {}
    for cell in scorable(cells, arm, metric):
        per_slug.setdefault(cell["slug"], []).append(float(cell[metric]))
    return {slug: statistics.fmean(vals) for slug, vals in per_slug.items()}


def paired_contrast(
    cells: Sequence[dict[str, Any]],
    *,
    arm_a: str,
    arm_b: str,
    metric: str = "state",
    resamples: int = BOOTSTRAP_RESAMPLES,
    seed: int = BOOTSTRAP_SEED,
) -> dict[str, Any]:
    """Mean per-slug difference (arm_a - arm_b) with a percentile interval.

    A slug contributes only when both arms have at least one scorable cell
    there; a slug where one arm never produced a measurable game cannot speak
    to a difference in degree, and is reported in ``dropped_slugs`` so that
    silence is visible rather than averaged away.
    """
    means_a = slug_means(cells, arm_a, metric)
    means_b = slug_means(cells, arm_b, metric)
    shared = sorted(set(means_a) & set(means_b))
    dropped = sorted((set(means_a) | set(means_b)) - set(shared))
    if not shared:
        return {
            "metric": metric, "arm_a": arm_a, "arm_b": arm_b,
            "slugs": 0, "dropped_slugs": dropped,
            "difference": None, "interval": None,
            "note": "no slug has scorable cells in both arms",
        }
    diffs = [means_a[s] - means_b[s] for s in shared]
    point = statistics.fmean(diffs)
    rng = random.Random(seed)
    boot = sorted(
        statistics.fmean(rng.choices(diffs, k=len(diffs)))
        for _ in range(resamples)
    )
    lo = boot[int(0.025 * (resamples - 1))]
    hi = boot[int(0.975 * (resamples - 1))]
    return {
        "metric": metric,
        "arm_a": arm_a,
        "arm_b": arm_b,
        "slugs": len(shared),
        "per_slug": {s: round(means_a[s] - means_b[s], 4) for s in shared},
        "dropped_slugs": dropped,
        "difference": round(point, 4),
        "interval": [round(lo, 4), round(hi, 4)],
        "resamples": resamples,
        "seed": seed,
    }


def report(cells: Sequence[dict[str, Any]]) -> dict[str, Any]:
    """The whole pre-registered output. No ranking, no single number.

    Ablation keys appear only when the record still has ``1game_bare`` cells
    (the frozen 2026-09 matrix). Subsequent two-arm runs omit them.
    """
    arms = sorted({c.get("arm") for c in cells if c.get("arm")})
    out: dict[str, Any] = {
        "cells": len(cells),
        "rates": [rates(cells, arm) for arm in arms],
        "primary": paired_contrast(cells, arm_a="godot", arm_b="1game_eco"),
        "reach_primary": paired_contrast(
            cells, arm_a="godot", arm_b="1game_eco", metric="reach"
        ),
    }
    if any(c.get("arm") == "1game_bare" for c in cells):
        out["ablation"] = paired_contrast(
            cells, arm_a="1game_eco", arm_b="1game_bare"
        )
        out["reach_ablation"] = paired_contrast(
            cells, arm_a="1game_eco", arm_b="1game_bare", metric="reach"
        )
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m gamecraft_bench.verifier.analyze",
        description="Pre-registered analysis of engine_toolchain_effect records.",
    )
    parser.add_argument("records", nargs="+", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)

    result = report(load_cells(args.records))
    text = json.dumps(result, indent=2) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text)
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

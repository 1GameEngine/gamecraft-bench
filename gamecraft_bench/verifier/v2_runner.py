"""Record + machine-score one v2 cell, and assemble a ledger payload.

Record uses the normal verifier CLI (stub judge, whose score is discarded);
the published numbers come from :mod:`gamecraft_bench.verifier.probe`.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from .host_paths import HostPathError, validate_experiment_id
from .probe import evaluate_output_dir

ARMS = {
    "godot": "godot",
    "1game_eco": "1game",
    "1game_bare": "1game",
}


def cell_path(
    run_dir: Path, arm: str, repeat: int, model: str, slug: str = ""
) -> Path:
    safe_model = "".join(c if c.isalnum() or c in "-_" else "-" for c in model)
    prefix = f"{slug}-" if slug else ""
    return Path(run_dir) / "cells" / f"{prefix}{arm}-r{repeat}-{safe_model}.json"


def project_dir(run_dir: Path, arm: str, *, slug: str, repeat: int) -> Path:
    return Path(run_dir) / "projects" / slug / arm / f"r{repeat}"


def record_dir(run_dir: Path, arm: str, *, slug: str, repeat: int) -> Path:
    return Path(run_dir) / "record" / slug / arm / f"r{repeat}"


def record_cell(
    *,
    run_dir: Path,
    arm: str,
    rubric: Path,
    python_bin: str = sys.executable,
    slug: str = "visualnovel-keepsake",
    repeat: int = 1,
) -> Path:
    """Replay the arm's traces into ``<run_dir>/record/<slug>/<arm>/r<n>``."""
    if arm not in ARMS:
        raise HostPathError(f"unknown arm {arm!r}")
    run_dir = Path(run_dir)
    project = project_dir(run_dir, arm, slug=slug, repeat=repeat)
    output = record_dir(run_dir, arm, slug=slug, repeat=repeat)
    cmd = [
        python_bin, "-m", "gamecraft_bench.verifier",
        "--project", str(project),
        "--rubric", str(rubric),
        "--output", str(output),
        "--engine", ARMS[arm],
        "--judge", "stub",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(Path.home()))
    output.mkdir(parents=True, exist_ok=True)
    (output / "record.log").write_text(
        f"$ {' '.join(cmd)}\nexit={proc.returncode}\n{proc.stdout}\n{proc.stderr}"
    )
    return output


def score_cell(
    *,
    run_dir: Path,
    arm: str,
    repeat: int,
    model: str,
    probe_schema: Path,
    slug: str = "visualnovel-keepsake",
) -> dict[str, Any]:
    output = record_dir(run_dir, arm, slug=slug, repeat=repeat)
    cell = evaluate_output_dir(output, probe_schema)
    cell.update({"arm": arm, "repeat": repeat, "model": model, "slug": slug})
    dest = cell_path(run_dir, arm, repeat, model, slug=slug)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(cell, indent=2) + "\n")
    return cell


def assemble(
    *,
    run_dir: Path,
    slug: str,
    prereg_frozen_at: str,
    user_sha256: str | None = None,
    versions: dict[str, str] | None = None,
) -> dict[str, Any]:
    run_dir = Path(run_dir)
    experiment_id = validate_experiment_id(run_dir.name)
    cells = []
    for path in sorted((run_dir / "cells").glob("*.json")):
        raw = json.loads(path.read_text())
        cell = {
            k: raw[k]
            for k in (
                "arm", "repeat", "model", "build_ok", "launch_ok",
                "void", "void_reason", "reach", "state",
                "still_source", "trace_author", "slug",
                "contaminated", "contamination_reason",
            )
            if k in raw
        }
        if cell.get("void"):
            cell["reach"] = None
            cell["state"] = None
        cells.append(cell)
    if not cells:
        raise HostPathError("no cells to assemble")
    payload: dict[str, Any] = {
        "experiment_id": experiment_id,
        "claim_class": "engine_toolchain_effect",
        "slug": slug,
        "probe_schema_version": 1,
        "prereg_frozen_at": prereg_frozen_at,
        "cells": cells,
    }
    if user_sha256:
        payload["user_sha256"] = user_sha256
    if versions:
        payload["versions"] = versions
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m gamecraft_bench.verifier.v2_runner",
        description="Record and machine-score one engine-toolchain cell.",
    )
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--arm", choices=sorted(ARMS))
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--model")
    parser.add_argument("--rubric", type=Path)
    parser.add_argument("--probe", type=Path)
    parser.add_argument("--skip-record", action="store_true",
                        help="Score an already recorded cell.")
    parser.add_argument("--assemble", action="store_true",
                        help="Print the ledger payload for every scored cell.")
    parser.add_argument("--slug", default="visualnovel-keepsake")
    parser.add_argument("--prereg-frozen-at",
                        help="sha256 of the frozen pre-registration document.")
    args = parser.parse_args(argv)

    if args.assemble:
        if not args.prereg_frozen_at:
            parser.error("--assemble needs --prereg-frozen-at")
        print(json.dumps(
            assemble(
                run_dir=args.run_dir,
                slug=args.slug,
                prereg_frozen_at=args.prereg_frozen_at,
            ),
            indent=2,
        ))
        return 0

    for required in ("arm", "model", "rubric", "probe"):
        if getattr(args, required) is None:
            parser.error(f"--{required.replace('_', '-')} is required")

    if not args.skip_record:
        record_cell(
            run_dir=args.run_dir,
            arm=args.arm,
            rubric=args.rubric,
            slug=args.slug,
            repeat=args.repeat,
        )
    cell = score_cell(
        run_dir=args.run_dir,
        arm=args.arm,
        repeat=args.repeat,
        model=args.model,
        probe_schema=args.probe,
        slug=args.slug,
    )
    print(json.dumps({k: cell[k] for k in
                      ("arm", "build_ok", "launch_ok", "void", "reach", "state")
                      if k in cell}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

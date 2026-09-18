"""Host dual-run path and identity gates (Harbor jobs stay a separate tree)."""

from __future__ import annotations

import os
import re
from pathlib import Path

EXPERIMENT_ID_RE = re.compile(r"^h-[0-9]{8}t[0-9]{6}z-[a-z0-9]{8}$")
LEDGER_DIRNAME = "host_excerpt_ledger"
HOST_RUNS_DIRNAME = "gamecraft-host-runs"
COMPARE_DIRNAME = "gamecraft-bench-jobs-compare"


class HostPathError(ValueError):
    """Forbidden jobs root or ledger write target."""


def host_exclusive_requested(engine: str | None) -> bool:
    """True when CLI requested ``--engine godot|1game`` (not Harbor auto/omit)."""
    return (engine or "").strip().lower() in ("godot", "1game")


def resolve_jobs_root(raw: str | os.PathLike[str] | Path) -> Path:
    root = Path(raw).expanduser().resolve()
    if root == Path.home().resolve():
        raise HostPathError(
            "JOBS_ROOT must not be $HOME itself; use "
            "$HOME/gamecraft-bench-jobs (Harbor) or a dedicated jobs tree"
        )
    return root


def assert_not_ledger_write(path: Path) -> Path:
    """Refuse verifier/compare output inside the git ledger directory."""
    resolved = Path(path).expanduser().resolve()
    parts = {p.lower() for p in resolved.parts}
    if LEDGER_DIRNAME.lower() in parts:
        raise HostPathError(
            f"refuse write into {LEDGER_DIRNAME}/ (not a verifier --output/--out)"
        )
    return resolved


def validate_experiment_id(experiment_id: str) -> str:
    if not EXPERIMENT_ID_RE.fullmatch(experiment_id):
        raise HostPathError(
            f"experiment_id {experiment_id!r} must match {EXPERIMENT_ID_RE.pattern}"
        )
    return experiment_id

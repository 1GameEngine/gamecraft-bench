"""Unique O_EXCL writer for optional git promotion (batch 4). Schema lives in the skill pack."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .host_paths import (
    LEDGER_DIRNAME,
    HostPathError,
    validate_experiment_id,
)

_SKILL_DIR = Path(__file__).resolve().parents[2] / "skills" / "gamecraft-host-dual-run"
_SKILL_SCHEMA = _SKILL_DIR / "ledger.schema.json"
_SKILL_SCHEMA_V2 = _SKILL_DIR / "ledger-v2.schema.json"
_ALLOWED_STILLS = {"x11_post_event", "1game_post_event_plus2"}
_V2_ARMS = {"godot", "1game_eco", "1game_bare"}


def load_schema() -> dict[str, Any]:
    return json.loads(_SKILL_SCHEMA.read_text())


def load_schema_v2() -> dict[str, Any]:
    return json.loads(_SKILL_SCHEMA_V2.read_text())


def validate_record(payload: dict[str, Any]) -> dict[str, Any]:
    if payload.get("claim_class") == "engine_toolchain_effect":
        return _validate_v2(payload)
    schema = load_schema()
    eid = payload.get("experiment_id")
    if not isinstance(eid, str):
        raise HostPathError("experiment_id required")
    validate_experiment_id(eid)
    if payload.get("claim_class") != schema["properties"]["claim_class"]["const"]:
        raise HostPathError("claim_class must be host_product_stack_diagnostic")
    if payload.get("cite_columns") is not False:
        raise HostPathError("cite_columns must be false")
    if payload.get("not_an_engine_ranking") is not True:
        raise HostPathError("not_an_engine_ranking must be true")
    if payload.get("protocol") != "cursor-subagent-png-excerpt":
        raise HostPathError("protocol mismatch")
    if payload.get("slug") != "visualnovel-keepsake":
        raise HostPathError("v1 slug is visualnovel-keepsake")
    surface = payload.get("parent_surface") or {}
    if surface.get("ids") != ["M3"] or surface.get("layout") != "split_cards":
        raise HostPathError("parent_surface must be split_cards ids=[M3]")
    arms = payload.get("arms") or {}
    for name in ("godot", "1game"):
        arm = arms.get(name)
        if not isinstance(arm, dict):
            raise HostPathError(f"missing arm {name}")
        src = arm.get("still_source")
        if src not in _ALLOWED_STILLS:
            raise HostPathError(f"illegal still_source {src!r} (mp4_sample is void)")
        if arm.get("trace_author") != "generator":
            raise HostPathError("trace_author must be generator")
        if arm.get("void"):
            raise HostPathError(
                "void arm: refuse promotion of host_product_stack_diagnostic"
            )
        if "M3" not in arm:
            raise HostPathError(f"{name} missing M3")
    user = payload.get("user_sha256")
    if not isinstance(user, str) or len(user) != 64:
        raise HostPathError("user_sha256 must be 64 lowercase hex")
    return payload


def _validate_v2(payload: dict[str, Any]) -> dict[str, Any]:
    """Engine-toolchain matrix record: void cells may not carry numbers."""
    load_schema_v2()
    validate_experiment_id(str(payload.get("experiment_id", "")))
    if payload.get("probe_schema_version") != 1:
        raise HostPathError("probe_schema_version must be 1")
    if not payload.get("slug"):
        raise HostPathError("slug required")
    if not payload.get("prereg_frozen_at"):
        raise HostPathError("prereg_frozen_at required before promotion")
    cells = payload.get("cells")
    if not isinstance(cells, list) or not cells:
        raise HostPathError("cells must be a non-empty list")
    seen: set[tuple[str, int, str]] = set()
    for cell in cells:
        if not isinstance(cell, dict):
            raise HostPathError("each cell must be an object")
        arm = cell.get("arm")
        if arm not in _V2_ARMS:
            raise HostPathError(f"illegal arm {arm!r}")
        repeat = cell.get("repeat")
        model = cell.get("model")
        if not isinstance(repeat, int) or repeat < 1:
            raise HostPathError("repeat must be a positive integer")
        if not isinstance(model, str) or not model:
            raise HostPathError("model required per cell")
        key = (arm, repeat, model)
        if key in seen:
            raise HostPathError(f"duplicate cell {key}")
        seen.add(key)
        if cell.get("trace_author") not in (None, "generator"):
            raise HostPathError("trace_author must be generator")
        still = cell.get("still_source")
        if still is not None and still not in _ALLOWED_STILLS:
            raise HostPathError(f"illegal still_source {still!r} (mp4_sample is void)")
        if cell.get("void"):
            if cell.get("reach") is not None or cell.get("state") is not None:
                raise HostPathError("void cell must not carry reach/state numbers")
            if not cell.get("void_reason"):
                raise HostPathError("void cell needs void_reason")
        elif cell.get("build_ok") and cell.get("launch_ok"):
            for metric in ("reach", "state"):
                value = cell.get(metric)
                if not isinstance(value, (int, float)) or isinstance(value, bool):
                    raise HostPathError(f"non-void cell needs numeric {metric}")
                if not 0.0 <= float(value) <= 1.0:
                    raise HostPathError(f"{metric} out of range: {value!r}")
    return payload


def write_ledger(path: Path, payload: dict[str, Any]) -> Path:
    """Create ``host_excerpt_ledger/<experiment_id>.json`` with O_EXCL."""
    payload = validate_record(dict(payload))
    dest = Path(path).expanduser()
    if dest.suffix != ".json":
        raise HostPathError("ledger files are .json")
    validate_experiment_id(dest.stem)
    if dest.stem != payload["experiment_id"]:
        raise HostPathError("filename stem must equal experiment_id")
    if dest.parent.name != LEDGER_DIRNAME:
        raise HostPathError(f"parent directory must be {LEDGER_DIRNAME}/")
    dest.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
    try:
        fd = os.open(dest, flags, 0o644)
    except FileExistsError as exc:
        raise HostPathError(f"O_EXCL: {dest} exists; abort, do not rewrite") from exc
    with os.fdopen(fd, "wb") as fh:
        fh.write(data)
    return dest

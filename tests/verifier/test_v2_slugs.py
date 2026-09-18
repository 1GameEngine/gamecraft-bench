"""Every v2 slug's brief and probe schema must agree, and stay engine-neutral.

A brief that names an engine, or asserts a flag it never asked the game to
track, scores generators on guessing rather than on building the game.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from gamecraft_bench.verifier.probe import load_probe_schema

_ROOT = Path(__file__).resolve().parents[2]
_PROBES = _ROOT / "host_probes"
_BRIEFS = _ROOT / "skills" / "gamecraft-host-dual-run" / "v2"

# Words that would make a brief mean different things to different arms.
_ENGINE_WORDS = (
    "godot", "1game", "gdscript", "tscn", "gdextension", "solid-js", "solidjs",
    "react", "tsx", "jsx", "node_modules", "npm", "pnpm", "project.godot",
    "colorrect", "control node", "scene tree", "engine-bundle",
)
_RUBRIC_ID = re.compile(r"\b[MDVA][1-9]\b")
_BACKTICKED = re.compile(r"`([a-z0-9_]+)`")


def _slugs() -> list[str]:
    return sorted(p.stem for p in _PROBES.glob("*.json"))


def _brief(slug: str) -> Path:
    return _BRIEFS / f"{slug}-main.md"


def _brief_section(text: str, heading: str) -> str:
    """Body of a '<heading>:' list in the self-report section."""
    _, _, rest = text.partition(heading)
    lines = []
    for line in rest.splitlines():
        if line.startswith("- "):
            lines.append(line)
        elif lines and line.strip() and not line.startswith("- "):
            break
    return "\n".join(lines)


@pytest.mark.parametrize("slug", _slugs())
def test_probe_schema_parses(slug: str) -> None:
    load_probe_schema(_PROBES / f"{slug}.json")


@pytest.mark.parametrize("slug", _slugs())
def test_brief_exists(slug: str) -> None:
    assert _brief(slug).is_file(), f"{slug} has a probe schema but no v2 brief"


@pytest.mark.parametrize("slug", _slugs())
def test_beat_ids_match_the_brief(slug: str) -> None:
    schema = load_probe_schema(_PROBES / f"{slug}.json")
    text = _brief(slug).read_text()
    documented = set(_BACKTICKED.findall(_brief_section(text, "Beat ids:")))
    declared = {b["id"] for b in schema["beats"]}
    assert declared <= documented, f"{slug}: undocumented beats {declared - documented}"
    assert documented <= declared, f"{slug}: brief lists beats the schema drops {documented - declared}"


@pytest.mark.parametrize("slug", _slugs())
def test_asserted_flags_are_documented(slug: str) -> None:
    schema = load_probe_schema(_PROBES / f"{slug}.json")
    documented = set(_BACKTICKED.findall(
        _brief_section(_brief(slug).read_text(), "Flag names:")
    ))
    asserted = {
        flag
        for beat in schema["beats"]
        for flag in (beat.get("assert") or {})
    }
    assert asserted <= documented, f"{slug}: undocumented flags {asserted - documented}"


@pytest.mark.parametrize("slug", _slugs())
def test_brief_is_engine_neutral(slug: str) -> None:
    lowered = _brief(slug).read_text().lower()
    found = [w for w in _ENGINE_WORDS if w in lowered]
    assert not found, f"{slug}: brief names a stack: {found}"


@pytest.mark.parametrize("slug", _slugs())
def test_brief_does_not_leak_rubric_ids(slug: str) -> None:
    hits = _RUBRIC_ID.findall(_brief(slug).read_text())
    assert not hits, f"{slug}: brief quotes rubric ids {sorted(set(hits))}"


@pytest.mark.parametrize("slug", _slugs())
def test_self_report_contract_is_shared_verbatim(slug: str) -> None:
    """All slugs must ask for the same line shape, or arms are not comparable."""
    text = _brief(slug).read_text()
    assert '{"probe": 1, "beat": "<beat id>", "flags": {"<name>": <value>, ...}}' in text
    assert "Print a line after **every** handled input" in text
    assert 'Do not print anything else that begins with `{"probe"' in text


@pytest.mark.parametrize("slug", _slugs())
def test_beat_count_is_in_range(slug: str) -> None:
    beats = load_probe_schema(_PROBES / f"{slug}.json")["beats"]
    assert 4 <= len(beats) <= 8, f"{slug}: {len(beats)} beats, want 4-8"

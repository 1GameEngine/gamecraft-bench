"""Assemble a host dual-engine diagnostic table. Not a Harbor ranking.

Never treat Harbor ``reward.txt`` / Overall as cross-engine quality.
V/A and formula Overall are not published. Weak-comparable ids are
M3/M4/D2–D5 only. Generation remains Godot-asymmetric.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

# Keepsake-oriented defaults; unknown ids are listed as "other".
WEAK_COMPARABLE_IDS = ("M3", "M4", "D2", "D3", "D4", "D5")
VISUAL_CONTAMINATED_IDS = ("M1", "M2", "M5", "D1")


def load_breakdown(output_dir: Path) -> dict:
    path = Path(output_dir) / "breakdown.json"
    if not path.is_file():
        raise SystemExit(f"missing {path}")
    return json.loads(path.read_text())


def _req_map(bd: dict) -> dict[str, dict]:
    return {r["id"]: r for r in bd.get("requirements", [])}


def merge_pair(godot_bd: dict, onegame_bd: dict) -> dict:
    blockers: list[str] = []
    if godot_bd.get("engine") != "godot":
        blockers.append(f"godot arm engine={godot_bd.get('engine')!r} (need exclusive godot)")
    if onegame_bd.get("engine") != "1game":
        blockers.append(f"1game arm engine={onegame_bd.get('engine')!r} (need exclusive 1game)")
    gj = godot_bd.get("judge") or {}
    oj = onegame_bd.get("judge") or {}
    if gj.get("name") != oj.get("name"):
        blockers.append(f"judge class {gj.get('name')!r} vs {oj.get('name')!r}")
    if gj.get("model") != oj.get("model"):
        blockers.append(f"judge model {gj.get('model')!r} vs {oj.get('model')!r}")
    if gj.get("name") == "StubJudge" or oj.get("name") == "StubJudge":
        blockers.append("StubJudge is not a ranking")
    if not godot_bd.get("comparable"):
        blockers.append("godot comparable=false")
    if not onegame_bd.get("comparable"):
        blockers.append("1game comparable=false")
    if onegame_bd.get("media") == "slideshow":
        media_note = "1Game evidence is slideshow (~0.5s last-shot concat), not x11grab"
    else:
        media_note = "1Game media field missing; assume slideshow"

    g_req = _req_map(godot_bd)
    o_req = _req_map(onegame_bd)
    weak: dict[str, dict] = {}
    for rid in WEAK_COMPARABLE_IDS:
        if rid in g_req and rid in o_req:
            weak[rid] = {
                "godot": g_req[rid].get("aggregated"),
                "1game": o_req[rid].get("aggregated"),
            }
    contaminated = {
        rid: {
            "godot": g_req[rid].get("aggregated"),
            "1game": o_req[rid].get("aggregated"),
            "note": "rubric text binds illustration/scene; not a mechanics column",
        }
        for rid in VISUAL_CONTAMINATED_IDS
        if rid in g_req and rid in o_req
    }

    publishable = not blockers
    return {
        "kind": "host-dual-engine-diagnostic",
        "not_a_paper_ranking": True,
        "publishable": publishable,
        "blockers": blockers,
        "notes": [
            "Harbor reward/Overall is not a comparison column.",
            "V/A and formula Overall are unpublished (slideshow vs x11grab; ColorRect cap).",
            "Instruction.md remains a Godot task; 1Game arm needs a separate brief.",
            "BUILD is a launch gate, not isomorphic compiler quality.",
            media_note,
            "mouse_click/key_press cost +2 1Game logic frames vs Godot same-frame xdotool.",
            "Do not copy Godot demo_outputs coordinates onto a 1Game layout.",
        ],
        "judge": {"name": gj.get("name"), "model": gj.get("model")},
        "build_ok": {
            "godot": godot_bd.get("build_ok"),
            "1game": onegame_bd.get("build_ok"),
        },
        "weak_comparable": weak,
        "visual_contaminated": contaminated,
        "unpublished": {
            "godot_reward": godot_bd.get("reward"),
            "1game_reward": onegame_bd.get("reward"),
            "reason": "formula Overall includes V/A; 1Game publishable_overall is false",
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m gamecraft_bench.verifier.compare",
        description="Merge two host verifier output dirs into a diagnostic table.",
    )
    parser.add_argument("--godot", type=Path, required=True,
                        help="Verifier output dir for --engine godot")
    parser.add_argument("--onegame", type=Path, required=True,
                        help="Verifier output dir for --engine 1game")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    table = merge_pair(load_breakdown(args.godot), load_breakdown(args.onegame))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(table, indent=2) + "\n")
    print(json.dumps({"publishable": table["publishable"], "blockers": table["blockers"]}))
    return 0 if table["publishable"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

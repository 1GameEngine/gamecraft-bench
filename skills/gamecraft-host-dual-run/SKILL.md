# GameCraft host dual-engine scoring

**HARD-no-tasks:** Do **not** spawn any Cursor Task (no generators, no scorers, no 1+1, no 10+5) until a follow-up **explicitly** unlocks **1+1-only** *and* a real VLM key is in the process env. Unlock slug is only `visualnovel-keepsake`. This file is a host-CLI contract, not a dispatch button.

Harbor 140-task Godot evaluation is unchanged. `detect_engine(auto)` is **always Godot**. 1Game exists only with exclusive `--engine 1game`. This skill does **not** replace `@1game/skill`. Do not commit `.cursor/skills/1game*`. Do not run `harbor run --agent claude-code` as the dual-engine path.

## Named greens (not Task unlocks)

- **A-merge-green:** Godot BUILD `--project` rewriter.
- **B-fixture-green / timeline-green:** `tests/fixtures/1game_minimal/` with in-step screenshots + concat (not `-loop 1`). Pipeline only.
- **score-green:** real VLM, `judge.name != StubJudge`, no `judge failed`, 1Game timeline mp4. Stub is noise.
- **publishable table:** `python -m gamecraft_bench.verifier.compare` with `publishable: true`. Never Harbor `reward` / Overall. V/A unpublished. Weak columns: M3/M4/D2–D5 only.

First same-slug 1Game generation after unlock: **`visualnovel-keepsake`** using `keepsake-1game-brief.md`, not sokoban, not the Godot `instruction.md` verbatim.

## Host CLI

Jobs for Harbor stay under `$HOME/gamecraft-bench-jobs`. Compare runs use a **different root** so the dashboard two-level trial scanner cannot ingest them:

```bash
unset PYTHONPATH
cd "$HOME"
# Godot arm
python -m gamecraft_bench.verifier \
  --project <godot-game> --rubric <rubric.json> \
  --output "$HOME/gamecraft-bench-jobs-compare/visualnovel-keepsake/godot" \
  --engine godot --judge <real> --judge-model <sku>
# 1Game arm — exclusive flag required
python -m gamecraft_bench.verifier \
  --project <1game-game> --rubric <same-rubric.json> \
  --output "$HOME/gamecraft-bench-jobs-compare/visualnovel-keepsake/1game" \
  --engine 1game --judge <real> --judge-model <sku>
python -m gamecraft_bench.verifier.compare \
  --godot "$HOME/gamecraft-bench-jobs-compare/visualnovel-keepsake/godot" \
  --onegame "$HOME/gamecraft-bench-jobs-compare/visualnovel-keepsake/1game" \
  --out "$HOME/gamecraft-bench-jobs-compare/visualnovel-keepsake/table.json"
```

`--engine auto` is Godot-only (Harbor). Do not use auto for a comparison. Reinstall non-editable after editing `gamecraft_bench/`. Never `pnpm exec 1gameplay`.

Missing `1gameplay` with `--engine 1game` is infra (exit 2, no `reward.txt`). Godot judge hard-fail still writes `reward.txt` (Harbor protocol). 1Game judge hard-fail skips `reward.txt`.

```bash
pytest tests/verifier -o python_files='test_*.py' -o testpaths=tests/verifier
```

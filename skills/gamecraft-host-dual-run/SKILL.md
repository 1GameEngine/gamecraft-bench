# GameCraft host dual-engine **diagnostic** (not a ranking)

**HARD-no-tasks:** Do **not** spawn any Cursor Task (no generators, no scorers, no 1+1, no 10+5) until a follow-up **explicitly** unlocks **1+1-only** *and* a real VLM key is already in the process env. Unlock slug is only `visualnovel-keepsake`. Key-first, then unlock. This file is not a dispatch button.

Harbor 140-task Godot evaluation is unchanged. `detect_engine(auto)` is **always Godot**. 1Game exists only with exclusive `--engine 1game`. Do not replace `@1game/skill`. Do not commit `.cursor/skills/1game*`. Do not run `harbor run --agent claude-code` as the dual-engine path.

`table.json` is `kind: host-dual-engine-diagnostic`. Do **not** call it a dual-engine score ranking. Do not cite Harbor `reward` / Overall / V/A / D3.

## Named greens (not Task unlocks)

- Pipeline greens: BUILD rewriter, 1Game timeline slideshow, fixture pixel-diff.
- **score-green:** real VLM, non-Stub, no `judge failed`, 1Game timeline mp4.
- **diagnostic table:** `python -m gamecraft_bench.verifier.compare` with `publishable: true`. Columns: **M3/M4/D2/D4/D5** only. Unpublished: V/A, Overall, D3.

After unlock, generate 1Game with **`keepsake-1game-brief.md`** (must include visible fragment board + gating + two traces for endings). Not sokoban. Not Godot `instruction.md` verbatim.

## Host CLI

Harbor jobs: `$HOME/gamecraft-bench-jobs`. Compare: **sibling** `$HOME/gamecraft-bench-jobs-compare/` (never nest under Harbor jobs; never point dashboard `JOBS_ROOT` at `$HOME`).

```bash
unset PYTHONPATH
cd "$HOME"
python -m gamecraft_bench.verifier \
  --project <godot-game> --rubric <keepsake-rubric.json> \
  --output "$HOME/gamecraft-bench-jobs-compare/visualnovel-keepsake/godot" \
  --engine godot --judge <real> --judge-model <sku>
python -m gamecraft_bench.verifier \
  --project <1game-game> --rubric <same-rubric.json> \
  --output "$HOME/gamecraft-bench-jobs-compare/visualnovel-keepsake/1game" \
  --engine 1game --judge <real> --judge-model <sku>
python -m gamecraft_bench.verifier.compare \
  --godot "$HOME/gamecraft-bench-jobs-compare/visualnovel-keepsake/godot" \
  --onegame "$HOME/gamecraft-bench-jobs-compare/visualnovel-keepsake/1game" \
  --out "$HOME/gamecraft-bench-jobs-compare/visualnovel-keepsake/table.json"
```

`--engine auto` is Harbor Godot. Reinstall non-editable after editing `gamecraft_bench/`. Never `pnpm exec 1gameplay`.

```bash
pytest tests/verifier -o python_files='test_*.py' -o testpaths=tests/verifier
```

# GameCraft host dual-engine **diagnostic** (not ranking / not comparison)

**HARD-no-spawn.** Do **not** spawn Cursor Tasks named `gen-godot`, `gen-1game`, or `pixel-reader` — or **any** other Task — until a later follow-up unlocks **phase-1-generate**. This file is not a dispatch button. A VLM key in the env is **not** a spawn gate (scoring is not this phase).

Harbor 140-task Godot evaluation is unchanged. Do not replace `@1game/skill`. Do not commit `.cursor/skills/1game*`.

## Future allow-list (locked until phase-1-generate)

When unlocked, **only** these Task names: `gen-godot`, `gen-1game`, `pixel-reader`. Never call that “1+1-only”. Orchestrator/parent writes the prompts. Stub verifier is **parent-only**. Generators must not run the verifier or `tools/screenshot.sh`.

Prompts live **here**, not in Harbor task files:

- `keepsake-main.md` — engine-neutral MAIN (both generators)
- `appendix-godot.md` — Godot plumbing only
- `keepsake-1game-brief.md` — Appendix 1 / 1Game generation only

Generators **MUST NOT** read `tasks/visualnovel-keepsake/instruction.md` or `tests/rubric.json`. Harbor `instruction.md` is never the 1Game spec and must not be used as the Godot diagnostic spec either.

Do **not** spawn `pixel-reader` in this phase. Pixel-reader notes are unpublished: not the only scores, not `compare` `diagnostic_columns`.

## Kill list

- No 10+5 Harbor sweep. No extra engines or slugs.
- No `harbor run --agent`.
- No nested Xvfb / `DISPLAY=` wrap for 1Game.
- Generators must not run the verifier or `tools/screenshot.sh`.
- Never write pixel scores into Harbor `reward.txt`.
- Never `JOBS_ROOT=$HOME`. Never nest compare under `$HOME/gamecraft-bench-jobs`.

## Jobs

| Path | Use |
| --- | --- |
| `$HOME/gamecraft-bench-jobs` | Harbor jobs only |
| `$HOME/gamecraft-bench-jobs-compare/` | **Sibling** host diagnostic (never nested under Harbor jobs) |

Stub smoke dirs **must** be:

`$HOME/gamecraft-bench-jobs-compare/visualnovel-keepsake/stub/{godot,1game}`

Separate from any later publish dirs. Dashboard `JOBS_ROOT` is never `$HOME`.

Godot `--project` for this diagnostic **MUST NOT** be `/workspace/game` (Harbor identity). Use a tree under the compare sibling dir.

## Engine

Host Godot **MUST** `--engine godot`. 1Game **MUST** `--engine 1game`. `auto` / omit is **always Godot**. Abort if `breakdown.engine` mismatches the arm you meant.

## Xvfb

Live verifier code is `:200`–`:500` (`GAMECRAFT_BENCH_XVFB_DISPLAY_START` / `END`). Dashboard Play is `:300`–`:307` with **no flock**. README `:99`–`:199` is **FALSE**.

Serialize **all** Godot Xvfb consumers with dashboard Play. 1Game never sets `DISPLAY=` and never uses `screenshot.sh` (`:99`–`:250`, no lock).

## Stub ≠ green

`--judge stub` is **pipeline smoke**, parent-only. Stub ≠ score-green. Fixture pixel-diff ≠ score-green. `compare` writing JSON / CLI exit is **not** success and **not** a ranking.

## pytest

```bash
pytest tests/verifier -o python_files='test_*.py' -o testpaths=tests/verifier
```

Reinstall non-editable after editing `gamecraft_bench/`. Never `pnpm exec 1gameplay`.

## CLI (stub smoke only)

```bash
unset PYTHONPATH
cd "$HOME"
COMPARE="$HOME/gamecraft-bench-jobs-compare"
PROJ="$COMPARE/visualnovel-keepsake/projects"
STUB="$COMPARE/visualnovel-keepsake/stub"
RUBRIC="/workspace/tasks/visualnovel-keepsake/tests/rubric.json"

# --project is the game tree; --output is verifier logs. Never the same directory.
python -m gamecraft_bench.verifier \
  --project "$PROJ/godot" \
  --rubric "$RUBRIC" \
  --output "$STUB/godot" \
  --engine godot --judge stub

python -m gamecraft_bench.verifier \
  --project "$PROJ/1game" \
  --rubric "$RUBRIC" \
  --output "$STUB/1game" \
  --engine 1game --judge stub

# Blocker dump: always writes JSON. Exit after a successful write is not a ranking.
python -m gamecraft_bench.verifier.compare \
  --godot "$STUB/godot" \
  --onegame "$STUB/1game" \
  --out "$STUB/table.json"
```

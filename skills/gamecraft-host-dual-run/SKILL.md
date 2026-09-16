# GameCraft host dual-engine **diagnostic** (not paper ranking)

**Claim lock:** Same USER bytes ≠ same total prompt. System envelopes differ; 1Game still has `@1game/skill`; Tasks may still see `/workspace`. Do not call the merge an engine ranking or a same-input-prompt comparison. Do not cite stub 1.0, `compare.publishable`, or Harbor `reward.txt` as 产物分数.

**Kill list (first):** No 10+5 Harbor sweep. No extra engines or slugs. No `harbor run --agent`. No nested Xvfb / `DISPLAY=` wrap for 1Game. Generators must not run the verifier or `tools/screenshot.sh`. Children spawn **zero** Tasks. Never write pixel scores into Harbor `reward.txt`. Never `JOBS_ROOT=$HOME`. Never nest compare under `$HOME/gamecraft-bench-jobs`. Never call this unlock `1+1-only`. A VLM key is **not** a spawn gate.

**Unlock: `phase-1-run-once-keepsake` (consumed).** Slug is only `visualnovel-keepsake`, once. That gen+score pair has already run. Do **not** spawn `gen-godot`, `gen-1game`, `score-godot`, or `score-1game` again for this slug (re-score is p-hacking unless protocol JSON fields are missing). Parent may have used **exactly** those four names. No `pixel-reader`. Harbor 140 is unchanged. Do not replace `@1game/skill`. Do not commit `.cursor/skills/1game*` or `$HOME` compare trees.

## Packing (USER bytes must match)

| Slot | Both arms | Differs |
| --- | --- | --- |
| **USER** | Exact bytes of `keepsake-main.md` | Never. Hash before spawn. |
| **System** | — | `appendix-godot.md` **or** `keepsake-1game-brief.md` (envelope) |
| Not attached | This `SKILL.md`, Harbor `instruction.md`, `rubric.json`, stub CLI | — |

Do not concatenate MAIN+appendix into USER. Do not put “you are Godot/1Game” in USER.

Trees: `$HOME/gamecraft-bench-jobs-compare/visualnovel-keepsake/projects/{godot,1game}` — **not** `/workspace/game`. Stub output: `.../stub/{godot,1game}` — never the same dir as `--project`. Score PNG copies: `.../score-evidence/{godot,1game}/`.

On the consumed run: spawn gens **in parallel**. Stub is **parent-only**. Scores are **sequential**: `score-godot` then a **new** `score-1game` (no prior scores in context). Do not repeat that spawn.

## Jobs / engine / Xvfb

Harbor jobs: `$HOME/gamecraft-bench-jobs`. Compare sibling: `$HOME/gamecraft-bench-jobs-compare/`. Dashboard `JOBS_ROOT` is never `$HOME`.

Host Godot **MUST** `--engine godot`. 1Game **MUST** `--engine 1game`. `auto` / omit is **always Godot**. Abort if `breakdown.engine` mismatches.

Verifier Xvfb is `:200`–`:500`. Dashboard Play is `:300`–`:307` with **no flock**. If dashboard might be running, **do not** Godot stub. Stub **1Game first**. Parent **`unset DISPLAY`** before 1Game (the helper inherits `os.environ`; it does not strip DISPLAY). 1Game never sets `DISPLAY=`.

## Stub ≠ scores

`--judge stub` is pipeline smoke. Stub 1.0 is not 产物分数. Fixture pixel-diff is not green. `compare` JSON / exit 0 is not success (`success_gate` / `cite_columns` are false).

产物分数 = sequential Cursor PNG JSON (`score-excerpt.md`) merged to markdown **with footer**, printing **child_raw** and **protocol_cap** (do not rewrite child JSON; stills M4 cannot stay 1 in `protocol_cap`). Not Harbor VLM. Not Harbor `reward.txt`. Not `compare` `diagnostic_columns`. Stub `reward.txt` under jobs-compare is smoke only.

Godot evidence: `demos/*/frames/frame_*.png`. 1Game evidence: `demos/*/timeline/shot_*.png`.

## pytest

```bash
pytest tests/verifier -o python_files='test_*.py' -o testpaths=tests/verifier
```

Reinstall non-editable after editing `gamecraft_bench/`. Never `pnpm exec 1gameplay`.

## CLI (parent stub smoke; 1Game first)

```bash
unset PYTHONPATH
cd "$HOME"
COMPARE="$HOME/gamecraft-bench-jobs-compare"
PROJ="$COMPARE/visualnovel-keepsake/projects"
STUB="$COMPARE/visualnovel-keepsake/stub"
RUBRIC="/workspace/tasks/visualnovel-keepsake/tests/rubric.json"

python -m gamecraft_bench.verifier \
  --project "$PROJ/1game" --rubric "$RUBRIC" --output "$STUB/1game" \
  --engine 1game --judge stub

# Godot only if dashboard Play is not holding :300–:307
python -m gamecraft_bench.verifier \
  --project "$PROJ/godot" --rubric "$RUBRIC" --output "$STUB/godot" \
  --engine godot --judge stub

python -m gamecraft_bench.verifier.compare \
  --godot "$STUB/godot" --onegame "$STUB/1game" \
  --out "$STUB/table.json"
```

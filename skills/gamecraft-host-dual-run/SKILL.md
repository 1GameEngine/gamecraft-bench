# Host Dual Protocol v1 (product-stack diagnostic, not an engine ranking)

**Claim class: `host_product_stack_diagnostic`.** Same USER bytes ≠ same total prompt. The 1Game arm includes `@1game/skill`; **no parent cell may be attributed to the engine.** Split cards, never an aligned `M3|godot|1game` subtraction table, never a ranking, never Harbor `reward.txt` / stub 1.0 / `compare.publishable` as 产物分数.

**Default: do not spawn.** Spawn only when the user says `GO：按 Host Dual Protocol 对 slug visualnovel-keepsake 开一轮` (new `experiment_id` every time). v1 registers **only** that slug. Looking at scores, listing `$HOME/gamecraft-host-runs`, or reading `host_excerpt_ledger/` is **not** a spawn gate. A VLM key is not a spawn gate.

**Kill list:** No 10+5 Harbor sweep. No extra engines or slugs. No `harbor run --agent`. No nested Xvfb / `DISPLAY=` wrap for 1Game. Generators must not run the verifier or `tools/screenshot.sh`. Children spawn **zero** Tasks. Never write Cursor pixel scores into Harbor `reward.txt`. Never `JOBS_ROOT=$HOME` (the home directory itself). Never nest host-runs under `$HOME/gamecraft-bench-jobs`. Never call an unlock `1+1-only`. Do not replace `@1game/skill`. Do not commit `.cursor/skills/1game*` or `$HOME` run trees. Do not promote the spent local n=1 tree under `gamecraft-bench-jobs-compare/visualnovel-keepsake/`. Do not strip skill off a frozen gen and re-score. Do not reuse consumed phrases `phase-1-run-once-keepsake` or `新录再打` as spawn keys.

**v2 lives beside this file.** `protocol-v2.md` defines the `engine_toolchain_effect` claim class (machine-checked probe metrics, two spawn arms `godot` / `1game_eco`, pre-registered matrix). The frozen 72-cell publication (`publication/72cell.md`) is option-0 reporting only; reading it is **not** a v1 or v2 spawn gate. This v1 document stays the narrative-diagnostic protocol. Never merge v1 excerpt cards with v2 metrics in one table.

## Identities and trees

`experiment_id` must match `^h-[0-9]{8}t[0-9]{6}z-[a-z0-9]{8}$` (example `h-20260917t134612z-k4n9xq2p`). It is **not** the slug.

Local source of truth:

`$HOME/gamecraft-host-runs/<experiment_id>/` — `projects/{godot,1game}/`, `replay/`, `stub/`, `excerpt/`, `merge.md`, `meta.json`.

Harbor jobs: `$HOME/gamecraft-bench-jobs` (or `GAMECRAFT_BENCH_JOBS_ROOT`). Compare sibling leftover: `$HOME/gamecraft-bench-jobs-compare/` (do not write new runs there).

Optional later git promotion (batch 4, not mkdir in this protocol pack): `host_excerpt_ledger/<experiment_id>.json`. Filename stem **is** `experiment_id` (`O_EXCL`). Schema: `ledger.schema.json` in this directory (not inside the ledger folder). Do not attach ledger files to generators.

## Packing

See `packing.md`. USER = exact `keepsake-main.md` bytes both arms. Appendices are system-only. Hash USER before spawn.

## Layers

1. **gen** — parallel Tasks, zero child Tasks. Traces are generator-authored; parent does not rewrite clicks.
2. **record** — parent replay. Evidence is 1280 event stills: Godot `demos/*/events/event_*.png` (`x11_post_event`); 1Game `demos/*/timeline/event_*.png` (`1game_post_event_plus2`). mp4 / `frame_*` / `shot_*` are archive. Do not zip `frame_i` to `shot_i`. Host `--engine godot|1game` with no event stills is **void** (do not mp4-sample). Harbor `--engine auto` may still sample Godot mp4.
3. **score** — sequential: `score-godot` then a **new** `score-1game` (no prior scores in the 1Game context). Excerpt ids in `score-excerpt.md`. Parent face is **M3 split cards only**. M4/D2/D4/D5 stay in the local appendix; M4 `protocol_cap` from stills is never 1.
4. **stub** — pipeline smoke only. Not 产物分数. Stub 1Game first. Skip Godot stub if dashboard Play may hold `:300`–`:307`. Parent `unset DISPLAY` before 1Game.

`void ≠ fail ≠ Unscored ≠ 0`. Either arm void ⇒ this claim class publishes **no parent pair**. `compare.py` smoke (`success_gate` / `cite_columns` false) is not the parent surface.

## Jobs / engine / Xvfb

Host Godot **MUST** `--engine godot`. 1Game **MUST** `--engine 1game`. `auto` / omit is **always Godot** (Harbor). Abort if `breakdown.engine` mismatches.

Verifier Xvfb is `:200`–`:500`. Dashboard Play is `:300`–`:307` with **no flock**.

## pytest

```bash
pytest tests/verifier -o python_files='test_*.py' -o testpaths=tests/verifier
```

Reinstall non-editable after editing `gamecraft_bench/`. Never `pnpm exec 1gameplay`.

## CLI (parent stub smoke; 1Game first)

```bash
unset PYTHONPATH
cd "$HOME"
RUN="$HOME/gamecraft-host-runs/<experiment_id>"
RUBRIC="/workspace/tasks/visualnovel-keepsake/tests/rubric.json"

python -m gamecraft_bench.verifier \
  --project "$RUN/projects/1game" --rubric "$RUBRIC" --output "$RUN/stub/1game" \
  --engine 1game --judge stub

python -m gamecraft_bench.verifier \
  --project "$RUN/projects/godot" --rubric "$RUBRIC" --output "$RUN/stub/godot" \
  --engine godot --judge stub

python -m gamecraft_bench.verifier.compare \
  --godot "$RUN/stub/godot" --onegame "$RUN/stub/1game" \
  --out "$RUN/stub/table.json"
```

Do not point `--output` / `--out` at `host_excerpt_ledger/`.

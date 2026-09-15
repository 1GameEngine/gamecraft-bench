# GameCraft host dual-engine scoring

**HARD-no-tasks:** Do **not** spawn any Cursor Task (no generators, no scorers, no 1+1, no 10+5) until a follow-up **explicitly** unlocks **1+1-only**. Unlock requires **both** engines scored with the **same real VLM SKU** **and** 1Game **timeline** mp4 evidence (not still-loop, not StubJudge). This file is a host-CLI contract, not a dispatch button.

Harbor 140-task Godot evaluation is unchanged. This skill does **not** replace `@1game/skill`. Do not commit `.cursor/skills/1game*`. Do not run `harbor run --agent claude-code` as the dual-engine path.

## Named greens (not Task unlocks)

- **A-merge-green:** Godot BUILD `--project` rewriter (already landed).
- **B-fixture-green:** `tests/fixtures/1game_minimal/` produces a non-empty mp4 + `breakdown.json` via host verifier.
- **timeline-green:** 1Game replay uses `frames list` + seq screenshots at ~0.5s engine-time cadence + ffmpeg concat. `_encode_still_mp4` / sole `--at last` + `-loop 1` is forbidden. Fixture pixel-diff of the slideshow is evidence; it is **not** a VLM ranking.
- **dual-engine-path-green:** two *different* host pipelines (Godot sokoban oracle copy **and** this 1Game fixture). Does **not** unlock Tasks.
- **score-green:** real VLM (`judge.name != StubJudge`) **and** no `judge failed` hard-error **and** timeline-green on the 1Game side. Stub `reward` / `gpt-5.5` with StubJudge is noise. Judge hard-failure must **not** be published as game-quality 0.

First same-slug 1Game generation after unlock: **`visualnovel-keepsake`** (not sokoban). ColorRect-capped visuals are **not** comparable to the paper Overall.

## Host CLI (jobs stay off `/workspace` and `/tmp`)

```bash
unset PYTHONPATH
cd "$HOME"
python -m gamecraft_bench.verifier \
  --project <abs-game-dir> \
  --rubric  <abs-rubric.json> \
  --output  "$HOME/gamecraft-bench-jobs/<run>/verifier" \
  --judge stub \
  --engine auto
```

After editing `gamecraft_bench/`, reinstall **non-editable**: `uv pip install --python <venv> .`. Do not use `scripts/run.sh` as this path's checker (`PYTHONPATH` would shadow the wheel).

1Game binaries: `/usr/local/bin/1game` and `/usr/local/bin/1gameplay`. **Never** `pnpm exec 1gameplay`. Set `NODE_PATH=/opt/1game/node_modules`. Archives go under `/tmp` (host CLI), not the Harbor jobs root.

Godot stays serial (Xvfb / xdotool). 1Game napi screenshots may run beside Godot. Do not start a Harbor trial and a host Godot canary together (host-wide stuck-godot watchdog).

Missing `1gameplay` on a 1Game tree is **infra** (CLI exit 2, no `reward.txt`), not game-quality 0. Missing `godot` stays today's failure, not skip. A real-judge **hard-failure** (missing key, API error) is also **infra** on this CLI (exit 2, no `reward.txt`). Harbor `test.sh` still writes 0 if the file is missing.

Verifier unit tests (do not use default `pytest`; Harbor collection would miss these):

```bash
pytest tests/verifier -o python_files='test_*.py' -o testpaths=tests/verifier
```

When HARD is replaced by **1+1-only**: one slug, two engines, Godot globally serial, same VLM SKU, timeline mp4. Still not 10+5 / five slugs / markdown ranking.

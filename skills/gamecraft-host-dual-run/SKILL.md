# GameCraft host dual-engine scoring

**HARD-no-tasks:** Until a follow-up explicitly unlocks **dual-engine-path-green**, do **not** spawn any Cursor Task (no generators, no scorers, no 1+1, no 10+5). This file is a host-CLI contract, not a dispatch button.

Harbor 140-task Godot evaluation is unchanged. This skill does **not** replace `@1game/skill`. Do not commit `.cursor/skills/1game*`. Do not run `harbor run --agent claude-code` as the dual-engine path.

## Named greens

- **A-merge-green:** Godot BUILD `--project` rewriter (already landed).
- **B-fixture-green:** `tests/fixtures/1game_minimal/` produces a non-empty mp4 + `breakdown.json` via host verifier.
- **dual-engine-path-green:** two *different* host pipelines (Godot sokoban oracle copy **and** this 1Game fixture). Optional; not a Task unlock by itself while this lock is HARD.
- **score-green:** real VLM (`judge.name != StubJudge`). Stub `reward` / `gpt-5.5` is noise, not a ranking.

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

Missing `1gameplay` on a 1Game tree is **infra** (CLI exit 2, no `reward.txt`), not game-quality 0. Missing `godot` stays today's failure, not skip.

When HARD is later replaced by 1+1-only: one slug, two engines, Godot globally serial. Still not 10+5.

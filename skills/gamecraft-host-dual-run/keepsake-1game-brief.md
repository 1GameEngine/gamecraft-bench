# 1Game overlay brief — visualnovel-keepsake (host only)

Use this **instead of** `tasks/visualnovel-keepsake/instruction.md` when generating
the 1Game arm. Do **not** spawn this Task while HARD-no-tasks is in effect.

Harbor 140 instruction remains Godot-only. This overlay is generation-asymmetric
on purpose.

## Engine

- 1Game 1.21.0 envelope: `src/game.tsx`, `1game.config.*`, `@1game/engine-bundle`.
- Scene **1280×720**. Pointer coordinates must match that scene, not Godot layouts.
- Follow `@1game/skill`. System `1game` / `1gameplay` only — never `pnpm exec`.
- Write **your own** `demo_outputs/*.json`. Do not copy Godot traces or `--scenario`.
- `mouse_click` / `key_press` each consume two 1Game logic frames.

## Rubric ids

Score against the **same hidden rubric ids** as the Godot task (M/D/V/A).
ColorRect / default-widget visuals: V/A/Overall are **not** comparable to paper
Godot Overall. Prefer authored illustration if you want V/A to ever be discussed.

## Host score (after unlock + real VLM)

```bash
unset PYTHONPATH
cd "$HOME"
python -m gamecraft_bench.verifier \
  --project <abs-1game-dir> \
  --rubric  /workspace/tasks/visualnovel-keepsake/tests/rubric.json \
  --output  "$HOME/gamecraft-bench-jobs-compare/visualnovel-keepsake/1game" \
  --engine 1game \
  --judge <real-backend> \
  --judge-model <same-sku>
```

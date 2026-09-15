# Appendix Godot — plumbing only (generation)

Read `keepsake-main.md` first. This file is host plumbing for the Godot arm of the diagnostic. Do **not** read `tasks/visualnovel-keepsake/instruction.md`. Do **not** copy 1Game coordinates or 1Game traces.

## Project

Use an **independent** `--project` tree under `$HOME/gamecraft-bench-jobs-compare/` (or the path the parent gives you). **Not** `/workspace/game` (Harbor identity).

The tree must contain `project.godot`. Host binary is `/usr/local/bin/godot`.

PLAY capture is the **existing x11grab verifier**. Generators do **not** wrap Xvfb, do **not** set `DISPLAY=`, and do **not** run `tools/screenshot.sh` during generation.

## Traces

Ship `demo_outputs/*.json` (1–10 files). Do **not** put a root `traces.json`.

**Do not put `"scenario"` in traces.** Replay still honors that key if present; omitting it is the only way this diagnostic stays on the default path.

Do not copy 1Game hit targets. Godot clicks must match this project’s layout.

There is no ColorRect mandate. Extra scenes are allowed.

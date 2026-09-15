# Appendix 1 — 1Game generation only (visualnovel-keepsake, host)

Read `keepsake-main.md` first, then this envelope. Do **not** read `tasks/visualnovel-keepsake/instruction.md`. Spawn policy is **HARD-no-spawn** in `SKILL.md` until **phase-1-generate**.

Harbor 140 instruction remains Godot-only. Do not emit `project.godot`, Godot scenes, `godot --headless`, `screenshot.sh`, `--scenario`, or copied Godot traces.

Follow `@1game/skill`. System `/usr/local/bin/1game` and `1gameplay` only — never `pnpm exec`.

## Envelope

```
<project>/
  src/game.tsx          ← entry
  1game.config.ts
  package.json          ← @1game/engine-bundle
  demo_outputs/*.json
  assets/               ← copies from host libraries if available
```

- Scene **1280×720**. Hit targets and trace `x,y` must match this **scene**.
- `mouse_click` / `key_press` each consume **two** 1Game logic frames. Put slack at the **end** of traces so the last state is visible.
- `1game build` / `1gameplay create` / `step --surface display --flush` are PLAY/BUILD **host** concerns. Generators must **not** wrap Xvfb or set `DISPLAY=`.

Assets if the host mounted them (read-only; copy into the project):

- `/workspace/assets/library/` (Kenney CC0)
- `/workspace/assets/library-oga/` (respect each `LICENSE.txt`)

## Product (same fantasy as MAIN)

Build **Keepsake** at 1280×720: a quiet memory-reconstruction visual novel about sorting a late person’s belongings. Short mechanical loop, not a long short-story. Memory board **visible and growing**; gating; two endings via **separate traces from title**.

ColorRect / default controls may exist; visual polish is unpublished for cross-engine tables. Do not treat that as Godot widget coaching.

## Traces

Ship 1–10 `demo_outputs/*.json` (30 fps, `duration_frames` ≤ 600). Events: `mouse_click` / `mouse_down` / `mouse_up` / `mouse_move` / `key_press` / `key_down` / `key_up` / `wait`. Omit Godot `scenario`. 1Game replay does not pass `--scenario`.

Minimum evidence set, each from **cold title**:

- One trace: title → examine **at least two** keepsakes in **non-default order** → memory board visibly grows.
- One trace: a path that **unlocks** a gated line/choice/ending the other path does not.
- One trace: a **different** authored ending.

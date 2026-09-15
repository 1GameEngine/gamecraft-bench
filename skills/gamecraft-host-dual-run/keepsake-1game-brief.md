# 1Game overlay brief — visualnovel-keepsake (host only)

Use this **instead of** `tasks/visualnovel-keepsake/instruction.md` when generating
the 1Game arm. Do **not** spawn this Task while HARD-no-tasks is in effect.

Harbor 140 instruction remains Godot-only. Scoring uses the **same hidden rubric
ids**. Generation is asymmetric on purpose: do not emit `project.godot`, Godot
scenes, `godot --headless`, screenshot.sh, or `--scenario` CLI.

Follow `@1game/skill`. System `/usr/local/bin/1game` and `1gameplay` only —
never `pnpm exec`.

## Product (same fantasy as the Godot task)

Build **Keepsake**, a complete, shippable 1280×720 micro-game: a quiet
memory-reconstruction visual novel about sorting a late person's belongings.
This is not a prototype and not a ColorRect tech demo.

Someone has died. The player sorts what they left behind. A faded photograph, a
folded letter, a worn ring, a diary with a torn-out page — objects hold
fragments of a life and do not reveal meaning in a fixed order. The loop is
**examine, remember, connect, understand**. Player order and how they read an
ambiguous choice the dead made must change the closing understanding.

## What the player must be able to do (mechanics — required)

These beats are the generation spec. Do not treat them as optional flavor.

1. **Authored opening** — Styled title into a room or box of belongings, with
   narration that sets mood and absence. Player-driven line advance (click or
   key), not a dump of all text and not auto-scroll-only.
2. **Free-order examination** — Several distinct keepsakes (not one item
   reskinned). The player **chooses which object to pick**, in any order, from a
   visible room/box. Examination is not a linear slideshow of “next”.
3. **Persistent visible fragments (M3)** — Each examined keepsake **records** a
   fragment. A **journal / list / memory board is on screen** (or one click away
   and actually shown in demos) and **grows**. The game tracks found vs not
   found. If fragments exist only in code and never appear, M3 is 0.
4. **Gating (M4)** — Later lines, interpretation choices, or endings **depend
   on which fragments were found**. At least one later beat is unavailable
   until a particular discovery. Not “everything reachable regardless of
   order”, not “only the last click matters”.
5. **Connecting fragments (D2)** — At least one later fragment **recontextualizes**
   an earlier one (a date explains a photo, an absence answers a question).
6. **More than one closing (D3 — evidence, not a ranking column)** — At least
   **two authored endings**, reached through different discovery/reading paths,
   shown as styled conclusions. Demonstrate them with **separate traces** from
   title (or from a documented in-game continue), not Godot `--scenario`.
7. **Full loop (M5)** — Title → examine → interpretation → ending → return to
   title or begin again without restarting the process. Host 1Game replay does
   not relaunch between events in one trace; still ship UI to restart.

Prefer illustrated or pixel-art keepsakes and themed UI. ColorRect / default
controls are allowed to exist but **V/A and Overall are unpublished** for
cross-engine tables.

## Engine envelope

```
<project>/
  src/game.tsx          ← entry
  1game.config.ts
  package.json          ← @1game/engine-bundle
  demo_outputs/*.json
  assets/               ← copies from host libraries if available
```

- Scene **1280×720**. Hit targets and trace `x,y` must match this scene.
- Do not copy Godot `demo_outputs` coordinates or scenario ids.
- `mouse_click` / `key_press` each consume **two** 1Game logic frames.

Assets if the host mounted them (read-only; copy into the project):

- `/workspace/assets/library/` (Kenney CC0)
- `/workspace/assets/library-oga/` (respect each `LICENSE.txt`)

## Traces

Ship 1–10 `demo_outputs/*.json` (30 fps, `duration_frames` ≤ 600). Events:
`mouse_click` / `mouse_down` / `mouse_up` / `mouse_move` / `key_press` /
`key_down` / `key_up` / `wait`. Omit Godot `scenario` or ignore it — 1Game
replay does not pass `--scenario`.

Minimum evidence set:

- One trace: title → examine **at least two** keepsakes in **non-default
  order** → memory board visibly grows.
- One trace: a path that **unlocks** a gated line/choice/ending the other path
  does not.
- One trace: a **different** authored ending.

## Host score (after unlock + real VLM only)

Output must live under `$HOME/gamecraft-bench-jobs-compare/` (never Harbor
`gamecraft-bench-jobs`).

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

The compare table is a **diagnostic**, not a paper ranking. Do not cite Harbor
`reward` / Overall / V/A as engine quality.

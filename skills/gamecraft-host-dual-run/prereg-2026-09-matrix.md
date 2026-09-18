# Pre-registration — `engine_toolchain_effect`, 8-slug matrix

Frozen before any v2 matrix cell exists. The keepsake pilot
(`h-20260918t031808z-27f3940d`) is the only v2 data seen at freeze time; it was
n=1, is contaminated on one arm, and contributes nothing here.

- Protocol: `protocol-v2.md`, probe schema version 1
- Claim class: `engine_toolchain_effect`
- Date frozen (UTC): 2026-09-18

## Hypothesis

Primary contrast: `godot` vs `1game_eco` on **STATE**. Two-sided — this design
is not built to confirm a favoured direction, and either runtime producing a
higher beat-assertion pass rate is a publishable outcome.

Ablation contrast: `1game_eco` vs `1game_bare`, which bounds how much of any
`1game_eco` result is contributed by `@1game/skill` rather than by the runtime.
The ablation cannot separate the runtime from the model's pretraining exposure
to it; see confounds.

## Fixed before any generation

- **Slugs (8):** `visualnovel-keepsake`, `puzzle-sokoban-dungeon`,
  `strategy-towerdefense`, `roguelike-dice-throne`, `simulation-kitchen-rush`,
  `platformer-echo-climb`, `shooter-wave-commander`, `tycoon-potion-shop`.
- **Arms (3):** `godot`, `1game_eco`, `1game_bare`.
- **Repeats:** 3 independent generations per (slug × arm). 72 cells.
- **Model:** one agent configuration for the whole matrix. A second model is a
  separate later experiment with its own pre-registration, not an extension of
  this one.
- **USER bytes:** `v2/<slug>-main.md`, identical across arms within a slug.
- **Envelopes:** `v2/appendix-godot.md`, `v2/appendix-1game-eco.md`,
  `v2/appendix-1game-bare.md`.
- **Probe schemas:** `host_probes/<slug>.json`, unchanged for the whole matrix.

Repeats are 3 rather than the ≥5 in `protocol-v2.md`. With task as a random
effect, 8 slugs contribute more to power than deeper repetition within a slug,
and 72 cells is what the host can actually generate and record. This is a
deliberate, pre-registered deviation, not a result of stopping early.

## Analysis plan

- Primary estimand: STATE, cells nested in slug, slug as a random effect.
- Report an effect size with an interval. No single-number leaderboard, no
  aggregate "engine score", no ranking table.
- BUILD and LAUNCH are reported as rates per arm, not folded into STATE.
- REACH is reported beside STATE, never instead of it. An arm reaching few
  beats correctly is a different finding from an arm reaching many beats wrongly.
- Void cells are reported as a rate per arm and are never counted as 0. Void
  rate is itself an outcome: an instrument that fails more often on one runtime
  is reporting something about that runtime.
- Contaminated cells (generator reached the scorer, the probe schemas, or the
  Harbor tasks) are excluded and counted in the exclusion table.

## Stopping and ordering rules

- No interim analysis. Cells are scored as they are recorded, but no arm-level
  or contrast-level summary is computed until all 72 cells are recorded or
  declared void.
- No generation may see any earlier cell's score, any ledger record, or any
  other arm's project tree.
- If the pipeline needs a fix mid-matrix, every cell recorded before the fix is
  re-recorded from its existing project tree, or the matrix restarts. Scoring
  code is never changed to make a recorded cell score better.

## Declared confounds

- Model pretraining exposure and public corpus size are confounded with the
  runtime in every arm. The ablation bounds the skill-doc contribution only.
- The v2 briefs are shorter and tighter than the Harbor instructions they came
  from: every slug needed added pacing constraints so its beats are reachable
  from a cold title inside 600 frames. Results describe agent codegen on short,
  demo-shaped tasks, not on the original task scope.
- Art and presentation quality are not measured at all. The rubric's visual
  criteria are written as negations of engine primitives and cannot be restated
  engine-neutrally, so v2 says nothing about how the games look.
- Trace authorship is per arm: each generator writes its own traces and click
  coordinates. An arm that writes bad traces scores low for a reason that is
  part of the codegen task but is not the runtime.

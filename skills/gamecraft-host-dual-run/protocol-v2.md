# Host Protocol v2 — engine-toolchain effect on agent codegen

**Claim class: `engine_toolchain_effect`.** Separate from v1 (`host_product_stack_diagnostic`). Never merge v1 narrative excerpt cards and v2 machine metrics into one table.

Publishable sentence shape:

> Under a fixed agent configuration and a fixed task spec, switching the runtime toolchain (Godot vs 1Game) changes the rate at which the agent produces a game that builds, launches, reaches the pre-registered beats, and satisfies the pre-registered state assertions.

Never publishable from this design: pure-engine quality. Model pretraining exposure, community corpus size, and skill-doc quality are confounded with the runtime. Subsequent matrices do not spawn an ablation arm; the skill mount stays part of the 1Game ecological default and is not separated from the runtime.

## Arms (all newly generated)

| Arm | System envelope | Role |
| --- | --- | --- |
| `godot` | Godot toolchain appendix | reference |
| `1game_eco` | 1Game appendix + `@1game/skill` | ecological default |

Do not spawn `1game_bare`. That arm existed only on the frozen 2026-09 72-cell run (`prereg-2026-09-matrix.md`) to bound the skill-doc contribution; later experiments are two-arm. The scorer may still read a `1game_bare` cell already on disk.

USER bytes identical across arms (hash before spawn, see `packing.md`). Do not give Godot a compensating skill; that would be a different design.

Primary contrast: `godot` vs `1game_eco`.

## Metrics

Machine-checked, no multimodal judge on the primary path:

1. **BUILD** — the code compiles (`1game build` for 1Game; for Godot the headless check is one invocation and cannot separate the two).
2. **LAUNCH** — the compiled game assembles and ticks, and replay produces demo logs without a fatal error. Code that typechecks but dies building its scene tree is a launch failure, not a build failure.
3. **REACH** — fraction of pre-registered beats observed anywhere in the run's probe streams.
4. **STATE** — of the beats the run reached, the fraction that passed their flag assertions everywhere they were reached. **Primary estimand.**
5. **Stability** — same trace replayed 3x yields the same beat outcomes.

Beats are task requirements, not per-trace requirements. A locked-gate trace is not supposed to reach the ending, so both metrics take the union across the run's demos. Scoring each demo against every beat would cap every arm below 1.0 and move the denominator with the number of traces a generator happened to ship — not comparable across arms. REACH and STATE separate two different failures: an arm that reached few beats but got them right scores low REACH and high STATE.

Secondary, descriptive only: v1 PNG excerpt (narrative), code size, dependency count, first build duration. These never enter the engine conclusion.

`void ≠ fail ≠ 0`. A cell with no probe output is void (instrument failure) and publishes no number; void rate is reported separately because it is itself a toolchain effect.

## Probe contract (engine-neutral)

The task brief requires the game to emit, after each handled input, one JSON line to stdout (Godot `print`) or the 1gameplay log:

```json
{"probe": 1, "beat": "examine_first", "flags": {"collected": 1, "gate": "locked", "ending": null}}
```

Beats and assertions live in `host_probes/<slug>.json` (`probe_schema_version: 1`, operators `eq` / `min` / `max` / `in` / `not_null`). Parser and scoring: `gamecraft_bench/verifier/probe.py`. The last record per beat wins. Pixels are archive evidence only.

Acknowledged bias: writing the probe is part of the codegen task, identical for every arm. If one runtime makes logging harder, that is a toolchain effect and is reported, not patched away.

## Beat alignment

Each arm authors its own traces and click coordinates (generator-authored; the parent never rewrites clicks). Only the **beat identity** is shared. A missing beat is `seen=false`, not a failed assertion. Cameras (`x11_post_event` vs `1game_post_event_plus2`) no longer affect the primary metric.

## Matrix

- Tasks: 8 slugs across narrative / strategy / action / simulation. Each needs a 1Game appendix and a `host_probes/<slug>.json`.
- Repeats: ≥5 independent gens per (task × arm).
- Agents: ≥2 models, identical wrapper settings (effort, timeout, tool surface).
- Order: gens of later repeats must not see earlier scores; nothing from `host_excerpt_ledger/` is attached to generators.

Generators are barred from `/workspace/gamecraft_bench/`, `/workspace/host_probes/`, and `/workspace/tasks/`. A generator that reads `host_probes/<slug>.json` has read the exact assertion thresholds it is scored on, which turns STATE into a measure of how well it can target a known oracle. The envelopes carry this as a hard line; a cell whose generator reached the scorer is contaminated and does not enter the matrix.

## Analysis

Pre-register before looking at any v2 data (`prereg-template.md`): primary estimand STATE, task as random effect, effect size with interval, no single-number leaderboard. Void and Unscored never become 0. Report void rates per arm.

## Phases

- **P0** protocol, probe schema, parser, ledger v2 (no gens)
- **P1** one slug end-to-end, pipeline validation only, results not published
- **P2** write appendices + probe schemas for the remaining slugs; review briefs for engine bias
- **P3** run the pre-registered matrix without interim analysis
- **P4** analysis and an explicit unidentified-confounds section

## Unchanged

Harbor 140 `instruction.md` / `rubric.json` / `reward.txt` stay a separate Godot track. v2 runs live under `$HOME/gamecraft-host-runs/<experiment_id>/`. `JOBS_ROOT` is never `$HOME`. Ledger promotion stays `O_EXCL` under `host_excerpt_ledger/<experiment_id>.json`.

# Host Protocol v2 — engine-toolchain effect on agent codegen

**Claim class: `engine_toolchain_effect`.** Separate from v1 (`host_product_stack_diagnostic`). Never merge v1 narrative excerpt cards and v2 machine metrics into one table.

Publishable sentence shape:

> Under a fixed agent configuration and a fixed task spec, switching the runtime toolchain (Godot vs 1Game) changes the rate at which the agent produces a game that builds, launches, reaches the pre-registered beats, and satisfies the pre-registered state assertions.

Never publishable from this design: pure-engine quality. Model pretraining exposure, community corpus size, and skill-doc quality are confounded with the runtime. The ablation arm bounds the doc contribution; it does not remove the corpus confound.

## Arms (all newly generated)

| Arm | System envelope | Role |
| --- | --- | --- |
| `godot` | Godot toolchain appendix | reference |
| `1game_eco` | 1Game appendix + `@1game/skill` | ecological default |
| `1game_bare` | 1Game appendix, skill **not** mounted | ablation |

USER bytes identical across arms (hash before spawn, see `packing.md`). The two 1Game appendices must differ only by the skill mount. Do not give Godot a compensating skill; that would be a different design.

Primary contrast: `godot` vs `1game_eco`. Ablation: `1game_eco` vs `1game_bare`.

## Metrics

Machine-checked, no multimodal judge on the primary path:

1. **BUILD** — build/launch check exits 0 (`build_check` for Godot, `1game build` for 1Game).
2. **LAUNCH** — replay starts and produces demo logs without a fatal error.
3. **REACH** — fraction of pre-registered beats observed in the probe stream.
4. **STATE** — fraction of pre-registered beats whose flag assertions pass. **Primary estimand.**
5. **Stability** — same trace replayed 3x yields the same beat outcomes.

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

## Analysis

Pre-register before looking at any v2 data (`prereg-template.md`): primary estimand STATE, task as random effect, effect size with interval, no single-number leaderboard. Void and Unscored never become 0. Report void rates per arm.

## Phases

- **P0** protocol, probe schema, parser, ledger v2 (no gens)
- **P1** one slug end-to-end, pipeline validation only, results not published
- **P2** write appendices + probe schemas for the remaining slugs; review briefs for engine bias
- **P3** run the pre-registered matrix without interim analysis
- **P4** analysis, ablation, and an explicit unidentified-confounds section

## Unchanged

Harbor 140 `instruction.md` / `rubric.json` / `reward.txt` stay a separate Godot track. v2 runs live under `$HOME/gamecraft-host-runs/<experiment_id>/`. `JOBS_ROOT` is never `$HOME`. Ledger promotion stays `O_EXCL` under `host_excerpt_ledger/<experiment_id>.json`.

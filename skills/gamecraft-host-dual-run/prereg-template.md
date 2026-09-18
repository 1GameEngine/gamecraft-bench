# Pre-registration — `engine_toolchain_effect` (fill before any v2 data is seen)

- `experiment_id`:
- Date (UTC):
- Protocol: `protocol-v2.md`, probe schema version 1

## Hypothesis

Primary contrast: `godot` vs `1game_eco` on **STATE** (pre-registered beat assertion pass rate).
Directional or two-sided:
Ablation contrast: `1game_eco` vs `1game_bare` (bounds the skill-doc contribution).

## Fixed before data

- Task slugs (8):
- Probe schemas (`host_probes/<slug>.json` hashes):
- Repeats per (task × arm):
- Models and wrapper settings (effort, timeout, tools):
- USER sha256 per slug; envelope hashes per arm:
- Engine versions (Godot, 1game, 1gameplay, engine-bundle):

## Analysis plan

- Primary estimand: STATE, task as random effect; report effect size + interval.
- Secondary: BUILD, LAUNCH, REACH, stability; reported separately, never summed into one score.
- Void handling: void cells publish no number; void rate reported per arm; void never becomes 0.
- Excluded from the engine conclusion: v1 PNG excerpt, Harbor `reward.txt`, stub scores, `compare.py` columns.
- No interim analysis. No metric added after seeing data. No slug dropped after seeing data.

## Declared confounds (cannot be removed by this design)

- Model pretraining exposure and community corpus size differ per runtime.
- Task suite originates from a Godot-oriented benchmark; brief bias review done at P2 by:
- The probe requirement may be easier to satisfy on one runtime.
- System envelopes differ by construction; only the skill mount is ablated.

## Sign-off

Filled by:
Frozen at (commit):

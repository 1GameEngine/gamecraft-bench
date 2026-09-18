# Authoring a v2 slug (USER brief + probe schema)

Parent-side work. Generators never see this file.

Each v2 slug needs two artifacts:

- `skills/gamecraft-host-dual-run/v2/<slug>-main.md` — the USER brief, identical bytes for every arm.
- `host_probes/<slug>.json` — the beat assertions the cell is scored on.

`visualnovel-keepsake` is the worked example for both. Read it before writing a new one.

## The brief

Source material is `tasks/<slug>/instruction.md` and `tasks/<slug>/tests/rubric.json`. Harbor's instruction is Godot-specific and far too long; the v2 brief is a compressed, engine-neutral restatement of the same game.

Hard rules:

- **No engine anywhere.** No Godot, no 1Game, no node types, no file layout, no API names, no language. "A scene", "the screen", "an input" are fine. If a sentence would need rewriting for the other arm, it is wrong.
- **No rubric ids.** Never mention M1/D3/A2 or quote rubric text. The generator is building a game, not targeting a scorer.
- **Keep the mechanics, drop the Godot scaffolding.** Viewport 1280×720, demo ≤20 seconds / 600 frames at 30 fps, cold start from title, `demo_outputs/*.json` traces, the asset mount paths. Copy this wording from the keepsake brief rather than inventing variants.
- **Same self-report section, verbatim**, except for the beat list and the flag list. Copy it from `keepsake-main.md`, including the fenced example line and the rules beneath it.

## The beats

Beats are the run's pre-registered checkpoints. Design them so that:

- **They are engine-neutral and mechanism-neutral.** A beat names a point in the game's progression ("the player has cleared a wave"), never how it is implemented.
- **They are observable from state, not from pixels.** Every beat's assertion reads flags the game already has to track.
- **They span the paths the task's traces are asked to demonstrate.** Scoring unions beats across the run's demos, so a gated beat and a failure beat may live on different traces; that is expected, not a gap.
- **4 to 8 beats.** Fewer cannot separate arms; more turns REACH into noise about trace budget.
- **Flags stay small.** 2 to 4 named flags, each a count, a named state string, or null. No nested objects, no arrays.

Ordering ids by progression makes the cell json readable but carries no meaning to the scorer.

## The assertions

Operators are `eq`, `min`, `max`, `in`, `not_null`. Write the weakest assertion that still catches the failure you care about:

- `{"collected": {"min": 1}}` at the first-progress beat catches a game that reports progress it has not made.
- `{"gate": {"in": ["locked", "blocked"]}}` tolerates naming the generator chose, since the brief does not dictate vocabulary beyond the listed values.
- Assert `not_null: false` where a state must *not* have happened yet; that is how a beat proves ordering.

Do not assert anything the brief does not require the game to track. An assertion on an unspecified flag scores generators on guessing.

## Check before shipping

- `python -c "from gamecraft_bench.verifier.probe import load_probe_schema; load_probe_schema('host_probes/<slug>.json')"` parses.
- Every beat id in the schema appears in the brief's beat list, and vice versa.
- Every flag named in an assertion appears in the brief's flag list.
- Grep the brief for engine names, rubric ids, and file extensions that imply a stack.

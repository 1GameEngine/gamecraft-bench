# Echo Climb

Build **Echo Climb**, a complete, shippable micro-game: a tower-climbing platformer where your past attempts become the platforms you climb on.

A climber ascends a tower that is mostly empty air. Every attempt that ends is recorded, and the recording replays on later attempts as a translucent past self whose body is **solid** — you can land on it, jump off it, ride it upward. The first attempt reaches a ledge or two and falls. The second attempt stands on the first. The loop is **climb, fall, climb on what fell**. The player's real decision is when to spend an attempt building a useful stepping stone and when to push for height.

This is not a physics sandbox and not a tech demo. Viewport is **1280×720**. A demo is **≤20 seconds / 600 frames** at 30 fps. That is a **short mechanical game**: an attempt is seconds long, not minutes, the height readout is **always on screen**, and ending an attempt drops straight back into the next one.

Every demo starts **cold from the title**. No mid-run continue, no pre-seeded attempt in progress. Omit the JSON key `scenario` on every trace.

## What the player can do

1. **Authored opening** — Styled title showing the tower stretching upward with past-self silhouettes on it, the game's name, and a way in plus a way to the stats. Starting is player-driven (click or key), not a timed auto-start.
2. **Climb** — The climber can run, jump, and slide down a vertical surface it is pressed against. Movement keys are **held**, and the climber keeps moving while a direction is held.
3. **Attempts become past selves** — When an attempt ends — a fall, or the player ending it — the whole attempt is recorded. On later attempts the recordings replay, **several at once**, translucent and clearly distinguishable from the live climber. A recording that exists only in memory and never replays does not count.
4. **Past selves are solid** — A replaying past self can be landed on, jumped from, and ridden as a moving platform. Not decoration: it carries the climber's weight.
5. **Gaps that need a scaffold** — Fixed ledges are sparse and the vertical gaps between them are too large to cross from the fixed geometry alone. **At least one such gap sits low enough that one or two recorded attempts make it crossable**, so blocked-then-crossed is showable inside a single short recording. Climbing past that, each further stretch of the tower needs more layered attempts. Not "the whole tower is climbable on the first try", not "the recordings are a bonus".
6. **Named height markers and a best-ever** — The tower has **named markers** up its height (a ledge name, a tier name, a floor number — your choice). The current height, the marker last passed, and the best-ever height are all visible while climbing, and the best-ever carries across sessions along with the recorded attempts.
7. **Solidify** — After several attempts the player may turn one recorded attempt into a **permanent ledge**: it stops replaying and stays put forever. The choice is irreversible and it costs that recording's movement, so which one to freeze matters.
8. **Height tiers and milestones** — The tower looks different as it rises (at least **three** visually distinct tiers — background, ledge style, atmosphere). Passing milestone heights unlocks a cosmetic trail or look for the climber that is **visible during play**.
9. **Full loop** — Title → attempt → end-of-attempt summary showing height reached and how many past selves were active → solidify choice when it is available → next attempt, without restarting the process. A stats view shows attempts, recordings, permanent ledges, and best height.

Prefer illustrated or pixel-art climber, past selves, ledges, and themed UI.

## Assets

Read-only host libraries (copy into this project's `assets/`; do not edit the mounts):

- `/workspace/assets/library/` — Kenney CC0
- `/workspace/assets/library-oga/` — respect each `LICENSE.txt`

If a mount is missing, ship with whatever is in-tree; do not invent a second library path.

## Self-report (required)

Your game must report its own state so the run can be checked automatically.

After each player input is fully handled, print exactly one line of JSON to standard output:

```
{"probe": 1, "beat": "<beat id>", "flags": {"<name>": <value>, ...}}
```

Rules:

- One line, valid JSON, nothing else on that line.
- `beat` is one of the beat ids listed below. Print the beat the player just reached.
- `flags` carries the named state values listed below. Use numbers for counts, strings for named states, and `null` when a state has not happened yet.
- Print a line after **every** handled input, including inputs that change nothing.
- Keep printing for the whole session; never buffer the lines until exit.
- Do not print anything else that begins with `{"probe"`.

This output is part of the deliverable. A build that plays correctly but prints no probe lines counts as incomplete.

Beat ids:

- `title` — the title screen is showing and no attempt has begun.
- `climb_start` — an attempt has begun and the climber is at the tower base.
- `wall_slide` — the climber has slid down a vertical surface during an attempt.
- `marker_reached` — the climber has passed a named height marker in the current attempt.
- `gap_blocked` — the attempt has stalled at a gap that what is currently in the tower cannot get the climber across.
- `fall_recorded` — an attempt has ended in a fall and that attempt is now part of the tower as a past self.
- `ghost_assist` — the climber has crossed the previously uncrossable gap using a past self's body.
- `solidify` — one recorded attempt has been made a permanent ledge.

Flag names:

- `attempts` — how many attempts have begun so far (a number).
- `ghosts` — how many past attempts are part of the tower right now, whether still replaying or made permanent (a number).
- `marker` — the name of the highest marker passed in the current attempt, or `null` before any has been passed.
- `gate` — the state of the low gap that needs a past self to cross, as one of `blocked`, `open`, or `null` before it is relevant.

## Demo traces (required)

Ship **1–10** files at `demo_outputs/*.json` (no root `traces.json`). Events: `mouse_click` / `mouse_down` / `mouse_up` / `mouse_move` / `key_press` / `key_down` / `key_up` / `wait`. Clicks must match **this** project's 1280×720 layout. Held movement is a `key_down` and a later `key_up`: each of those is a handled input, so each gets its own reported line, and while a key is simply held down there is no new input to report. A beat is a point in the climb the game already tracks — a marker passed, a slide, a fall, a crossing — not a position on a particular frame, so repeat the beat the climber is on for inputs that reach nothing new.

You need **three separate traces**, each from **cold title**:

1. **Climbing** — start an attempt, run and jump between fixed ledges, slide down a vertical surface, pass **≥1 named marker**, stall at the low gap, and fall so the attempt is recorded.
2. **Scaffold contrast** — inside one recording, end a first attempt quickly, then in the following attempt stand on that past self to cross the gap the first attempt could not.
3. **Solidify** — reach the point where a recorded attempt can be frozen, and freeze one.

Traces 2 and 3 may share the fall-then-climb-again shape as long as all three listed evidences exist as separate cold-title recordings. Ending an attempt on purpose is legitimate: falling costs a second or two and buys a scaffold.

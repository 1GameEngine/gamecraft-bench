# Bulwark

Build **Bulwark**, a complete, shippable micro-game: a tower-defense game about holding a chokepoint with too few defenders and too little budget.

Hostiles pour along fixed corridors toward a base that cannot move. The player's only tools are a small hand of deployable defender types and a deployment budget that ticks upward on its own. The loop is **read the wave, spend or save, place, hold**. Every placement is a commitment; every wave is stronger than the last; the tension is that budget spent on a safe pick now is not there for the desperate answer later.

This is not a sandbox and not a tech demo. Viewport is **1280×720**. A demo is **≤20 seconds / 600 frames** at 30 fps. That is a **short mechanical game**: the battlefield is **always on screen**, placing a defender is **1–2 inputs**, waves are **seconds long, not minutes**, and the budget ticks fast enough that a player can afford a second defender within the demo window.

Every demo starts **cold from the title**. No mid-run continue, no pre-placed defenders, no pre-banked budget. Omit the JSON key `scenario` on every trace.

## What the player can do

1. **Authored opening** — Styled title into a stage choice, then into a battlefield. Entry is player-driven (click or key), not an auto-advance cutscene and not a straight drop into combat.
2. **Deployment** — A visible grid battlefield with the enemy corridor, the legal deployment spots, the spawn point, and the base endpoint all distinguishable. The player picks a defender from a visible hand of cards, each showing its cost, and places it on a legal spot. A successful placement spends budget and puts a defender on the field.
3. **Clean refusal** — Placing on an illegal spot, or placing something the current budget cannot pay for, **refuses visibly and changes nothing** — no defender, no spend. Silent no-ops do not count.
4. **Distinct defenders and hostiles** — At least three defender types with different roles (hold the line, hit at range, hit a group, support), and at least three hostile types that differ in a way the player must answer differently (tougher, faster, arriving in numbers, ignoring a blocker). Not recolors of one unit.
5. **The assault** — Hostiles walk the corridor. Defenders engage what is in reach, both sides lose health, and anything at zero health leaves the field. A hostile that reaches the base endpoint costs the base some of its remaining life.
6. **Discrete waves that escalate** — At least two waves, arriving as separate pushes with a readable pause between them, each harder than the one before through count, type, speed, or toughness. Clearing a wave is a visible event.
7. **Both resolutions** — Clearing the **final** wave declares victory. The base's life reaching zero declares defeat. Both are shown as styled result screens, not a frozen field.
8. **Full loop** — Title → stage → deploy → waves → result → retry or return to the stage choice without restarting the process.

Prefer illustrated or pixel-art units, corridors, and themed HUD over plain shapes and default widgets. The budget, the current wave, and the base's remaining life must be readable on screen for the whole battle.

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

- `title` — the title screen is showing, no battle has started and nothing has been deployed.
- `deploy_first` — the player has successfully placed their first defender in this battle.
- `deploy_refused` — the player's placement attempt was refused, because the spot was illegal or the budget could not pay for it.
- `wave_cleared` — the player has cleared a wave with the base still standing.
- `wave_later` — a second or later wave has begun.
- `defeat` — the base's life has reached zero and the defeat result is showing.
- `victory` — the final wave has been cleared and the victory result is showing.

Flag names:

- `deployed` — how many defenders the player has successfully placed in this battle so far (a number).
- `wave` — the number of the wave now under way, counting from 1, and `0` before the first wave arrives (a number).
- `base` — the base's remaining life (a number; `0` once the base has fallen).
- `outcome` — the resolution now showing, as one of `victory`, `defeat`, or `null` while the battle is still live.

## Demo traces (required)

Ship **1–10** files at `demo_outputs/*.json` (no root `traces.json`). Events: `mouse_click` / `mouse_down` / `mouse_up` / `mouse_move` / `key_press` / `key_down` / `key_up` / `wait`. Drags are `mouse_down`, `mouse_move`, `mouse_up`. Clicks must match **this** project's 1280×720 layout.

You need **three separate traces**, each from **cold title**:

1. Deployment works and refusal works: at least one successful placement **and** at least one refused attempt in the same trace.
2. **Victory**: at least two waves arrive, a wave is cleared, and the final wave is cleared into the victory result.
3. **Defeat**: hostiles leak until the base's life reaches zero and the defeat result is shown.

Traces 2 and 3 may reuse the same stage as long as all three listed evidences exist as separate cold-title recordings.

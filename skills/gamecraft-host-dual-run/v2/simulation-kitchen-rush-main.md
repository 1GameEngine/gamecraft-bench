# Kitchen Rush

Build **Kitchen Rush**, a complete, shippable micro-game: a time-pressure cooking simulation about running a restaurant kitchen through a dinner rush.

Orders land on the rail with a recipe and a countdown. Each dish wants specific steps at specific stations in a specific order — chop, cook, assemble, plate, serve — and several dishes are live at once. The tension is multitasking: food left cooking too long is ruined, a dish sent out wrong is a lost order, and a dish sent out fast is worth more. The loop is **take the order, work the stations in sequence, deliver, get paid**. Between shifts the takings buy better stations and new recipes, and the next shift asks for more.

This is not a management epic and not a tech demo. Viewport is **1280×720**. A demo is **≤20 seconds / 600 frames** at 30 fps. That is a **short mechanical game**: the kitchen and the order rail are **always on screen**, a station step is **1–2 clicks or one drag**, and the first shift is **small enough to finish, see its summary, and reach the upgrade screen inside one demo** — not a ten-minute service.

Every demo starts **cold from the title**. No mid-run continue, no pre-stocked stations, no pre-banked coins. Omit the JSON key `scenario` on every trace.

## What the player can do

1. **Authored opening** — Styled storefront title with the game name and a start control, leading into the first shift. Starting is player-driven (click or key), not an auto-advance from a splash.
2. **Distinct stations** — Several genuinely different work stations (a board to chop at, heat to cook on, a fryer, an oven, a plating counter, a serving window), each with its own interaction and its own visible progress while it works. Not one station reskinned five times.
3. **Orders with a clock** — Orders arrive on a visible rail carrying their recipe and a countdown that the player can read. An order that runs out of time is **lost**, with visible negative feedback. Several orders are live at once.
4. **Sequenced recipes** — A recipe is multiple steps at different stations in a **required order**. Doing steps out of order, or delivering a dish that is missing a step, does not complete the order. Several distinct recipes, not one recipe renamed.
5. **Ruining food** — Food left on heat past its window is **ruined** and wasted, with visible warning before and visible feedback after. Monitoring more than one station at once must be a real demand.
6. **Pay and spend** — Delivering an order correctly pays, and paying faster pays better. The takings are spendable between shifts on station improvements and new recipes, and the purchase changes something the player can see.
7. **Full loop** — Title → shift → shift summary (delivered, lost, earnings, rating) → upgrade screen → next shift, and back, without restarting the process.

Order countdowns, cooking windows, and the length of a shift are all measured in the game's own frames, so the same inputs replayed on a fresh launch produce the same outcome. Running tallies — orders delivered, orders lost, steps completed — move when the game handles the input or resolves the outcome that caused them, never on a clock of their own. Keep the first shift's order list short: the summary and the upgrade screen must be reachable by a player who is quick, inside the demo budget.

Prefer illustrated or pixel-art food, stations, and themed UI.

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

- `title` — the title screen is showing and no shift has started.
- `shift_start` — a shift is underway and at least one order is waiting on the rail.
- `prep_step` — the player has completed a required preparation step of an order at a station.
- `order_served` — an order has been delivered correctly.
- `order_lost` — an order has been lost: it ran out of time, was delivered wrong, or its food was ruined.
- `shift_summary` — the end-of-shift summary is showing.
- `shop` — the between-shift upgrade screen is showing.

Flag names:

- `served` — how many orders have been delivered correctly so far this session (a number).
- `lost` — how many orders have been lost so far this session, counting timeouts, wrong deliveries, and orders whose food was ruined (a number).
- `steps` — how many required recipe steps the player has completed at stations so far this session (a number).
- `stage` — what is on screen now, as one of `title`, `kitchen`, `summary`, `shop`, or `null` before it is set.

## Demo traces (required)

Ship **1–10** files at `demo_outputs/*.json` (no root `traces.json`). Events: `mouse_click` / `mouse_down` / `mouse_up` / `mouse_move` / `key_press` / `key_down` / `key_up` / `wait`. Clicks must match **this** project's 1280×720 layout.

You need **three separate traces**, each from **cold title**:

1. A **delivered order**: start the shift, work a recipe through its steps in order, and deliver it correctly.
2. A **lost order**: a dish ruined on heat, or an order allowed to run out its clock, with the loss visible on screen.
3. **Shift end**: reach the shift summary and then the upgrade screen, both inside the trace.

Traces may overlap as long as all three listed evidences exist as separate cold-title recordings. Every trace must fit the 600-frame budget without relying on a specific real-world speed: if a beat can only be reached when playback happens to run fast, the trace will not count.

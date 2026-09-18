# Wave Commander

Build **Wave Commander**, a complete, shippable micro-game: a wave-defense shooter about one defender holding the centre of an arena against organised attacks.

The player commands a lone turret or mobile defender in the middle of an arena. Enemies arrive in waves from the edges — fast rushers, ranged shooters, shielded tanks, and heavier support units — and each cleared wave pays out currency that is never enough for everything the player wants. The loop is **hold the line, clear the wave, spend, adapt**. Between waves the player buys weapon and defence upgrades, and those purchases must visibly change the fighting that follows.

This is not a survival grind and not a tech demo. Viewport is **1280×720**. A demo is **≤20 seconds / 600 frames** at 30 fps. That is a **short mechanical game**: the arena is **always on screen**, the defender fires from the first second, and the between-wave shop is **a few clicks** — not a menu tree.

Pacing is a hard requirement, not a taste note. The first wave must be **clearable in seconds**, and the between-wave shop plus the opening of the following wave must all fit inside **one** 20-second recording. Nothing the game needs to prove about its loop may sit behind several waves of grinding.

Every demo starts **cold from the title**. No mid-run continue, no preloaded upgrades, no pre-advanced wave counter. Omit the JSON key `scenario` on every trace.

## What the player can do

1. **Authored opening** — Styled military-themed title with the game name and a difficulty choice, then deploy into the arena. The title is a screen the player acts on, not a splash that times out.
2. **Move, aim, fire** — The defender moves freely inside a bounded arena, aims a full 360 degrees toward the pointer, and fires on click. Aiming is not snapped to four directions.
3. **Organised waves** — Enemies arrive in announced waves, not as a random trickle. Each wave is a stated wave number with a visible start announcement, and later waves grow in count, mix, and arrival pattern (one-sided rush, pincer, encirclement, shielded column with support behind).
4. **Several distinct enemies** — At least five enemy kinds that **behave** differently, not one silhouette recoloured: something that charges, something that shoots from range, something armoured that soaks fire, something that splits or spawns, something that buffs or shields its neighbours.
5. **Earned currency and a between-wave shop** — Clearing a wave opens a brief shop showing several distinct purchases (fire rate, damage, spread, shield repair, a deployable, extra charges of the special). The player spends earned currency, cannot afford everything, and the purchase **changes the next wave's combat observably**.
6. **A limited-charge screen clear** — A special strike the player triggers directly that destroys the enemies currently on screen with a loud visual payoff. It has **a small number of charges**, spends one per use, and can run out.
7. **Damage and defeat** — The defender has health or shields that deplete when hit, with visible damage feedback, and the run ends when it is gone.
8. **Escalation and a summary** — Every fifth wave is a heavier wave built around one large enemy with distinct attack phases and its own escorts. The run ends after the final wave or on defeat with a summary of how far the player got and what they destroyed and bought.
9. **Full loop** — Title → wave → shop → next wave → summary → back to the title or straight into another run, without restarting the process.

Prefer illustrated or pixel-art units, projectiles, arena dressing, and themed HUD panels over plain shapes and unstyled labels.

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

- `title` — the title screen is showing and no wave has started.
- `wave_start` — a wave is underway and the defender can fight.
- `first_kill` — the player has destroyed their first enemy.
- `special_used` — the player has spent a charge of the screen-clearing strike.
- `shop_open` — a wave has been cleared and the between-wave shop is showing.
- `upgrade_bought` — the player has bought at least one upgrade with earned currency.
- `wave_advanced` — a later wave is underway after leaving the shop.
- `results` — the run is over and the summary is showing.

Flag names:

- `wave` — the number of the wave now in progress, `0` before the first wave begins (a number).
- `kills` — how many enemies have been destroyed so far this session (a number).
- `upgrades` — how many upgrades have been bought so far this session (a number).
- `phase` — what the game is showing right now, as one of `title`, `combat`, `shop`, or `results`.

## Demo traces (required)

Ship **1–10** files at `demo_outputs/*.json` (no root `traces.json`). Events: `mouse_click` / `mouse_down` / `mouse_up` / `mouse_move` / `key_press` / `key_down` / `key_up` / `wait`. Clicks must match **this** project's 1280×720 layout.

You need **three separate traces**, each from **cold title**:

1. Title into the first wave, with the defender moving, aiming, destroying enemies, and spending the screen-clearing strike.
2. The first wave **cleared**, an upgrade **bought** in the shop, and the following wave underway.
3. The run **ending** with the summary showing.

A trace may carry more than one of these evidences as long as all three exist across the shipped cold-title recordings.

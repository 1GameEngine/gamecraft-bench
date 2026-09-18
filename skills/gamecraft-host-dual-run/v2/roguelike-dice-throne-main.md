# Dice Throne

Build **Dice Throne**, a complete, shippable micro-game: a dungeon-crawling roguelike whose whole combat system is a handful of dice.

A warrior fights down a dungeon by rolling dice. Each turn the player rolls a set of dice, keeps the faces they want, and rerolls the rest — **at most two rerolls per turn**. Faces are abilities, not numbers: swords deal damage, shields block, hearts heal, skulls fire a special, a blank does nothing. The enemy rolls its own dice **in the open**, so both sides can read the turn before it resolves. Equipment found between fights **rewrites die faces** — a flame sword turns a sword face into a fire-sword, enchanted plate adds a shield face — so the set of faces the player is carrying is the thing that grows over a run.

This is not a 40-minute deckbuilder and not a tech demo. Viewport is **1280×720**. A demo is **≤20 seconds / 600 frames** at 30 fps. That is a **short mechanical game**: the dice are **always on screen**, a turn is **a few clicks**, the route to the boss is **short enough that one demo can reach a run's result screen**, and screens are **styled cards** — not menus of unread text.

Every demo starts **cold from the title**. No mid-run continue, no pre-owned equipment, no partially cleared route. Omit the JSON key `scenario` on every trace.

## What the player can do

1. **Authored title** — Styled title with dice and readable face icons, into a run. Starting a run is player-driven (click or key).
2. **A route with choices** — A branching route of stops the player picks between: ordinary fights, a tougher one, a place to buy face changes or new dice, a place to recover, and a boss at the end. Not a single forced corridor.
3. **Roll, keep, reroll** — Each turn the player rolls their set (at least five dice), then **locks the faces they keep** and rerolls the rest. The reroll allowance is **two per turn and no more**; a further reroll attempt must visibly do nothing rather than roll again. Locked and unlocked dice must be distinguishable on screen.
4. **Faces resolve, both sides** — Finalizing a turn activates the kept faces: damage, blocking, healing, and a special each have a distinct and visible effect. The enemy's dice are **shown before the turn resolves**, then resolve the same way. At least four face types must actually do something.
5. **Equipment rewrites faces** — Between fights, the player is offered equipment that **replaces, upgrades, or adds a die face**. Several distinct items with different effects, so two runs can carry different sets. Items that only add flat stats and leave the faces alone do not count.
6. **Enemies that demand different keeps** — Several distinct opponents whose dice differ (more attack faces, more shields, a special of their own), so the keep/reroll choice is not the same every fight. The boss has faces the ordinary enemies do not.
7. **A run that ends** — Win or die, the run closes on a result screen naming the outcome and what the run achieved (how far it got, what it was carrying), and the player can return to the title and start again without restarting the process. Returning to the title clears the run: a fresh run starts from nothing.

Prefer illustrated or pixel-art dice, enemies, and item icons, and themed UI.

## Randomness

Dice are random; the run must still be replayable.

- On a cold start the game must seed its randomness from a **fixed value baked into the build**, never from the clock, the process, or system entropy. Replaying the same recorded inputs on a fresh launch must produce the same rolls, the same fight, and the same self-report lines every time.
- Nothing the run is checked on may depend on what a die happens to show. Reaching a checkpoint below, and the state reported with it, must hold for any roll: report counts and named states, not the faces that came up.
- Randomness may still drive variety *within* a run (which enemy, which loot is offered) as long as a replay of the same inputs reproduces it.

## Assets

Read-only host libraries (copy into this project’s `assets/`; do not edit the mounts):

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

- `title` — the title screen is showing and no run is under way.
- `route_choice` — the branching route is showing and the player is choosing where to go next; no turn is in progress.
- `roll_ready` — the turn's dice have been rolled, the enemy's dice are showing too, and the keep/reroll decision is waiting on the player.
- `reroll_exhausted` — the turn's reroll allowance is used up and no further reroll is available.
- `turn_resolved` — a turn has been finalized and both sides' faces have been applied.
- `encounter_cleared` — an opponent has been defeated.
- `equip_applied` — equipment has changed at least one die face on the player's dice.
- `run_over` — the run has ended and its result screen is showing.

Flag names:

- `rerolls_left` — how many rerolls are still available in the keep/reroll decision the player is being asked to make right now (a number), or `null` whenever no keep/reroll decision is pending.
- `encounters_won` — how many opponents this run has defeated so far (a number).
- `faces_modified` — how many die faces equipment has changed this run (a number; 0 before any equipment applies).
- `outcome` — the id or short name of the run result now showing, or `null` while the run is still live.

## Demo traces (required)

Ship **1–10** files at `demo_outputs/*.json` (no root `traces.json`). Events: `mouse_click` / `mouse_down` / `mouse_up` / `mouse_move` / `key_press` / `key_down` / `key_up` / `wait`. Clicks must match **this** project’s 1280×720 layout.

You need **three separate traces**, each from **cold title**:

1. **The loop** — title, a route choice, then a fight: roll, keep some dice, reroll the rest, finalize, and beat the opponent.
2. **The reroll ceiling** — one turn in which the whole reroll allowance is spent and a further reroll attempt changes nothing, then the turn resolves.
3. **Faces change** — equipment is taken between fights and the player keeps playing with the rewritten faces, and the run reaches its result screen.

Traces may overlap as long as all three listed evidences exist as separate cold-title recordings.

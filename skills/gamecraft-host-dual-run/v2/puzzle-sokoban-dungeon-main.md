# Sokoban Dungeon

Build **Sokoban Dungeon**, a complete, shippable micro-game: a turn-based crate-pushing dungeon puzzle where every step the player takes is a step the dungeon takes back.

The player walks a grid of stone rooms, shoving crates onto pressure plates to open doors, picking up keys, and dropping down a staircase to the next floor. Enemies move on the same clock: the board is frozen until the player acts, and the moment the player acts, everything else moves once too. The loop is **read the room, plan the push, take the turn, live with it**. Solving the spatial puzzle and surviving the things walking toward you are the same problem.

This is not a level editor and not a tech demo. Viewport is **1280×720**. A demo is **≤20 seconds / 600 frames** at 30 fps. That is a **short mechanical game**: the whole room is **on screen at once**, a turn is **one key press**, and the first room must be solvable in a handful of turns so a cold demo can actually reach the staircase.

Every demo starts **cold from the title**. No mid-run continue, no preloaded floor. Omit the JSON key `scenario` on every trace.

## What the player can do

1. **Authored opening** — Styled title into the first room, with a clear way to begin. Play starts on the grid, not in a settings menu.
2. **Grid movement and pushing** — Four-direction movement, one tile per input. Walking into a crate pushes it one tile the same way; a crate stops against a wall or another crate. Nothing on the board moves until the player moves.
3. **Simultaneous enemy turns** — Every player turn is an enemy turn. Enemies step toward the player or along a patrol, occupy tiles, and end the floor on contact. Enemies that drift in real time, or that ignore the player's turns, are the wrong mechanic. Several kinds with different movement, visibly different from each other.
4. **Gating** — Plates and doors, and keys and the doors they match, gate the room. A door the player has not earned is **refused**, visibly, and the player can see why. Not "everything is walkable anyway", not a door that opens on a timer.
5. **Crate and item variety** — More than one kind of crate (for example one that slides until it hits something, one that takes two shoves). One-use pickups found in the room that change a turn — freeze what is chasing you, pull a crate back, step across the room.
6. **Undo** — The player can rewind a turn: the crates, the enemies, and the turn count all go back. Undo is available during play and after being caught, and the board visibly rewinds.
7. **Full loop** — Title → room → cleared or caught → next floor or retry, and back to the title without restarting the process. Later floors are laid out differently from the first, not the same room again.

Prefer illustrated or pixel-art dungeon tiles, creatures, and themed UI over flat shapes. A readable HUD: which floor, how the player is doing, what they are carrying, how many turns they have spent.

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

- `title` — the title screen is showing and no turn has been taken yet.
- `first_move` — the player has taken their first turn and everything else on the board has moved once.
- `door_blocked` — the player tried a door that the room's plates or keys have not yet opened.
- `door_open` — a door has opened, through a crate on its plate or the matching key.
- `item_used` — the player has spent a one-use pickup.
- `undo` — the player has rewound a turn and the board is back where it was.
- `caught` — an enemy has reached the player and the floor has ended.
- `floor_cleared` — the player has reached the staircase and the floor is done.

Flag names:

- `turns` — how many turns the player has taken on this floor so far (a number, and undo takes it back down).
- `floor` — which floor is in play, counting from 1 (a number).
- `door` — the state of the gated door the player is working on, as one of `locked`, `open`, or `null` before any door is relevant.
- `outcome` — how the current floor ended, as one of `caught`, `cleared`, or `null` while the floor is still in play.

## Demo traces (required)

Ship **1–10** files at `demo_outputs/*.json` (no root `traces.json`). Events: `mouse_click` / `mouse_down` / `mouse_up` / `mouse_move` / `key_press` / `key_down` / `key_up` / `wait`. Clicks must match **this** project's 1280×720 layout.

You need **three separate traces**, each from **cold title**:

1. **Puzzle**: a door refused first, then a crate pushed onto its plate and the same door open.
2. **Threat**: enemies closing in over successive turns, a turn rewound, and a floor ended by enemy contact.
3. **Progress**: a one-use pickup spent, and the staircase reached so the next floor begins.

Traces 2 and 3 may reuse the same opening moves as long as all three listed evidences exist as separate cold-title recordings.

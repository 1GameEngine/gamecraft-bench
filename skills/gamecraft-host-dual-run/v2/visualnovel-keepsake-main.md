# Keepsake

Build **Keepsake**, a complete, shippable micro-game: a quiet memory-reconstruction visual novel about sorting a late person’s belongings.

Someone has died. The player sorts what they left behind. A faded photograph, a folded letter, a worn ring, a diary with a torn-out page — objects hold fragments of a life and do not reveal meaning in a fixed order. The loop is **examine, remember, connect, understand**. Player order, and how they read an ambiguous choice the dead made, must change the closing understanding.

This is not a long short-story and not a tech demo. Viewport is **1280×720**. A demo is **≤20 seconds / 600 frames** at 30 fps. That is a **short mechanical game**: the memory board is **always on screen**, examining an object is **1–2 clicks**, and endings are **styled cards or a title change** — not pages of unread prose.

Every demo starts **cold from the title**. No mid-run continue, no preloaded inventory. Omit the JSON key `scenario` on every trace.

## What the player can do

1. **Authored opening** — Styled title into a room or box of belongings, with a little narration that sets mood and absence. Line advance is player-driven (click or key), not a dump of all text and not auto-scroll-only.
2. **Free-order examination** — Several distinct keepsakes (not one item reskinned). The player **chooses which object to pick**, in any order, from a visible room/box. Not a linear “next” slideshow.
3. **Visible memory board** — Each examined keepsake **records** a fragment on a board/journal **already on screen**. The board **grows**. The game tracks found vs not found. Fragments that exist only in code and never appear do not count.
4. **Gating** — Later lines, interpretation choices, or endings **depend on which fragments were found**. At least one later beat is unavailable until a particular discovery. Not “everything reachable regardless of order”, not “only the last click matters”.
5. **Connecting fragments** — At least one later fragment **recontextualizes** an earlier one (a date explains a photo, an absence answers a question).
6. **Two authored endings** — At least two genuinely different closing understandings, shown as styled cards or a title change, reached through different discovery/reading paths.
7. **Full loop** — Title → examine → interpretation → ending → return to title or begin again without restarting the process.

Prefer illustrated or pixel-art keepsakes and themed UI.

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

- `title` — the title screen is showing and nothing has been examined yet.
- `examine_first` — the player has examined their first keepsake.
- `examine_second` — the player has examined a second, different keepsake.
- `gate_locked` — the player tried a later beat that their discoveries do not yet unlock.
- `gate_open` — the later beat has become available through discoveries.
- `ending` — an ending card or title change is showing.

Flag names:

- `collected` — how many distinct keepsakes have been examined so far (a number).
- `gate` — the current state of the gated beat, as one of `locked`, `open`, or `null` before it is relevant.
- `ending` — the id or short name of the ending now showing, or `null` while no ending is showing.

## Demo traces (required)

Ship **1–10** files at `demo_outputs/*.json` (no root `traces.json`). Events: `mouse_click` / `mouse_down` / `mouse_up` / `mouse_move` / `key_press` / `key_down` / `key_up` / `wait`. Clicks must match **this** project’s 1280×720 layout.

You need **three separate traces**, each from **cold title**:

1. Board grows after examining **≥2 objects** in **non-default order**.
2. **Gating contrast** across two traces (one path unlocks a later beat the other path does not).
3. A **different authored ending** than the other ending trace.

Traces 2 and 3 may reuse the two-path idea as long as all three listed evidences exist as separate cold-title recordings.

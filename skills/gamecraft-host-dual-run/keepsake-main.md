# Keepsake — generation MAIN (engine-neutral)

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

## Assets (both arms)

Read-only host libraries (copy into this project’s `assets/`; do not edit the mounts):

- `/workspace/assets/library/` — Kenney CC0
- `/workspace/assets/library-oga/` — respect each `LICENSE.txt`

If a mount is missing, ship with whatever is in-tree; do not invent a second library path. Missing polish is not an engine ranking.

## Demo traces (required)

Ship **1–10** files at `demo_outputs/*.json` (no root `traces.json`). Events: `mouse_click` / `mouse_down` / `mouse_up` / `mouse_move` / `key_press` / `key_down` / `key_up` / `wait`. Clicks must match **this** project’s 1280×720 layout.

You need **three separate traces**, each from **cold title**:

1. Board grows after examining **≥2 objects** in **non-default order**.
2. **Gating contrast** across two traces (one path unlocks a later beat the other path does not).
3. A **different authored ending** than the other ending trace.

Traces 2 and 3 may reuse the two-path idea as long as all three listed evidences exist as separate cold-title recordings.

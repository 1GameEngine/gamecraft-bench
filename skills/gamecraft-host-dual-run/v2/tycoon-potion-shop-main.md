# Potion Shop

Build **Potion Shop**, a complete, shippable micro-game: a cozy-magical alchemy shop where the player brews potions from ingredients and sells them to customers with ailments.

The shop has a cauldron, an ingredient cabinet, shelves, and a counter. The loop is **brew, stock, price, sell, restock**. Ingredients are finite and cost gold; potions are made from them by recipe; customers arrive with a visible ailment and buy the potion that matches it, if the shelf has one and the price suits them. The tension is the ledger: rare ingredients run out, an empty shelf turns a customer away, and a greedy price turns one away just as surely.

This is not an idle game and not a tech demo. Viewport is **1280×720**. A demo is **≤20 seconds / 600 frames** at 30 fps. That is a **short mechanical game**: the whole shop is **on one screen**, brewing is **1–2 clicks and resolves in a second or two**, a customer is waiting at the counter almost immediately, and a day ends on a single input. Measure a day in inputs, not in minutes — every stage of the loop has to be reachable inside one 20-second demo.

Every demo starts **cold from the title**. No mid-run continue, no pre-brewed shelves, no saved shop. The shop opens with a **small starting stock of ingredients and a little starting gold**, so the first brew is possible without shopping first. Omit the JSON key `scenario` on every trace.

## What the player can do

1. **Authored opening** — Styled title into the shop interior. Opening the shop for the day is player-driven (click or key), not a cutscene the player waits out.
2. **Brewing** — The player picks ingredients from the cabinet and combines them at the cauldron. Known recipes show what they need. **Ingredients are spent when a brew starts** and the stock count drops; a finished potion goes onto a shelf. Potions that appear without being crafted do not count.
3. **Recipes that grow** — Not every recipe is known at the start. New ones are found by trying combinations or bought from a recipe book, and the known-recipe collection visibly grows.
4. **Customers with needs** — Customers arrive with a **visible ailment** and buy the potion that matches it. At least three kinds of customer, differing in ailment, budget, and patience. A customer who is served **pays gold**; a customer who finds no match, or finds one priced past their budget, **leaves unserved** and costs the shop reputation.
5. **Pricing** — The player sets the price on a potion that is on the shelf. A high price earns more per sale and turns more customers away; a low price sells faster for less. Price must have an observable effect on whether a sale closes.
6. **Restocking and the ledger** — Ingredients are bought back from a supplier, **spending gold**. Gold tracks income from sales against expense from restocking, and is always visible. Free or infinite ingredients do not count.
7. **Shop upgrades** — At least three purchasable improvements (more shelf space, a faster cauldron, a growing garden, better decor) that change capacity or speed.
8. **Full loop** — Title → open the day → brew / price / sell / restock → a styled day-end summary → the next day begins, with a running count of days and a reputation that carries between them.

Content depth: at least **four potion types** (healing, curing, buffing, antidote) and **five ingredients**, cheap-and-common through rare-and-expensive, each visually its own thing rather than a recolour. Prefer illustrated or pixel-art vials, herbs, crystals and mushrooms, warm shop interior, and themed UI.

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

- `title` — the title screen is showing and the first day has not been opened yet.
- `brew_started` — ingredients have been committed to the cauldron for a brew and spent from the cabinet.
- `potion_ready` — a brewed potion has finished and is on a shelf.
- `price_set` — the player has set or changed the price on a potion that is on a shelf.
- `sale_closed` — a customer has bought a potion and paid for it.
- `sale_lost` — a customer has left without buying, because nothing on the shelf matched their ailment or the price was past their budget.
- `restock_bought` — ingredients have been bought from the supplier and paid for.
- `day_advanced` — a day has ended, its summary has been shown, and the next day has begun.

Flag names:

- `gold` — the shop’s current gold (a number).
- `stock` — how many ingredient units are in the cabinet right now (a number).
- `potions` — how many potions are on the shelves right now (a number).
- `sold` — how many potions have been sold to customers so far this session (a number).

## Demo traces (required)

Ship **1–10** files at `demo_outputs/*.json` (no root `traces.json`). Events: `mouse_click` / `mouse_down` / `mouse_up` / `mouse_move` / `key_press` / `key_down` / `key_up` / `wait`. Clicks must match **this** project’s 1280×720 layout.

You need **three separate traces**, each from **cold title**:

1. One full first cycle: brew from the starting stock, put the potion on a shelf, price it, and close a sale.
2. **Pricing / stock contrast**: a customer leaves unserved on one path where a customer is served on another (nothing matching on the shelf, or a price set past what they will pay).
3. Restock and turnover: buy ingredients from the supplier, then end the day and carry the shop into the next one.

Traces 1 and 2 may reuse the same opening as long as all three listed evidences exist as separate cold-title recordings.

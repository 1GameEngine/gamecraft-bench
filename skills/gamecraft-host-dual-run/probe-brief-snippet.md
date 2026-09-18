# Probe contract snippet (v2 USER brief, engine-neutral)

Paste verbatim into the v2 USER brief of **every** slug and **every** arm. Same bytes for all arms — it must not name an engine, a class, a file layout, or an API.

---

Your game must report its own state so the run can be checked automatically.

After each player input is fully handled, print exactly one line of JSON to standard output:

```
{"probe": 1, "beat": "<beat id>", "flags": {"<name>": <value>, ...}}
```

Rules:

- One line, valid JSON, nothing else on that line.
- `beat` is one of the beat ids listed in this brief. Print the beat the player just reached.
- `flags` carries the named state values listed in this brief. Use numbers for counts, strings for named states, and `null` when a state has not happened yet.
- Print a line after **every** handled input, including inputs that change nothing.
- Keep printing for the whole session; never buffer the lines until exit.
- Do not print anything else that begins with `{"probe"`.

This output is part of the deliverable. A build that plays correctly but prints no probe lines counts as incomplete.

---

The beat ids and flag names come from `host_probes/<slug>.json`; list them in the brief in plain prose (ids and meanings only, never the assertion thresholds).

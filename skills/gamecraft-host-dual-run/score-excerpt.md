# Parent-only score excerpt (do not attach to generators)

Score only these ids. Each value must be `0`, `0.5`, `1`, or `"Unscored"`. Do not score V* or A*. Do not apply “default Godot widgets” to either arm.

**M3.** Each examined keepsake records a persistent fragment into the player's gathered knowledge, and that collection is visible (a list, journal, or memory board) and grows as objects are examined. The game tracks what has and has not been found. Score 0 if examined objects are not recorded, if the gathered fragments are never shown, or if examining leaves no tracked state.

**M4.** The fragments gate later content: which interpretations, lines, or endings become available depends on which keepsakes the player examined. A later beat must demonstrably depend on an earlier discovery. Score 0 if fragments never affect anything beyond a list on screen, if all content is reachable regardless of what was examined, or if the experience is effectively linear. Stills cannot prove a lock: if both paths look complete, use 0.5 or Unscored, not 1.

**D2.** Fragments genuinely connect and recontextualize: at least one later fragment changes the meaning of an earlier one, and the order or combination the player examines materially affects the understanding they assemble. Score 0 if fragments are independent and never inform one another, or if there is only one fixed reading.

**D4.** The reconstructed life has narrative breadth: the keepsakes together sketch a real person across more than one episode or relationship, and interpretation choices pose genuinely different ways to read the dead person's actions. Score 0 if there is only a single short fragment with no breadth.

**D5.** The writing delivers an authored, emotionally resonant reconstruction with specific texture and voice. Score 0 if there is no actual narrative content or only lorem-style placeholder text.

Write only JSON:

```json
{
  "protocol": "cursor-subagent-png-excerpt",
  "not_harbor_vlm": true,
  "not_compare_diagnostic_columns": true,
  "arm": "<godot|1game>",
  "scores": { "M3": 0, "M4": 0, "D2": 0, "D4": 0, "D5": 0 },
  "rationales": { "M3": "", "M4": "", "D2": "", "D4": "", "D5": "" }
}
```

Replace numeric placeholders with `0 | 0.5 | 1 | "Unscored"`. Cite PNG filenames in rationales.

**Footer for the parent merge (required):** Not Harbor VLM; not `reward.txt`; not `compare` `diagnostic_columns`; not paper / not an engine ranking; V/A unpublished; Godot x11grab frames vs 1Game timeline last-shots are not the same medium; M4 stills cannot prove a lock; Unscored ≠ 0; sequential Tasks; n=1 `visualnovel-keepsake`; Tasks may still see `/workspace`.

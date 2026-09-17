# Parent-only score excerpt (do not attach to generators)

Score only these ids. Each value must be `0`, `0.5`, `1`, or `"Unscored"`. Do not score V* or A*. Do not apply “default Godot widgets” to either arm.

**M3.** Each examined keepsake records a persistent fragment into the player's gathered knowledge, and that collection is visible (a list, journal, or memory board) and grows as objects are examined. The game tracks what has and has not been found. Score 0 if examined objects are not recorded, if the gathered fragments are never shown, or if examining leaves no tracked state. If stills are insufficient to judge the board, use `"Unscored"`, not 0.

**M4.** The fragments gate later content: which interpretations, lines, or endings become available depends on which keepsakes the player examined. A later beat must demonstrably depend on an earlier discovery. Score 0 if fragments never affect anything beyond a list on screen, if all content is reachable regardless of what was examined, or if the experience is effectively linear. Stills cannot prove a lock: if both paths look complete, use 0.5 or Unscored, not 1. **Appendix only** (not the parent face).

**D2.** Fragments genuinely connect and recontextualize: at least one later fragment changes the meaning of an earlier one, and the order or combination the player examines materially affects the understanding they assemble. Score 0 if fragments are independent and never inform one another, or if there is only one fixed reading. **Appendix only.**

**D4.** The reconstructed life has narrative breadth: the keepsakes together sketch a real person across more than one episode or relationship. On stills, score only whether multiple distinct episode texts are readable; do not treat “different readings / choices” as proven. Score 0 if there is only a single short fragment with no breadth. **Appendix only** until a still operational definition is promoted.

**D5.** The writing delivers an authored, emotionally resonant reconstruction with specific texture and voice. Score 0 if there is no actual narrative content or only lorem-style placeholder text. **Appendix only** (skill/envelope-dominated; not an engine cell).

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

**Footer for the parent merge (required):** Claim class `host_product_stack_diagnostic`. 1Game arm includes `@1game/skill`; do not attribute any parent cell to the engine. Not Harbor VLM; not `reward.txt`; not `compare` `diagnostic_columns`; not paper / not an engine ranking; V/A unpublished; Godot `x11_post_event` vs 1Game `1game_post_event_plus2` are not the same camera; M4 stills cannot prove a lock; Unscored ≠ 0 ≠ void ≠ fail; sequential Tasks; slug `visualnovel-keepsake`; Tasks may still see `/workspace`. Same USER bytes ≠ same total prompt.

**Parent merge (do not attach this block to scorers):** Keep child JSON unmodified in the local appendix. **Parent face allowlist:** M3 **split cards** (one card per arm, not one aligned numeric row). Do not print M4, D2, D4, D5, `protocol_cap`, stub, or compare columns on the parent face. If M4 is 1 from stills, appendix `protocol_cap` is `0.5` or `"Unscored"`, never 1. Unscored stays Unscored (not 0). Do not average Unscored. Either arm void ⇒ publish no parent pair for this class.

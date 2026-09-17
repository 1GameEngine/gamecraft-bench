# Host Dual Protocol packing (parent-enforced)

v1 registered slug: **`visualnovel-keepsake` only**. Other slugs: refuse spawn.

| Slot | Both arms | Differs |
| --- | --- | --- |
| **USER** | Exact bytes of `keepsake-main.md` (sha256 `f1f97886f18d6a0ef59a3c96a007a11824e657e1408e756e061932977654119a`) | Never. Hash before spawn. |
| **System** | — | `appendix-godot.md` **or** `keepsake-1game-brief.md` |
| **Not attached** | This file, `SKILL.md`, `score-excerpt.md`, `ledger.schema.json`, Harbor `instruction.md` / `rubric.json` / `reward.txt`, stub CLI, `host_excerpt_ledger/**`, `$HOME/gamecraft-host-runs/**`, excerpt/merge JSON, `prereg-roles.md` | — |

Do not concatenate MAIN+appendix into USER. Do not put “you are Godot/1Game” in USER.

Parent is the enforcement point: child Tasks may still `cat /workspace`. Do not attach scores, ledger files, or this packing table to generators.

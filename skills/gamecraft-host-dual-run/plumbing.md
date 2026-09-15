# Host dual-engine plumbing (not a ranking)

Compare (`python -m gamecraft_bench.verifier.compare`) writes a **blocker dump**.
`publishable` means the pair is internally consistent. It is not paper-ready and
not “the run succeeded”. CLI exit after a successful write is **0** even when
`publishable` is false. Do not cite diagnostic columns as engine quality.

Harbor `instruction.md` stays the Godot academic task. Generation MAIN is
`keepsake-main.md`. 1Game overlay is `keepsake-1game-brief.md`.

## Jobs roots

- Harbor: `$HOME/gamecraft-bench-jobs`
- Compare: sibling `$HOME/gamecraft-bench-jobs-compare/` (never nest under Harbor)

## Media and timing (noisy columns)

- Godot PLAY is x11grab; 1Game PLAY is a timeline **slideshow** (~0.5s last-shot
  concat), not equivalent capture.
- `mouse_click` / `key_press` cost **+2** 1Game logic frames vs Godot same-frame
  xdotool.
- Traces are **20s from title** (`duration_frames` ≤ 600 at 30 fps).
- Do not copy Godot `demo_outputs` coordinates onto a 1Game layout.
- Do not copy pixel-reader notes into `diagnostic_columns`.

## StubJudge

StubJudge is **smoke**. A Stub pair is a blocker, not a ranking.

## Engine pin

`--engine auto` is Harbor Godot. Exclusive `--engine 1game` is host-only.
`detect_engine(auto)` must not select 1Game.

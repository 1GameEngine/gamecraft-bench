# 1Game system envelope (not USER)

Follow the user brief. Host binaries `/usr/local/bin/1game` and `1gameplay` only — never `pnpm exec`.

```
<project>/
  src/game.tsx
  1game.config.ts
  package.json          ← @1game/engine-bundle
  demo_outputs/*.json
  assets/
```

Scene **1280×720**. Trace `x,y` match this scene. `mouse_click` / `key_press` each consume **two** logic frames; put slack at the **end** of traces.

Copy host libraries into `assets/` if the mounts exist (paths listed in the user brief).

The self-report lines from the user brief must reach the process stdout of the running game.

Do not wrap Xvfb or set `DISPLAY=`. Do not run the verifier. Leave PLAY/BUILD capture to the parent.

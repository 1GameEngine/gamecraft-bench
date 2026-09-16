# 1Game system envelope (not USER)

Follow MAIN. Follow `@1game/skill`. Host binaries `/usr/local/bin/1game` and `1gameplay` only — never `pnpm exec`.

```
<project>/
  src/game.tsx
  1game.config.ts
  package.json          ← @1game/engine-bundle
  demo_outputs/*.json
  assets/
```

Scene **1280×720**. Trace `x,y` match this scene. `mouse_click` / `key_press` each consume **two** logic frames; put slack at the **end** of traces.

Copy host libraries into `assets/` if the mounts exist (same paths as MAIN).

Do not wrap Xvfb or set `DISPLAY=`. Do not run the verifier. Leave PLAY/BUILD capture to the parent.

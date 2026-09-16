# Godot system envelope (not USER)

Parent injects the concrete project root under `$HOME/gamecraft-bench-jobs-compare/` (must contain `project.godot`). Host binary: `/usr/local/bin/godot`. Extra scenes are allowed.

Copy host libraries into this tree’s `assets/` if the mounts exist (same paths as MAIN). Hit targets in `demo_outputs/*.json` must match **this** layout.

Do not wrap Xvfb or set `DISPLAY=`. Do not run the verifier. Leave PLAY capture to the parent.

# Godot system envelope (not USER)

Parent injects the concrete project root under `$HOME/gamecraft-host-runs/` (must contain `project.godot`). Host binary: `/usr/local/bin/godot`. Extra scenes are allowed.

Copy host libraries into this tree’s `assets/` if the mounts exist (paths listed in the user brief). Hit targets in `demo_outputs/*.json` must match **this** layout.

The self-report lines from the user brief must reach the process stdout of the running game.

Do not wrap Xvfb or set `DISPLAY=`. Do not run the verifier. Leave PLAY capture to the parent.

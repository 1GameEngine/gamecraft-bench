#!/usr/bin/env bash
# Idempotent local / Cloud Agent bootstrap for GameCraft-Bench.
# Installs system libs, pinned Godot 4.6.2, the 1Game 1.21.0 toolchain
# (cli / 1gameplay / engine-bundle / skill), uv, the Python package, and a
# stub-judge .env if one is missing. Safe to run twice.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

GODOT_VERSION="4.6.2"
ONEGAME_VERSION="1.21.0"
ONEGAME_PREFIX="/opt/1game"
GODOT_ZIP="Godot_v${GODOT_VERSION}-stable_linux.x86_64.zip"
GODOT_URL="https://github.com/godotengine/godot/releases/download/${GODOT_VERSION}-stable/${GODOT_ZIP}"
GODOT_MIRROR="https://gh-proxy.com/${GODOT_URL}"

need_sudo() {
    if [ "$(id -u)" -eq 0 ]; then
        "$@"
    else
        sudo "$@"
    fi
}

export PATH="${HOME}/.local/bin:/usr/local/bin:${PATH}"

# Prefer nvm Node 22 over apt's nodejs 18 when present.
if [ -d "${HOME}/.nvm/versions/node" ]; then
    _node_dir="$(ls -d "${HOME}/.nvm/versions/node"/v22* 2>/dev/null | sort -V | tail -1 || true)"
    if [ -n "${_node_dir:-}" ]; then
        export PATH="${_node_dir}/bin:${PATH}"
    fi
fi

echo "==> system packages"
need_sudo apt-get update -qq
need_sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    xvfb xdotool ffmpeg x11-utils x11-xserver-utils \
    libxcursor1 libxinerama1 libxrandr2 libxi6 libgl1 libegl1 \
    unzip ca-certificates curl \
    x11vnc novnc \
    python3 make g++ pkg-config

echo "==> Godot ${GODOT_VERSION}"
if [ -x /opt/godot/godot ] && /opt/godot/godot --version 2>/dev/null | grep -q "${GODOT_VERSION}"; then
    echo "    already present: $(/opt/godot/godot --version)"
else
    tmp="$(mktemp -d)"
    if ! curl -fL --retry 3 -o "${tmp}/godot.zip" "$GODOT_URL"; then
        echo "    GitHub download failed; trying gh-proxy mirror"
        curl -fL --retry 3 -o "${tmp}/godot.zip" "$GODOT_MIRROR"
    fi
    unzip -o -q "${tmp}/godot.zip" -d "$tmp"
    need_sudo mkdir -p /opt/godot
    need_sudo mv -f "${tmp}/Godot_v${GODOT_VERSION}-stable_linux.x86_64" /opt/godot/godot
    need_sudo chmod +x /opt/godot/godot
    rm -rf "$tmp"
fi
need_sudo ln -sf /opt/godot/godot /usr/local/bin/godot
godot --version

echo "==> uv"
if ! command -v uv >/dev/null 2>&1; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
    # shellcheck disable=SC1091
    source "${HOME}/.local/bin/env"
fi

echo "==> Python venv + gamecraft-bench"
# Cloud Agent checkouts live at /workspace, which LocalSubprocessEnvironment
# overlays with the trial sandbox. Keep the venv *outside* that path and
# install the package non-editable so imports work inside the namespace.
if [ "$REPO_ROOT" = "/workspace" ]; then
    VENV_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/gamecraft-bench/venv"
    mkdir -p "$(dirname "$VENV_DIR")"
    if [ -d .venv ] && [ ! -L .venv ]; then
        if [ ! -d "$VENV_DIR" ]; then
            mv .venv "$VENV_DIR"
        else
            rm -rf .venv
        fi
    fi
    if [ ! -d "$VENV_DIR" ]; then
        uv venv --python 3.12 "$VENV_DIR"
    fi
    ln -sfn "$VENV_DIR" .venv
elif [ ! -d .venv ]; then
    uv venv --python 3.12 .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
if [ "$REPO_ROOT" = "/workspace" ]; then
    uv pip install .
else
    uv pip install -e .
fi

echo "==> .env"
if [ ! -f .env ]; then
    cp .env.example .env
    # Harbor smoke works without a paid judge; fill keys later for real scoring.
    sed -i 's/^GAMECRAFT_BENCH_JUDGE=.*/GAMECRAFT_BENCH_JUDGE=stub/' .env
    sed -i "s|^GAMECRAFT_BENCH_PYTEST_BIN=.*|GAMECRAFT_BENCH_PYTEST_BIN=${REPO_ROOT}/.venv/bin/pytest|" .env
    echo "    wrote .env with GAMECRAFT_BENCH_JUDGE=stub"
else
    echo "    left existing .env untouched"
fi
if ! grep -q '^GAMECRAFT_BENCH_JOBS_ROOT=' .env; then
    if mkdir -p "$REPO_ROOT/../gamecraft-bench-jobs" 2>/dev/null; then
        echo "GAMECRAFT_BENCH_JOBS_ROOT=$REPO_ROOT/../gamecraft-bench-jobs" >> .env
    else
        echo "GAMECRAFT_BENCH_JOBS_ROOT=${HOME}/gamecraft-bench-jobs" >> .env
    fi
    echo "    set GAMECRAFT_BENCH_JOBS_ROOT"
fi

echo "==> container mountpoints"
# LocalSubprocessEnvironment bind-mounts sandbox dirs onto these host
# paths inside a user namespace. User-ns "root" cannot create them on
# the real rootfs, so they must exist and be writable by this user.
for d in /logs /tests /solution /installed_agent /tools; do
    if [ ! -d "$d" ]; then
        need_sudo mkdir -p "$d"
    fi
    need_sudo chown "$(id -u):$(id -g)" "$d"
done

echo "==> 1Game ${ONEGAME_VERSION}"
node_major="$(node -p "process.versions.node.split('.')[0]" 2>/dev/null || echo 0)"
if [ "$node_major" -lt 20 ]; then
    echo "    Node 20+ required for 1Game (got $(node -v 2>/dev/null || echo none))" >&2
    exit 1
fi
echo "    node $(node -v) npm $(npm -v)"
need_sudo mkdir -p "$ONEGAME_PREFIX"
need_sudo chown "$(id -u):$(id -g)" "$ONEGAME_PREFIX"
cli_pkg="${ONEGAME_PREFIX}/node_modules/@1game/cli/package.json"
if [ -f "$cli_pkg" ] && grep -q "\"version\": \"${ONEGAME_VERSION}\"" "$cli_pkg"; then
    echo "    already present: ${ONEGAME_VERSION}"
else
    cat > "${ONEGAME_PREFIX}/package.json" <<EOF
{
  "name": "gamecraft-1game-toolchain",
  "private": true,
  "dependencies": {
    "@1game/cli": "${ONEGAME_VERSION}",
    "@1game/cli-1gameplay": "${ONEGAME_VERSION}",
    "@1game/engine-bundle": "${ONEGAME_VERSION}",
    "@1game/skill": "${ONEGAME_VERSION}"
  }
}
EOF
    (cd "$ONEGAME_PREFIX" && npm install --omit=dev)
fi
need_sudo ln -sf "${ONEGAME_PREFIX}/node_modules/.bin/1game" /usr/local/bin/1game
need_sudo ln -sf "${ONEGAME_PREFIX}/node_modules/.bin/1gameplay" /usr/local/bin/1gameplay
# pnpm 10 ignores better-sqlite3 / esbuild scripts until approved. The
# /opt/1game npm install already compiled them; `pnpm exec 1gameplay` in a
# freshly inited game still needs this once:
need_sudo tee /usr/local/bin/1game-pnpm-natives >/dev/null <<'EOS'
#!/usr/bin/env bash
set -euo pipefail
pnpm approve-builds --all
pnpm rebuild
EOS
need_sudo chmod +x /usr/local/bin/1game-pnpm-natives
1game --help >/dev/null
1gameplay --help >/dev/null
echo "    1game $(node -p "require('${ONEGAME_PREFIX}/node_modules/@1game/cli/package.json').version")"
echo "    1gameplay $(node -p "require('${ONEGAME_PREFIX}/node_modules/@1game/cli-1gameplay/package.json').version")"
echo "    engine-bundle $(node -p "require('${ONEGAME_PREFIX}/node_modules/@1game/engine-bundle/package.json').version")"

echo "==> smoke"
command -v harbor
harbor --help >/dev/null
python -c "import gamecraft_bench; print('gamecraft_bench ok')"
unshare --user --map-root-user --mount true
command -v 1game
command -v 1gameplay
echo "setup_local.sh complete"

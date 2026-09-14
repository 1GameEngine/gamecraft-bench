#!/usr/bin/env bash
# Idempotent local / Cloud Agent bootstrap for GameCraft-Bench.
# Installs system libs, pinned Godot 4.6.2, uv, the Python package, and a
# stub-judge .env if one is missing. Safe to run twice.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

GODOT_VERSION="4.6.2"
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

echo "==> system packages"
need_sudo apt-get update -qq
need_sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    xvfb xdotool ffmpeg x11-utils x11-xserver-utils \
    libxcursor1 libxinerama1 libxrandr2 libxi6 libgl1 libegl1 \
    unzip ca-certificates curl \
    x11vnc novnc

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
if [ ! -d .venv ]; then
    uv venv --python 3.12 .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
uv pip install -e .

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
        echo "GAMECRAFT_BENCH_JOBS_ROOT=$REPO_ROOT/gamecraft-bench-jobs" >> .env
    fi
    echo "    set GAMECRAFT_BENCH_JOBS_ROOT"
fi

echo "==> smoke"
command -v harbor
harbor --help >/dev/null
python -c "import gamecraft_bench; print('gamecraft_bench ok')"
unshare --user --map-root-user --mount true
echo "setup_local.sh complete"

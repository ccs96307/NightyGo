#!/usr/bin/env bash
# Rebuild the static browser KataGo engine shipped with NightyGo.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
KATAGO_REF="d5ad1c0423dba989c60a2f06b1848e7eec2b5941"
SOURCE_DIR="${KATAGO_WEBGPU_DIR:-${TMPDIR:-/tmp}/nightygo-katago-webgpu}"
SDK="${EMSDK_DIR:-${EMSDK:-}}"
if [[ -z "$SDK" || ! -f "$SDK/emsdk_env.sh" ]]; then
  echo 'Set EMSDK_DIR (or EMSDK) to an installed Emscripten SDK.' >&2; exit 2
fi
if [[ ! -f "$SOURCE_DIR/scripts/build-eval.sh" ]]; then
  git clone --filter=blob:none https://github.com/saigo-online/katago-webgpu.git "$SOURCE_DIR"
fi
git -C "$SOURCE_DIR" checkout --detach "$KATAGO_REF"
if [[ ! -f /usr/include/eigen3/Eigen/Dense ]]; then
  echo 'Install Eigen 3 headers (for example: apt install libeigen3-dev).' >&2; exit 2
fi
# Emscripten 7 requires em++ for the Dawn/WebGPU final link. Upstream currently
# uses emcc; patch only this disposable checkout and keep the pinned source intact.
sed -i 's/^emcc "${OBJS\[@\]}"/em++ "${OBJS[@]}"/' "$SOURCE_DIR/scripts/build-eval.sh"
EMSDK_DIR="$SDK" B5_NET= B20_NET= B18_NET= bash "$SOURCE_DIR/scripts/build-eval.sh"
mkdir -p "$ROOT/web/assets/engine"
cp "$SOURCE_DIR/web/demo/kataeval.js" "$SOURCE_DIR/web/demo/kataeval.wasm" "$ROOT/web/assets/engine/"
cp "$SOURCE_DIR/LICENSE" "$ROOT/web/assets/engine/UPSTREAM-LICENSE"
echo "Built NightyGo web engine from saigo-online/katago-webgpu@$KATAGO_REF"

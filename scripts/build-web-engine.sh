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
# Both the live page and checked-in engine use this fix for the direct eval ABI.
PATCH="$ROOT/scripts/katago-browser-eval.patch"
if ! git -C "$SOURCE_DIR" apply --reverse --check "$PATCH" 2>/dev/null; then
  git -C "$SOURCE_DIR" apply --check "$PATCH"
  git -C "$SOURCE_DIR" apply "$PATCH"
fi
if [[ ! -f /usr/include/eigen3/Eigen/Dense ]]; then
  echo 'Install Eigen 3 headers (for example: apt install libeigen3-dev).' >&2; exit 2
fi
# Emscripten 7 requires em++ for the Dawn/WebGPU final link. Upstream currently
# uses emcc; patch only this disposable checkout and keep the pinned source intact.
sed -i 's/^emcc "${OBJS\[@\]}"/em++ "${OBJS[@]}"/' "$SOURCE_DIR/scripts/build-eval.sh"
# A failed compilation must not be mistaken for a successful build from old output.
rm -f "$SOURCE_DIR/web/demo/kataeval.js" "$SOURCE_DIR/web/demo/kataeval.wasm"
set +e
EMSDK_DIR="$SDK" B5_NET= B20_NET= B18_NET= bash "$SOURCE_DIR/scripts/build-eval.sh"
build_status=$?
set -e
if [[ "$build_status" -ne 0 && ( ! -s "$SOURCE_DIR/web/demo/kataeval.js" || ! -s "$SOURCE_DIR/web/demo/kataeval.wasm" ) ]]; then
  echo "KataGo engine build failed with status $build_status and did not produce both output files." >&2
  exit "$build_status"
fi
if [[ "$build_status" -ne 0 ]]; then
  echo "KataGo engine outputs are present; upstream ended with status $build_status after optional demo model bundling." >&2
fi
mkdir -p "$ROOT/web/assets/engine"
cp "$SOURCE_DIR/web/demo/kataeval.js" "$SOURCE_DIR/web/demo/kataeval.wasm" "$ROOT/web/assets/engine/"
cp "$SOURCE_DIR/LICENSE" "$ROOT/web/assets/engine/UPSTREAM-LICENSE"
echo "Built NightyGo web engine from saigo-online/katago-webgpu@$KATAGO_REF"

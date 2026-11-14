#!/usr/bin/env bash
set -euo pipefail

# This script must run from the checked-out Aseprite source root.
if [[ ! -f CMakeLists.txt || ! -f .gitmodules || ! -f EULA.txt ]]; then
  echo "Run this script from the root of the Aseprite source checkout." >&2
  exit 1
fi

for tool in cmake ninja curl unzip; do
  command -v "$tool" >/dev/null 2>&1 || {
    echo "Required tool not found: $tool" >&2
    exit 1
  }
done

echo "Resolving the Skia package required by this Aseprite source revision..."
skia_url="$(bash laf/misc/skia-url.sh Release | xargs)"

if [[ -z "$skia_url" ]]; then
  echo "Could not determine the Skia download URL." >&2
  exit 1
fi

deps_dir="${RUNNER_TEMP:-${TMPDIR:-/tmp}}/aseprite-deps"
skia_dir="$deps_dir/skia"
mkdir -p "$skia_dir"

skia_archive="$skia_dir/$(basename "$skia_url")"
if [[ ! -f "$skia_archive" ]]; then
  curl --fail --location --retry 3 --retry-delay 2 \
    --ssl-revoke-best-effort \
    --output "$skia_archive" "$skia_url"
fi

if [[ ! -d "$skia_dir/out/Release-x64" ]]; then
  unzip -o "$skia_archive" -d "$skia_dir"
fi

if [[ ! -d "$skia_dir/out/Release-x64" ]]; then
  echo "Skia archive did not contain out/Release-x64." >&2
  echo "Downloaded archive: $skia_archive" >&2
  exit 1
fi

skia_dir_abs="$(cd "$skia_dir" && pwd -P)"
skia_lib_dir_abs="$(cd "$skia_dir/out/Release-x64" && pwd -P)"

echo "Configuring Aseprite with CMake/Ninja..."
cmake -S . -B build -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DLAF_BACKEND=skia \
  -DSKIA_DIR="$skia_dir_abs" \
  -DSKIA_LIBRARY_DIR="$skia_lib_dir_abs" \
  -DENABLE_TESTS=OFF \
  -DENABLE_CCACHE=OFF

echo "Building Aseprite..."
cmake --build build --target aseprite --parallel

if [[ ! -f build/bin/aseprite.exe ]]; then
  echo "Build completed but build/bin/aseprite.exe was not found." >&2
  exit 1
fi

mkdir -p dist
echo "Aseprite executable built at: build/bin/aseprite.exe"
echo "The workflow will package the complete build/bin directory."

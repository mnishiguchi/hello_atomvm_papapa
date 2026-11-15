#!/usr/bin/env bash
set -euo pipefail

repo_dir=$(cd "$(dirname "$0")/.." && pwd)
atomvm_root=${ATOMVM_REPO_PATH:-"$repo_dir/../AtomVM"}
esp32_dir="$atomvm_root/src/platforms/esp32"
target="$esp32_dir/components/hello_atomvm_papapa"

if [ ! -d "$esp32_dir" ]; then
  echo "AtomVM ESP32 platform not found: $esp32_dir" >&2
  echo "Set ATOMVM_REPO_PATH to your AtomVM checkout." >&2
  exit 1
fi
if [ -e "$target" ] && [ ! -L "$target" ]; then
  echo "Component path exists and is not a symlink: $target" >&2
  exit 1
fi
if [ -L "$target" ]; then
  if [ "$(readlink -f "$target")" != "$repo_dir" ]; then
    echo "Existing symlink points elsewhere: $target" >&2
    exit 1
  fi
else
  ln -s "$repo_dir" "$target"
fi
printf 'Native component: %s -> %s\n' "$target" "$repo_dir"
echo "Next: follow docs/getting-started.md to build with the papapa defaults and Elixir boot library."

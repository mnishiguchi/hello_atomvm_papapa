#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/firmware-env.sh"

case "${1:-}" in
    build) [ "$#" -eq 1 ] || exit 2 ;;
    flash) [ "$#" -eq 2 ] && [ -n "$2" ] || exit 2 ;;
    *) echo "使い方: $0 build | flash PORT" >&2; exit 2 ;;
esac

cd "$papapa_repo_dir"
papapa_atomvm_paths
boot_avm="$atomvm_root/build/libs/esp32boot/elixir_esp32boot.avm"

if [ "$1" = build ]; then
    jobs=${PAPAPA_JOBS:-4}
    [[ "$jobs" =~ ^[1-9][0-9]*$ ]] || { echo "PAPAPA_JOBS は正の整数で指定してください。" >&2; exit 2; }
    mise exec -- cmake -S "$atomvm_root" -B "$atomvm_root/build"
    mise exec -- cmake --build "$atomvm_root/build" --target elixir_esp32boot -j "$jobs"
    ATOMVM_REPO_PATH="$atomvm_root" bash scripts/setup-native.sh
else
    if [ ! -f "$build_dir/atomvm-esp32.bin" ] || [ ! -f "$boot_avm" ] ||
       [ ! -f "$build_dir/papapa-source-path" ] ||
       [ "$(cat "$build_dir/papapa-source-path")" != "$papapa_repo_dir" ]; then
        echo "この checkout のファームウェアが未ビルドです。just build-firmware を先に実行してください。" >&2
        exit 1
    fi
fi

if [ ! -f "$boot_avm" ]; then
    echo "Elixir 用 boot.avm が生成されていません: $boot_avm" >&2
    exit 1
fi

papapa_load_idf
cd "$esp32_dir"
idf_args=(-B "$build_dir" -D IDF_TARGET=esp32c5 -D ATOMVM_ELIXIR_SUPPORT=ON
    -D "SDKCONFIG=$esp32_dir/sdkconfig.papapa"
    -D "SDKCONFIG_DEFAULTS=$esp32_dir/sdkconfig.defaults;$papapa_repo_dir/config/sdkconfig.papapa.defaults")

if [ "$1" = build ]; then
    idf.py "${idf_args[@]}" build
    printf '%s\n' "$papapa_repo_dir" > "$build_dir/papapa-source-path"
else
    idf.py "${idf_args[@]}" -p "$2" flash
fi

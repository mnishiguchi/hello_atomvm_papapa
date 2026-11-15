#!/usr/bin/env bash
# firmware.sh と flash-app.sh で共有する設定。source して使用する。

papapa_repo_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)

papapa_load_idf() {
    local idf_root=${ESP_IDF_PATH:-${IDF_PATH:-"$HOME/.espressif/v5.5/esp-idf"}}
    if [ ! -f "$idf_root/export.sh" ]; then
        echo "ESP-IDF が見つかりません: $idf_root/export.sh" >&2
        echo "ESP_IDF_PATH に ESP-IDF のインストール先を指定してください。" >&2
        return 1
    fi
    export IDF_PATH
    IDF_PATH=$(cd "$idf_root" && pwd)
    # ESP-IDF の環境設定は、未定義の変数を参照することがある。
    set +u
    source "$IDF_PATH/export.sh"
    set -u
}

papapa_atomvm_paths() {
    local requested=${ATOMVM_REPO_PATH:-"$papapa_repo_dir/../AtomVM-papapa"}
    if [ ! -f "$requested/CMakeLists.txt" ] || [ ! -d "$requested/src/platforms/esp32" ]; then
        echo "AtomVM のソースが見つかりません: $requested" >&2
        echo "専用 checkout を用意し、ATOMVM_REPO_PATH を指定してください。" >&2
        return 1
    fi
    atomvm_root=$(cd "$requested" && pwd)
    esp32_dir="$atomvm_root/src/platforms/esp32"
    build_dir=${PAPAPA_BUILD_DIR:-"$esp32_dir/build-papapa"}
    if [[ "$build_dir" != /* ]]; then
        build_dir="$esp32_dir/$build_dir"
    fi
}

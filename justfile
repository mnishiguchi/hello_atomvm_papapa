set shell := ["bash", "-euo", "pipefail", "-c"]
set positional-arguments

# 利用できる操作を表示
@default:
    just --list

# ホストテストと整形確認（実機不要）
check:
    mise exec -- make check

# PC で試聴する WAV を生成
preview:
    mise exec -- make preview

# Elixir boot と音声 NIF を含むファームウェアをビルド
build-firmware:
    bash scripts/firmware.sh build

# ビルド済みファームウェアと Elixir boot を書き込み
flash-firmware port:
    bash scripts/firmware.sh flash "$1"

# 曲を選び、prod で clean してアプリを書き込み
flash-app port track="smoke":
    bash scripts/flash-app.sh "$1" "$2"

# シリアルログを表示（Ctrl-T、q で終了）
monitor port:
    tio -b 115200 -- "$1"

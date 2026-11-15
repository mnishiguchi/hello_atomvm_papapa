#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/firmware-env.sh"

if [ "$#" -ne 2 ] || [ -z "$1" ]; then
    echo "使い方: $0 PORT TRACK" >&2
    exit 2
fi
port=$1
track=$2
repeat=${PAPAPA_REPEAT:-false}
case "$repeat" in
    true|false) ;;
    *) echo "PAPAPA_REPEAT は true または false で指定してください。" >&2; exit 2 ;;
esac

cd "$papapa_repo_dir"
# 不明なトラックなら、clean やデバイスへの接続前に止める。
mise exec -- elixir -r lib/hello_atomvm_papapa/catalog.ex -e '
  unless Enum.member?(HelloAtomvmPapapa.Catalog.names(), hd(System.argv())) do
    IO.puts(:stderr, "不明なトラックです。Catalog.names/0 を確認してください。")
    System.halt(2)
  end
' -- "$track"

# BEAM ツールの場所を先に確定し、ESP-IDF の Python 環境を優先する。
# IDF 設定後に mise exec を重ねると、別の Python が PATH の先頭に戻る。
elixir_bin="$(mise where elixir)/bin"
erlang_bin="$(mise where erlang)/bin"
export PATH="$elixir_bin:$erlang_bin:$PATH"
papapa_load_idf
export MIX_ENV=prod
export PAPAPA_TRACK="$track"
export PAPAPA_REPEAT="$repeat"
mix deps.get
mix clean
exec mix atomvm.esp32.flash --port "$port"

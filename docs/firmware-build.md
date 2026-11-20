# カスタムファームウェアの準備

`just build-firmware` は、Elixir 用の起動ライブラリ、音声 NIF を含む ESP32-C5 ファームウェアを順にビルドします。アプリの書き込みとは別の操作です。

## 1. ツールを用意する

- `.tool-versions` の Erlang/OTP、Elixir、just：`mise install`
- AtomVM のホストビルド：C コンパイラ、CMake、make、gperf、zlib、Mbed TLS、rebar3
- [ESP-IDF 5.5 と ESP32-C5 用ツールチェーン](https://docs.espressif.com/projects/esp-idf/en/v5.5/esp32c5/get-started/index.html)
- シリアルモニター：`tio`

ホスト側の依存関係は [AtomVM のビルド手順](https://doc.atomvm.org/main/build-instructions.html#building-for-generic-unix) を参照してください。`just` は [コマンドの実行ツール](https://just.systems/man/en/) で、既存の `Makefile` も引き続き使えます。

## 2. 専用 AtomVM checkout を用意する

このリポジトリのルートで実行します。ほかの実験用 checkout と設定が混ざらないように分けます。

```sh
export ATOMVM_REPO_PATH="$PWD/../AtomVM-papapa"
git clone https://github.com/atomvm/AtomVM.git "$ATOMVM_REPO_PATH"
git -C "$ATOMVM_REPO_PATH" checkout 18b35870a0be75c42892db9a0762e8c7a7d61323
```

すでに専用 checkout がある場合は clone を省略し、その場所を指定してください。上のコミットは [実機確認済みの版](hardware-validation.md#確認した環境) です。

## 3. ESP-IDF の場所を指定する

```sh
export ESP_IDF_PATH="$HOME/.espressif/v5.5/esp-idf"
```

実際のインストール先に合わせてください。`export.sh` はスクリプト内で読み込みます。別のターミナルでは環境変数を設定し直します。

| 設定 | 既定値・役割 |
| --- | --- |
| `ATOMVM_REPO_PATH` | このリポジトリの隣の `AtomVM-papapa` |
| `ESP_IDF_PATH` | 指定があれば優先。未指定なら `IDF_PATH`、それもなければ `$HOME/.espressif/v5.5/esp-idf` |
| `IDF_PYTHON_ENV_PATH` | ESP-IDF が使う Python 仮想環境。通常は ESP-IDF が判定 |
| `PAPAPA_BUILD_DIR` | AtomVM の `src/platforms/esp32/build-papapa`。相対指定は同じ `esp32` ディレクトリ基準 |
| `PAPAPA_JOBS` | ホストの起動ライブラリの並列ビルド数。既定は `4` |

mise の Python と ESP-IDF インストール時の Python が異なる場合、ESP-IDF の仮想環境が見つからないことがあります。その場合は、インストール済みの環境を明示します。

```sh
# 例。自分の ESP-IDF に対応する実在のディレクトリを指定する
export IDF_PYTHON_ENV_PATH="$HOME/.espressif/python_env/idf5.5_py3.13_env"
```

この設定は `build-firmware`、`flash-firmware`、`flash-app` で共通です。アプリ書き込み時も、ESP-IDF の Python を優先したまま Mix を実行します。

## 4. ビルド・書き込み

```sh
just build-firmware
just flash-firmware /dev/ttyACM0
just flash-app /dev/ttyACM0 smoke
```

ビルド後はこのリポジトリのソースパスをビルド先に記録します。`flash-firmware` はその記録と生成物を確認し、別の checkout のバイナリを使わないようにしています。初回は必ず `build-firmware` を先に実行してください。

`flash-firmware` は IDF の `flash` を使い、bootloader、partition table、カスタム AtomVM、Elixir 用 `boot.avm` を書き込みます。アプリの `.avm` は `flash-app` で別に書き込みます。`erase-flash` や `set-target` による消去・設定初期化は行いません。

C や PCM を変えたらファームウェアとアプリを両方更新します。Elixir コードや曲の選択だけなら `flash-app` で更新できます。

## 提供音源で2台のデュエットを再生する

使用した音源は `assets/audio/` にあります。

| 音源 | ファイル | 形式 | サンプルレート | ビット深度 | チャンネル |
| --- | --- | --- | --- | --- | --- |
| 生成した練習用フレーズ | `demo_papageno.pcm`、`demo_papagena.pcm`、`demo_duet.pcm` | Raw PCM | 8 kHz | unsigned 8-bit | mono |
| Papageno（男声） | `song_male.pcm` | Raw PCM | 16 kHz | unsigned 8-bit | mono |
| Papagena（女声） | `song_female.pcm` | Raw PCM | 16 kHz | unsigned 8-bit | mono |
| 参考用の二重唱 | `papapa_duet.wav` | WAV | 48 kHz | signed 16-bit | stereo |

個別の歌声は提供された `rmenu_papapa_audio_tracks.zip`、参考用の二重唱は提供された `papa-link-source-audio.tar.gz` 由来です。練習用フレーズは `scripts/build_assets.py` で生成できます。

2台構成では、男声と女声を役ごとに標準の `factory` 領域へ収めます。FFmpeg で Raw PCM に WAV ヘッダを付けてから取り込みます。取り込み時は 16 kHz と曲中の休止を保ち、振幅には既存の WAV 取り込みゲイン（0.22）を適用します。

`/dev/serial/by-id/` で2台の USB 識別番号を確認し、それぞれのパスを `papageno_port` と `papagena_port` に設定します。専用の作業コピーで、リポジトリのルートから次の順に実行します。

```sh
set -eu
audio_tmp=$(mktemp -d)
ffmpeg -f u8 -ar 16000 -ac 1 -i assets/audio/song_male.pcm -c:a pcm_u8 "$audio_tmp/papageno.wav"
ffmpeg -f u8 -ar 16000 -ac 1 -i assets/audio/song_female.pcm -c:a pcm_u8 "$audio_tmp/papagena.wav"

python3 scripts/build_assets.py --rate 16000 --no-demo --papageno-wav "$audio_tmp/papageno.wav"
just build-firmware
just flash-firmware "$papageno_port"
PAPAPA_REPEAT=false just flash-app "$papageno_port" papageno

python3 scripts/build_assets.py --rate 16000 --no-demo --papagena-wav "$audio_tmp/papagena.wav"
just build-firmware
just flash-firmware "$papagena_port"
PAPAPA_REPEAT=false just flash-app "$papagena_port" papagena
```

各基板は電源投入時に担当パートを1回再生します。2台を同時に通電すると、元の音源の時間軸で歌い始めます。最初の発声まで、Papageno は約12秒、Papagena は約14秒の休止があります。

## スクリプトが行う処理

実行の入口は [justfile](../justfile)、処理の本体は [firmware.sh](../scripts/firmware.sh) と [flash-app.sh](../scripts/flash-app.sh) です。ファームウェアのビルドは次の順で行います。

1. AtomVM のホストビルドで `elixir_esp32boot` ターゲットを生成する。
2. [setup-native.sh](../scripts/setup-native.sh) で、このリポジトリを ESP-IDF コンポーネントへリンクする。
3. ESP-IDF の環境を読み込み、次の設定でビルドする。

手動で処理を追う場合の IDF コマンドです。`PAPAPA_REPO_PATH` はこのリポジトリの絶対パスに置き換えます。

```sh
export PAPAPA_REPO_PATH=/path/to/hello_atomvm_papapa
source "$ESP_IDF_PATH/export.sh"
cd "$ATOMVM_REPO_PATH/src/platforms/esp32"
idf.py -B build-papapa \
  -D IDF_TARGET=esp32c5 \
  -D ATOMVM_ELIXIR_SUPPORT=ON \
  -D "SDKCONFIG=$PWD/sdkconfig.papapa" \
  -D "SDKCONFIG_DEFAULTS=$PWD/sdkconfig.defaults;$PAPAPA_REPO_PATH/config/sdkconfig.papapa.defaults" \
  build
```

`ATOMVM_ELIXIR_SUPPORT=ON` で Elixir 用 partition と起動ライブラリを選びます。`config/sdkconfig.papapa.defaults` はサイズ優先の最適化と不要なネットワーク API の無効化です。PCM を含むファームウェアが `factory` 領域へ収まるか、ビルド末尾の容量チェックで確認します。

Elixir 用 boot は `AtomVM-papapa/build/libs/esp32boot/elixir_esp32boot.avm` に生成されます。見つからない場合は、ホストビルド時に CMake が `elixirc` を検出しているか確認してください。Flash の書き込み位置は、その checkout の partition table に従います。

# 最初の音を出す

ゴールは **起動すると短い音が鳴り、RESET で同じ音を再生できること**です。PC での試聴から始め、カスタム AtomVM、Elixir アプリの順に書き込みます。

以下は Linux の例です。macOS ではシリアルポート名などを読み替えてください。[配線と部品](wiring.md) の確認は、USB を外した状態で済ませておきます。

## 1. PC で音源を試聴する

このリポジトリのルートで実行します。必要なのは Python 3.10 以降、C コンパイラ、make、Erlang / Elixir です。`.tool-versions` では Erlang/OTP を `28`、Elixir を `1.19.6-otp-28` に指定します。Elixir は OTP 28 向けのビルドを明示し、Erlang のパッチ版は固定しません。CI も OTP 28 と Elixir 1.19.6 を使います。ここでは mise を使います。

```sh
mise install
mise exec -- make check
mise exec -- make preview
```

`make check` は音源テスト、生成 C のホストコンパイル、Elixir のコンパイルとテスト、整形を確認します。Mix の依存取得や XIAO は不要です。

`preview/smoke.wav` と `preview/demo_papageno.wav` を PC の音楽プレーヤーで開いてください。後で実機と聴き比べる基準になります。

## 2. 書き込むものを理解する

| 書き込むもの | 内容 | 更新するタイミング |
| --- | --- | --- |
| カスタム AtomVM ファームウェア | VM 本体、C の音声 NIF、PCM 音源 | 初回、C や音源の変更時 |
| Elixir 用 `boot.avm` | 起動処理と標準ライブラリ | 初回、対応する AtomVM の更新時 |
| このアプリの `.avm` | 曲の選択、開始・完了確認、繰り返し | 曲や Elixir コードの変更時 |

NIF は Elixir から呼び出す C の関数です。**標準の AtomVM を入れてアプリだけ書き込んでも、この音声 NIF は追加されません。** すでに本プロジェクトのカスタムファームウェアが入っている場合は [手順 4](#4-アプリを書き込み音を確認する) へ進めます。

## 3. カスタム AtomVM を準備する（初回）

### 開発環境

次の準備が必要です。

- ESP32-C5 向けの [ESP-IDF 5.5 とツールチェーン](https://docs.espressif.com/projects/esp-idf/en/v5.5/esp32c5/get-started/index.html)
- ESP32-C5 に対応する AtomVM のソース
- AtomVM のホストビルドに必要な CMake、make、gperf、zlib、Mbed TLS、Erlang / Elixir、rebar3
- 書き込み用の `esptool` と、ログを見るシリアル端末（以下は `tio`）

ツールのインストールは [AtomVM のビルド手順](https://doc.atomvm.org/main/build-instructions.html#building-for-generic-unix) を参照してください。実機確認に使ったコミットと版は [動作確認のまとめ](hardware-validation.md#確認した環境) にあります。

### Elixir 用の起動ライブラリを作る

このリポジトリのルートから開始します。AtomVM はほかの実験と設定が混ざらないよう、専用のチェックアウトを用意します。

```sh
export PAPAPA_REPO_PATH="$PWD"
export ATOMVM_REPO_PATH="$PWD/../AtomVM-papapa"

# 確認に使った AtomVM のコミット
# すでに専用のチェックアウトがある場合は clone を省略する
git clone https://github.com/atomvm/AtomVM.git "$ATOMVM_REPO_PATH"
git -C "$ATOMVM_REPO_PATH" checkout 18b35870a0be75c42892db9a0762e8c7a7d61323

mise exec -- cmake -S "$ATOMVM_REPO_PATH" -B "$ATOMVM_REPO_PATH/build"
mise exec -- cmake --build "$ATOMVM_REPO_PATH/build" --target elixir_esp32boot -j 4
ls "$ATOMVM_REPO_PATH/build/libs/esp32boot/elixir_esp32boot.avm"
```

最後のファイルが必要です。見つからない場合は、CMake が `elixirc` を見つけているか確認してください。

### 音声 NIF を追加してビルドする

```sh
cd "$PAPAPA_REPO_PATH"
bash scripts/setup-native.sh

# ESP-IDF をインストールした実際の場所に合わせる
source "$HOME/.espressif/v5.5/esp-idf/export.sh"
cd "$ATOMVM_REPO_PATH/src/platforms/esp32"
idf.py -B build-papapa \
  -D IDF_TARGET=esp32c5 \
  -D ATOMVM_ELIXIR_SUPPORT=ON \
  -D SDKCONFIG=sdkconfig.papapa \
  -D "SDKCONFIG_DEFAULTS=sdkconfig.defaults;$PAPAPA_REPO_PATH/config/sdkconfig.papapa.defaults" \
  build
```

`setup-native.sh` は、このリポジトリを AtomVM の ESP-IDF コンポーネントとしてリンクします。追加設定はサイズ優先の最適化と不要なネットワーク API の無効化です。これで PCM を含むファームウェアを標準の Elixir 用 partition（Flash 内の領域）へ収めます。

### XIAO に書き込む

[通電前の確認](wiring.md#3-通電前に確認する) を済ませて USB を接続し、音量は最小にします。

```sh
ls /dev/serial/by-id/
# /dev/ttyACM0 は、実際に接続した XIAO のポートへ置き換える
idf.py -B build-papapa -p /dev/ttyACM0 flash
```

ログに `elixir_esp32boot.avm` も書き込まれることを確認してください。書き込み位置は AtomVM の partition 設定から決まります。別の構成のオフセットを流用しません。

## 4. アプリを書き込み、音を確認する

このリポジトリのルートで実行します。新しいターミナルなら、前の手順のパス変数や ESP-IDF 環境も設定し直してください。

```sh
cd "$PAPAPA_REPO_PATH"
mise exec -- mix deps.get
MIX_ENV=prod mise exec -- mix clean
PAPAPA_TRACK=smoke MIX_ENV=prod mise exec -- mix atomvm.esp32.flash --port /dev/ttyACM0
```

音量を少しずつ上げ、短い発声が聴こえるか確認します。シリアル端末を開いてから **RESET** を押すと、起動ログと音を一緒に確認できます。

```sh
tio -b 115200 /dev/ttyACM0
```

表示例です。`<<"smoke">>` は文字列の表示で、Elixir の `"smoke"` と同じ内容です。

```text
{papapa,boot,<<"smoke">>,gpio7}
papapa_audio: GPIO7: PWM 156352 Hz, PCM 8000 Hz
papapa_audio: GPIO7 pad transitions in 2 ms: 608
{papapa,finished,<<"smoke">>,skipped_samples,0}
```

周波数や変化回数は実行環境で異なります。再生後は待機し、RESET で同じ音を再生します。**ログの完了と、実際に聴こえることを両方確認**してください。次の書き込み前にはシリアル端末を終了し、ポートを空けます。

## 5. 曲を変える

| トラック | 聴こえる内容 |
| --- | --- |
| `smoke` | 約 2 秒の短い発声 |
| `demo_papageno` | 約 10 秒の低音の練習フレーズ。既定値 |
| `demo_papagena` | 高音の練習フレーズ |
| `demo_duet` | 2 声を混合した練習フレーズ。スピーカーは 1 台 |
| `tone_440` | 無音の切り分け用。1 秒の音と 1 秒の休止を 3 回 |

`PAPAPA_TRACK` と `PAPAPA_REPEAT` は **ビルド時**に決まります。曲を変えるときは、同じ `MIX_ENV=prod` で clean してから書き込みます。

```sh
MIX_ENV=prod mise exec -- mix clean
PAPAPA_TRACK=demo_papageno MIX_ENV=prod mise exec -- mix atomvm.esp32.flash --port /dev/ttyACM0
```

繰り返したい場合は、書き込みコマンドに `PAPAPA_REPEAT=true` を加えます。初回は指定せず、1 回再生してから音量を確認します。音源データ自体を変更した場合は、アプリだけでなく手順 3 のファームウェアも再ビルド・書き込みしてください。

## うまくいかないとき

| 症状 | 最初に確認すること |
| --- | --- |
| USB ポートが見つからない | データ対応の USB ケーブル、接続先、ポートへのアクセス権 |
| `:native_component_missing` | このリポジトリの C NIF を含むカスタムファームウェアを入れたか |
| `{:native_init_failed, code}` | `audio_nif.c` の `nif_init`。`-4` / `-5` は PWM、`-6` 以降はタイマーや出力タスクの初期化 |
| `skipped_samples` が増える | C の出力が追いついていない。トラック名とログを記録する |
| 完了ログは出るが無音 | **XIAO の 3V3 → pin 6、GND → pin 7**、CD pin 1 → GND、音量つまみ、スピーカーの接続先 |
| 音が割れる・ノイズが出る | 音量を下げる。アンプ付近の電源コンデンサと GND 配線を確認する |

無音なら `tone_440` を選び、必要なら `PAPAPA_REPEAT=true` で繰り返して確認します。実機試験では、XIAO の電源配線を直すと診断音が聴こえ、続いて歌声も再生できました。

`pad transitions` は GPIO の入力バッファで読み戻した変化回数です。0 なら出力設定やピンの状態を確認します。値が出ていても、ジャンパー・アンプ・スピーカーまでの導通を保証するものではありません。

音が出たら [音声再生の仕組み](audio-design.md) へ進み、データと回路がどうつながっているか見てみましょう。

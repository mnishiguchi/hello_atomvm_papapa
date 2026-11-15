# 最初の音を出す

ゴールは **短い音が鳴り、RESET で同じ音を再生できること**です。以下は Linux の例です。最初に [配線と部品](wiring.md) を確認してください。

## 1. PC で試聴する

Python 3.10 以降、C コンパイラ、make が必要です。Erlang/OTP 28、Elixir `1.19.6-otp-28`、just 1 系は `.tool-versions` で指定しています。

```sh
mise install
just check
just preview
```

`just` が見つからない場合は mise をシェルで有効にするか、`mise exec -- just check` のように実行します。`just` または `just --list` で操作一覧を表示できます。

`preview/smoke.wav` と `preview/demo_papageno.wav` を PC のプレーヤーで開いてください。実機と聴き比べる基準になります。

## 2. 初回のファームウェアを準備する

このプロジェクトでは、次の 3 つを書き込みます。

| 書き込むもの | 内容 | 更新するタイミング |
| --- | --- | --- |
| カスタム AtomVM ファームウェア | VM 本体、C の音声 NIF、PCM 音源 | 初回、C や音源の変更時 |
| Elixir 用 `boot.avm` | 起動処理と標準ライブラリ | 初回、対応する AtomVM の更新時 |
| アプリの `.avm` | 曲の選択、開始・完了確認、繰り返し | 曲や Elixir コードの変更時 |

**標準 AtomVM へのアプリ書き込みだけでは、音声 NIF は追加されません。** [ファームウェアの準備](firmware-build.md) に従い、専用の AtomVM checkout と ESP-IDF を用意します。初回の設定後は次のコマンドでビルドできます。

```sh
just build-firmware
```

すでにこのプロジェクトのカスタムファームウェアが入っている場合は、手順 3 のアプリ書き込みだけで進められます。

## 3. 書き込んで音を確認する

USB を外して [通電前の確認](wiring.md#3-通電前に確認する) を済ませ、音量を最小にしてから接続します。`/dev/ttyACM0` は実際の XIAO のポートへ置き換えてください。

```sh
ls /dev/serial/by-id/
just flash-firmware /dev/ttyACM0
just flash-app /dev/ttyACM0 smoke
just monitor /dev/ttyACM0
```

`flash-firmware` はファームウェアと Elixir boot を書き込みます。`flash-app` は依存取得、`MIX_ENV=prod` での clean、指定トラックのビルド・書き込みを行います。Flash 全消去は行いません。

音量を少しずつ上げ、短い発声を確認します。モニターを開いて **RESET** を押すと、音と起動ログを一緒に確認できます。

```text
{papapa,boot,<<"smoke">>,gpio7}
papapa_audio: GPIO7: PWM 156352 Hz, PCM 8000 Hz
papapa_audio: GPIO7 pad transitions in 2 ms: 608
{papapa,finished,<<"smoke">>,skipped_samples,0}
```

数値は環境で異なります。`<<"smoke">>` は文字列の表示です。再生後は待機し、RESET で同じ音を再生します。**完了ログと、実際に聴こえることを両方確認**してください。

モニターは **Ctrl-T、続けて q** で終了します。次の書き込み前に終了し、ポートを空けてください。

## 4. 曲を変える

```sh
just flash-app /dev/ttyACM0 demo_papageno
```

| トラック | 内容 |
| --- | --- |
| `smoke` | 約 2 秒の短い発声 |
| `demo_papageno` | 約 10 秒の低音の練習フレーズ。アプリの既定値 |
| `demo_papagena` | 高音の練習フレーズ |
| `demo_duet` | 2 声を混合した練習フレーズ。スピーカーは 1 台 |
| `tone_440` | 無音の切り分け用。1 秒の音と 1 秒の休止を 3 回 |

`just flash-app PORT` でトラックを省略した場合は、短い確認用の `smoke` を使います。`PAPAPA_TRACK` と `PAPAPA_REPEAT` はビルド時設定で、曲の変更時もレシピ内で prod の clean を挟みます。

繰り返したい場合は、音量を確認してから指定します。

```sh
PAPAPA_REPEAT=true just flash-app /dev/ttyACM0 demo_papageno
```

C NIF や PCM 音源を変更したときは、`just build-firmware` → `just flash-firmware PORT` → `just flash-app PORT TRACK` の順に実行してください。

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

# hello_atomvm_papapa

XIAO ESP32-C5 と [AtomVM](https://github.com/atomvm/AtomVM) で、スピーカーから「パパパ」と歌う Hello World です。1 台の基板とブレッドボードで、**音声データが音になるまで**を学びます。

起動すると約 10 秒の練習フレーズを 1 回歌い、その後は待機します。RESET で同じフレーズを再生します。音源はこの実験用に新しく合成したものです。

## 着想のきっかけ：友人のデモ

次の動画は、IoT に詳しい友人によるデモです。これを見て自分でもマイコンから音を出してみたいと思い、このリポジトリで AtomVM を使った「パパパ」と歌う小さな実験を始めました。

https://github.com/user-attachments/assets/4ede73e9-82b0-4ec1-a785-5fb46208fc44

## 動作デモ

次の動画は、このリポジトリの実験です。XIAO ESP32-C5 と AtomVM で、スピーカーから練習フレーズを再生しています。

https://github.com/user-attachments/assets/21771486-e17e-401e-a53b-dcae369f2555

[動作確認済みの構成](docs/hardware-validation.md)

## はじめる

必要なものは **XIAO ESP32-C5、NJM2113D アンプ、8 Ω スピーカー**と抵抗・コンデンサです。Elixir が曲を選び、C が一定間隔で PCM 音声データを PWM として出力し、回路でスピーカーを動かします。

1. [配線と部品](docs/wiring.md) — 部品をそろえ、電源・音声回路をつなぐ。
2. [最初の音を出す](docs/getting-started.md) — 音声 NIF を含むカスタム AtomVM とアプリを書き込む。
3. [音声再生の仕組み](docs/audio-design.md) — PCM、PWM、回路、コードの役割を学ぶ。

## PC だけで試聴する

実機を用意する前でも音源を生成できます。Python 3.10 以降、C コンパイラ、make と、`.tool-versions` の Erlang / Elixir / just を使います。

```sh
mise install
just check
just preview
```

`just` が見つからない場合は `mise exec -- just check` のように実行できます。既存の `make check` / `make preview` も使えます。

`preview/demo_papageno.wav` を PC の音楽プレーヤーで開いてください。

回路は [Piyopiyo PCB](https://github.com/piyopiyoex/piyopiyo-pcb) を参考にしています。PWM 音声回路の学習資料としても参照できます。曲の変更や無音時の確認は [ドキュメント一覧](docs/README.md) へ。

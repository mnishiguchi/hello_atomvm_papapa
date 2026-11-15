# ドキュメントの画像・動画

| ファイル | 内容・出典 |
| --- | --- |
| [breadboard.jpg](breadboard.jpg) | 提供された実機写真（元ファイル `DSC_1778~2.jpg`）。配置の参考に使用 |
| [parts.jpg](parts.jpg) | 提供された部品写真。外観の参考に使用 |
| [xiao-esp32c5-pinout.jpg](xiao-esp32c5-pinout.jpg) | 提供された Seeed Studio のピン配置図。[メーカーの説明](https://wiki.seeedstudio.com/xiao_esp32c5_getting_started/#pin-map) を参照 |
| [wiring.svg](wiring.svg) | 本プロジェクトの配線図。Piyopiyo PCB v1.9 の音声回路を参考に GPIO7 と追加電源バイパスを反映 |
| [pwm-duty.svg](pwm-duty.svg) | PWM のデューティ比を比べる図 |
| [rc-filter.svg](rc-filter.svg) | RC フィルタの平滑化を示す概念図 |
| [volume-wiper.svg](volume-wiper.svg) | 可変抵抗のワイパーと接続先の模式図 |
| [btl-speaker.svg](btl-speaker.svg) | BTL 出力とスピーカーの接続図 |
| `papapa-audio-test.mp4` | 約 11 秒の実機再生動画の原本。動画は [README](../../README.md#動作デモ) と [動作確認のまとめ](../hardware-validation.md) に埋め込み。音量・音質の測定用ではない |

写真・動画・ピン配置図は、提供された元の内容を保っています。

4 枚の学習用 SVG は、提供された `tmp/study-notes/` の図をもとにしています。明るい背景でも読める配色・表示サイズに整え、日本語の代替説明を付けました。RC フィルタ図は入力のデューティ比の変化を明示し、可変抵抗図はラベルの重なりを調整しています。

配線と部品値の説明は [配線ガイド](../wiring.md)、動作確認の条件は [動作確認のまとめ](../hardware-validation.md) を参照してください。

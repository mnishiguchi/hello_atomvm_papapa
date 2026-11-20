# ドキュメントの画像・動画

| ファイル                                           | 内容・出典                                                                                                                        |
| -------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| [breadboard0.jpg](breadboard0.jpg)                 | 音声回路を真上から撮影した実機写真                                                                                                |
| [breadboard1.jpg](breadboard1.jpg)                 | 初回検証の実機写真                                                                                                                |
| [breadboard2.jpg](breadboard2.jpg)                 | XIAO と音声回路の実機写真。[配線ガイド](../wiring.md) に掲載                                                                      |
| [parts.jpg](parts.jpg)                             | 提供された部品写真。外観の参考に使用                                                                                              |
| [xiao-esp32c5-pinout.jpg](xiao-esp32c5-pinout.jpg) | 提供された Seeed Studio のピン配置図。[メーカーの説明](https://wiki.seeedstudio.com/xiao_esp32c5_getting_started/#pin-map) を参照 |
| [wiring.svg](wiring.svg)                           | 本プロジェクトの配線図。Piyopiyo PCB v1.9 の音声回路を参考に GPIO7 と追加電源バイパスを反映                                       |
| [pwm-duty.svg](pwm-duty.svg)                       | PWM のデューティ比を比べる図                                                                                                      |
| [rc-filter.svg](rc-filter.svg)                     | RC フィルタの平滑化を示す概念図                                                                                                   |
| [volume-wiper.svg](volume-wiper.svg)               | 可変抵抗のワイパーと接続先の模式図                                                                                                |
| [btl-speaker.svg](btl-speaker.svg)                 | BTL 出力とスピーカーの接続図                                                                                                      |
| [papapa-audio-test0.mp4](papapa-audio-test0.mp4)   | 1台で練習フレーズを再生した動画（約11秒）                                                                                         |
| [papapa-audio-test1.mp4](papapa-audio-test1.mp4)   | 2台で Papageno と Papagena を再生した動画（約23秒）                                                                               |

写真・動画・ピン配置図は、提供された元の内容を保っています。

4 枚の学習用 SVG は、提供された `tmp/study-notes/` の図をもとにしています。明るい背景でも読める配色・表示サイズに整え、日本語の代替説明を付けました。RC フィルタ図は入力のデューティ比の変化を明示し、可変抵抗図はラベルの重なりを調整しています。

配線と部品値の説明は [配線ガイド](../wiring.md)、動作確認の条件は [動作確認のまとめ](../hardware-validation.md) を参照してください。

# MVP の動作確認

**2026-11-15、実機のスピーカーから「パパパ」が聴こえ、RESET 後も同じフレーズを再生できることを確認しました。** 既定の `demo_papageno` は約 10 秒の練習フレーズを 1 回歌い、その後は待機します。

[実機写真](assets/breadboard1.jpg) / [再現手順](getting-started.md)

https://github.com/user-attachments/assets/21771486-e17e-401e-a53b-dcae369f2555

## 確認した環境

| 項目 | 内容 |
| --- | --- |
| 基板・音声回路 | XIAO ESP32-C5 revision v1.0、D3/GPIO7、NJM2113D、UGSM23A 8 Ω / 0.08 W |
| AtomVM | [コミット `18b35870`](https://github.com/atomvm/AtomVM/commit/18b35870a0be75c42892db9a0762e8c7a7d61323)、起動表示 `0.7.0-beta.1` |
| ビルド設定 | ESP-IDF v5.5、Elixir 用 `boot.avm`、`config/sdkconfig.papapa.defaults` |
| ホスト | Linux、Erlang 28.5.0.7、Elixir 1.19.6-otp-28 |
| アプリ用ツール | exatomvm `14c293b`。依存の確定値は `mix.lock` |
| 音源・Flash | 8 kHz / unsigned 8-bit / mono。実機の 8 MiB Flash のうち、標準 Elixir 用の 4 MiB 構成を使用 |

## 確認結果

| 音源 | 実機の完了ログ | 試聴 |
| --- | --- | --- |
| `tone_440` | `skipped_samples=0` | 診断音を確認 |
| `demo_papageno` | `skipped_samples=0` | 歌声と RESET 後の再生を確認 |
| `demo_papagena` | `skipped_samples=0` | 高音フレーズが良好に聴こえることを確認 |
| `demo_duet` | `skipped_samples=0` | 混合した 2 声が良好に聴こえることを確認 |

各アプリの Flash 書き込みはハッシュ照合に成功。ホストの音源テスト 6 件、Elixir テスト 3 件、AVM のパッケージ生成も成功しました。

## 再現時に押さえる点

| 点 | 採用した対応 |
| --- | --- |
| ファームウェアの容量 | サイズ優先の最適化と不要なネットワーク API の無効化。診断音を含む構成で `factory` 領域に約 31% の空き |
| PWM の duty 更新 | 出力タスクから `ledc_set_duty()` → `ledc_update_duty()` を呼ぶ。ESP-IDF 5.5 で fade service を要求する `ledc_set_duty_and_update()` は使用しない |
| 電源配線 | XIAO の **3V3 → アンプ pin 6、GND → pin 7**。再生完了ログが正常でも、誤配線が残っている間は無音だった |

PWM 周波数はドライバ報告値で約 156 kHz。波形、出力電力、歪み、周波数特性、長時間再生は未評価です。

## just コマンドの確認

同日、XIAO ESP32-C5（MAC 末尾 `CF:09:04`）で `just build-firmware`、`just flash-firmware`、`just flash-app`、`just monitor` を検証しました。新しいビルドは `factory` 領域に約 32% の空きがあり、Elixir 用 boot を含む書き込みと照合に成功しました。

`smoke` と `demo_papageno` を書き込み、ユーザーが音を確認。Papageno の完了ログは `skipped_samples=0` でした。ホストでは `just check` のテスト 14 件（音源 6、コマンド 5、Elixir 3）、整形、`just preview` の WAV 生成も確認しました。

## 提供音源での2台再生

[提供音源の取り込み手順](firmware-build.md#提供音源で2台のデュエットを再生する) に沿って、役ごとのファームウェアとアプリを作成しました。2026-11-20 に2台へ書き込み、ハッシュ照合後、USB 経由で再起動して確認しました。

| パート | USB 識別番号の末尾 | 音源の長さ | 完了ログ |
| --- | --- | ---: | --- |
| Papageno（男声） | `CF:09:04` | 32.17 秒 | `skipped_samples=0` |
| Papagena（女声） | `CC:06:48` | 33.22 秒 | `skipped_samples=0` |

両方の起動ログで GPIO7 と 16 kHz を確認しました。ユーザーが2台を同時に通電して試聴し、両方の歌声が聞こえ、掛け合いのタイミングも合うことを確認しました。

[2台で再生したときの動画（約23秒）](assets/papapa-audio-test1.mp4)

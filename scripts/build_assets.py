#!/usr/bin/env python3
"""練習音源の合成・WAV 取り込みから、unsigned 8-bit mono PCM を生成する。

Python 標準ライブラリのみ使用し、tar 内のファイルはディスクへ展開しない。
"""
from __future__ import annotations

import argparse
import io
import math
import pathlib
import re
import struct
import tarfile
import wave

SAMPLE_RATE = 8000  # Default first-test rate; the GPTimer source is 8 MHz.
ROOT = pathlib.Path(__file__).resolve().parents[1]

# (start seconds, pitch in Hz, duration seconds); entirely original practice events.
PRACTICE = {
    "demo_papageno": [
        (0.30, 196.00, .35), (.77, 220.00, .34), (1.25, 246.94, .57),
        (2.35, 246.94, .34), (2.78, 220.00, .36), (3.30, 196.00, .61),
        (5.00, 220.00, .42), (5.54, 246.94, .40), (6.04, 261.63, .69),
        (7.52, 246.94, .51), (8.25, 196.00, .73),
    ],
    "demo_papagena": [
        (1.65, 392.00, .31), (2.05, 440.00, .36), (2.54, 493.88, .48),
        (3.97, 523.25, .35), (4.43, 493.88, .41), (4.94, 440.00, .62),
        (6.86, 493.88, .39), (7.39, 523.25, .38), (7.91, 587.33, .55),
        (8.75, 493.88, .34), (9.21, 440.00, .59),
    ],
}
DURATION = 10.2


def synth_voice(events: list[tuple[float, float, float]], rate: int, high_voice: bool) -> list[float]:
    """Deterministic, quiet 'pa'-like vowel with a short unvoiced onset."""
    out = [0.0] * round(DURATION * rate)
    # Fundamental + overtones, approximate formant weighting for /a/ vowel.
    # 練習用の簡単な音色を、基本波と倍音の重み付けで作る。
    for start, pitch, duration in events:
        begin = round(start * rate)
        end = min(len(out), begin + round(duration * rate))
        if end <= begin:
            continue
        harmonics = []
        for k in range(1, 18):
            freq = pitch * k
            if freq >= rate / 2 - 30:
                break
            f1 = 890 if high_voice else 720
            f2 = 1550 if high_voice else 1260
            band = math.exp(-.5 * ((freq - f1) / 260) ** 2)
            band += 0.65 * math.exp(-.5 * ((freq - f2) / 330) ** 2)
            harmonics.append((k, (0.28 + band) / (k ** 1.13)))
        normalization = sum(w for _, w in harmonics) or 1.0
        for i in range(begin, end):
            t = (i - begin) / rate
            u = t / duration
            attack = min(1.0, t / 0.018)
            release = min(1.0, max(0.0, (duration - t) / 0.055))
            envelope = attack * release * (0.88 + 0.12 * math.sin(math.pi * u))
            # Add quiet deterministic plosive burst only at note onset.
            burst = 0.0
            if t < .022:
                pseudo_noise = (math.sin(i * 12.9898) * 43758.5453) % 1.0
                burst = (pseudo_noise * 2.0 - 1.0) * (1 - t / .022) * .06
            vibrato = 1.0 + .002 * math.sin(2 * math.pi * 5.4 * t)
            tone = sum(w * math.sin(2 * math.pi * k * pitch * t * vibrato)
                       for k, w in harmonics) / normalization
            out[i] += .28 * envelope * tone + burst
    return out


def as_u8(samples: list[float], gain: float = 0.45) -> bytes:
    # Reject negative/out-of-range gain. For first hardware tests, keep it low.
    if not 0 < gain <= 1:
        raise ValueError("gain must be in (0, 1]")
    return bytes(max(0, min(255, round(128 + 127 * gain * v))) for v in samples)


def diagnostic_tone(rate: int) -> bytes:
    """Three quiet 440-Hz, one-second tones separated by one-second rests."""
    out = bytearray([128] * (6 * rate))
    for begin in (0, 2 * rate, 4 * rate):
        for i in range(rate):
            envelope = min(1.0, i / (rate * .01), (rate - 1 - i) / (rate * .01))
            out[begin + i] = round(128 + 6 * envelope * math.sin(2 * math.pi * 440 * i / rate))
    return bytes(out)


def read_wav(raw: bytes, target_rate: int, gain: float = .22) -> bytes:
    with wave.open(io.BytesIO(raw), "rb") as wav:
        if wav.getcomptype() != "NONE":
            raise ValueError("compressed WAV is not supported")
        rate, channels, width, frames = wav.getframerate(), wav.getnchannels(), wav.getsampwidth(), wav.getnframes()
        if channels not in (1, 2) or width not in (1, 2) or rate <= 0:
            raise ValueError("requires PCM 8/16-bit mono/stereo WAV")
        if frames > rate * 120:
            raise ValueError("WAV too long (>120 s)")
        raw_pcm = wav.readframes(frames)
    if width == 1:
        values = [(v - 128) / 128.0 for v in raw_pcm]
    else:
        values = [x / 32768.0 for (x,) in struct.iter_unpack("<h", raw_pcm)]
    mono = ([sum(values[j:j + channels]) / channels for j in range(0, len(values), channels)]
            if channels == 2 else values)
    if not mono:
        raise ValueError("empty WAV")
    n = max(1, round(len(mono) * target_rate / rate))
    converted = []
    for i in range(n):
        pos = i * rate / target_rate
        a = min(int(pos), len(mono) - 1)
        b = min(a + 1, len(mono) - 1)
        converted.append(mono[a] + (mono[b] - mono[a]) * (pos - int(pos)))
    return as_u8(converted, gain)


def wav_bytes(pcm: bytes, rate: int) -> bytes:
    dest = io.BytesIO()
    with wave.open(dest, "wb") as out:
        out.setnchannels(1)
        out.setsampwidth(1)
        out.setframerate(rate)
        out.writeframes(pcm)
    return dest.getvalue()


def find_duet_in_archive(path: pathlib.Path) -> bytes | None:
    """Only import a directly matched recording, never run/extract archive code."""
    with tarfile.open(path, mode="r:gz") as tar:
        matches = [m for m in tar.getmembers() if m.isfile() and
                   m.name.lower().endswith("papapa_duet.wav")]
        if len(matches) != 1:
            return None
        if matches[0].size > 20 * 1024 * 1024:
            raise ValueError("WAV exceeds 20 MB limit")
        member = tar.extractfile(matches[0])
        if member is None:
            raise ValueError("Cannot read WAV member")
        return member.read()


def generated_files(clips: dict[str, bytes], rate: int) -> tuple[str, str, str]:
    if not clips:
        raise ValueError("no clips available")
    header = """/* Generated by scripts/build_assets.py; do not edit. */
#pragma once
#include <stdint.h>
typedef struct {
    const char *name;
    const uint8_t *samples;
    uint32_t count;
} papapa_clip_t;
extern const papapa_clip_t papapa_clips[];
extern const unsigned papapa_clips_count;
extern const unsigned papapa_sample_rate_hz;
"""
    c = ['/* Generated by scripts/build_assets.py; do not edit. */',
         '#include "audio_catalog.generated.h"', '']
    elixir = ['defmodule HelloAtomvmPapapa.Catalog do',
              '  @moduledoc "Generated track IDs matching the native C audio catalog."',
              '  @tracks [']
    for index, (name, pcm) in enumerate(clips.items()):
        if not re.fullmatch(r"[a-z][a-z0-9_]*", name):
            raise ValueError("unsafe clip name")
        symbol = "pcm_" + name
        c.append(f"static const uint8_t {symbol}[] = {{")
        for pos in range(0, len(pcm), 24):
            c.append("  " + ", ".join(str(i) for i in pcm[pos:pos + 24]) + ",")
        c.append("};\n")
        suffix = "," if index < len(clips) - 1 else ""
        elixir.append(f'    {{"{name}", {index}, {round(len(pcm)*1000/rate)}}}{suffix}')
    c.append("const papapa_clip_t papapa_clips[] = {")
    for name, pcm in clips.items():
        c.append(f'  {{"{name}", pcm_{name}, {len(pcm)}U}},')
    c += ['};', f'const unsigned papapa_clips_count = {len(clips)}U;',
          f'const unsigned papapa_sample_rate_hz = {rate}U;', '']
    elixir += ['  ]', '', '  def names, do: Enum.map(@tracks, fn {name, _id, _duration} -> name end)',
               '', '  def id(name) do',
               '    case Enum.find(@tracks, fn {track, _id, _duration} -> track == name end) do',
               '      {_name, id, _duration} -> id',
               '      nil -> nil',
               '    end',
               '  end',
               '', '  def duration_ms(name) do',
               '    case Enum.find(@tracks, fn {track, _id, _duration} -> track == name end) do',
               '      {_name, _id, duration} -> duration',
               '      nil -> nil',
               '    end',
               '  end', 'end', '']
    return "\n".join(c), header, "\n".join(elixir)


def build(args: argparse.Namespace) -> dict[str, bytes]:
    rate = args.rate
    if 8000000 % rate:
        raise ValueError("rate must exactly divide 8MHz GPTimer resolution")
    clips: dict[str, bytes] = {}
    if not args.no_demo:
        lower = synth_voice(PRACTICE["demo_papageno"], rate, False)
        upper = synth_voice(PRACTICE["demo_papagena"], rate, True)
        clips["smoke"] = as_u8(lower[:round(2.0 * rate)])
        clips["demo_papageno"] = as_u8(lower)
        clips["demo_papagena"] = as_u8(upper)
        clips["demo_duet"] = as_u8([max(-1.0, min(1.0, a + b)) for a, b in zip(lower, upper)])
        clips["tone_440"] = diagnostic_tone(rate)

    inputs = {"papageno": args.papageno_wav, "papagena": args.papagena_wav, "duet": args.duet_wav}
    if args.from_tar and inputs["duet"] is None:
        found = find_duet_in_archive(args.from_tar)
        if found is None:
            raise ValueError("archive contains no unique papapa_duet.wav; supply explicit --duet-wav")
        clips["duet"] = read_wav(found, rate)
    for name, file in inputs.items():
        if file is not None:
            clips[name] = read_wav(file.read_bytes(), rate)
    return clips


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rate", type=int, choices=[8000, 16000], default=SAMPLE_RATE)
    parser.add_argument("--out-dir", type=pathlib.Path, default=ROOT)
    parser.add_argument("--preview-dir", type=pathlib.Path)
    parser.add_argument("--from-tar", type=pathlib.Path, help="papapa_duet.wav を含む .tar.gz")
    parser.add_argument("--papageno-wav", type=pathlib.Path)
    parser.add_argument("--papagena-wav", type=pathlib.Path)
    parser.add_argument("--duet-wav", type=pathlib.Path)
    parser.add_argument("--no-demo", action="store_true")
    args = parser.parse_args()
    clips = build(args)
    c, h, ex = generated_files(clips, args.rate)
    native = args.out_dir / "components" / "papapa_audio"
    native.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "lib" / "hello_atomvm_papapa").mkdir(parents=True, exist_ok=True)
    (native / "audio_catalog.generated.c").write_text(c, encoding="utf-8")
    (native / "audio_catalog.generated.h").write_text(h, encoding="utf-8")
    (args.out_dir / "lib" / "hello_atomvm_papapa" / "catalog.ex").write_text(ex, encoding="utf-8")
    if args.preview_dir:
        args.preview_dir.mkdir(parents=True, exist_ok=True)
        for name, pcm in clips.items():
            (args.preview_dir / f"{name}.wav").write_bytes(wav_bytes(pcm, args.rate))
    for name, clip in clips.items():
        print(f"{name:18} {len(clip) / args.rate:7.2f}s  {len(clip):8} samples")
    print(f"generated {len(clips)} clips at {args.rate} Hz; embedded native PCM requires firmware rebuild")


if __name__ == "__main__":
    main()

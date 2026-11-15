#!/usr/bin/env python3
"""Host-side audio generation tests; does not require Elixir or ESP32."""
import argparse
import importlib.util
import io
import pathlib
import shutil
import struct
import subprocess
import tarfile
import tempfile
import unittest
import wave

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("build_assets", HERE / "build_assets.py")
assets = importlib.util.module_from_spec(spec)
spec.loader.exec_module(assets)


class AssetTests(unittest.TestCase):
    def test_demos_have_correct_length_and_safe_low_amplitude(self):
        args = argparse.Namespace(rate=8000, no_demo=False, from_tar=None,
                                  papageno_wav=None, papagena_wav=None, duet_wav=None)
        clips = assets.build(args)
        self.assertEqual(list(clips), ["smoke", "demo_papageno", "demo_papagena", "demo_duet", "tone_440"])
        self.assertEqual(len(clips["demo_duet"]), 81600)
        self.assertTrue(any(x != 128 for x in clips["demo_duet"]))
        # Absolute swing under 20% of maximum PWM range on first power-up.
        self.assertLess(max(abs(x - 128) for clip in clips.values() for x in clip), 26)

    def test_generation_is_deterministic(self):
        self.assertEqual(assets.synth_voice(assets.PRACTICE["demo_papageno"], 8000, False),
                         assets.synth_voice(assets.PRACTICE["demo_papageno"], 8000, False))

    def test_diagnostic_tone_has_quiet_pulses_and_silent_gaps(self):
        for rate in (8000, 16000):
            tone = assets.diagnostic_tone(rate)
            self.assertEqual(len(tone), 6 * rate)
            self.assertEqual((min(tone), max(tone)), (122, 134))
            for second in (1, 3, 5):
                self.assertEqual(tone[second * rate:(second + 1) * rate], bytes([128]) * rate)
            # Rising zero crossings in the sustained portion identify the pitch.
            plateau = tone[rate // 10:rate * 9 // 10]
            crossings = sum(a <= 128 < b for a, b in zip(plateau, plateau[1:]))
            self.assertAlmostEqual(crossings / .8, 440, delta=2)

    def test_generated_catalog_and_c_compile(self):
        args = argparse.Namespace(rate=8000, no_demo=False, from_tar=None,
                                  papageno_wav=None, papagena_wav=None, duet_wav=None)
        c, h, ex = assets.generated_files(assets.build(args), 8000)
        self.assertIn('"demo_duet"', c)
        self.assertIn('"demo_papageno"', ex)
        self.assertIn("extern const papapa_clip_t", h)
        cc = shutil.which("cc")
        if cc:
            with tempfile.TemporaryDirectory() as tmp:
                native = pathlib.Path(tmp)
                (native / "audio_catalog.generated.c").write_text(c)
                (native / "audio_catalog.generated.h").write_text(h)
                subprocess.run([cc, "-std=c11", "-Wall", "-Wextra", "-Werror", "-c",
                                str(native / "audio_catalog.generated.c"), "-o",
                                str(native / "catalog.o")], check=True, capture_output=True)

    def test_import_wav_and_tar(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            pcm = [round(9000 * __import__("math").sin(i / 20)) for i in range(4000)]
            data = io.BytesIO()
            with wave.open(data, "wb") as wav:
                wav.setnchannels(1)
                wav.setsampwidth(2)
                wav.setframerate(16000)
                wav.writeframes(struct.pack("<" + "h" * len(pcm), *pcm))
            recording = root / "papapa_duet.wav"
            recording.write_bytes(data.getvalue())
            audio = assets.read_wav(data.getvalue(), 8000)
            self.assertEqual(len(audio), 2000)
            self.assertLess(max(abs(x - 128) for x in audio), 26)
            archive = root / "snapshot.tar.gz"
            with tarfile.open(archive, "w:gz") as tar:
                tar.add(recording, arcname="some/private/priv/audio/papapa_duet.wav")
            self.assertEqual(assets.find_duet_in_archive(archive), data.getvalue())

    def test_gain_validation(self):
        with self.assertRaises(ValueError):
            assets.as_u8([1.0], 2.0)
        with self.assertRaises(ValueError):
            assets.as_u8([1.0], 0.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)

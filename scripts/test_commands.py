#!/usr/bin/env python3
"""実機を使わず、ビルド・書き込みコマンドの引数と実行順を検証する。"""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
FAKE_TOOL = r'''#!/usr/bin/env python3
import json, os, pathlib, shutil, sys
name = pathlib.Path(sys.argv[0]).name
args = sys.argv[1:]
if name == "mise":
    if args[0] == "where":
        print(pathlib.Path(shutil.which("erl" if args[1] == "erlang" else args[1])).resolve().parent.parent)
        sys.exit(0)
    os.execvp(args[2], args[2:])
with open(os.environ["COMMAND_LOG"], "a") as log:
    log.write(json.dumps({"name": name, "args": args, "env": {
        k: os.environ.get(k) for k in ("MIX_ENV", "PAPAPA_TRACK", "PAPAPA_REPEAT")}}) + "\n")
if name == "cmake" and "--build" in args:
    out = pathlib.Path(args[args.index("--build") + 1]) / "libs/esp32boot/elixir_esp32boot.avm"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.touch()
if name == "idf.py" and "build" in args:
    out = pathlib.Path(args[args.index("-B") + 1]) / "atomvm-esp32.bin"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.touch()
'''


class CommandTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.bin = self.root / "bin"
        self.bin.mkdir()
        for name in ("mise", "cmake", "idf.py", "mix"):
            path = self.bin / name
            path.write_text(FAKE_TOOL)
            path.chmod(0o755)
        self.atomvm = self.root / "AtomVM with spaces"
        (self.atomvm / "src/platforms/esp32/components").mkdir(parents=True)
        (self.atomvm / "CMakeLists.txt").touch()
        idf = self.root / "IDF with spaces"
        idf.mkdir()
        (idf / "export.sh").write_text('export PATH="$FAKE_BIN:$PATH"\n')
        self.log = self.root / "commands.jsonl"
        self.env = dict(os.environ, PATH=f"{self.bin}:{os.environ['PATH']}",
                        ATOMVM_REPO_PATH=str(self.atomvm), ESP_IDF_PATH=str(idf),
                        PAPAPA_BUILD_DIR="build with spaces", PAPAPA_JOBS="2",
                        PAPAPA_REPEAT="false", FAKE_BIN=str(self.bin), COMMAND_LOG=str(self.log))

    def run_script(self, script, *args, ok=True):
        r = subprocess.run(["bash", str(ROOT / "scripts" / script), *args],
                           cwd=self.root, env=self.env, text=True, capture_output=True)
        if ok:
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        else:
            self.assertNotEqual(r.returncode, 0)
        return r

    def commands(self):
        return [json.loads(line) for line in self.log.read_text().splitlines()] if self.log.exists() else []

    def test_build_prepares_boot_before_idf_and_preserves_paths(self):
        self.run_script("firmware.sh", "build")
        commands = self.commands()
        self.assertEqual([c["name"] for c in commands], ["cmake", "cmake", "idf.py"])
        args = commands[-1]["args"]
        self.assertIn("IDF_TARGET=esp32c5", args)
        self.assertIn("ATOMVM_ELIXIR_SUPPORT=ON", args)
        self.assertIn(f"SDKCONFIG_DEFAULTS={self.atomvm}/src/platforms/esp32/sdkconfig.defaults;{ROOT}/config/sdkconfig.papapa.defaults", args)
        build = self.atomvm / "src/platforms/esp32/build with spaces"
        self.assertEqual((build / "papapa-source-path").read_text().strip(), str(ROOT))
        self.assertEqual((self.atomvm / "src/platforms/esp32/components/hello_atomvm_papapa").resolve(), ROOT)

    def test_flash_requires_build_and_rejects_a_different_source(self):
        self.run_script("firmware.sh", "flash", "/dev/test", ok=False)
        self.assertEqual(self.commands(), [])
        self.run_script("firmware.sh", "build")
        marker = self.atomvm / "src/platforms/esp32/build with spaces/papapa-source-path"
        marker.write_text("/different/repo\n")
        before = self.commands()
        self.run_script("firmware.sh", "flash", "/dev/test", ok=False)
        self.assertEqual(self.commands(), before)

    def test_flash_uses_explicit_port_without_erasing(self):
        self.run_script("firmware.sh", "build")
        self.run_script("firmware.sh", "flash", "/dev/serial/device with spaces")
        args = self.commands()[-1]["args"]
        self.assertEqual(args[-3:], ["-p", "/dev/serial/device with spaces", "flash"])
        self.assertNotIn("erase-flash", args)

    def test_app_clean_and_flash_share_prod_track_and_repeat(self):
        self.env["PAPAPA_REPEAT"] = "true"
        self.run_script("flash-app.sh", "/dev/test", "demo_papagena")
        commands = self.commands()
        self.assertEqual([c["args"] for c in commands], [
            ["deps.get"], ["clean"], ["atomvm.esp32.flash", "--port", "/dev/test"]])
        for c in commands:
            self.assertEqual(c["env"], {"MIX_ENV": "prod", "PAPAPA_TRACK": "demo_papagena", "PAPAPA_REPEAT": "true"})

    def test_invalid_track_or_repeat_stops_before_mix(self):
        self.run_script("flash-app.sh", "/dev/test", "unknown", ok=False)
        self.env["PAPAPA_REPEAT"] = "yes"
        self.run_script("flash-app.sh", "/dev/test", "smoke", ok=False)
        self.assertEqual(self.commands(), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)

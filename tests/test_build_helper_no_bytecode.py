from __future__ import annotations

import importlib.util
import shutil
import tempfile
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class BuildHelperBytecodeTest(unittest.TestCase):
    def test_build_module_load_does_not_create_src_pycache(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            shutil.copy2(ROOT / "build.py", temp_root / "build.py")
            (temp_root / "src").mkdir()
            shutil.copy2(
                ROOT / "src" / "faceplate_native_canvas.py",
                temp_root / "src" / "faceplate_native_canvas.py",
            )

            spec = importlib.util.spec_from_file_location(
                "_switch_vision_build_bytecode_test",
                temp_root / "build.py",
            )
            self.assertIsNotNone(spec)
            self.assertIsNotNone(spec.loader)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            self.assertFalse((temp_root / "src" / "__pycache__").exists())

    def test_zip_directory_is_deterministic_across_source_mtimes(self) -> None:
        import hashlib
        import os
        import time

        spec = importlib.util.spec_from_file_location(
            "_switch_vision_build_zip_test", ROOT / "build.py"
        )
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            source = base / "release"
            source.mkdir()
            (source / "README.txt").write_text("stable\n", encoding="utf-8")
            script = source / "run.sh"
            script.write_text("#!/bin/sh\necho stable\n", encoding="utf-8")
            script.chmod(0o755)
            first = base / "first.zip"
            second = base / "second.zip"

            module.zip_directory(source, first, base)
            future = time.time() + 3600
            os.utime(source / "README.txt", (future, future))
            os.utime(script, (future, future))
            module.zip_directory(source, second, base)

            self.assertEqual(
                hashlib.sha256(first.read_bytes()).hexdigest(),
                hashlib.sha256(second.read_bytes()).hexdigest(),
            )


if __name__ == "__main__":
    unittest.main()

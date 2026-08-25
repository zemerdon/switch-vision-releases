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


if __name__ == "__main__":
    unittest.main()

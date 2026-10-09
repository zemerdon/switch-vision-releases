from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("switch_vision_core_builder", ROOT / "build.py")
assert spec is not None and spec.loader is not None
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)


class BuildEditorBackupExclusionTests(unittest.TestCase):
    def test_only_timestamped_editor_backups_are_excluded(self) -> None:
        self.assertTrue(build.is_editor_backup(Path("faceplate.json.bak.20261009-223815-287375")))
        self.assertFalse(build.is_editor_backup(Path("faceplate.json")))
        self.assertFalse(build.is_editor_backup(Path("faceplate-bak.png")))

    def test_copy_and_public_zip_exclude_editor_backups(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "source"
            dest = root / "release"
            src.mkdir()
            (src / "faceplate.png").write_bytes(b"PNG_OK")
            (src / "faceplate.png.bak.20261009-223815-287375").write_bytes(b"DO_NOT_PUBLISH")
            build.copy_tree_files(src, dest)
            self.assertTrue((dest / "faceplate.png").is_file())
            self.assertFalse(any(".bak." in p.name for p in dest.iterdir()))
            archive = root / "release.zip"
            build.zip_directory(src, archive, root)
            with ZipFile(archive) as z:
                self.assertEqual(z.namelist(), ["source/faceplate.png"])
                self.assertNotIn(b"DO_NOT_PUBLISH", z.read("source/faceplate.png"))


if __name__ == "__main__":
    unittest.main()

"""Core artwork revisions must be an atomic, versioned PNG+factory-geometry pair."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("faceplate_revision_build", ROOT / "faceplate_revision_build.py")
assert spec and spec.loader
import sys
sys.modules[spec.name] = module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
spec2 = importlib.util.spec_from_file_location(
    "faceplate_artwork_history", ROOT / "src/custom_components/switch_vision/faceplate_artwork_history.py")
assert spec2 and spec2.loader
sys.modules[spec2.name] = history = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(history)


def run(repo: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


class VersionedFaceplateTests(unittest.TestCase):
    def test_image_and_geometry_revisions_and_tamper(self) -> None:
        with TemporaryDirectory(prefix="faceplate-revision-") as temp:
            repo = Path(temp) / "repo"
            frontend = Path(temp) / "www"
            (repo / "src/faceplates").mkdir(parents=True)
            (repo / "src/calibration").mkdir()
            name = "example.png"
            image = repo / "src/faceplates" / name
            factory_file = repo / "src/calibration/faceplate-example.json"

            def revision(version: str, pixels: bytes, port_x: int) -> None:
                (repo / "VERSION").write_text(version + "\n")
                image.write_bytes(pixels)
                factory_file.write_text(json.dumps({
                    "schema": "switch-vision-interactive-calibration-v1",
                    "image": {"file": "faceplates/" + name, "width": 100, "height": 40},
                    "ports": {"1": {"center": [port_x, 20]}}, "sfp": {}
                }))

            run(repo, "init", "-q")
            revision("2.7.92", b"pixels-a", 10)
            run(repo, "add", ".")
            run(repo, "-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "-qm", "original")
            revision("2.7.93", b"pixels-b", 10)
            run(repo, "add", ".")
            run(repo, "-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "-qm", "new image")
            revision("2.7.94", b"pixels-b", 30)
            (frontend / "faceplates").mkdir(parents=True)
            (frontend / "calibration").mkdir()
            (frontend / "faceplates" / name).write_bytes(image.read_bytes())
            (frontend / "calibration" / factory_file.name).write_bytes(factory_file.read_bytes())

            result = module.generate(repo, frontend, "2.7.94")
            revisions = result["faceplates"][name]
            self.assertEqual([x["version"] for x in revisions], ["2.7.92", "2.7.93", "2.7.94"])
            self.assertEqual(revisions[1]["sha256"], revisions[2]["sha256"])
            self.assertNotEqual(revisions[1]["geometry_sha256"], revisions[2]["geometry_sha256"])
            verified = history.catalog_revisions(frontend, name)
            self.assertEqual(len(verified), 3)
            self.assertEqual(history.revision_choice(frontend, name, revisions[1]["sha256"],
                                                     revisions[2]["sha256"], "2.7.93")["geometry"]["ports"]["1"]["center"][0], 10)
            self.assertEqual(history.revision_choice(frontend, name, revisions[2]["sha256"],
                                                     revisions[2]["sha256"], "2.7.94")["geometry"]["ports"]["1"]["center"][0], 30)
            self.assertEqual(len(history.catalog_revisions(frontend, name)), 3)
            (frontend / revisions[0]["geometry_path"]).write_text("tampered")
            self.assertEqual(len(history.catalog_revisions(frontend, name)), 2)
            self.assertFalse(history.revision_choice(frontend, name, revisions[0]["sha256"],
                                                     revisions[2]["sha256"], "2.7.92"))
            with self.assertRaisesRegex(ValueError, "conflicting"):
                module.generate(repo, frontend, "2.7.94")
            (frontend / revisions[0]["geometry_path"]).unlink()
            result2 = module.generate(repo, frontend, "2.7.94")
            self.assertEqual(result2["faceplates"][name], revisions)
            self.assertEqual(len(history.catalog_revisions(frontend, name)), 3)


if __name__ == "__main__":
    unittest.main()

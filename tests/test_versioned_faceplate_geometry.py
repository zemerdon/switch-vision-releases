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


    def test_three_distinct_pairs_rotate_without_release_only_revision(self) -> None:
        with TemporaryDirectory(prefix="faceplate-cap-") as temp:
            repo = Path(temp) / "repo"
            frontend = Path(temp) / "www"
            (repo / "src/faceplates").mkdir(parents=True)
            (repo / "src/calibration").mkdir()
            image = repo / "src/faceplates/example.png"
            geometry = repo / "src/calibration/faceplate-example.json"
            run(repo, "init", "-q")

            def commit(version: str, pixels: bytes, x: int) -> None:
                (repo / "VERSION").write_text(version + "\n")
                image.write_bytes(pixels)
                geometry.write_text(json.dumps({
                    "schema": "switch-vision-interactive-calibration-v1",
                    "image": {"file": "faceplates/example.png"},
                    "ports": {"1": {"center": [x, 10]}}, "sfp": {},
                }))
                run(repo, "add", ".")
                run(repo, "-c", "user.name=Test", "-c",
                    "user.email=test@example.invalid", "commit", "-qm", version)

            commit("2.7.70", b"art-a", 10)
            commit("2.7.71", b"art-b", 10)  # PNG-only
            commit("2.7.72", b"art-b", 20)  # geometry-only, same PNG SHA
            commit("2.7.73", b"art-c", 20)  # fourth distinct pair
            (repo / "VERSION").write_text("2.7.99\n")
            run(repo, "add", ".")
            run(repo, "-c", "user.name=Test", "-c",
                "user.email=test@example.invalid", "commit", "-qm", "version-only")
            (frontend / "faceplates").mkdir(parents=True)
            (frontend / "calibration").mkdir()
            (frontend / "faceplates/example.png").write_bytes(image.read_bytes())
            (frontend / "calibration/faceplate-example.json").write_bytes(geometry.read_bytes())
            index = module.generate(repo, frontend, "2.7.99")
            rows = index["faceplates"]["example.png"]
            self.assertEqual(len(rows), 3)
            self.assertEqual([r["version"] for r in rows],
                             ["2.7.71", "2.7.72", "2.7.73"])
            self.assertEqual(rows[0]["sha256"], rows[1]["sha256"])
            self.assertNotEqual(rows[0]["geometry_sha256"], rows[1]["geometry_sha256"])
            self.assertEqual(len(history.catalog_revisions(frontend, "example.png")), 3)
            self.assertFalse((frontend / "faceplates-old/2.7.70/example.png").exists())
            self.assertEqual(rows[-1]["path"], "faceplates/example.png")
            self.assertEqual(index["core_version"], "2.7.99")
            # A new version with no actual change does not create an extra pair.
            (repo / "VERSION").write_text("2.7.100\n")
            (frontend / "faceplates-old").rename(frontend / "archive")
            again = module.generate(repo, frontend, "2.7.100")
            self.assertEqual([r["version"] for r in again["faceplates"]["example.png"]],
                             ["2.7.71", "2.7.72", "2.7.73"])


    def test_retained_selected_pair_requires_exact_version_and_geometry(self) -> None:
        import hashlib
        with TemporaryDirectory(prefix="faceplate-selected-") as temp:
            root = Path(temp)
            name, pixels = "example.png", b"identical-pixels"
            sha = hashlib.sha256(pixels).hexdigest()
            old = root / "faceplate-history/revisions/2.7.70"
            old.mkdir(parents=True)
            (old / name).write_bytes(pixels)
            factory = json.dumps({
                "schema": "switch-vision-interactive-calibration-v1",
                "image": {"file": "faceplates/" + name},
                "ports": {"1": {"center": [10, 20]}}, "sfp": {},
            }).encode()
            geometry_sha = hashlib.sha256(factory).hexdigest()
            (old / "example.json").write_bytes(factory)
            (root / "faceplate-history/revisions/manifest.json").write_text(
                json.dumps({"schema": 1, "faceplates": {name: [{
                    "version": "2.7.70", "filename": name,
                    "sha256": sha, "geometry_sha256": geometry_sha,
                    "path": "faceplate-history/revisions/2.7.70/example.png",
                    "geometry_path": "faceplate-history/revisions/2.7.70/example.json",
                }]}}))
            # Same PNG hash as currently shipped, but different old geometry:
            # a sha-only comparison would silently select the wrong ports.
            selected = history.verified_choice(root, name, sha, sha,
                                               "2.7.70", geometry_sha)
            self.assertEqual(selected["geometry"]["ports"]["1"]["center"], [10, 20])
            self.assertEqual(selected["path"],
                             "faceplate-history/revisions/2.7.70/example.png")
            self.assertEqual(history.verified_choice(root, name, sha, sha,
                                   "2.7.70", "0" * 64).get("unavailable"), "true")
            (old / "example.json").write_text("tampered")
            self.assertEqual(history.verified_choice(root, name, sha, sha,
                                   "2.7.70", geometry_sha).get("unavailable"), "true")


if __name__ == "__main__":
    unittest.main()

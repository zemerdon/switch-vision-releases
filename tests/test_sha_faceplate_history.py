"""Core accepts Installer's content-paired history and current dedicated stock."""
import hashlib
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src/custom_components/switch_vision"))
import faceplate_artwork_history as art


def digest(data):
    return hashlib.sha256(data).hexdigest()


def pair(root, filename, png, x, prior=False):
    geo = {
        "schema": "switch-vision-interactive-calibration-v1",
        "image": {"file": "faceplates/" + filename},
        "ports": {"1": {"center": [x, 1]}}, "sfp": {},
    }
    blob = json.dumps(geo).encode()
    sha, geometry_sha = digest(png), digest(blob)
    identity = digest((sha + ":" + geometry_sha).encode())
    base = (root / "faceplate-history/revisions/sha" / identity
            if prior else root / "faceplates")
    base.mkdir(parents=True, exist_ok=True)
    (base / filename).write_bytes(png)
    if prior:
        (base / (filename[:-4] + ".json")).write_bytes(blob)
    else:
        factory = root / "calibration"
        factory.mkdir(parents=True, exist_ok=True)
        (factory / ("faceplate-" + filename[:-4] + ".json")).write_bytes(blob)
    return {"identity": identity, "sha256": sha, "geometry_sha256": geometry_sha,
            "filename": filename, "geometry_file": "faceplate-" + filename[:-4] + ".json",
            "path": (f"faceplate-history/revisions/sha/{identity}/{filename}"
                     if prior else "faceplates/" + filename),
            "geometry_path": (f"faceplate-history/revisions/sha/{identity}/{filename[:-4]}.json"
                              if prior else f"calibration/faceplate-{filename[:-4]}.json")}


class SHAHistoryTests(unittest.TestCase):
    def test_old_and_current_revisions_have_matched_factory_geometry(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            old = pair(root, "dedicated.png", b"A", 10, prior=True)
            now = pair(root, "dedicated.png", b"B", 20)
            manifest = root / "faceplate-history/revisions/sha/manifest.json"
            manifest.write_text(json.dumps({"schema": 2, "faceplates": {"dedicated.png": [old]}}))
            catalog = art.catalog_revisions(root, "dedicated.png")
            self.assertEqual(len(catalog), 2)
            self.assertEqual([a["geometry"]["ports"]["1"]["center"][0] for a in catalog], [10, 20])
            self.assertEqual(art.revision_choice(root, "dedicated.png", old["sha256"], now["sha256"],
                                                 "sha-" + old["identity"][:20])["path"], old["path"])
            self.assertEqual(art.revision_choice(root, "dedicated.png", now["sha256"], now["sha256"])
                             ["geometry"]["ports"]["1"]["center"][0], 20)
            self.assertEqual(len(art.revision_index(root)["dedicated.png"]), 2)
            self.assertEqual(art.saved_artwork(root, {
                "image": {"file": "faceplates/dedicated.png"},
                art.STOCK_SHA_FIELD: old["sha256"],
            }, now["sha256"])[1], old["path"])
            (root / old["geometry_path"]).write_text("corrupt")
            self.assertEqual(len(art.catalog_revisions(root, "dedicated.png")), 1)
            self.assertFalse(art.revision_choice(root, "dedicated.png", old["sha256"], now["sha256"]))

    def test_new_dedicated_artwork_available_without_history_archive(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            dedicated = pair(root, "new-model.png", b"dedicated", 42)
            rows = art.catalog_revisions(root, "new-model.png")
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["sha256"], dedicated["sha256"])
            self.assertEqual(rows[0]["geometry_sha256"], dedicated["geometry_sha256"])
            self.assertEqual(art.revision_index(root)["new-model.png"][0]["path"],
                             "faceplates/new-model.png")


if __name__ == "__main__":
    unittest.main()

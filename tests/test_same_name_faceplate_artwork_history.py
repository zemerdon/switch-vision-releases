"""Protect stable model filenames and historical image provenance."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "src/custom_components/switch_vision/faceplate_artwork_history.py"
spec = importlib.util.spec_from_file_location("faceplate_artwork_history", MODULE)
assert spec and spec.loader
history = importlib.util.module_from_spec(spec)
spec.loader.exec_module(history)



class SameNameArtworkHistoryTests(unittest.TestCase):
    def test_stock_image_revision_keeps_model_filename_and_geometry(self) -> None:
        asset = ROOT / "src/faceplates/cisco-3850-12xs.png"
        geometry = ROOT / "src/calibration/faceplate-cisco-3850-12xs.json"
        data = json.loads(geometry.read_text(encoding="utf-8"))
        manifest = json.loads((ROOT / "src/custom_components/switch_vision/stock-assets.json").read_text())
        assert data["image"]["width"] == 2680
        assert data["image"]["height"] == 356
        assert len(data["sfp"]) == 12
        sha = hashlib.sha256(asset.read_bytes()).hexdigest()
        assert sha == "990a72433510e64e164a55bf07fb814dd2d276fac256be726f530b53334b3dc9"
        assert manifest["assets"]["faceplates"]["cisco-3850-12xs.png"] == sha


    def test_verified_previous_stock_version_and_legacy(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            name = "switch.png"
            old_data = b"prior-reviewed-original"
            new_data = b"updated-stock"
            old_sha = hashlib.sha256(old_data).hexdigest()
            new_sha = hashlib.sha256(new_data).hexdigest()
            current = root / "faceplates" / name
            current.parent.mkdir(parents=True)
            current.write_bytes(new_data)
            for folder in (old_sha, "legacy"):
                archive = root / "faceplate-history" / folder / name
                archive.parent.mkdir(parents=True)
                archive.write_bytes(old_data)
            profile = {"image": {"file": "faceplates/" + name},
                       "ui": {"faceplate": {"source": "custom", "file": name}}}
            assert history.stock_filename(profile) == name
            assert history.current_stock_sha(root, profile, {"faceplates": {name: new_sha}}) == new_sha
            assert history.current_stock_sha(root, profile, {"faceplates": {name: old_sha}}) == ""
            assert history.saved_artwork(root, profile, new_sha) == (
                old_sha, "faceplate-history/legacy/" + name
            )
            profile[history.STOCK_SHA_FIELD] = old_sha
            assert history.saved_artwork(root, profile, new_sha) == (
                old_sha, "faceplate-history/" + old_sha + "/" + name
            )
            profile[history.STOCK_SHA_FIELD] = new_sha
            assert history.saved_artwork(root, profile, new_sha) == (new_sha, "")
            profile[history.STOCK_SHA_FIELD] = old_sha
            (root / "faceplate-history" / old_sha / name).write_bytes(b"tampered")
            assert history.saved_artwork(root, profile, new_sha) == ("", "")
            profile.pop(history.STOCK_SHA_FIELD)
            assert history.saved_artwork(root, profile, new_sha) == ("", ""), (
                "unverified legacy image cannot create an upgrade offer"
            )
            profile["ui"]["faceplate"]["file"] = "../bad.png"
            assert history.stock_filename(profile) == ""

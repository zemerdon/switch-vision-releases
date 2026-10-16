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
        assert sha == "bc34fc58e818014a3d1b031221e4aab87ae567654075f4f2011f695c23572d74"
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


    def test_switch_choice_uses_exact_previous_pixels_without_geometry_mutation(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            name = "switch.png"
            old, new = b"catalog-before", b"catalog-after"
            old_sha, new_sha = hashlib.sha256(old).hexdigest(), hashlib.sha256(new).hexdigest()
            (root / "faceplates").mkdir()
            (root / "faceplates" / name).write_bytes(new)
            historical = root / "faceplate-history" / old_sha / name
            historical.parent.mkdir(parents=True)
            historical.write_bytes(old)
            old_profile = {"image": {"file": "faceplates/" + name},
                           "ui": {"faceplate": {"source": "default", "file": "default"}},
                           history.STOCK_SHA_FIELD: old_sha}
            assert history.pin_for_profile(root, name, new_sha, old_profile) == old_sha
            assert history.pin_for_profile(root, name, new_sha, None) == new_sha
            kept = history.verified_choice(root, name, old_sha, new_sha)
            assert kept["path"] == f"faceplate-history/{old_sha}/{name}"
            assert kept["sha256"] == old_sha
            assert history.verified_choice(root, name, new_sha, new_sha)["path"] == f"faceplates/{name}"
            historical.write_bytes(b"damaged")
            missing = history.verified_choice(root, name, old_sha, new_sha)
            assert "path" not in missing and missing["unavailable"] == "true"
            assert history.verified_choice(root, "../not-stock.png", old_sha, new_sha) == {}
            assert history.verified_choice(root, name, "bad", new_sha) == {}

    def test_real_card_path_is_pinned_and_explicit_upgrade_resets_switch_geometry(self) -> None:
        source = (ROOT / "src/custom_components/switch_vision/__init__.py").read_text()
        card = (ROOT / "src/js/switch-vision.js").read_text()
        assert '"switch_vision/approve_stock_artwork"' in source
        assert 'websocket_api.require_admin' in source
        assert '"stock_artwork_choices"' in source
        assert '_stock_selection.apply_approved_switch_artwork(' in source
        assert 'reset_switch_calibration' in source
        assert '"calibration_reset": True' in source
        assert '"geometry_sha256": revision["geometry_sha256"]' in source
        assert 'stock_artwork: artwork_choice' not in source  # JSON response is keyed
        assert '"stock_artwork": artwork_choice' in source
        assert '"stock_artwork": artwork_choice' in source
        assert 'this._stockArtworkChoice' in card
        assert 'faceplate-history/' in card
        assert 'Verifying this switch' in card

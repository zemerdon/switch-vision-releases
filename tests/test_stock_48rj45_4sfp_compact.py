#!/usr/bin/env python3
"""Owner-supplied compact stock 48 RJ45 / 4 SFP artwork and exact geometry."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from faceplate_native_canvas import png_dimensions, render_space_calibration

ART = ROOT / "src/faceplates/48rj45-4sfp-compact.png"
LEGACY_ART = ROOT / "src/faceplates/48rj45-4sfp.png"
LEGACY_FACTORY = ROOT / "src/calibration/faceplate-stock-48rj45-4sfp.json"
OWNER = ROOT / "src/calibration/geometry-stock-48rj45-4sfp-compact.json"
FACTORY = ROOT / "src/calibration/faceplate-stock-48rj45-4sfp-compact.json"
ASSETS = ROOT / "src/custom_components/switch_vision/stock-assets.json"
EXPECTED_ART_SHA = "b69bcff85fc4d682fa19a16a9afabc74afa94de9b86504a69646a487b5c8ccd9"
EXPECTED_OWNER_SHA = "c99793343fd3f353fbc0eb5b01389bc7b2575b8ae9d9847371b8d9d69aa46cd8"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class CompactStock48By4Tests(unittest.TestCase):
    def test_original_owner_artwork_and_export_are_exact(self) -> None:
        self.assertEqual(sha256(ART), EXPECTED_ART_SHA)
        self.assertEqual(sha256(OWNER), EXPECTED_OWNER_SHA)
        self.assertEqual(png_dimensions(ART), (6000, 900))
        exported = json.loads(OWNER.read_text(encoding="utf-8"))
        self.assertEqual(exported["transfer_type"], "switch-vision-geometry-profile-v1")
        self.assertEqual(exported["model"], "stock-48rj45-4sfp")
        self.assertEqual(exported["geometry"]["image"]["coordinate_space"], "switch-vision-render-2048x448-v1")
        self.assertEqual(set(exported["geometry"]["ports"]), {str(i) for i in range(1, 49)})
        self.assertEqual(set(exported["geometry"]["sfp"]), {"SFP1", "SFP2", "SFP3", "SFP4"})
        self.assertEqual(len(exported["geometry"]["status_leds"]), 7)

    def test_native_factory_round_trips_every_owner_geometry_value(self) -> None:
        source = json.loads(OWNER.read_text(encoding="utf-8"))["geometry"]
        factory = json.loads(FACTORY.read_text(encoding="utf-8"))
        self.assertEqual(factory["model"], "stock-48rj45-4sfp-compact")
        self.assertEqual(factory["profile"], "stock_48rj45_4sfp_compact")
        self.assertEqual(factory["image"]["file"], "faceplates/48rj45-4sfp-compact.png")
        self.assertEqual(factory["ui"]["faceplate"]["file"], "faceplates/48rj45-4sfp-compact.png")
        self.assertEqual(factory["image"]["coordinate_space"], "image-native-v1")
        self.assertEqual((factory["image"]["width"], factory["image"]["height"]), (6000, 900))
        self.assertFalse(factory["stack"]["enabled"])
        self.assertEqual(factory["management"]["switch_ip"], "")
        rendered = render_space_calibration(factory)
        self.assertEqual((rendered["image"]["width"], rendered["image"]["height"]), (2048, 448))

        def compare(expected: object, actual: object, path: str) -> None:
            if isinstance(expected, dict):
                self.assertIsInstance(actual, dict, path)
                for key, value in expected.items():
                    self.assertIn(key, actual, path)
                    compare(value, actual[key], f"{path}.{key}")
            elif isinstance(expected, list):
                self.assertIsInstance(actual, list, path)
                self.assertEqual(len(expected), len(actual), path)
                for index, (left, right) in enumerate(zip(expected, actual)):
                    compare(left, right, f"{path}[{index}]")
            elif isinstance(expected, (int, float)) and not isinstance(expected, bool):
                self.assertAlmostEqual(expected, actual, delta=2e-7, msg=path)
            else:
                self.assertEqual(expected, actual, path)

        for section in ("ports", "sfp", "status_leds", "ui"):
            compare(source[section], rendered[section], section)
        self.assertEqual(factory["sfp"]["SFP1"]["display_name"], "G1")
        self.assertEqual(factory["sfp"]["SFP4"]["display_name"], "G4/TE2")

    def test_original_factory_is_recovered_without_overwriting_compact(self) -> None:
        self.assertEqual(
            sha256(LEGACY_ART),
            "73c6f017a09f91d2979e50cd8c0de5f4763cac521174f527ec99edfbf5523047",
        )
        self.assertEqual(png_dimensions(LEGACY_ART), (6000, 1325))
        original = json.loads(LEGACY_FACTORY.read_text(encoding="utf-8"))
        compact = json.loads(FACTORY.read_text(encoding="utf-8"))
        self.assertEqual(original["profile"], "stock_48rj45_4sfp")
        self.assertEqual(original["image"]["file"], "faceplates/48rj45-4sfp.png")
        self.assertEqual(original["ui"]["faceplate"]["file"], "faceplates/48rj45-4sfp.png")
        self.assertEqual((original["image"]["width"], original["image"]["height"]), (6000, 1325))
        self.assertEqual(set(original["ports"]), {str(i) for i in range(1, 49)})
        self.assertEqual(len(original["sfp"]), 4)
        self.assertNotEqual(original["ports"]["1"]["center"], compact["ports"]["1"]["center"])
        catalog = json.loads((ROOT / "src/faceplates/catalog.json").read_text(encoding="utf-8"))
        entries = {item["filename"]: item["display_name"] for item in catalog["faceplates"]}
        self.assertEqual(entries["48rj45-4sfp.png"], "48 × RJ45 · 4 × SFP")
        self.assertEqual(entries["48rj45-4sfp-compact.png"], "48 × RJ45 · 4 × SFP · Compact")
        release_original = ROOT / "Releases/switch-vision-2.8.24/faceplates/48rj45-4sfp.png"
        self.assertEqual(sha256(LEGACY_ART), sha256(release_original))

    def test_48x4_registry_keeps_compact_default_and_original_optional(self) -> None:
        registry = json.loads((ROOT / "src/devices/supported_devices.json").read_text(encoding="utf-8"))
        models = {
            "WS-C3650-48PD-E", "WS-C3650-48PD-L", "WS-C2960XR-48LPS-I",
            "EX3300-48P", "US 48 PoE 500W", "US 48", "WS-C3750-48P",
            "WS-C3750X-48P", "WS-C3750X-48P-S",
        }
        found = [row for row in registry["devices"] if row["model"] in models]
        self.assertEqual({row["model"] for row in found}, models)
        for row in found:
            with self.subTest(model=row["model"]):
                self.assertEqual(row["default_faceplate"], "faceplates/48rj45-4sfp-compact.png")
                self.assertEqual(row["visuals"]["recommended_faceplate"], "faceplates/48rj45-4sfp-compact.png")
                self.assertIn("faceplates/48rj45-4sfp.png", row["optional_faceplates"])
                self.assertIn("faceplates/48rj45-4sfp.png", row["visuals"]["optional_faceplates"])
                if row["model"].startswith("US 48"):
                    self.assertEqual(row["calibration_profile"], "stock_48rj45_4sfp_compact")

    def test_preexisting_compact_pin_never_renders_replaced_stock_bytes(self) -> None:
        # Prior Core builds used the original filename for compact pixels. A
        # saved SHA must resolve only those exact historical bytes, or remain
        # explicitly unavailable until the Installer's retained copy exists.
        sys.path.insert(0, str(ROOT / "src/custom_components/switch_vision"))
        from faceplate_artwork_history import verified_choice
        original_sha = sha256(LEGACY_ART)
        compact_sha = sha256(ART)
        name = "48rj45-4sfp.png"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "faceplates").mkdir()
            shutil.copy2(LEGACY_ART, root / "faceplates" / name)
            missing = verified_choice(root, name, compact_sha, original_sha)
            self.assertEqual(missing.get("unavailable"), "true")
            self.assertNotIn("path", missing)

            archive = root / "faceplate-history" / compact_sha
            archive.mkdir(parents=True)
            shutil.copy2(ART, archive / name)
            retained = verified_choice(root, name, compact_sha, original_sha)
            self.assertEqual(retained.get("sha256"), compact_sha)
            self.assertEqual(retained.get("current_sha256"), original_sha)
            self.assertEqual(retained.get("path"), f"faceplate-history/{compact_sha}/{name}")

    def test_image_sha_is_bound_to_stock_asset_manifest(self) -> None:
        manifest = json.loads(ASSETS.read_text(encoding="utf-8"))
        self.assertEqual(
            manifest["assets"]["faceplates"]["48rj45-4sfp-compact.png"], EXPECTED_ART_SHA
        )
        self.assertEqual(
            manifest["assets"]["faceplates"]["48rj45-4sfp.png"], sha256(LEGACY_ART)
        )


if __name__ == "__main__":
    unittest.main()

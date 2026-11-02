"""Original and compact 24-port stock artwork must remain independent."""
from pathlib import Path
import hashlib
import json
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
PAIRS = {
    2: (
        "917b638525ba0a6dbed76f7b619a38cf81a6da3c090bd60b3a76aa0006304bcd",
        "f6ca8c07deadb1b3da538f8f5d00566475c7a7d58d3ed6498a80ae01b8445996",
        "7d2783df6be194a0b5aa200e3f13d57d088bfce06b4347131d91b752ac5d42d7",
    ),
    4: (
        "dfc1a7e3ec675e9ce534eb675c8692358e8e122fb09976956fb0858a77760851",
        "7574f1a5a61898b76fdd4dc3bb1fd506d18ad075f5db54c15a0e14413a8bb48f",
        "ccf4c5d056872c617fc5d16a46968f2dfbe6f18c612474418608e86d4ace1a1c",
    ),
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Stock24OriginalCompactIsolationTests(unittest.TestCase):
    def test_old_stock_artwork_and_geometry_remain_byte_identical(self):
        for uplinks, (image_sha, geometry_sha, _) in PAIRS.items():
            slug = f"24rj45-{uplinks}sfp"
            with self.subTest(slug=slug):
                self.assertEqual(sha(SRC / "faceplates" / f"{slug}.png"), image_sha)
                old_path = SRC / "calibration" / f"faceplate-stock-{slug}.json"
                self.assertEqual(sha(old_path), geometry_sha)
                old = json.loads(old_path.read_text())
                self.assertEqual(old["image"]["file"], f"faceplates/{slug}.png")
                self.assertEqual(old["profile"], f"stock_24rj45_{uplinks}sfp")
                self.assertEqual((old["image"]["width"], old["image"]["height"]), (6000, 1325))

    def test_compact_is_separate_and_correctly_bundled(self):
        manifest = json.loads(
            (SRC / "custom_components" / "switch_vision" / "stock-assets.json").read_text()
        )["assets"]["faceplates"]
        catalog = {
            row["filename"]: row["display_name"]
            for row in json.loads((SRC / "faceplates" / "catalog.json").read_text())["faceplates"]
        }
        for uplinks, (original_sha, _, compact_sha) in PAIRS.items():
            slug = f"24rj45-{uplinks}sfp"
            compact = f"{slug}-compact.png"
            with self.subTest(slug=slug):
                self.assertEqual(sha(SRC / "faceplates" / compact), compact_sha)
                self.assertEqual(manifest[f"{slug}.png"], original_sha)
                self.assertEqual(manifest[compact], compact_sha)
                self.assertEqual(catalog[f"{slug}.png"], f"24 × RJ45 · {uplinks} × SFP")
                self.assertEqual(
                    catalog[compact], f"24 × RJ45 · {uplinks} × SFP · Compact"
                )
                g = json.loads(
                    (SRC / "calibration" / f"faceplate-stock-{slug}-compact.json").read_text()
                )
                self.assertEqual(g["profile"], f"stock_24rj45_{uplinks}sfp_compact")
                self.assertEqual(g["image"]["file"], f"faceplates/{compact}")
                self.assertEqual(g["ui"]["faceplate"]["file"], compact)
                self.assertEqual(set(g["ports"]), {str(i) for i in range(1, 25)})
                self.assertEqual(set(g["sfp"]), {f"G{i}" for i in range(1, uplinks + 1)})
                self.assertEqual((g["image"]["width"], g["image"]["height"]), (6000, 750))
                self.assertNotEqual(
                    g["ports"]["1"]["center"],
                    json.loads(
                        (SRC / "calibration" / f"faceplate-stock-{slug}.json").read_text()
                    )["ports"]["1"]["center"],
                )

    def test_recommend_compact_only_for_reviewed_generic_models(self):
        devices = json.loads((SRC / "devices" / "supported_devices.json").read_text())["devices"]
        counts = {2: 0, 4: 0}
        for device in devices:
            for uplinks in (2, 4):
                slug = f"24rj45-{uplinks}sfp"
                expected = f"faceplates/{slug}-compact.png"
                if device.get("default_faceplate") != expected:
                    continue
                with self.subTest(model=device["model"], uplinks=uplinks):
                    self.assertEqual(device["visuals"]["recommended_faceplate"], expected)
                    original = f"faceplates/{slug}.png"
                    self.assertIn(original, device["optional_faceplates"])
                    self.assertIn(original, device["visuals"]["optional_faceplates"])
                    if device["visuals"]["calibration_profile"].startswith("stock_24"):
                        self.assertEqual(
                            device["visuals"]["calibration_profile"],
                            f"stock_24rj45_{uplinks}sfp_compact",
                        )
                    counts[uplinks] += 1
        self.assertEqual(counts, {2: 8, 4: 9})

    def test_both_original_and_compact_calibrations_are_addressable(self):
        text = (SRC / "js" / "switch-vision.js").read_text()
        for uplinks in (2, 4):
            slug = f"24rj45-{uplinks}sfp"
            profile = f"stock_24rj45_{uplinks}sfp"
            self.assertIn(f'{profile}: "{slug}.png"', text)
            self.assertIn(f'{profile}_compact: "{slug}-compact.png"', text)
        self.assertIn("this.factoryCalibrationForCurrentSwitch(", text)
        self.assertIn('await this.resetSavedCalibrations("switch")', text)


if __name__ == "__main__":
    unittest.main()

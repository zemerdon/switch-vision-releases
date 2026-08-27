from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
CARD = ROOT / "src/custom_components/switch_vision/switch-vision-card.js"
MIRROR = ROOT / "src/js/switch-vision.js"

EXPECTED = {
    "48rj45-4sfp.png": "48-Port · 4 × SFP",
    "48rj45-2sfp.png": "48-Port · 2 × SFP",
    "24rj45-4sfp.png": "24-Port · 4 × SFP",
    "24rj45-2sfp.png": "24-Port · 2 × SFP",
    "c3560cg-8pc-s.png": "Cisco Catalyst 3560-C · 8-Port · 2 × SFP",
    "dell-28-rj45-2sfp.png": "Dell N2128PX-ON · 28-Port · 2 × SFP",
    "submarine-48rj45-4sfp.png": "Submarine 48-Port · 4 × SFP",
    "unifi-24p-rj45-2sfp.png": "UniFi 24-Port · 2 × SFP",
    "unifi-24-rj45-2sfp-dark.png": "UniFi 24-Port · 2 × SFP · Dark",
    "unifi-5rj45.png": "UniFi 5-Port",
    "unifi-8rj45.png": "UniFi 8-Port",
}


class CalibrationAssetLabelTests(unittest.TestCase):
    def setUp(self):
        self.card = CARD.read_text(encoding="utf-8")
        self.mirror = MIRROR.read_text(encoding="utf-8")

    def test_shipped_faceplates_have_stable_friendly_labels(self):
        for filename, label in EXPECTED.items():
            needle = f'"{filename}": "{label}"'
            self.assertIn(needle, self.card)
            self.assertIn(needle, self.mirror)

    def test_mirrored_card_sources_remain_byte_identical(self):
        self.assertEqual(CARD.read_bytes(), MIRROR.read_bytes())

    def test_option_value_remains_original_filename(self):
        needle = 'rows.push(option(file, assetDisplayLabel(kind, file)));'
        self.assertIn(needle, self.card)
        self.assertIn(needle, self.mirror)

    def test_custom_asset_fallback_remains_available(self):
        for needle in (
            '.replace(/\\.[^.]+$/, "")',
            '.replace(/[-_]+/g, " ")',
            '.replace(/\\b\\w/g, (char) => char.toUpperCase())',
        ):
            self.assertIn(needle, self.card)
            self.assertIn(needle, self.mirror)


if __name__ == "__main__":
    unittest.main()

"""Exact switch-only, explicitly approved stock faceplate + Calibration reset."""
from __future__ import annotations
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src/custom_components/switch_vision"))
from stock_artwork_selection import apply_approved_switch_artwork


def revision(image: str, ver: str) -> dict:
    return {"filename": image, "sha256": "a" * 64, "geometry_sha256": "b" * 64,
            "version": ver}


class StockArtworkSelectionTests(unittest.TestCase):
    def test_exact_switch_reset_does_not_touch_neighbors_or_other_scopes(self):
        old = {"ports": {"1": {"center": [88, 23]}}, "custom": True}
        neighbor = {"ports": {"1": {"center": [16, 28]}}}
        data = {"profiles": {
            "native_SW3": old,
            "native_SW3__faceplate__manual": {"ui": {"faceplate": "manual.png"}},
            "native_SW30": neighbor,
            "custom_SW3": {"custom": True},
        }, "active_profiles": {
            "native_SW3": "native_SW3__faceplate__manual",
            "native_SW30": "native_SW30__faceplate__manual",
        }, "stock_artwork_choices": {
            "native_SW3": {"filename": "generic.png", "sha256": "c" * 64},
            "native_SW30": {"filename": "generic.png", "sha256": "d" * 64},
        }}
        removed = apply_approved_switch_artwork(data, "native_SW3", "generic.png",
                                                 "dedicated.png", revision("dedicated.png", "sha-v2"))
        self.assertEqual(set(removed), {"native_SW3", "native_SW3__faceplate__manual"})
        self.assertNotIn("native_SW3", data["profiles"])
        self.assertNotIn("native_SW3", data["active_profiles"])
        self.assertIs(data["profiles"]["native_SW30"], neighbor)
        self.assertEqual(data["profiles"]["custom_SW3"], {"custom": True})
        self.assertEqual(data["active_profiles"]["native_SW30"], "native_SW30__faceplate__manual")
        self.assertEqual(data["stock_artwork_choices"]["native_SW30"]["sha256"], "d" * 64)
        pin = data["stock_artwork_choices"]["native_SW3"]
        self.assertEqual(pin["eligible_faceplates"], ["generic.png", "dedicated.png"])
        self.assertEqual(pin["geometry_sha256"], "b" * 64)

        # Going back to a previously accepted generic stock never loses
        # the newer dedicated option from this particular switch's picker.
        apply_approved_switch_artwork(
            data, "native_SW3", "dedicated.png", "generic.png",
            revision("generic.png", "sha-v1"),
        )
        self.assertEqual(data["stock_artwork_choices"]["native_SW3"]["eligible_faceplates"],
                         ["dedicated.png", "generic.png"])

    def test_invalid_or_stale_input_never_resets_anything(self):
        for base, name, former in [
            ("native_SW30", "dedicated.png", "generic.png"),
            ("native_SW3__faceplate__evil", "dedicated.png", "generic.png"),
            ("native_SW3", "../dedicated.png", "generic.png"),
            ("native_SW3", "dedicated.png", "other.png"),
        ]:
            with self.subTest(base=base, name=name, former=former):
                data = {"profiles": {"native_SW3": {"custom": 1}},
                        "active_profiles": {"native_SW3": "selected"},
                        "stock_artwork_choices": {
                            "native_SW3": {"filename": "generic.png", "sha256": "a" * 64}}}
                with self.assertRaises(ValueError):
                    apply_approved_switch_artwork(data, base, former, name,
                                                  revision("dedicated.png", "sha-v2"))
                self.assertEqual(data["profiles"]["native_SW3"], {"custom": 1})
                self.assertEqual(data["stock_artwork_choices"]["native_SW3"]["filename"], "generic.png")

if __name__ == "__main__":
    unittest.main()

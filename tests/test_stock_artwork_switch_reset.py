"""Exact switch-only, explicitly approved stock faceplate + Calibration reset."""
from __future__ import annotations
import sys
from copy import deepcopy
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src/custom_components/switch_vision"))
from stock_artwork_selection import (apply_approved_switch_artwork,
                                     expected_artwork_choice_matches,
                                     rebase_after_confirmed_factory_reset)


def revision(image: str, ver: str) -> dict:
    return {"filename": image, "sha256": "a" * 64, "geometry_sha256": "b" * 64,
            "version": ver, "geometry": {
                "schema": "switch-vision-interactive-calibration-v1",
                "profile": "stock_48rj45_4sfp",
                "image": {"file": "faceplates/" + image, "width": 6000, "height": 900},
                "ports": {"1": {"center": [123, 456]}},
                "sfp": {"SFP1": {"center": [789, 456]}},
                "status_leds": {"SYSTEM": [400, 40]},
                "ui": {"faceplate": {"file": image, "source": "custom", "show": True}},
            }}


def validate_factory(base: str, calibration: dict) -> dict:
    """Represent Core's required full validation callback in isolated tests."""
    if (calibration.get("profile_name") != base
            or not isinstance(calibration.get("status_leds"), dict)):
        raise ValueError("Invalid factory Calibration: status_leds required")
    return calibration


class StockArtworkSelectionTests(unittest.TestCase):
    def test_legacy_sha_pin_accepts_verified_display_version_but_keeps_stale_guards(self):
        """Regression: a 3850 pin predating versioned art must upgrade."""
        original = "eba68a052bc0baff1a5af583eb869895e30c93a51d3836bc763baee1025eacde"
        pinned = {"filename": "cisco-3850-12xs.png", "sha256": original,
                  "eligible_faceplates": ["cisco-3850-12xs.png"]}
        historical_display_version = "sha-a2834c0fffb3"
        self.assertTrue(expected_artwork_choice_matches(
            pinned, "cisco-3850-12xs.png", original, historical_display_version))
        self.assertFalse(expected_artwork_choice_matches(
            pinned, "cisco-3850-12xs.png", "0" * 64, historical_display_version))
        self.assertFalse(expected_artwork_choice_matches(
            pinned, "some-other-switch.png", original, historical_display_version))
        self.assertFalse(expected_artwork_choice_matches(
            None, "cisco-3850-12xs.png", original, historical_display_version))
        # Once a switch has an explicitly selected revision, its version is
        # authoritative; changed geometry with identical pixels is not stale-safe.
        chosen = {**pinned, "version": "sha-exact-approved", "geometry_sha256": "a" * 64}
        self.assertTrue(expected_artwork_choice_matches(
            chosen, "cisco-3850-12xs.png", original, "sha-exact-approved"))
        self.assertFalse(expected_artwork_choice_matches(
            chosen, "cisco-3850-12xs.png", original, "sha-another-revision"))

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
                                                 "dedicated.png", revision("dedicated.png", "sha-v2"), validate_factory)
        self.assertEqual(set(removed), {"native_SW3", "native_SW3__faceplate__manual"})
        # The approved geometry is durable even with no Native card mounted.
        approved = data["profiles"]["native_SW3"]
        self.assertEqual(approved["ports"]["1"]["center"], [123, 456])
        self.assertEqual(approved["sfp"]["SFP1"]["center"], [789, 456])
        self.assertEqual(approved["image"]["file"], "faceplates/dedicated.png")
        self.assertEqual(approved["ui"]["faceplate"]["file"], "__default__")
        self.assertEqual(approved["ui"]["faceplate"]["source"], "default")
        self.assertEqual(approved["stock_faceplate_sha256"], "a" * 64)
        self.assertEqual(approved["profile_name"], "native_SW3")
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
            revision("generic.png", "sha-v1"), validate_factory,
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
                                                  revision("dedicated.png", "sha-v2"), validate_factory)
                self.assertEqual(data["profiles"]["native_SW3"], {"custom": 1})
                self.assertEqual(data["stock_artwork_choices"]["native_SW3"]["filename"], "generic.png")

    def test_missing_verified_factory_fails_without_mutating_calibration(self):
        state = {
            "profiles": {"native_SW3": {"owner": "unchanged"}},
            "stock_artwork_choices": {
                "native_SW3": {"filename": "generic.png", "sha256": "c" * 64},
            },
        }
        unpaired = revision("dedicated.png", "sha-v2")
        unpaired.pop("geometry")
        with self.assertRaisesRegex(ValueError, "factory geometry"):
            apply_approved_switch_artwork(
                state, "native_SW3", "generic.png", "dedicated.png", unpaired,
                validate_factory,
            )
        self.assertEqual(state["profiles"]["native_SW3"], {"owner": "unchanged"})
        self.assertEqual(state["stock_artwork_choices"]["native_SW3"]["sha256"], "c" * 64)

    def test_incomplete_sha_verified_geometry_fails_before_any_switch_change(self):
        """Verified bytes without a required field are not a usable factory."""
        state = {
            "profiles": {"native_SW3": {"saved": "user-custom-layout"}},
            "active_profiles": {"native_SW3": "native_SW3__faceplate__old"},
            "stock_artwork_choices": {"native_SW3": {
                "filename": "generic.png", "sha256": "c" * 64,
            }},
        }
        before = deepcopy(state)
        incomplete = revision("dedicated.png", "sha-v2")
        incomplete["geometry"].pop("status_leds")
        with self.assertRaisesRegex(ValueError, "status_leds required"):
            apply_approved_switch_artwork(
                state, "native_SW3", "generic.png", "dedicated.png",
                incomplete, validate_factory,
            )
        self.assertEqual(state, before)

    def test_confirmed_switch_factory_reset_rebases_only_one_sha(self):
        latest = {"3850.png": {
            "filename": "3850.png", "sha256": "a" * 64,
            "geometry_sha256": "b" * 64, "version": "sha-" + "c" * 20,
            "path": "faceplates/3850.png",
        }}
        state = {"stock_artwork_choices": {
            "native_SW2": {"filename": "3850.png", "sha256": "d" * 64},
            "custom_SW2": {"filename": "3850.png", "sha256": "e" * 64},
            "native_SW3": {"filename": "3850.png", "sha256": "f" * 64},
        }, "profiles": {"native_SW2": {"user": True}}}
        changed = rebase_after_confirmed_factory_reset(
            state, "switch", "native_SW2", "", latest, "3850.png"
        )
        self.assertEqual(changed, ["native_SW2"])
        self.assertEqual(state["stock_artwork_choices"]["native_SW2"]["sha256"], "a" * 64)
        self.assertEqual(state["stock_artwork_choices"]["native_SW2"]["geometry_sha256"], "b" * 64)
        self.assertEqual(state["stock_artwork_choices"]["custom_SW2"]["sha256"], "e" * 64)
        self.assertEqual(state["stock_artwork_choices"]["native_SW3"]["sha256"], "f" * 64)
        self.assertEqual(state["profiles"]["native_SW2"], {"user": True})

    def test_namespace_rebases_only_matching_pins(self):
        latest = {"3850.png": {"filename": "3850.png", "sha256": "a" * 64,
            "geometry_sha256": "b" * 64, "version": "sha-" + "c" * 20,
            "path": "faceplates/3850.png"}}
        state = {"stock_artwork_choices": {
            "native_SW2": {"filename": "3850.png", "sha256": "d" * 64},
            "native_SW3": {"filename": "3850.png", "sha256": "e" * 64},
            "custom_SW2": {"filename": "3850.png", "sha256": "f" * 64},
        }}
        changed = rebase_after_confirmed_factory_reset(
            state, "namespace", "", "native_", latest
        )
        self.assertEqual(changed, ["native_SW2", "native_SW3"])
        self.assertEqual(state["stock_artwork_choices"]["native_SW3"]["sha256"], "a" * 64)
        self.assertEqual(state["stock_artwork_choices"]["custom_SW2"]["sha256"], "f" * 64)

    def test_missing_verified_latest_fails_without_mutating_any_pin(self):
        state = {"stock_artwork_choices": {
            "native_SW2": {"filename": "3850.png", "sha256": "d" * 64},
            "native_SW3": {"filename": "missing.png", "sha256": "e" * 64},
        }}
        before = {name: dict(value) for name, value in state["stock_artwork_choices"].items()}
        latest = {"3850.png": {"filename": "3850.png", "sha256": "a" * 64,
            "geometry_sha256": "b" * 64, "version": "sha-" + "c" * 20,
            "path": "faceplates/3850.png"}}
        with self.assertRaises(ValueError):
            rebase_after_confirmed_factory_reset(state, "namespace", "", "native_", latest)
        self.assertEqual(state["stock_artwork_choices"], before)

if __name__ == "__main__":
    unittest.main()

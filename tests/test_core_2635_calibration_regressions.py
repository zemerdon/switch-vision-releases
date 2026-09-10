from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.faceplate_native_canvas import render_space_calibration
CARD = ROOT / "src" / "js" / "switch-vision.js"
MIRROR = ROOT / "src" / "custom_components" / "switch_vision" / "switch-vision-card.js"
CATALOG = ROOT / "src" / "faceplates" / "catalog.json"
PROFILE = ROOT / "src" / "calibration" / "faceplate-cisco-3850-12xs.json"
FACEPLATE = ROOT / "src" / "faceplates" / "cisco-3850-12xs.png"
NATIVE = ROOT / "src" / "faceplate_native_canvas.py"
REGISTRY = ROOT / "src" / "devices" / "supported_devices.json"

STABLE_HELPER = 'function stableCalibrationJson(value) {\n  const normalise = (item) => {\n    if (Array.isArray(item)) return item.map(normalise);\n    if (item && typeof item === "object") {\n      const sorted = {};\n      for (const key of Object.keys(item).sort()) sorted[key] = normalise(item[key]);\n      return sorted;\n    }\n    if (typeof item === "number" && Object.is(item, -0)) return 0;\n    return item;\n  };\n  return JSON.stringify(normalise(value));\n}\n'


class Core2635CalibrationRegressionTests(unittest.TestCase):
    def setUp(self):
        self.card = CARD.read_text(encoding="utf-8")

    def test_card_sources_remain_mirrored(self):
        self.assertEqual(CARD.read_bytes(), MIRROR.read_bytes())

    def test_3850_faceplate_catalog_and_geometry(self):
        catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
        labels = {row["filename"]: row["display_name"] for row in catalog["faceplates"]}
        self.assertEqual(
            labels["cisco-3850-12xs.png"],
            "Cisco Catalyst 3850 12XS · 12 × SFP",
        )
        self.assertNotIn("Cisco Catalyst 3850-12XS · 12 × SFP", labels.values())
        profile = json.loads(PROFILE.read_text(encoding="utf-8"))
        self.assertEqual(profile["model"], "cisco-3850-12xs")
        self.assertEqual(profile["profile"], "cisco_3850_12xs")
        self.assertEqual(profile["image"]["file"], "faceplates/cisco-3850-12xs.png")
        self.assertEqual(profile["image"]["coordinate_space"], "image-native-v1")
        self.assertEqual((profile["image"]["width"], profile["image"]["height"]), (2680, 356))
        render = render_space_calibration(profile)
        self.assertEqual((render["image"]["width"], render["image"]["height"]), (2048, 448))
        self.assertEqual(render["ports"], {})
        self.assertEqual(list(render["sfp"]), [f"SFP{n}" for n in range(1, 13)])
        self.assertEqual(len(render["status_leds"]), 7)
        self.assertTrue(all(item.get("supported_speed", "") == "" for item in render["sfp"].values()))
        self.assertEqual(render["sfp"]["SFP1"]["center"], [295, 306])
        self.assertEqual(render["sfp"]["SFP7"]["center"], [1079, 306])
        self.assertEqual(render["sfp"]["SFP12"]["center"], [1722, 306])
        self.assertEqual(render["sfp"]["SFP1"]["hitbox"], [99, 58])
        self.assertEqual(render["sfp"]["SFP12"]["led_right_size"], [30, 15])
        # The owner-supplied Geometry v2 presentation is authoritative for this
        # exact faceplate factory; only faceplate artwork identity is supplied by Core.
        self.assertFalse(render["ui"]["logo"]["show"])
        self.assertEqual(render["ui"]["logo"]["y"], 0)
        self.assertEqual(render["ui"]["status_panel"]["x"], -337)
        self.assertEqual(render["ui"]["status_panel"]["y"], 237)
        self.assertFalse(render["ui"]["status_panel_2"]["show"])
        self.assertEqual(render["ui"]["status_panel_2"]["x"], 0)
        self.assertEqual(render["ui"]["status_leds"]["hidden"], ["STAT", "SYST", "DUPLX", "ACTV", "SPEED", "STACK", "PoE"])
        self.assertFalse(render["ui"]["show_link_leds"])
        self.assertTrue(render["ui"]["show_activity_leds"])
        self.assertEqual(render["ui"]["calibration_button"]["x"], 1888)
        self.assertEqual(render["ui"]["calibration_button"]["y"], 14)
        self.assertEqual(render["ui"]["test_mode_button"]["x"], 1888)
        self.assertEqual(render["ui"]["test_mode_button"]["y"], 58)

    def test_3850_png_dimensions(self):
        raw = FACEPLATE.read_bytes()[:24]
        self.assertEqual(raw[:8], b"\x89PNG\r\n\x1a\n")
        self.assertEqual(raw[12:16], b"IHDR")
        self.assertEqual(
            (int.from_bytes(raw[16:20], "big"), int.from_bytes(raw[20:24], "big")),
            (2680, 356),
        )

    def test_3850_exact_model_uses_existing_faceplate_and_profile(self):
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        models = {str(row.get("model") or ""): row for row in registry.get("devices", [])}
        self.assertNotIn("WS-C3850-12XS", models)
        self.assertNotIn("WS-C3850-12XS-S", models)
        exact = models["WS-C3850-12XS-E"]
        self.assertEqual(exact["status"], "experimental")
        self.assertEqual(exact["ports"]["rj45"], 0)
        self.assertEqual(exact["ports"]["uplinks"], 12)
        self.assertEqual(exact["default_faceplate"], "faceplates/cisco-3850-12xs.png")
        self.assertEqual(exact["calibration_profile"], "cisco_3850_12xs")
        self.assertEqual(exact["visuals"]["recommended_faceplate"], "faceplates/cisco-3850-12xs.png")
        self.assertEqual(exact["visuals"]["calibration_profile"], "cisco_3850_12xs")
        self.assertEqual(exact["visuals"]["canvas"], {"width": 2048, "height": 448})

    def test_dirty_state_is_baseline_difference_not_touch_flag(self):
        for marker in (
            "function stableCalibrationJson(value)",
            "function calibrationPersistedFingerprint(cal)",
            "captureCalibrationBaseline(cal = null)",
            "refreshCalibrationDirtyState(cal = null)",
            "this._calibrationDirty = calibrationPersistedFingerprint(current) !== this._calibrationBaselineFingerprint;",
            "button.disabled = !dirty;",
            'data-cv-dirty-dot',
            'data-cv-dirty-label',
            'dirtyAuditRoot.addEventListener(eventName',
        ):
            self.assertIn(marker, self.card)
        self.assertNotIn(
            "markCalibrationDirty() {\n    this._calibrationDirty = true;\n  }",
            self.card,
        )
        self.assertIn("const originalBaselineFingerprint = this._calibrationBaselineFingerprint;", self.card)
        self.assertIn("this._calibrationBaselineFingerprint = originalBaselineFingerprint;", self.card)

    def test_stable_fingerprint_change_and_revert_contract(self):
        self.assertIn(STABLE_HELPER.strip(), self.card)
        harness = STABLE_HELPER + """
const base = stableCalibrationJson({ui:{show:false,leds:false}, ports:{b:[2,1],a:[1,2]}});
const changed = stableCalibrationJson({ports:{a:[1,2],b:[2,1]},ui:{show:true,leds:false}});
const changedTwo = stableCalibrationJson({ports:{a:[1,2],b:[2,1]},ui:{show:true,leds:true}});
const revertedOne = stableCalibrationJson({ports:{a:[1,2],b:[2,1]},ui:{show:false,leds:true}});
const reverted = stableCalibrationJson({ports:{b:[2,1],a:[1,2]},ui:{show:false,leds:false}});
if (base === changed) throw new Error("changed state compared equal");
if (base === changedTwo) throw new Error("multi-change state compared equal");
if (base === revertedOne) throw new Error("partial revert incorrectly compared clean");
if (base !== reverted) throw new Error("full revert did not compare clean");
"""
        result = subprocess.run(["node", "-e", harness], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_target_selection_survives_repeated_set_config(self):
        required = (
            "function calibrationEnabled(config = {})",
            "const SV_CALIBRATION_TRANSIENT_CONFIG_KEYS = Object.freeze([",
            "function calibrationTransientEditorState(config)",
            "const calibrationEditorState = calibrationControlsEnabled(this.config)",
            "if (calibrationEditorState) Object.assign(this.config, calibrationEditorState);",
            '"calibration_target"',
            '"calibration_part"',
            '"calibration_step"',
            '"calibration_port_selection"',
            '"calibration_sfp_selection"',
            '"selected_interface"',
            '"selected_port"',
        )
        for marker in required:
            self.assertIn(marker, self.card)
        set_start = self.card.index("  setConfig(config) {")
        set_end = self.card.index("\n  set hass(", set_start)
        set_config = self.card[set_start:set_end]
        self.assertLess(set_config.index("const calibrationEditorState"), set_config.index("this.config = {"))
        self.assertGreater(
            set_config.index("Object.assign(this.config, calibrationEditorState)"),
            set_config.index("this.config = {"),
        )

    def test_target_selection_is_not_persisted_profile_state(self):
        start = self.card.index("function calibrationExportData(cal) {")
        end = self.card.index("\n}\n", start) + 2
        export_block = self.card[start:end]
        for transient in (
            "calibration_target",
            "calibration_part",
            "calibration_step",
            "calibration_port_selection",
            "calibration_sfp_selection",
            "calibration_test_mode",
        ):
            self.assertNotIn(transient, export_block)

    def test_test_mode_button_target_is_position_only(self):
        self.assertIn('"test_mode_button", "Test Mode button"', self.card)
        self.assertIn('if (type === "test_mode_button") return option("box", "Position (X/Y or arrows)");', self.card)
        self.assertIn('editable.type === "calibration_button" || editable.type === "test_mode_button"', self.card)
        self.assertIn('"TEST MODE BUTTON"', self.card)
        self.assertIn('testButtonActive', self.card)
        self.assertIn('const workingUi = uiFromCalibration(calibrationRenderSpaceData(this.calibrationData()));', self.card)
        self.assertIn('const ui = workingUi.calibration_button || {};', self.card)
        self.assertIn('const testModeUi = workingUi.test_mode_button || {};', self.card)
        self.assertNotIn('const testModeUi = ui.test_mode_button || {};', self.card)
        self.assertNotIn('calibration.ui?.test_mode_button', self.card)

        coordinate_start = self.card.index("function calibrationCoordinatePoints(")
        coordinate_end = self.card.index("\nfunction commonCalibrationCoordinate", coordinate_start)
        self.assertIn('"test_mode_button"', self.card[coordinate_start:coordinate_end])

        size_start = self.card.index("function calibrationSizePairs(")
        size_end = self.card.index("\nfunction nextCalibrationPortNumber", size_start)
        self.assertNotIn('"test_mode_button"', self.card[size_start:size_end])

        direct_start = self.card.index("  setCalibrationTargetCoordinates(")
        direct_end = self.card.index("\n  setCalibrationTargetSize(", direct_start)
        self.assertIn('"test_mode_button"', self.card[direct_start:direct_end])

        editable_start = self.card.index('  if (type === "test_mode_button") {')
        editable_end = self.card.index("\n  if (type === \"status_box\")", editable_start)
        self.assertIn("hitbox: null", self.card[editable_start:editable_end])

        # Selection overlay is visual only. Port/SFP click hitboxes remain the only
        # SVG pointer selection path; no draggable Test Mode target is introduced.
        selection_start = self.card.index("  attachSelectionHandlers(svg")
        selection_end = self.card.index("\n}\n\n// Expose the renderer version", selection_start)
        selection = self.card[selection_start:selection_end]
        self.assertNotIn('addHitbox("test_mode_button"', selection)
        self.assertNotIn('draggable', selection)

    def test_native_canvas_normalizes_test_mode_button(self):
        native = NATIVE.read_text(encoding="utf-8")
        self.assertIn(
            '("logo", "calibration_button", "test_mode_button", "status_panel", "status_panel_2")',
            native,
        )

    def test_default_recommended_label_contract_is_preserved(self):
        self.assertIn(
            '${htmlEscape(this.config.switch_model || this.config.model || layout.model_text?.text || "Switch model")} (Default / recommended)',
            self.card,
        )


if __name__ == "__main__":
    unittest.main()

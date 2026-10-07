from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.faceplate_native_canvas import render_space_calibration

CARD = ROOT / "src" / "js" / "switch-vision.js"
REGISTRY = ROOT / "src" / "devices" / "supported_devices.yaml"
PROFILE = ROOT / "src" / "calibration" / "faceplate-dell-4032f.json"
FACEPLATE = ROOT / "src" / "faceplates" / "dell-4032f.png"
GEOMETRY_ORACLE = ROOT / "tests" / "fixtures" / "dell-n4032f-geometry.json"


def extract_js_function(source: str, signature: str) -> str:
    start = source.find(signature)
    if start < 0:
        raise AssertionError(f"JavaScript function not found: {signature}")
    brace = source.find("{", start)
    depth = 0
    quote = None
    escape = False
    for pos in range(brace, len(source)):
        char = source[pos]
        if quote is not None:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == quote:
                quote = None
            continue
        if char in {"'", '"', chr(96)}:
            quote = char
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return source[start : pos + 1]
    raise AssertionError(f"Closing brace not found for {signature}")


class DellN4032FFaceplateBindingTests(unittest.TestCase):
    def test_registry_binds_exact_model_to_reviewed_optical_faceplate(self) -> None:
        data = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
        row = next(item for item in data["devices"] if item["model"] == "N4032F")
        self.assertEqual(row["status"], "experimental")
        self.assertTrue(row["dashboard_support"])
        self.assertEqual(row["ports"]["uplinks"], 24)
        self.assertEqual(row["default_faceplate"], "faceplates/dell-4032f.png")
        self.assertEqual(row["calibration_profile"], "dell_n4032f")

    def test_owner_geometry_round_trips_exactly(self) -> None:
        profile = json.loads(PROFILE.read_text(encoding="utf-8"))
        oracle = json.loads(GEOMETRY_ORACLE.read_text(encoding="utf-8"))
        self.assertEqual(profile["model"], "dell-n4032f")
        self.assertEqual(profile["profile"], "dell_n4032f")
        self.assertEqual(profile["image"]["file"], "faceplates/dell-4032f.png")
        self.assertEqual(profile["image"]["coordinate_space"], "image-native-v1")
        self.assertEqual((profile["image"]["width"], profile["image"]["height"]), (1935, 262))
        render = render_space_calibration(profile)
        expected = json.loads(json.dumps(oracle))
        expected["image"].pop("coordinate_space", None)

        def assert_subset(actual, wanted, where="root"):
            if isinstance(wanted, dict):
                self.assertIsInstance(actual, dict, where)
                for key, value in wanted.items():
                    self.assertIn(key, actual, where)
                    assert_subset(actual[key], value, f"{where}.{key}")
            elif isinstance(wanted, list):
                self.assertIsInstance(actual, list, where)
                self.assertEqual(len(actual), len(wanted), where)
                for index, value in enumerate(wanted):
                    assert_subset(actual[index], value, f"{where}[{index}]")
            else:
                if isinstance(wanted, (int, float)) and isinstance(actual, (int, float)):
                    self.assertAlmostEqual(float(actual), float(wanted), places=8, msg=where)
                else:
                    self.assertEqual(actual, wanted, where)

        assert_subset(render, expected)
        self.assertEqual(list(render["sfp"]), [f"SFP{n}" for n in range(1, 27)])

    def test_faceplate_png_and_header_report_real_native_resolution(self) -> None:
        raw = FACEPLATE.read_bytes()[:24]
        self.assertEqual(raw[:8], bytes.fromhex("89504e470d0a1a0a"))
        self.assertEqual(raw[12:16], b"IHDR")
        self.assertEqual(
            (int.from_bytes(raw[16:20], "big"), int.from_bytes(raw[20:24], "big")),
            (1935, 262),
        )
        source = CARD.read_text(encoding="utf-8")
        self.assertIn("data-cv-native-resolution", source)
        self.assertIn("faceplateImage.naturalWidth", source)
        self.assertIn("native ${w} × ${h}", source)
        self.assertNotIn("native 2048 × 448", source)

    def test_native_projection_matches_legacy_runtime_mapping(self) -> None:
        profile = json.loads(PROFILE.read_text(encoding="utf-8"))
        render = render_space_calibration(profile)
        native_width = float(profile["image"]["width"])
        native_height = float(profile["image"]["height"])
        viewport_width = 1360.0
        viewport_height = viewport_width * native_height / native_width
        svg_scale = min(viewport_width / 2048.0, viewport_height / 448.0)
        svg_offset_x = (viewport_width - (2048.0 * svg_scale)) / 2.0
        svg_offset_y = (viewport_height - (448.0 * svg_scale)) / 2.0
        image_scale = viewport_width / native_width

        for key in ("SFP1", "SFP2", "SFP12", "SFP13", "SFP24", "SFP25", "SFP26"):
            native = profile["sfp"][key]["center"]
            logical = render["sfp"][key]["center"]
            svg_screen = (
                svg_offset_x + float(logical[0]) * svg_scale,
                svg_offset_y + float(logical[1]) * svg_scale,
            )
            image_screen = (
                float(native[0]) * image_scale,
                float(native[1]) * image_scale,
            )
            self.assertAlmostEqual(svg_screen[0], image_screen[0], places=7, msg=key)
            self.assertAlmostEqual(svg_screen[1], image_screen[1], places=7, msg=key)

        source = CARD.read_text(encoding="utf-8")
        css = (ROOT / "src" / "css" / "switch-vision.css").read_text(encoding="utf-8")
        self.assertIn('preserveAspectRatio="xMidYMid meet"', source)
        self.assertIn(".cv-image{position:relative;z-index:1;display:block;width:100%;height:auto", css)
        self.assertNotIn("aspect-ratio:2048/448", css)

    def test_qsfp_module_slots_resolve_to_real_40g_entities(self) -> None:
        source = CARD.read_text(encoding="utf-8")
        canonical_helper = extract_js_function(
            source, "function n4032QsfpEntity(config, port, suffix)"
        )
        legacy_helper = extract_js_function(
            source, "function n4032RearQsfpEntity(config, port, suffix)"
        )
        status = extract_js_function(
            source, "function sfpStatusEntities(config, member, port)"
        )
        harness = f"""
function normalizeEntityPrefix(config) {{ return 'n4032'; }}
{canonical_helper}
{legacy_helper}
{status}
const config = {{switch_model:'N4032F'}};
const p25 = sfpStatusEntities(config, 'N4032', 25);
const p26 = sfpStatusEntities(config, 'N4032', 26);
if (p25[0] !== 'sensor.n4032_qsfp_40g_1_status') throw new Error(p25[0]);
if (p25[1] !== 'sensor.n4032_rear_qsfp_40g_1_status') throw new Error(p25[1]);
if (p26[0] !== 'sensor.n4032_qsfp_40g_2_status') throw new Error(p26[0]);
if (p26[1] !== 'sensor.n4032_rear_qsfp_40g_2_status') throw new Error(p26[1]);
if (n4032QsfpEntity(config, 24, 'status') !== null) throw new Error('front port remapped');
if (n4032RearQsfpEntity(config, 24, 'status') !== null) throw new Error('legacy front port remapped');
"""
        result = subprocess.run(
            ["node", "-e", harness],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        byte_fn = extract_js_function(source, "function sfpByteEntities(config, port, direction)")
        speed_fn = extract_js_function(source, "function sfpSpeedMbps(hass, config, port)")
        self.assertIn("n4032QsfpEntity", byte_fn)
        self.assertIn("n4032RearQsfpEntity", byte_fn)
        self.assertIn("n4032QsfpEntity", speed_fn)
        self.assertIn("n4032RearQsfpEntity", speed_fn)
        self.assertIn('"speed_mbps"', speed_fn)
        self.assertIn('"speed_bps"', speed_fn)


if __name__ == "__main__":
    unittest.main()

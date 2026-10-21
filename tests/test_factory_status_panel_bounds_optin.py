from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILD_PATH = ROOT / "build.py"
DELL_PROFILE = ROOT / "src" / "calibration" / "faceplate-dell-28-rj45-2sfp.json"


def load_build_module():
    spec = importlib.util.spec_from_file_location("switch_vision_build", BUILD_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load build.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def synthetic_profile(*, allow_out_of_bounds_rows: bool) -> dict:
    panel = {
        "show": True,
        "x": 0,
        "y": 0,
        "width": 200,
        "height": 60,
        "font_size": 30,
        "field_order": {
            "switch": [
                "model",
                "ip",
                "cpu",
                "temp",
                "poe",
                "uptime",
                "vendor",
                "os",
                "firmware",
                "serial",
                "stack",
                "fans",
                "psu",
            ],
            "port": [],
            "sfp": [],
        },
        "hidden_fields": {
            "switch": [
                "cpu",
                "temp",
                "poe",
                "uptime",
                "vendor",
                "os",
                "firmware",
                "serial",
                "stack",
                "fans",
                "psu",
            ],
            "port": [],
            "sfp": [],
        },
        "fields": {
            "row1_key": [19, 39],
            "row1_value": [107, 39],
            "row2_key": [19, 58],
            "row2_value": [107, 58],
        },
    }
    if allow_out_of_bounds_rows:
        panel["allow_out_of_bounds_rows"] = True
    return {
        "ui": {
            "status_panel": panel,
            "status_panel_2": {"show": False},
        }
    }


class FactoryStatusPanelBoundsOptInTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.build = load_build_module()

    def validate(self, profile: dict) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            calibration = root / "src" / "calibration"
            calibration.mkdir(parents=True)
            (calibration / "faceplate-test.json").write_text(
                json.dumps(profile, indent=2) + "\n",
                encoding="utf-8",
            )
            self.build.validate_factory_status_panel_bounds(root, source_layout=True)

    def test_out_of_bounds_rows_remain_strict_without_explicit_opt_in(self) -> None:
        with self.assertRaises(SystemExit) as caught:
            self.validate(synthetic_profile(allow_out_of_bounds_rows=False))
        self.assertIn("renders outside panel", str(caught.exception))

    def test_explicit_factory_opt_in_accepts_runtime_suppressed_rows(self) -> None:
        self.validate(synthetic_profile(allow_out_of_bounds_rows=True))

    def test_only_reviewed_original_geometry_cases_have_factory_opt_in(self) -> None:
        dell = json.loads(DELL_PROFILE.read_text(encoding="utf-8"))
        self.assertIs(
            ((dell.get("ui") or {}).get("status_panel") or {}).get("allow_out_of_bounds_rows"),
            True,
        )
        # The exact owner-supplied Cisco geometry has a sixth visible row below
        # the owner's own 121px panel. Respect the original dimensions rather
        # than manufacturing a larger panel or moving the row.
        cisco = ROOT / "src" / "calibration" / "faceplate-c3560cg-8pc-s-compact.json"
        export = ROOT / "src" / "calibration" / "geometry-c3560cg-8pc-s-compact.json"
        supplied = json.loads(export.read_text(encoding="utf-8"))["geometry"]
        native = json.loads(cisco.read_text(encoding="utf-8"))
        rendered = self.build.render_space_calibration(native)
        self.assertEqual(native["profile"], "cisco_3560cg_8pc_compact")
        self.assertTrue(native["ui"]["status_panel"]["allow_out_of_bounds_rows"])
        self.assertAlmostEqual(
            rendered["ui"]["status_panel"]["height"],
            supplied["ui"]["status_panel"]["height"],
            delta=2e-7,
        )
        self.assertAlmostEqual(
            rendered["ui"]["status_panel"]["fields"]["row6_key"][1],
            supplied["ui"]["status_panel"]["fields"]["row6_key"][1],
            delta=2e-7,
        )
        opted_in = []
        for path in sorted((ROOT / "src" / "calibration").glob("faceplate-*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            panel = ((data.get("ui") or {}).get("status_panel") or {})
            if panel.get("allow_out_of_bounds_rows") is True:
                opted_in.append(path.name)
        self.assertEqual(
            opted_in,
            ["faceplate-c3560cg-8pc-s-compact.json", "faceplate-dell-28-rj45-2sfp.json"],
        )


if __name__ == "__main__":
    unittest.main()

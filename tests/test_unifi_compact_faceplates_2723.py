from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from faceplate_native_canvas import png_dimensions, render_space_calibration
REGISTRY = SRC / "devices" / "supported_devices.json"
CALIBRATION = SRC / "calibration"
FACEPLATES = SRC / "faceplates"

FACEPLATE_CONTRACTS = {
    "unifi-16rj45-2sfp.png": {
        "profile": "unifi_16_rj45_2sfp",
        "calibration": "faceplate-unifi-16rj45-2sfp.json",
        "ports": 16,
        "sfp": 2,
        "checks": {
            ("ports", "1"): [1349, 175],
            ("ports", "16"): [2463, 301],
            ("sfp", "SFP1"): [2770, 166],
            ("sfp", "SFP2"): [2775, 306],
        },
    },
    "unifi-9rj45-2sfp.png": {
        "profile": "unifi_9_rj45_2sfp",
        "calibration": "faceplate-unifi-9rj45-2sfp.json",
        "ports": 9,
        "sfp": 2,
        "checks": {
            ("ports", "1"): [1847, 161],
            ("ports", "9"): [2597, 276],
            ("sfp", "SFP1"): [2787, 146],
            ("sfp", "SFP2"): [2787, 296],
        },
    },
    "unifi-3sfp.png": {
        "profile": "unifi_3sfp",
        "calibration": "faceplate-unifi-3sfp.json",
        "ports": 0,
        "sfp": 3,
        "checks": {
            ("sfp", "SFP1"): [2478.762666667, 320.768],
            ("sfp", "SFP2"): [2665.130666667, 320.768],
            ("sfp", "SFP3"): [2960.042666667, 320.768],
        },
    },
}

MODEL_VISUALS = {
    "USW-16-PoE": ("unifi-16rj45-2sfp.png", "unifi_16_rj45_2sfp", 16, 2),
    "US 16 PoE 150W": ("unifi-16rj45-2sfp.png", "unifi_16_rj45_2sfp", 16, 2),
    "UDM Pro": ("unifi-9rj45-2sfp.png", "unifi_9_rj45_2sfp", 9, 2),
    "UniFi Dream Machine PRO SE": ("unifi-9rj45-2sfp.png", "unifi_9_rj45_2sfp", 9, 2),
    "UDM Pro Max": ("unifi-9rj45-2sfp.png", "unifi_9_rj45_2sfp", 9, 2),
    "USW WAN": ("unifi-3sfp.png", "unifi_3sfp", 1, 3),
}


class CompactUniFiFaceplateContract(unittest.TestCase):
    def test_new_faceplate_geometry_is_owner_calibrated_and_role_neutral(self) -> None:
        for filename, spec in FACEPLATE_CONTRACTS.items():
            png = FACEPLATES / filename
            profile = json.loads((CALIBRATION / spec["calibration"]).read_text(encoding="utf-8"))
            assert png.is_file()
            assert png_dimensions(png) == (profile["image"]["width"], profile["image"]["height"])
            assert profile["image"]["coordinate_space"] == "image-native-v1"
            assert Path(profile["image"]["file"]).name == filename
            assert profile["profile"] == spec["profile"]
            assert len(profile.get("ports") or {}) == spec["ports"]
            assert len(profile.get("sfp") or {}) == spec["sfp"]
            all_ports = [*(profile.get("ports") or {}).values(), *(profile.get("sfp") or {}).values()]
            assert all((item.get("supported_speed") or "") == "" for item in all_ports)
            assert all((item.get("port_role") or "") == "" for item in all_ports)
            rendered = render_space_calibration(profile)
            for (group, key), expected in spec["checks"].items():
                actual = rendered[group][key]["center"]
                assert len(actual) == 2
                assert abs(float(actual[0]) - float(expected[0])) < 1e-6, (filename, group, key, actual)
                assert abs(float(actual[1]) - float(expected[1])) < 1e-6, (filename, group, key, actual)

    def test_six_exact_models_use_new_faceplates_without_changing_physical_truth(self) -> None:
        rows = {
            row["model"]: row
            for row in json.loads(REGISTRY.read_text(encoding="utf-8"))["devices"]
            if isinstance(row, dict)
        }
        for model, (filename, profile, rj45, sfp) in MODEL_VISUALS.items():
            row = rows[model]
            visuals = row["visuals"]
            assert row["ports"]["rj45"] == rj45, model
            assert row["ports"]["uplinks"] == sfp, model
            assert row["default_faceplate"] == f"faceplates/{filename}", model
            assert row["calibration_profile"] == profile, model
            assert visuals["recommended_faceplate"] == row["default_faceplate"], model
            assert visuals["calibration_profile"] == profile, model

        # Role semantics belong to exact models, not shared artwork.
        assert rows["UDM Pro"]["port_roles"] == {"rj45": {"9": "wan"}}
        assert not rows["UniFi Dream Machine PRO SE"].get("port_roles")
        assert not rows["UDM Pro Max"].get("port_roles")

        # USW WAN keeps the real rear management RJ45/API4 in device truth while
        # the shipped front-panel profile contains only the three SFP+ cages.
        usw = rows["USW WAN"]
        assert usw["ports"]["rj45"] == 1
        assert usw["unifi_api_port_map"] == {"rj45": [4], "sfp": [1, 2, 3]}
        front = json.loads((CALIBRATION / "faceplate-unifi-3sfp.json").read_text(encoding="utf-8"))
        assert front["ports"] == {}
        assert list(front["sfp"]) == ["SFP1", "SFP2", "SFP3"]


if __name__ == "__main__":
    unittest.main()

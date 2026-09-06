from __future__ import annotations

import ast
import json
import math
import unittest
from pathlib import Path
from types import SimpleNamespace
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "src" / "custom_components" / "switch_vision" / "__init__.py"


class Invalid(ValueError):
    pass


def load_calibration_validator():
    """Execute only the production calibration validator and its pure helpers."""
    source = BACKEND.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(BACKEND))
    functions = {
        "_normalise_profile",
        "_validate_profile_name",
        "_safe_asset_filename",
        "_finite_number",
        "_validate_pair",
        "_validate_calibration",
    }
    constants = {
        "MAX_PROFILE_NAME_LENGTH",
        "FACEPLATE_DEFAULT",
        "FACEPLATE_NONE",
        "MAX_ASSET_FILENAME_LENGTH",
        "MAX_CALIBRATION_BYTES",
        "MAX_CALIBRATION_DIMENSION",
        "MAX_CALIBRATION_PIXELS",
        "MAX_CALIBRATION_PORTS",
        "MAX_CALIBRATION_UPLINKS",
        "MAX_CALIBRATION_STATUS_LEDS",
    }

    selected: list[ast.stmt] = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in functions:
            selected.append(node)
            continue
        if isinstance(node, ast.Assign):
            names = {
                target.id
                for target in node.targets
                if isinstance(target, ast.Name)
            }
            if names & constants:
                selected.append(node)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            if node.target.id in constants:
                selected.append(node)

    namespace = {
        "Any": Any,
        "Path": Path,
        "json": json,
        "math": math,
        "vol": SimpleNamespace(Invalid=Invalid),
    }
    module = ast.Module(body=selected, type_ignores=[])
    ast.fix_missing_locations(module)
    exec(compile(module, str(BACKEND), "exec"), namespace)
    missing = functions - namespace.keys()
    if missing:
        raise AssertionError(f"validator extraction missed: {sorted(missing)}")
    return namespace["_validate_calibration"]


class OpticalOnlyCalibrationTests(unittest.TestCase):
    def test_zero_rj45_thirty_two_optical_ports_are_valid(self) -> None:
        validate = load_calibration_validator()
        calibration = {
            "schema_version": 1,
            "image": {"width": 2048, "height": 448},
            "ports": {},
            "sfp": {
                str(index): {"center": [40 + (index * 40), 160]}
                for index in range(1, 33)
            },
            "status_leds": {},
        }
        result = validate("unifi_pro_aggregation_32_optical", calibration)
        self.assertIs(result, calibration)
        self.assertEqual(len(result["ports"]), 0)
        self.assertEqual(len(result["sfp"]), 32)

    def test_calibration_allows_no_connectors(self) -> None:
        validate = load_calibration_validator()
        calibration = {
            "schema_version": 1,
            "image": {"width": 2048, "height": 448},
            "ports": {},
            "sfp": {},
            "status_leds": {},
        }
        result = validate("empty_connector_test", calibration)
        self.assertIs(result, calibration)


if __name__ == "__main__":
    unittest.main()

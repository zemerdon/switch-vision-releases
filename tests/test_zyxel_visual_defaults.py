#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
payload = json.loads((ROOT / "src" / "devices" / "supported_devices.json").read_text(encoding="utf-8"))
row = next(item for item in payload["devices"] if item.get("model") == "XS1930-10")

assert row["ports"]["rj45"] == 8
assert row["ports"]["uplinks"] == 2
assert row["calibration_profile"] == "cisco_3560cg_8pc"
assert row["default_faceplate"] == "faceplates/c3560cg-8pc-s.png"
visuals = row["visuals"]
assert visuals["recommended_faceplate"] == "faceplates/c3560cg-8pc-s.png"
assert visuals["calibration_profile"] == "cisco_3560cg_8pc"
assert visuals["canvas"] == {"width": 2048, "height": 329}

build = (ROOT / "build.py").read_text(encoding="utf-8")
assert 'compact_8x2_visual_models = {"WS-C3560CG-8PC-S", "XS1930-10"}' in build
assert "if model not in compact_8x2_visual_models:" in build
assert "compact 8+2 calibration leaked into an unapproved exact model" in build
assert "compact 8+2 faceplate leaked into an unapproved exact model" in build
print("Core XS1930-10 visual default contract: PASS")

#!/usr/bin/env python3
"""Core exposes read-only installed image hashes for Hub after Core restart."""
from pathlib import Path
import ast

ROOT = Path(__file__).resolve().parents[1]
core = ROOT / "src/custom_components/switch_vision/__init__.py"
text = core.read_text(encoding="utf-8")
tree = ast.parse(text)

def find_fn(name):
    return [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name]

assert len(find_fn("_fingerprint_faceplates")) == 1
assert len(find_fn("websocket_list_assets")) == 1
node = find_fn("websocket_list_assets")[0]
source = ast.get_source_segment(text, node)
assert source and 'assets["faceplate_fingerprints"]' in source
assert '_fingerprint_faceplates' in source
assert 'assets["core_version"] = PANEL_VERSION' in source
assert "reset_calibrations" not in source
assert "save_calibration" not in source
assert "snmp" not in source.lower()
assert "saved_calibration_image" in text
assert "image_file = str(saved_image.get(\"file\") or \"\").strip()" in text
card = (ROOT / "src/js/switch-vision.js").read_text(encoding="utf-8")
assert "if (selection === SV_ASSET_DEFAULT && this._profileCalibration)" in card
assert "this._profileCalibration.image?.file" in card
assert "return original;" in card
assert "if (selection === SV_ASSET_DEFAULT || selection === SV_ASSET_NONE) return recommended;" in card
print("CORE_HUB_FACEPLATE_ASSET_CONTRACT_PASS")

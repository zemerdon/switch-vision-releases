#!/usr/bin/env python3
from copy import deepcopy
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
ORIGINAL_IMAGE = "unifi-24p-rj45-2sfp.png"
DARK_IMAGE = "unifi-24-rj45-2sfp-dark.png"
ORIGINAL_CAL = SRC / "calibration" / "faceplate-unifi-24p-rj45-2sfp.json"
DARK_CAL = SRC / "calibration" / "faceplate-unifi-24-rj45-2sfp-dark.json"

assert (SRC / "faceplates" / ORIGINAL_IMAGE).is_file()
assert (SRC / "faceplates" / DARK_IMAGE).is_file()
assert DARK_CAL.is_file()

original = json.loads(ORIGINAL_CAL.read_text(encoding="utf-8"))
dark = json.loads(DARK_CAL.read_text(encoding="utf-8"))
assert dark.get("profile") == original.get("profile") == "unifi_24p_rj45_2sfp"
assert Path(str((dark.get("image") or {}).get("file") or "")).name == DARK_IMAGE
assert Path(str(((dark.get("ui") or {}).get("faceplate") or {}).get("file") or "")).name == DARK_IMAGE

def normalized(value, image_name):
    data = deepcopy(value)
    data["model"] = "__identity__"
    data["generated_by"] = "__identity__"
    image = data.get("image") or {}
    image["file"] = f"faceplates/{image_name}"
    image["master"] = "__identity__"
    ui = data.get("ui") or {}
    faceplate = ui.get("faceplate") or {}
    faceplate["file"] = image_name
    return data

# After normalizing identity/filename fields, every functional default must be identical.
assert normalized(original, "__faceplate__.png") == normalized(dark, "__faceplate__.png")

# The new artwork must never become an exact-model/default mapping.
for registry in (SRC / "devices" / "supported_devices.yaml", SRC / "devices" / "supported_devices.json"):
    assert DARK_IMAGE not in registry.read_text(encoding="utf-8")

card = (SRC / "js" / "switch-vision.js").read_text(encoding="utf-8")
profile_block = re.search(r"const SV_FACEPLATE_PROFILE_FILES = \{(.*?)\n\};", card, re.S)
assert profile_block
assert f'unifi_24p_rj45_2sfp: "{ORIGINAL_IMAGE}"' in profile_block.group(1)
assert DARK_IMAGE not in profile_block.group(1)
factory_marker = f'"{DARK_IMAGE}":'
assert factory_marker in card

recommendations = re.search(r"const SV_DEVICE_VISUAL_RECOMMENDATIONS = (\[.*?\]);\n", card, re.S)
assert recommendations
rows = json.loads(recommendations.group(1))
assert all(str(row.get("faceplate") or "").split("/")[-1] != DARK_IMAGE for row in rows)
assert all(DARK_IMAGE not in [str(x).split("/")[-1] for x in (row.get("optional_faceplates") or [])] for row in rows)
print("UniFi dark manual-only faceplate contract: PASS")

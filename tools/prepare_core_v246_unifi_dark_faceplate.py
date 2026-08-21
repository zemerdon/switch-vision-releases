#!/usr/bin/env python3
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
CAL = SRC / "calibration"
FACEPLATES = SRC / "faceplates"
ORIGINAL_IMAGE = "unifi-24p-rj45-2sfp.png"
DARK_IMAGE = "unifi-24-rj45-2sfp-dark.png"
ORIGINAL_CAL = CAL / "faceplate-unifi-24p-rj45-2sfp.json"
DARK_CAL = CAL / "faceplate-unifi-24-rj45-2sfp-dark.json"
VERSION = "2.4.6"


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.replace("\r\n", "\n").replace("\r", "\n"), encoding="utf-8", newline="\n")


if not (FACEPLATES / DARK_IMAGE).is_file():
    raise SystemExit(f"Missing imported dark faceplate: {FACEPLATES / DARK_IMAGE}")
if not ORIGINAL_CAL.is_file():
    raise SystemExit(f"Missing authoritative UniFi calibration: {ORIGINAL_CAL}")

original = json.loads(ORIGINAL_CAL.read_text(encoding="utf-8"))
dark = deepcopy(original)
dark["model"] = "unifi-24-rj45-2sfp-dark"
dark["profile"] = original.get("profile") or "unifi_24p_rj45_2sfp"
dark["generated_by"] = f"Switch Vision v{VERSION}"
image = dark.setdefault("image", {})
image["file"] = f"faceplates/{DARK_IMAGE}"
image["master"] = f"unifi-24-rj45-2sfp-dark-v{VERSION}"
ui = dark.setdefault("ui", {})
ui_faceplate = ui.setdefault("faceplate", {})
ui_faceplate["file"] = DARK_IMAGE
write_text(DARK_CAL, json.dumps(dark, indent=2, ensure_ascii=False) + "\n")

readme = FACEPLATES / "README.txt"
text = readme.read_text(encoding="utf-8")
line = (
    "- unifi-24-rj45-2sfp-dark.png — manual-only dark UniFi alternative; "
    "uses the exact unifi-24p-rj45-2sfp.png calibration geometry and is not mapped to any model\n"
)
if DARK_IMAGE not in text:
    text = text.rstrip() + "\n" + line
    write_text(readme, text)

for changelog in (ROOT / "CHANGELOG.md", SRC / "CHANGELOG.md"):
    text = changelog.read_text(encoding="utf-8")
    entry = (
        "# Changelog\n\n"
        "## 2.4.6\n\n"
        "- Add `unifi-24-rj45-2sfp-dark.png` as a manually selectable alternative UniFi faceplate.\n"
        "- Give the dark alternative the exact factory calibration geometry/defaults of `unifi-24p-rj45-2sfp.png`.\n"
        "- Do not map the dark faceplate to any device model and do not replace any existing default/recommended faceplate.\n\n"
    )
    if text.startswith("# Changelog\n\n") and not text.startswith("# Changelog\n\n## 2.4.6"):
        text = entry + text[len("# Changelog\n\n"):]
        write_text(changelog, text)

notes = ROOT / "RELEASE_NOTES.md"
write_text(
    notes,
    "# Switch Vision Core 2.4.6\n\n"
    "Core 2.4.6 adds the manually selectable `unifi-24-rj45-2sfp-dark.png` faceplate. "
    "It uses the exact factory geometry and presentation defaults from `unifi-24p-rj45-2sfp.png`.\n\n"
    "The new artwork is an alternative only: it is not mapped to any device model, does not replace the existing UniFi faceplate, "
    "and does not change any factory device recommendation.\n",
)
write_text(SRC / "RELEASE_NOTES.md", notes.read_text(encoding="utf-8"))

# Permanent regression proving this remains a manual-only visual alternative.
test = ROOT / "tests" / "test_unifi_dark_faceplate_contract.py"
write_text(
    test,
    '''#!/usr/bin/env python3\nfrom copy import deepcopy\nfrom pathlib import Path\nimport json\nimport re\n\nROOT = Path(__file__).resolve().parents[1]\nSRC = ROOT / "src"\nORIGINAL_IMAGE = "unifi-24p-rj45-2sfp.png"\nDARK_IMAGE = "unifi-24-rj45-2sfp-dark.png"\nORIGINAL_CAL = SRC / "calibration" / "faceplate-unifi-24p-rj45-2sfp.json"\nDARK_CAL = SRC / "calibration" / "faceplate-unifi-24-rj45-2sfp-dark.json"\n\nassert (SRC / "faceplates" / ORIGINAL_IMAGE).is_file()\nassert (SRC / "faceplates" / DARK_IMAGE).is_file()\nassert DARK_CAL.is_file()\n\noriginal = json.loads(ORIGINAL_CAL.read_text(encoding="utf-8"))\ndark = json.loads(DARK_CAL.read_text(encoding="utf-8"))\nassert dark.get("profile") == original.get("profile") == "unifi_24p_rj45_2sfp"\nassert Path(str((dark.get("image") or {}).get("file") or "")).name == DARK_IMAGE\nassert Path(str(((dark.get("ui") or {}).get("faceplate") or {}).get("file") or "")).name == DARK_IMAGE\n\ndef normalized(value, image_name):\n    data = deepcopy(value)\n    data["model"] = "__identity__"\n    data["generated_by"] = "__identity__"\n    image = data.get("image") or {}\n    image["file"] = f"faceplates/{image_name}"\n    image["master"] = "__identity__"\n    ui = data.get("ui") or {}\n    faceplate = ui.get("faceplate") or {}\n    faceplate["file"] = image_name\n    return data\n\n# After normalizing identity/filename fields, every functional default must be identical.\nassert normalized(original, "__faceplate__.png") == normalized(dark, "__faceplate__.png")\n\n# The new artwork must never become an exact-model/default mapping.\nfor registry in (SRC / "devices" / "supported_devices.yaml", SRC / "devices" / "supported_devices.json"):\n    assert DARK_IMAGE not in registry.read_text(encoding="utf-8")\n\ncard = (SRC / "js" / "switch-vision.js").read_text(encoding="utf-8")\nprofile_block = re.search(r"const SV_FACEPLATE_PROFILE_FILES = \\{(.*?)\\n\\};", card, re.S)\nassert profile_block\nassert f'unifi_24p_rj45_2sfp: "{ORIGINAL_IMAGE}"' in profile_block.group(1)\nassert DARK_IMAGE not in profile_block.group(1)\nfactory_marker = f'"{DARK_IMAGE}":'\nassert factory_marker in card\n\nrecommendations = re.search(r"const SV_DEVICE_VISUAL_RECOMMENDATIONS = (\\[.*?\\]);\\n", card, re.S)\nassert recommendations\nrows = json.loads(recommendations.group(1))\nassert all(str(row.get("faceplate") or "").split("/")[-1] != DARK_IMAGE for row in rows)\nassert all(DARK_IMAGE not in [str(x).split("/")[-1] for x in (row.get("optional_faceplates") or [])] for row in rows)\nprint("UniFi dark manual-only faceplate contract: PASS")\n''',
)

print("Prepared Core 2.4.6 UniFi dark alternative faceplate")

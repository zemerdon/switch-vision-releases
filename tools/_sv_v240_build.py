#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import shutil
import struct
import subprocess
import sys
import urllib.request
import zipfile

VERSION = "2.4.0"
ASSET = "unifi-24p-rj45-2sfp.png"
PROFILE = "unifi_24p_rj45_2sfp"
EXPECTED_SHA = "3843544aedd63e8d591fec3c77741686ce2820a1d49ab464cee2b25f23c1f7b7"
SRC_ASSET = Path("src/faceplates") / ASSET
RELEASE_DIR = Path("Releases") / f"switch-vision-{VERSION}"


def stop(msg: str) -> None:
    raise SystemExit(f"STOP: {msg}")


def run(*args: str) -> None:
    print("+", " ".join(args), flush=True)
    subprocess.run(args, check=True)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.replace("\r\n", "\n").replace("\r", "\n"), encoding="utf-8", newline="\n")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        stop(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def fetch_asset(url: str) -> None:
    archive = Path("/tmp/core-v240-unifi.zip")
    urllib.request.urlretrieve(url, archive)
    with zipfile.ZipFile(archive) as zf:
        matches = [n for n in zf.namelist() if Path(n).name == ASSET and not n.endswith("/")]
        if len(matches) != 1:
            stop(f"artifact should contain exactly one {ASSET}, found {len(matches)}")
        raw = zf.read(matches[0])
    digest = hashlib.sha256(raw).hexdigest()
    if digest != EXPECTED_SHA:
        stop(f"approved UniFi PNG SHA mismatch: {digest}")
    if raw[:8] != b"\x89PNG\r\n\x1a\n":
        stop("approved asset is not PNG")
    width, height = struct.unpack(">II", raw[16:24])
    if (width, height) != (1592, 149):
        stop(f"unexpected approved asset dimensions {width}x{height}")
    SRC_ASSET.parent.mkdir(parents=True, exist_ok=True)
    SRC_ASSET.write_bytes(raw)
    print(f"Verified approved UniFi PNG {width}x{height} sha256={digest}")


def normalize_profiles() -> None:
    specs = {
        Path("src/calibration/faceplate-stock-24rj45-2sfp.json"): ("stock-24rj45-2sfp", "stock_24rj45_2sfp", "24rj45-2sfp.png"),
        Path("src/calibration/faceplate-stock-24rj45-4sfp.json"): ("stock-24rj45-4sfp", "stock_24rj45_4sfp", "24rj45-4sfp.png"),
        Path("src/calibration/faceplate-unifi-24p-rj45-2sfp.json"): ("unifi-24p-rj45-2sfp", PROFILE, ASSET),
    }
    for path, (model, profile, faceplate_name) in specs.items():
        data = json.loads(path.read_text(encoding="utf-8"))
        data["schema_version"] = 2
        data["schema"] = "switch-vision-interactive-calibration-v1"
        data["model"] = model
        data["profile"] = profile
        data["generated_by"] = "Switch Vision v2.4.0"
        image = data.setdefault("image", {})
        image["file"] = f"faceplates/{faceplate_name}"
        image["width"] = 2048
        image["height"] = 448
        if faceplate_name == ASSET:
            image["master"] = "unifi-24p-rj45-2sfp-v2.4.0"
        data.setdefault("ui", {}).setdefault("faceplate", {})["file"] = faceplate_name
        stack = data.setdefault("stack", {})
        stack.update({"enabled": False, "stack_id": "", "uptime_source": "", "members": {}})
        data.setdefault("management", {})["switch_ip"] = ""
        for key in ("switch_ip", "management_ip", "host", "hostname", "snmp_community", "community", "username", "password", "credential", "credentials", "instance", "instance_id", "instance_name", "switch_name", "selected_switch", "discovery_selected_switch", "source", "runtime"):
            data.pop(key, None)
        write(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def patch_build_guard() -> None:
    path = Path("build.py")
    text = path.read_text(encoding="utf-8")
    old = '''        if model in exact_visual_overrides:\n            expected_profile, expected_faceplate = exact_visual_overrides[model]\n        else:\n            family = 24 if rj45 <= 24 else 48\n            sfp = 2 if uplinks <= 2 else 4\n            expected_profile = f"stock_{family}rj45_{sfp}sfp"\n            expected_faceplate = f"faceplates/{family}rj45-{sfp}sfp.png"\n'''
    new = '''        vendor = str(device.get("vendor") or "").strip()\n        if vendor == "Ubiquiti":\n            expected_profile = "unifi_24p_rj45_2sfp"\n            expected_faceplate = "faceplates/unifi-24p-rj45-2sfp.png"\n        elif model in exact_visual_overrides:\n            expected_profile, expected_faceplate = exact_visual_overrides[model]\n        else:\n            family = 24 if rj45 <= 24 else 48\n            sfp = 2 if uplinks <= 2 else 4\n            expected_profile = f"stock_{family}rj45_{sfp}sfp"\n            expected_faceplate = f"faceplates/{family}rj45-{sfp}sfp.png"\n'''
    if new not in text:
        write(path, replace_once(text, old, new, "Ubiquiti visual-family guard"))


def patch_profile_aliases() -> None:
    path = Path("src/js/switch-vision.js")
    text = path.read_text(encoding="utf-8")
    old = '''function factoryCalibrationForProfile(profile) {\n  return SV_FACTORY_CALIBRATIONS[String(profile || "").trim()] || null;\n}\n'''
    new = '''const SV_FACEPLATE_PROFILE_FILES = {\n  stock_24rj45_2sfp: "24rj45-2sfp.png",\n  stock_24rj45_4sfp: "24rj45-4sfp.png",\n  stock_48rj45_2sfp: "48rj45-2sfp.png",\n  stock_48rj45_4sfp: "48rj45-4sfp.png",\n  unifi_24p_rj45_2sfp: "unifi-24p-rj45-2sfp.png",\n};\n\nfunction factoryCalibrationForProfile(profile) {\n  const key = String(profile || "").trim();\n  const direct = SV_FACTORY_CALIBRATIONS[key] || null;\n  if (direct) return direct;\n  const filename = SV_FACEPLATE_PROFILE_FILES[key];\n  return filename ? faceplateFactoryCalibrationForFile(filename) : null;\n}\n'''
    if new not in text:
        write(path, replace_once(text, old, new, "factory profile alias map"))


def patch_registry() -> None:
    path = Path("src/devices/supported_devices.yaml")
    blocks = re.split(r"(?=^- vendor: )", path.read_text(encoding="utf-8"), flags=re.M)
    count = 0
    out: list[str] = []
    for block in blocks:
        if not block.startswith("- vendor: Ubiquiti\n"):
            out.append(block)
            continue
        count += 1
        block, a = re.subn(r"(?m)^  calibration_profile: .*$", f"  calibration_profile: {PROFILE}", block, count=1)
        block, b = re.subn(r"(?m)^  default_faceplate: .*$", f"  default_faceplate: faceplates/{ASSET}", block, count=1)
        block, c = re.subn(r"(?m)^    recommended_faceplate: .*$", f"    recommended_faceplate: faceplates/{ASSET}", block, count=1)
        block, d = re.subn(r"(?m)^    calibration_profile: .*$", f"    calibration_profile: {PROFILE}", block, count=1)
        if (a, b, c, d) != (1, 1, 1, 1):
            stop(f"Ubiquiti registry block shape changed: {(a,b,c,d)}")
        out.append(block)
    if count != 5:
        stop(f"expected 5 current Ubiquiti exact-model entries, found {count}")
    write(path, "".join(out))


def patch_docs() -> None:
    readme = Path("src/faceplates/README.txt")
    text = readme.read_text(encoding="utf-8")
    line = f"- {ASSET} — default UniFi / Ubiquiti faceplate; current UniFi model mappings recommend this artwork\n"
    if line not in text:
        write(readme, text + "\n" + line + "Faceplate artwork may use native source dimensions; Switch Vision scales it to the calibration canvas at runtime.\n")

    upgrading = Path("src/docs/UPGRADING.md")
    text = upgrading.read_text(encoding="utf-8")
    heading = "## Faceplate defaults updated in v2.4.0"
    if heading not in text:
        note = f'''\n\n{heading}\n\nExisting saved/custom faceplate calibrations are preserved during upgrade. To use the new v2.4.0 built-in defaults on an existing switch, open **Calibration** and choose **Reset Current Faceplate** to reload the current bundled/model default.\n\nUpdated defaults:\n\n- **UniFi / Ubiquiti models** now default to `{ASSET}`.\n- **Stock 24 RJ45 / 4 SFP** calibration defaults were updated.\n- **Stock 24 RJ45 / 2 SFP** calibration defaults were updated.\n'''
        marker = "\n## Rollback\n"
        write(upgrading, text.replace(marker, note + marker, 1) if marker in text else text + note)

    changelog = Path("CHANGELOG.md")
    text = changelog.read_text(encoding="utf-8")
    if "## v2.4.0" not in text:
        entry = f'''## v2.4.0\n\n- Added the dedicated `{ASSET}` UniFi / Ubiquiti faceplate and authoritative factory calibration.\n- Made UniFi / Ubiquiti an explicit visual family instead of using the generic stock fallback.\n- Updated stock 24 RJ45 / 2 SFP and stock 24 RJ45 / 4 SFP factory calibration defaults.\n- Preserved existing saved/custom calibrations; **Reset Current Faceplate** adopts refreshed defaults.\n- Preserved v2.3.16 TEST MODE no-overlap behavior.\n\n'''
        write(changelog, entry + text)


def clean_outputs() -> None:
    for path in (
        Path("Releases") / f"switch-vision-{VERSION}.zip",
        Path("Releases") / f"switch-vision-{VERSION}.zip.sha256",
        Path(f"Switch_Vision_v{VERSION}_source.zip"),
        Path(f"Switch_Vision_v{VERSION}_SHA256SUMS.txt"),
    ):
        path.unlink(missing_ok=True)


def validate() -> None:
    if Path("VERSION").read_text(encoding="utf-8").strip() != VERSION:
        stop("VERSION did not become 2.4.0")
    release_asset = RELEASE_DIR / "faceplates" / ASSET
    if not release_asset.exists():
        stop("release tree is missing approved UniFi faceplate")
    for path in (SRC_ASSET, release_asset):
        if hashlib.sha256(path.read_bytes()).hexdigest() != EXPECTED_SHA:
            stop(f"approved UniFi faceplate hash changed: {path}")
    registry = Path("src/devices/supported_devices.yaml").read_text(encoding="utf-8")
    if registry.count("vendor: Ubiquiti") != 5:
        stop("unexpected Ubiquiti exact-model count")
    if registry.count(f"default_faceplate: faceplates/{ASSET}") != 5:
        stop("not all Ubiquiti defaults use the UniFi faceplate")
    if registry.count(f"recommended_faceplate: faceplates/{ASSET}") != 5:
        stop("not all Ubiquiti visual recommendations use the UniFi faceplate")
    js = Path("src/js/switch-vision.js").read_text(encoding="utf-8")
    if 'unifi_24p_rj45_2sfp: "unifi-24p-rj45-2sfp.png"' not in js:
        stop("UniFi profile alias is missing")
    run("node", "--check", "src/js/switch-vision.js")
    run("node", "--check", "src/custom_components/switch_vision/switch-vision-card.js")
    run("python3", "tools/check_core_release_parity.py")
    run("git", "diff", "--check")
    for root in (Path("src"), RELEASE_DIR):
        if any(root.rglob("__pycache__")) or any(root.rglob("*.pyc")) or any(root.rglob("*.pyo")):
            stop(f"Python cache material found under {root}")


def main() -> None:
    if len(sys.argv) != 2:
        stop("usage: tools/_sv_v240_build.py <verified-artifact-url>")
    fetch_asset(sys.argv[1])
    normalize_profiles()
    patch_build_guard()
    patch_profile_aliases()
    patch_registry()
    patch_docs()
    for temp in (Path(".sv-v240-asset"), Path(".sv-v240-b64")):
        if temp.exists():
            shutil.rmtree(temp)
    Path(".sv-v240-pr-trigger").unlink(missing_ok=True)
    run("python3", "build.py", "-v", VERSION)
    clean_outputs()
    validate()
    Path(__file__).unlink(missing_ok=True)
    print("Core v2.4.0 build/validation PASS", flush=True)


if __name__ == "__main__":
    main()

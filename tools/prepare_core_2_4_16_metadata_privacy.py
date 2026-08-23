#!/usr/bin/env python3
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import re
import subprocess
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]
OLD_VERSION = "2.4.15"
NEW_VERSION = "2.4.16"
TARGET_MODELS = {
    "UCG Ultra",
    "US 16 PoE 150W",
    "USW Pro Max 24",
    "USW Ultra",
}
PROMOTE_MODELS = {
    "UCG Ultra",
    "US 16 PoE 150W",
    "USW Ultra",
}
NEUTRAL_EVIDENCE = "multiple_real_hardware_unifi_api_contributions"
SUBMISSION_ID = re.compile(r"(?i)SV[-_]20\d{2}[-_]\d+")
HARDWARE_KEYS = {
    "vendor",
    "family",
    "model",
    "ports",
    "stack_support",
    "discovery_support",
    "dashboard_support",
    "mapping_profile",
    "calibration_profile",
    "default_faceplate",
    "optional_faceplates",
    "tested_firmware",
    "validation",
    "visuals",
    "api_port_map",
    "data_source",
}


def run(args: list[str]) -> None:
    print("$", " ".join(args))
    subprocess.run(args, cwd=ROOT, check=True)


def write_lf(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def model_map(document: dict) -> dict[str, dict]:
    rows = document.get("devices") if isinstance(document, dict) else None
    if not isinstance(rows, list):
        raise SystemExit("supported_devices.yaml is missing a devices list")
    return {
        str(row.get("model") or ""): row
        for row in rows
        if isinstance(row, dict) and str(row.get("model") or "")
    }


def hardware_contract(row: dict) -> dict:
    return {key: deepcopy(row.get(key)) for key in sorted(HARDWARE_KEYS)}


def prepend_release_entry(path: Path, entry: str) -> None:
    old = path.read_text(encoding="utf-8")
    if old.startswith(f"## v{NEW_VERSION} "):
        return
    write_lf(path, entry + old.lstrip())


def main() -> int:
    version_path = ROOT / "VERSION"
    current = version_path.read_text(encoding="utf-8").strip()
    if current != OLD_VERSION:
        raise SystemExit(
            f"Core {NEW_VERSION} preparer requires {OLD_VERSION}; found {current}"
        )

    registry_path = ROOT / "src/devices/supported_devices.yaml"
    registry = yaml.safe_load(registry_path.read_text(encoding="utf-8")) or {}
    models = model_map(registry)
    missing = TARGET_MODELS - set(models)
    if missing:
        raise SystemExit(f"Missing target Core models: {sorted(missing)}")

    hardware_before = {
        model: hardware_contract(row)
        for model, row in models.items()
    }

    for model in sorted(TARGET_MODELS):
        row = models[model]
        old_status = str(row.get("status") or "")
        if model in PROMOTE_MODELS:
            if old_status not in {"detected", "experimental"}:
                raise SystemExit(
                    f"Unexpected pre-promotion status for {model}: {old_status!r}"
                )
            row["status"] = "experimental"
        elif old_status != "experimental":
            raise SystemExit(
                f"USW Pro Max 24 must remain Experimental; found {old_status!r}"
            )
        row["evidence"] = NEUTRAL_EVIDENCE

        contributor = row.get("contributor") or {}
        if str(contributor.get("display_name") or "").casefold() not in {
            "",
            "community contributor",
        }:
            raise SystemExit(f"Non-neutral public contributor on {model}")
        if contributor.get("public_credit") is True:
            raise SystemExit(f"Public credit unexpectedly enabled on {model}")

    write_lf(
        registry_path,
        yaml.safe_dump(registry, sort_keys=False, allow_unicode=True),
    )

    sanitizer_path = ROOT / "tools/sanitize_public_attribution.py"
    sanitizer = sanitizer_path.read_text(encoding="utf-8")
    old_block = (
        '    text = PACKAGE_RE.sub("community submission", text)\n'
        '    text = SUBMISSION_ID_RE.sub("community validation", text)\n'
    )
    new_block = (
        '    text = PACKAGE_RE.sub("community submission", text)\n'
        '    text = re.sub(\n'
        '        r"(?i)Two independent SV[-_]20\\d{2}[-_]\\d+ units",\n'
        '        "Two independent community hardware captures",\n'
        '        text,\n'
        '    )\n'
        '    text = re.sub(\n'
        '        r"(?i)SV[-_]20\\d{2}[-_]\\d+\\s+confirms",\n'
        '        "Community hardware evidence confirms",\n'
        '        text,\n'
        '    )\n'
        '    text = SUBMISSION_ID_RE.sub("community validation", text)\n'
    )
    if old_block not in sanitizer:
        raise SystemExit("Could not locate sanitizer submission-ID block")
    sanitizer = sanitizer.replace(old_block, new_block, 1)

    old_dict_line = (
        '        result = {key: sanitize_structured(child, identities, owner) for key, child in value.items()}\n'
    )
    new_dict_block = (
        '        result = {}\n'
        '        for key, child in value.items():\n'
        '            clean_key = sanitize_text(key, identities) if isinstance(key, str) else key\n'
        '            if clean_key in result and clean_key != key:\n'
        '                raise ValueError(f"Public metadata key collision after sanitization: {clean_key!r}")\n'
        '            result[clean_key] = sanitize_structured(child, identities, owner)\n'
    )
    if old_dict_line not in sanitizer:
        raise SystemExit("Could not locate structured sanitizer dictionary handling")
    sanitizer = sanitizer.replace(old_dict_line, new_dict_block, 1)
    write_lf(sanitizer_path, sanitizer)

    privacy_test_path = ROOT / "tests/test_public_attribution_privacy.py"
    privacy_test = privacy_test_path.read_text(encoding="utf-8")
    privacy_dict_marker = (
        '    if isinstance(value, dict):\n'
        '        if "display_name" in value and "public_credit" in value:\n'
    )
    privacy_dict_replacement = (
        '    if isinstance(value, dict):\n'
        '        for key in value:\n'
        '            key_text = str(key)\n'
        '            assert not SUBMISSION_ID.search(key_text), (path, key_text)\n'
        '            assert not PACKAGE_NAME.search(key_text), (path, key_text)\n'
        '        if "display_name" in value and "public_credit" in value:\n'
    )
    if privacy_dict_marker not in privacy_test:
        raise SystemExit("Could not locate structured privacy regression dictionary handling")
    privacy_test = privacy_test.replace(
        privacy_dict_marker,
        privacy_dict_replacement,
        1,
    )
    if 'if __name__ == "__main__":' not in privacy_test:
        privacy_test += (
            '\n\nif __name__ == "__main__":\n'
            '    test_all_public_device_registries_are_neutral()\n'
            '    test_public_release_history_has_no_private_submission_references()\n'
            '    print("Switch Vision Core public attribution privacy: PASS")\n'
        )
    write_lf(privacy_test_path, privacy_test)

    community_test_path = ROOT / "tests/test_unifi_community_contracts.py"
    community_test = community_test_path.read_text(encoding="utf-8")
    old_status_line = (
        '    expected_status = "experimental" if model == "USW Pro Max 24" else "detected"\n'
    )
    if old_status_line not in community_test:
        raise SystemExit("Could not locate UniFi community status assertion")
    community_test = community_test.replace(
        old_status_line,
        '    expected_status = "experimental"\n',
        1,
    )
    anchor = '    assert item["mapping_profile"] == profile, model\n'
    if anchor not in community_test:
        raise SystemExit("Could not locate UniFi community evidence insertion point")
    community_test = community_test.replace(
        anchor,
        anchor
        + f'    assert item["evidence"] == "{NEUTRAL_EVIDENCE}", model\n',
        1,
    )
    write_lf(community_test_path, community_test)

    changelog_entry = f"""## v{NEW_VERSION} — UniFi support-status and privacy synchronization\n\n- Promote `UCG Ultra`, `US 16 PoE 150W`, and `USW Ultra` from Detected to Experimental after corroborating real-hardware UniFi API evidence; keep `USW Pro Max 24` Experimental.\n- Synchronize Core public support evidence with Discovery using neutral community-hardware wording and no private Support My Switch submission identifiers.\n- Activate the permanent public-attribution privacy regression under the repository's direct-test CI runner and extend sanitization/regression coverage to structured public metadata keys.\n- Preserve every existing port count, connector type, PoE mask, API/interface ordering, mapping profile, faceplate/calibration contract, validation field, and maximum-speed contract.\n- No dashboard telemetry, port-selection, LED, SNMP, UniFi API, or other runtime behaviour changes.\n\n"""
    for path in (ROOT / "CHANGELOG.md", ROOT / "src/CHANGELOG.md"):
        prepend_release_entry(path, changelog_entry)

    release_notes = f"""# Switch Vision Core v{NEW_VERSION}\n\nCore {NEW_VERSION} synchronizes public UniFi support status and privacy metadata with the current Discovery evidence.\n\n`UCG Ultra`, `US 16 PoE 150W`, and `USW Ultra` move from Detected to Experimental after corroborating real-hardware UniFi API captures. `USW Pro Max 24` remains Experimental. The release also removes private Support My Switch submission identifiers from public registry history, including structured metadata keys, and makes the permanent privacy regression actually execute in the repository's direct-test CI path.\n\nThis is a metadata/privacy maintenance release only. Port counts, connector types, PoE capability, API/interface ordering, maximum speed capability, faceplates, calibration, telemetry, LED behaviour and runtime logic are unchanged.\n"""
    for path in (ROOT / "RELEASE_NOTES.md", ROOT / "src/RELEASE_NOTES.md"):
        write_lf(path, release_notes)

    run([
        sys.executable,
        "tools/sanitize_public_attribution.py",
        "--root",
        ".",
        "--owner",
        "zemerdon",
    ])
    run([sys.executable, "build.py", "-v", NEW_VERSION])

    for path in (
        ROOT / f"Releases/switch-vision-{NEW_VERSION}.zip",
        ROOT / f"Releases/switch-vision-{NEW_VERSION}.zip.sha256",
        ROOT / f"Switch_Vision_v{NEW_VERSION}_source.zip",
        ROOT / f"Switch_Vision_v{NEW_VERSION}_SHA256SUMS.txt",
    ):
        path.unlink(missing_ok=True)

    final_registry = yaml.safe_load(registry_path.read_text(encoding="utf-8")) or {}
    final_models = model_map(final_registry)
    if set(final_models) != set(models):
        raise SystemExit("Device model inventory changed unexpectedly")
    for model, row in final_models.items():
        if hardware_contract(row) != hardware_before[model]:
            raise SystemExit(f"Hardware contract changed unexpectedly for {model}")

    for model in TARGET_MODELS:
        row = final_models[model]
        if row.get("status") != "experimental":
            raise SystemExit(f"Final support status is not Experimental for {model}")
        if row.get("evidence") != NEUTRAL_EVIDENCE:
            raise SystemExit(f"Final public evidence is not neutral for {model}")

    for path in (
        ROOT / "src/devices/supported_devices.yaml",
        ROOT / "src/devices/supported_devices.json",
        ROOT / "CHANGELOG.md",
        ROOT / "RELEASE_NOTES.md",
    ):
        text = path.read_text(encoding="utf-8", errors="ignore")
        if SUBMISSION_ID.search(text):
            raise SystemExit(f"Private submission identifier remains in {path}")

    run([sys.executable, "tests/test_public_attribution_privacy.py"])
    run([sys.executable, "tests/test_unifi_community_contracts.py"])
    run([sys.executable, "tools/check_core_release_parity.py"])

    print(f"Switch Vision Core {NEW_VERSION} deterministic preparation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

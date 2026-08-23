#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
OLD_VERSION = "2.4.16"
NEW_VERSION = "2.4.17"


def write_lf(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match, found {count}")
    write_lf(path, text.replace(old, new, 1))


def run(*args: str) -> None:
    print("$", " ".join(args))
    subprocess.run(args, cwd=ROOT, check=True)


def prepend_release_entry(path: Path, entry: str) -> None:
    text = path.read_text(encoding="utf-8")
    if text.startswith(f"## v{NEW_VERSION} "):
        return
    write_lf(path, entry + text.lstrip())


def main() -> int:
    current = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if current != OLD_VERSION:
        raise SystemExit(
            f"Core {NEW_VERSION} preparer requires {OLD_VERSION}; found {current}"
        )

    frontend = ROOT / "src/js/switch-vision.js"
    backend = ROOT / "src/custom_components/switch_vision/__init__.py"

    # Backend: allow callers to request the independent base profile without
    # following the active faceplate pointer. Normal reads remain unchanged.
    replace_once(
        backend,
        '''GET_WS_SCHEMA = {
    vol.Required("type"): "switch_vision/get_calibration",
    vol.Required("profile"): vol.All(str, vol.Length(min=1)),
}
''',
        '''GET_WS_SCHEMA = {
    vol.Required("type"): "switch_vision/get_calibration",
    vol.Required("profile"): vol.All(str, vol.Length(min=1)),
    vol.Optional("exact", default=False): bool,
}
''',
        "get_calibration websocket schema",
    )

    replace_once(
        backend,
        '''        requested_profile = _validate_profile_name(msg["profile"])
        resolved_profile = requested_profile
        active_profile = ""
        async with storage_lock:
''',
        '''        requested_profile = _validate_profile_name(msg["profile"])
        resolved_profile = requested_profile
        active_profile = ""
        exact_profile = bool(msg.get("exact", False))
        async with storage_lock:
''',
        "get_calibration exact flag",
    )

    replace_once(
        backend,
        '''            candidate = _normalise_profile(active_profiles.get(requested_profile, ""))
            if candidate:
''',
        '''            candidate = "" if exact_profile else _normalise_profile(active_profiles.get(requested_profile, ""))
            if candidate:
''',
        "get_calibration active-profile resolution",
    )

    # Frontend: normal loads still follow the active faceplate pointer. The
    # explicit Default/recommended selection requests the exact base profile.
    replace_once(
        frontend,
        '''    const applyToWorking = options.applyToWorking === true;
    if (!force && !applyToWorking && this._profileLoadRequested === profile) return this._profileLoadInfo || null;
''',
        '''    const applyToWorking = options.applyToWorking === true;
    const exactProfile = options.exactProfile === true;
    if (!force && !applyToWorking && this._profileLoadRequested === profile) return this._profileLoadInfo || null;
''',
        "frontend exact-profile option",
    )

    replace_once(
        frontend,
        '''      const result = await this._hass.callWS({
        type: "switch_vision/get_calibration",
        profile
      });
      if (this.calibrationProfileName() !== profile) return null;
      const resolvedProfile = String(result?.profile || profile).trim() || profile;
      const expectedPrefix = `${profile}__faceplate__`;
      if (resolvedProfile !== profile && !resolvedProfile.startsWith(expectedPrefix)) {
        throw new Error(`Stored active faceplate profile escaped switch scope: ${resolvedProfile}`);
      }
''',
        '''      const result = await this._hass.callWS({
        type: "switch_vision/get_calibration",
        profile,
        exact: exactProfile
      });
      if (this.calibrationProfileName() !== profile) return null;
      const resolvedProfile = String(result?.profile || profile).trim() || profile;
      if (exactProfile && resolvedProfile !== profile) {
        throw new Error(`Exact calibration profile resolved unexpectedly: ${resolvedProfile}`);
      }
      const expectedPrefix = `${profile}__faceplate__`;
      if (!exactProfile && resolvedProfile !== profile && !resolvedProfile.startsWith(expectedPrefix)) {
        throw new Error(`Stored active faceplate profile escaped switch scope: ${resolvedProfile}`);
      }
''',
        "frontend get_calibration exact request",
    )

    replace_once(
        frontend,
        '''        const requestedFaceplate = cloneCalibrationData(cal.ui.faceplate);

        // A faceplate change selects a different calibration namespace. A bundled
''',
        '''        const requestedFaceplate = cloneCalibrationData(cal.ui.faceplate);
        const useExactBaseProfile = value === SV_ASSET_DEFAULT || value === SV_ASSET_NONE;

        // A faceplate change selects a different calibration namespace. A bundled
''',
        "Default faceplate exact-base decision",
    )

    replace_once(
        frontend,
        '''        await this.loadCalibrationProfile(true, { applyToWorking: true, starterCalibration: starter });
''',
        '''        await this.loadCalibrationProfile(true, {
          applyToWorking: true,
          starterCalibration: starter,
          exactProfile: useExactBaseProfile
        });
''',
        "Default faceplate exact-base load",
    )

    changelog_entry = f"""## v{NEW_VERSION} — Default faceplate profile restoration\n\n- Fix Calibration → Faceplate → Default / recommended so an explicit Default selection loads the independent switch base profile instead of following the currently active custom-faceplate pointer back into that faceplate.\n- Add an exact-profile option to the authenticated `switch_vision/get_calibration` websocket command; normal card/profile loads keep the existing active-faceplate behaviour.\n- Add a permanent regression covering the backend pointer bypass and frontend Default-selection contract.\n- No switch mapping, port geometry, SNMP/UniFi polling, telemetry, LED sensitivity, support status, or device capability changes.\n\n"""
    for path in (ROOT / "CHANGELOG.md", ROOT / "src/CHANGELOG.md"):
        prepend_release_entry(path, changelog_entry)

    release_notes = f"""# Switch Vision Core v{NEW_VERSION}\n\nCore {NEW_VERSION} fixes the Calibration faceplate selector so choosing **Default / recommended** reliably returns to the switch's independent base calibration profile.\n\nPreviously, the base-profile load followed the saved active custom-faceplate pointer, which could immediately restore the faceplate the user was trying to leave. The websocket contract now supports an exact base-profile read used only for an explicit Default selection; normal profile loads continue to follow the active faceplate as before.\n\nThis release changes the Switch Vision Home Assistant custom component and frontend card. It does not change switch mappings, hardware geometry, polling, telemetry, support status, or device capability data.\n"""
    for path in (ROOT / "RELEASE_NOTES.md", ROOT / "src/RELEASE_NOTES.md"):
        write_lf(path, release_notes)

    run(sys.executable, "build.py", "-v", NEW_VERSION)

    # Build artifacts are generated for local/public release workflows, but the
    # repository contract tracks source plus the extracted deterministic release.
    for path in (
        ROOT / f"Releases/switch-vision-{NEW_VERSION}.zip",
        ROOT / f"Releases/switch-vision-{NEW_VERSION}.zip.sha256",
        ROOT / f"Switch_Vision_v{NEW_VERSION}_source.zip",
        ROOT / f"Switch_Vision_v{NEW_VERSION}_SHA256SUMS.txt",
    ):
        path.unlink(missing_ok=True)

    run(sys.executable, "tests/test_faceplate_default_profile_contract.py")
    run(sys.executable, "tests/test_release_metadata_contract.py")
    run(sys.executable, "tools/check_core_release_parity.py")

    print(f"Switch Vision Core {NEW_VERSION} deterministic preparation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

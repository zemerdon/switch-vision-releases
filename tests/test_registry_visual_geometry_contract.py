from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "src" / "devices" / "supported_devices.json"
CALIBRATION_DIR = ROOT / "src" / "calibration"
FACEPLATE_DIR = ROOT / "src" / "faceplates"


def _load_calibration_profiles() -> dict[str, tuple[Path, dict]]:
    profiles: dict[str, tuple[Path, dict]] = {}
    for path in sorted(CALIBRATION_DIR.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        profile = str(payload.get("profile") or "").strip()
        if not profile:
            continue
        if profile in profiles:
            previous = profiles[profile][0]
            raise AssertionError(
                f"duplicate calibration profile {profile!r}: {previous.name}, {path.name}"
            )
        profiles[profile] = (path, payload)
    return profiles


def _geometry_count(payload: dict, key: str) -> int:
    group = payload.get(key)
    if isinstance(group, dict):
        return len(group)
    if isinstance(group, list):
        return len(group)
    return 0


class RegistryVisualGeometryContractTests(unittest.TestCase):
    def test_exact_dashboard_geometry_matches_registry_physical_contract(self) -> None:
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        profiles = _load_calibration_profiles()
        errors: list[str] = []

        for device in registry.get("devices", []):
            if not isinstance(device, dict) or device.get("dashboard_support") is not True:
                continue

            model = str(device.get("model") or "<missing model>")
            ports = device.get("ports") or {}
            expected_rj45 = int(ports.get("rj45") or 0)
            expected_sfp = int(ports.get("uplinks") or 0)
            profile_name = str(device.get("calibration_profile") or "").strip()
            faceplate = str(device.get("default_faceplate") or "").strip()

            if not profile_name:
                errors.append(f"{model}: dashboard_support=true but calibration_profile is empty")
                continue
            if not faceplate:
                errors.append(f"{model}: dashboard_support=true but default_faceplate is empty")
                continue
            if profile_name not in profiles:
                errors.append(
                    f"{model}: calibration profile {profile_name!r} has no source JSON in src/calibration"
                )
                continue

            profile_path, calibration = profiles[profile_name]
            actual_rj45 = _geometry_count(calibration, "ports")
            actual_sfp = _geometry_count(calibration, "sfp")

            if actual_rj45 != expected_rj45:
                errors.append(
                    f"{model}: registry expects {expected_rj45} RJ45 but "
                    f"{profile_path.name} ({profile_name}) defines {actual_rj45}"
                )
            if actual_sfp != expected_sfp:
                errors.append(
                    f"{model}: registry expects {expected_sfp} uplink/SFP positions but "
                    f"{profile_path.name} ({profile_name}) defines {actual_sfp}"
                )

            image = calibration.get("image") or {}
            calibration_faceplate = str(image.get("file") or "").strip()
            if calibration_faceplate and calibration_faceplate != faceplate:
                errors.append(
                    f"{model}: registry faceplate {faceplate!r} disagrees with "
                    f"{profile_path.name} image {calibration_faceplate!r}"
                )

            faceplate_name = faceplate.removeprefix("faceplates/")
            if not (FACEPLATE_DIR / faceplate_name).is_file():
                errors.append(f"{model}: registry faceplate {faceplate!r} does not exist in src/faceplates")

            visuals = device.get("visuals") or {}
            visuals_profile = str(visuals.get("calibration_profile") or "").strip()
            visuals_faceplate = str(visuals.get("recommended_faceplate") or "").strip()
            if visuals_profile != profile_name:
                errors.append(
                    f"{model}: visuals.calibration_profile {visuals_profile!r} != {profile_name!r}"
                )
            if visuals_faceplate != faceplate:
                errors.append(
                    f"{model}: visuals.recommended_faceplate {visuals_faceplate!r} != {faceplate!r}"
                )

        self.assertEqual([], errors, "\n" + "\n".join(errors))


if __name__ == "__main__":
    unittest.main()

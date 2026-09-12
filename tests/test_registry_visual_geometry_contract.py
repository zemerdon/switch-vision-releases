from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "src" / "devices" / "supported_devices.json"
CALIBRATION_DIR = ROOT / "src" / "calibration"
FACEPLATE_DIR = ROOT / "src" / "faceplates"


def _load_calibration_profiles() -> dict[str, list[tuple[Path, dict]]]:
    profiles: dict[str, list[tuple[Path, dict]]] = {}
    for path in sorted(CALIBRATION_DIR.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        profile = str(payload.get("profile") or "").strip()
        if not profile:
            continue
        profiles.setdefault(profile, []).append((path, payload))
    return profiles


def _geometry_count(payload: dict, key: str) -> int:
    group = payload.get(key)
    if isinstance(group, dict):
        return len(group)
    if isinstance(group, list):
        return len(group)
    return 0


def _image_file(payload: dict) -> str:
    return str(((payload.get("image") or {}).get("file") or "")).strip()


class RegistryVisualGeometryContractTests(unittest.TestCase):
    def test_dashboard_visual_capacity_covers_registry_physical_contract(self) -> None:
        """Registry defines real hardware; calibration/faceplate may be oversized fallback.

        An exact model may intentionally use a larger generic visual profile when no
        model-specific faceplate exists yet. That visual geometry is capacity only and
        must never create additional physical ports downstream. The Core-side contract
        is therefore: assigned visual capacity must be large enough to draw every real
        RJ45/uplink position, while registry topology remains authoritative.
        """
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

            candidates = profiles.get(profile_name) or []
            if not candidates:
                errors.append(
                    f"{model}: calibration profile {profile_name!r} has no source JSON in src/calibration"
                )
                continue

            matching_faceplate = [item for item in candidates if _image_file(item[1]) == faceplate]
            usable = matching_faceplate or candidates

            capacities = [
                (
                    path,
                    calibration,
                    _geometry_count(calibration, "ports"),
                    _geometry_count(calibration, "sfp"),
                )
                for path, calibration in usable
            ]
            adequate = [
                item
                for item in capacities
                if item[2] >= expected_rj45 and item[3] >= expected_sfp
            ]

            if not adequate:
                described = ", ".join(
                    f"{path.name}={rj45} RJ45/{sfp} uplink"
                    for path, _, rj45, sfp in capacities
                )
                errors.append(
                    f"{model}: registry requires at least {expected_rj45} RJ45/"
                    f"{expected_sfp} uplink positions but profile {profile_name!r} "
                    f"provides only: {described}"
                )

            if matching_faceplate:
                # At least one calibration payload explicitly targets the assigned faceplate.
                pass
            elif len(candidates) == 1:
                calibration_faceplate = _image_file(candidates[0][1])
                if calibration_faceplate and calibration_faceplate != faceplate:
                    errors.append(
                        f"{model}: registry faceplate {faceplate!r} disagrees with "
                        f"{candidates[0][0].name} image {calibration_faceplate!r}"
                    )
            else:
                names = ", ".join(path.name for path, _ in candidates)
                errors.append(
                    f"{model}: profile {profile_name!r} has multiple calibration payloads "
                    f"but none targets assigned faceplate {faceplate!r}; candidates: {names}"
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

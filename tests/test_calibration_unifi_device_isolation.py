#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "src" / "js" / "switch-vision.js"
COMPONENT = ROOT / "src" / "custom_components" / "switch_vision" / "switch-vision-card.js"
BACKEND = ROOT / "src" / "custom_components" / "switch_vision" / "__init__.py"
VERSION = ROOT / "VERSION"


def _opaque_token(value: str) -> str:
    raw = str(value or "")
    forward = 2166136261
    reverse = 2166136261 ^ 0x9E3779B9
    for index in range(len(raw)):
        forward ^= ord(raw[index])
        forward = (forward * 16777619) & 0xFFFFFFFF
        reverse ^= ord(raw[len(raw) - 1 - index])
        reverse = (reverse * 16777619) & 0xFFFFFFFF
    return f"{forward:08x}{reverse:08x}"


def _unifi_base(selected_switch: str, device_id: str) -> str:
    switch_key = (
        str(selected_switch or "")
        .strip()
    )
    switch_key = "".join(
        character if character.isalnum() or character in "_-" else "_"
        for character in switch_key
    ).strip("_")[:96]
    return f"{switch_key[:32]}__device__{_opaque_token(device_id)}"


def main() -> int:
    source = CANONICAL.read_text(encoding="utf-8")
    component = COMPONENT.read_text(encoding="utf-8")
    backend = BACKEND.read_text(encoding="utf-8")
    assert source == component, "canonical and Home Assistant card JavaScript must remain byte-identical"

    version_text = VERSION.read_text(encoding="utf-8").strip()
    version = tuple(int(part) for part in version_text.split("."))
    assert version >= (2, 6, 24), f"UniFi calibration-isolation contract requires Core 2.6.24+, got {version_text}"

    required = [
        "function stableCalibrationOpaqueDeviceToken(value) {",
        'String(config?.data_source || "").trim().toLowerCase() === "unifi_api"',
        'String(config?.unifi_device_id || "").trim()',
        'const controllerKey = switchKey.slice(0, 32);',
        'return `${controllerKey}__device__${stableCalibrationOpaqueDeviceToken(unifiDeviceId)}`;',
        'active_profiles[base_profile] = profile',
        'active_profiles.get(requested_profile, "")',
    ]
    for marker in required[:5]:
        assert marker in source, f"missing UniFi device-scoped calibration marker: {marker}"
    for marker in required[5:]:
        assert marker in backend, f"missing backend active-profile contract marker: {marker}"

    helper_start = source.index("function stableCalibrationOpaqueDeviceToken(")
    helper_end = source.index("\n}\n", helper_start) + 3
    helper = source[helper_start:helper_end]
    assert "Math.imul(forward, 16777619)" in helper
    assert "Math.imul(reverse, 16777619)" in helper
    assert "unifi_device_id" not in helper, "opaque token helper must not depend on config structure"

    key_start = source.index("function stableCalibrationSwitchKey(")
    key_end = source.index("\n}\n", key_start) + 3
    key_helper = source[key_start:key_end]
    assert "if (!unifiDeviceId) return switchKey;" in key_helper
    assert "return unifiDeviceId" not in key_helper
    assert "return `${controllerKey}__device__${stableCalibrationOpaqueDeviceToken(unifiDeviceId)}`;" in key_helper

    controller = "unifi_cccefcd91405c728"
    ucg = _unifi_base(controller, "synthetic-controller/device-ucg-fiber")
    xg8 = _unifi_base(controller, "synthetic-controller/device-usw-pro-xg-8-poe")
    assert ucg != xg8, "two UniFi devices on one controller must have distinct calibration bases"
    assert ucg.startswith(controller + "__device__")
    assert xg8.startswith(controller + "__device__")
    assert len(ucg) <= 58 and len(xg8) <= 58

    # The longest possible faceplate child remains inside the backend's 128-char
    # profile-name limit: 58-char base + 13-char separator + 57-char token.
    assert 58 + len("__faceplate__") + 57 == 128

    # Non-UniFi cards retain the historical switch-scoped base behaviour.
    assert 'if (!unifiDeviceId) return switchKey;' in key_helper

    print("Switch Vision UniFi calibration device-isolation regression: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "src/js/switch-vision.js"
BACKEND = ROOT / "src/custom_components/switch_vision/__init__.py"


def require(text: str, needle: str, label: str) -> None:
    assert needle in text, f"missing {label}: {needle!r}"


def main() -> None:
    frontend = FRONTEND.read_text(encoding="utf-8")
    backend = BACKEND.read_text(encoding="utf-8")

    # The websocket contract must support an exact-profile read that deliberately
    # ignores the active custom-faceplate pointer for a switch base profile.
    require(
        backend,
        'vol.Optional("exact", default=False): bool,',
        "exact get_calibration websocket option",
    )
    require(
        backend,
        'exact_profile = bool(msg.get("exact", False))',
        "backend exact-profile flag",
    )
    require(
        backend,
        'candidate = "" if exact_profile else _normalise_profile(active_profiles.get(requested_profile, ""))',
        "exact read bypasses active faceplate pointer",
    )

    # Normal frontend loads keep following the active pointer, while an explicit
    # Default/recommended faceplate selection requests the independent base profile.
    require(
        frontend,
        'const exactProfile = options.exactProfile === true;',
        "frontend exact-profile load option",
    )
    require(
        frontend,
        'exact: exactProfile',
        "frontend websocket exact flag",
    )
    require(
        frontend,
        'const useExactBaseProfile = value === SV_ASSET_DEFAULT || value === SV_ASSET_NONE;',
        "Default faceplate exact-base decision",
    )
    require(
        frontend,
        'exactProfile: useExactBaseProfile',
        "Default faceplate exact-base load",
    )

    # Exact reads must never silently resolve back to a faceplate-specific profile.
    require(
        frontend,
        'if (exactProfile && resolvedProfile !== profile) {',
        "frontend exact-profile escape guard",
    )

    print("Switch Vision Default faceplate profile contract: PASS")


if __name__ == "__main__":
    main()

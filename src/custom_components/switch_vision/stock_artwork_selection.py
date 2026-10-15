"""Single-authority switch-scoped stock art selection and visual reset.

Caller must verify the incoming SHA/geometry pair and the exact existing pin,
and must have explicit admin consent. Changes only the passed (not persisted)
Home Assistant storage dict. Caller saves it once under the storage lock.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any


def apply_approved_switch_artwork(
    state: dict[str, Any], base: str, previous_name: str,
    name: str, revision: dict[str, Any],
) -> list[str]:
    """Replace exactly one switch's saved Calibration and stock selection."""
    if (not isinstance(base, str)
            or not base.startswith(("native_", "custom_"))
            or "__faceplate__" in base or len(base) > 145
            or not isinstance(previous_name, str)
            or not isinstance(name, str)
            or previous_name != Path(previous_name).name
            or name != Path(name).name):
        raise ValueError("Invalid switch artwork identity.")
    if not isinstance(revision, dict) or revision.get("filename") != name:
        raise ValueError("The selected factory revision is inconsistent.")

    profiles = state.setdefault("profiles", {})
    active_profiles = state.setdefault("active_profiles", {})
    pins = state.setdefault("stock_artwork_choices", {})
    if not all(isinstance(value, dict) for value in (profiles, active_profiles, pins)):
        raise ValueError("Invalid stored Calibration containers.")
    pin = pins.get(base)
    if not isinstance(pin, dict) or pin.get("filename") != previous_name:
        raise ValueError("Switch artwork selection became stale.")

    prefix = base + "__faceplate__"
    removed = [profile for profile in list(profiles)
               if isinstance(profile, str)
               and (profile == base or profile.startswith(prefix))]
    earlier = pin.get("eligible_faceplates", [])
    if not isinstance(earlier, list):
        earlier = []
    eligible: list[str] = []
    for candidate in [previous_name, *earlier[:16], name]:
        if (isinstance(candidate, str) and candidate == Path(candidate).name
                and candidate.lower().endswith(".png") and len(candidate) <= 145
                and candidate not in eligible):
            eligible.append(candidate)

    for profile in removed:
        profiles.pop(profile, None)
    active_profiles.pop(base, None)
    pins[base] = {
        "filename": name,
        "sha256": revision["sha256"],
        "version": revision["version"],
        "geometry_sha256": revision["geometry_sha256"],
        "eligible_faceplates": eligible[-16:],
    }
    return removed

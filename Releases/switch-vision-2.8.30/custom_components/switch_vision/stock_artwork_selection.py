"""Single-authority switch-scoped stock art selection and visual reset.

Caller must verify the incoming SHA/geometry pair and the exact existing pin,
and must have explicit admin consent. Changes only the passed (not persisted)
Home Assistant storage dict. Caller saves it once under the storage lock.
"""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import re
from typing import Any, Callable


def initial_stock_choice(
    recommended_file: str, recommended_sha: str,
    saved_file: str = "", saved_sha: str = "",
) -> dict[str, Any] | None:
    """First-use pin: an existing *verified* saved faceplate wins over a new model default.

    An unverified old saved image must not be silently labelled as the new
    selection. The caller supplies SHA values only after manifest/byte checks.
    """
    if saved_file and saved_file != recommended_file:
        if not re.fullmatch(r"[a-f0-9]{64}", saved_sha):
            return None
        return {
            "filename": saved_file,
            "sha256": saved_sha,
            "eligible_faceplates": [saved_file, recommended_file],
        }
    return {
        "filename": recommended_file,
        "sha256": recommended_sha,
        "eligible_faceplates": [recommended_file],
    }


def recover_implicit_new_default_pin(
    previous: Any, recommended_file: str, recommended_sha: str,
    saved_file: str, saved_sha: str,
) -> dict[str, Any] | None:
    """Recover a previously auto-created latest pin, never an approved choice.

    Older Core builds could seed a new default filename even when the saved
    Native factory still referenced the old stock filename. Only the exact
    legacy first-use structure may be corrected from verified saved bytes.
    """
    if (
        not isinstance(previous, dict)
        or previous.get("filename") != recommended_file
        or previous.get("sha256") != recommended_sha
        or previous.get("version")
        or previous.get("geometry_sha256")
        or previous.get("eligible_faceplates") != [recommended_file]
        or not saved_file
        or saved_file == recommended_file
        or saved_file != Path(saved_file).name
        or not saved_file.endswith(".png")
        or not re.fullmatch(r"[a-f0-9]{64}", saved_sha or "")
    ):
        return None
    return initial_stock_choice(recommended_file, recommended_sha, saved_file, saved_sha)


def expected_artwork_choice_matches(
    pin: Any, filename: str, sha256: str, expected_version: str = "",
) -> bool:
    """Compare the persisted pin, not an inferred display revision.

    Legacy first-use pins contain filename and SHA but no version. Core's
    verified list supplies an historical revision label for those pins; that
    label is not a persisted choice change. An existing saved version remains
    a concurrency guard, while filename/SHA always protect every selection.
    """
    if (not isinstance(pin, dict)
            or pin.get("filename") != filename
            or pin.get("sha256") != sha256):
        return False
    stored_version = str(pin.get("version") or "")
    return not (expected_version and stored_version
                and expected_version != stored_version)


def apply_approved_switch_artwork(
    state: dict[str, Any], base: str, previous_name: str,
    name: str, revision: dict[str, Any],
    validate_factory: Callable[[str, dict[str, Any]], Any],
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
    # The chosen geometry was already byte-verified against Core's local
    # revision manifest. Persist that exact factory here, in the approval's
    # single storage transaction: an unmounted Native card cannot receive an
    # event and must not be required to finish the approved reset later.
    factory = revision.get("geometry")
    image = factory.get("image") if isinstance(factory, dict) else None
    ui = factory.get("ui") if isinstance(factory, dict) else None
    faceplate_ui = ui.get("faceplate") if isinstance(ui, dict) else None
    if (not isinstance(factory, dict)
            or factory.get("schema") != "switch-vision-interactive-calibration-v1"
            or not isinstance(image, dict)
            or image.get("file") != "faceplates/" + name
            or not isinstance(factory.get("ports"), dict)
            or not isinstance(factory.get("sfp"), dict)
            or not isinstance(faceplate_ui, dict)):
        raise ValueError("The selected factory geometry is unavailable or inconsistent.")
    prepared_factory = deepcopy(factory)
    prepared_factory["ui"]["faceplate"].update({
        "file": "__default__", "source": "default", "show": True,
    })
    prepared_factory.update({
        "profile_name": base,
        "base_profile_name": base,
        "profile_scope": "Switch default",
        "faceplate_file": "__default__",
        "user_topology_authoritative": False,
        "stock_faceplate_sha256": revision["sha256"],
    })
    # A SHA match proves byte identity, not that a historical JSON revision is
    # a loadable Calibration. Run Core's complete saved-profile validator before
    # removing any old profiles or changing the approved artwork pin.
    validate_factory(base, prepared_factory)

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
    # The verified factory is now durable before any browser event is sent.
    profiles[base] = prepared_factory
    active_profiles.pop(base, None)
    pins[base] = {
        "filename": name,
        "sha256": revision["sha256"],
        "version": revision["version"],
        "geometry_sha256": revision["geometry_sha256"],
        "eligible_faceplates": eligible[-16:],
    }
    return removed


def rebase_after_confirmed_factory_reset(
    state: dict[str, Any], scope: str, base: str, scope_prefix: str,
    verified_latest: dict[str, dict[str, str]],
    preferred_filename: str = "",
) -> list[str]:
    """Return factory artwork pins to latest only after explicit Reset consent.

    Work on the existing in-memory storage transaction, fail closed before any
    mutation if even one existing pin cannot be paired to verified factory art.
    Ordinary Calibration saves, automatic Core upgrades and Keep Current never
    call this method.
    """
    if scope not in {"switch", "namespace", "all"}:
        raise ValueError("Invalid factory-reset scope.")
    if scope == "switch" and (not base.startswith(("native_", "custom_"))
                             or "__faceplate__" in base or len(base) > 145):
        raise ValueError("Invalid switch reset target.")
    if scope == "namespace" and scope_prefix not in {"native_", "custom_"}:
        raise ValueError("Invalid reset namespace.")
    if preferred_filename and (scope != "switch" or
            preferred_filename != Path(preferred_filename).name or
            not preferred_filename.lower().endswith(".png") or
            len(preferred_filename) > 145):
        raise ValueError("Invalid preferred factory image.")
    pins = state.setdefault("stock_artwork_choices", {})
    if not isinstance(pins, dict):
        raise ValueError("Invalid stored artwork selections.")
    if scope == "switch":
        targets = [base] if base in pins or preferred_filename else []
    elif scope == "namespace":
        targets = [key for key in pins if isinstance(key, str)
                   and key.startswith(scope_prefix)]
    else:
        targets = [key for key in pins if isinstance(key, str)
                   and key.startswith(("native_", "custom_"))]

    replacements: dict[str, dict[str, Any]] = {}
    for target in targets:
        previous = pins.get(target, {})
        if not isinstance(previous, dict):
            raise ValueError("Stored artwork selection is invalid.")
        old_name = str(previous.get("filename") or "")
        name = preferred_filename if scope == "switch" and preferred_filename else old_name
        if (not name or name != Path(name).name or
                not name.lower().endswith(".png") or len(name) > 145):
            raise ValueError("Factory artwork filename is invalid.")
        revision = verified_latest.get(name)
        if (not isinstance(revision, dict) or revision.get("filename") != name
                or revision.get("path") != "faceplates/" + name
                or not isinstance(revision.get("sha256"), str)
                or not re.fullmatch("[a-f0-9]{64}", revision["sha256"])
                or not isinstance(revision.get("geometry_sha256"), str)
                or not re.fullmatch("[a-f0-9]{64}", revision["geometry_sha256"])
                or not isinstance(revision.get("version"), str)
                or not revision["version"].startswith("sha-")):
            raise ValueError("Latest factory image/geometry is not verified.")
        earlier = previous.get("eligible_faceplates", [])
        if not isinstance(earlier, list):
            earlier = []
        allowed = []
        for filename in [old_name, *earlier[:16], name]:
            if (isinstance(filename, str) and filename == Path(filename).name
                    and filename.lower().endswith(".png") and len(filename) <= 145
                    and filename not in allowed):
                allowed.append(filename)
        replacements[target] = {
            "filename": name,
            "sha256": revision["sha256"],
            "geometry_sha256": revision["geometry_sha256"],
            "version": revision["version"],
            "eligible_faceplates": allowed[-16:],
        }
    pins.update(replacements)
    return sorted(replacements)

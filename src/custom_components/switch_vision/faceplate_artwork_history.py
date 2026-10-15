"""Read-only, provenance-checked stock artwork version binding.

Core saves the current stock SHA with each future user Calibration save.
Installer preserves prior *verified* stock PNG bytes outside the replaceable
faceplates directory. Legacy profiles may use its first retained original.
No profile is reset automatically, and no renderer/geometry is rewritten.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from typing import Any

_SHA = re.compile(r"^[0-9a-f]{64}$")
_FILE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,140}\.png$")
_MAX_BYTES = 32 * 1024 * 1024
STOCK_SHA_FIELD = "stock_faceplate_sha256"


def stock_filename(calibration: dict[str, Any]) -> str:
    ui = calibration.get("ui")
    ui = ui if isinstance(ui, dict) else {}
    faceplate = ui.get("faceplate")
    faceplate = faceplate if isinstance(faceplate, dict) else {}
    selected = str(faceplate.get("file") or "default").strip()
    source = str(faceplate.get("source") or "default").strip().lower()
    if source not in ("", "default", "custom"):
        return ""
    img = calibration.get("image")
    img = img if isinstance(img, dict) else {}
    filename = str(img.get("file") or "")
    if filename.startswith("faceplates/"):
        filename = filename[len("faceplates/"):]
    if not _FILE.fullmatch(filename):
        return ""
    if selected in ("", "default", "__default__"):
        return filename
    # The existing 3850/other factory profiles may select their bundled
    # filename as a 'custom' visual even though the pixels remain stock.
    return filename if selected == filename else ""


def digest_at(path: Path) -> str:
    if not path.is_file() or path.is_symlink():
        return ""
    try:
        if path.stat().st_size > _MAX_BYTES:
            return ""
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return ""


def current_stock_sha(root: Path, calibration: dict[str, Any],
                      stock_assets: dict[str, Any]) -> str:
    name = stock_filename(calibration)
    expected = stock_assets.get("faceplates", {}).get(name) if name else ""
    if not isinstance(expected, str) or not _SHA.fullmatch(expected):
        return ""
    actual = digest_at(root / "faceplates" / name)
    return actual if actual == expected else ""


def saved_artwork(root: Path, calibration: dict[str, Any],
                  current_sha: str) -> tuple[str, str]:
    """Return saved SHA and verified historical preview path, if possible.

    The filename is *never* versioned. The previous bytes live in an
    independent managed history area, not the stock catalogue.
    """
    name = stock_filename(calibration)
    if not name or not _SHA.fullmatch(current_sha):
        return "", ""
    saved = calibration.get(STOCK_SHA_FIELD)
    if saved is not None:
        if not isinstance(saved, str) or not _SHA.fullmatch(saved):
            return "", ""
        if saved == current_sha:
            return saved, ""
        revision = revision_choice(root, name, saved, current_sha)
        if revision and revision["path"].startswith("faceplates-old/"):
            return saved, revision["path"]
        relative = f"faceplate-history/{saved}/{name}"
    else:
        # Legacy profiles predate Core's server-owned save-time hash. The
        # installer records the earliest verified installed stock art when
        # it first replaces a PNG; never guess old bytes from a filename.
        relative = f"faceplate-history/legacy/{name}"
    history_root = root / "faceplate-history"
    if history_root.is_symlink() or (root / "faceplate-history" / relative.split("/")[1]).is_symlink():
        return "", ""
    historical = digest_at(root / relative)
    if not historical or historical == current_sha:
        return "", ""
    if saved is not None and historical != saved:
        return "", ""
    if saved is None and digest_at(history_root / historical / name) != historical:
        # The legacy alias is trustworthy only with its content-addressed
        # companion, both retained from an installer-verified old stock PNG.
        return "", ""
    return historical, relative


def verified_choice(root: Path, filename: str, selected_sha: str,
                    current_sha: str, selected_version: str = "",
                    selected_geometry_sha: str = "") -> dict[str, Any]:
    """Resolve a switch's accepted stock artwork without trusting a filename.

    The caller supplies current_sha only after checking the stock manifest.
    Historical pixels are usable only if their actual SHA equals the saved pin.
    A missing historical original is reported; it is never fabricated from the
    new same-name artwork or passed through a path supplied by the browser.
    """
    if not _FILE.fullmatch(filename):
        return {}
    if not isinstance(selected_sha, str) or not _SHA.fullmatch(selected_sha):
        return {}
    if current_sha and not _SHA.fullmatch(current_sha):
        return {}
    if current_sha:
        bundle = revision_choice(root, filename, selected_sha, current_sha, selected_version)
        if bundle and (not selected_geometry_sha or
                       bundle.get("geometry_sha256") == selected_geometry_sha):
            return bundle
        if selected_version:
            local = retained_revision(root, filename, selected_sha,
                                      selected_version, selected_geometry_sha)
            if local:
                return {**local, "current_sha256": current_sha}
            return {"filename": filename, "sha256": selected_sha,
                    "current_sha256": current_sha, "unavailable": "true"}
    if current_sha and selected_sha == current_sha:
        return {"filename": filename, "sha256": selected_sha,
                "current_sha256": current_sha, "path": f"faceplates/{filename}"}
    directory = root / "faceplate-history"
    revision = directory / selected_sha
    if directory.is_symlink() or revision.is_symlink():
        return {}
    relative = f"faceplate-history/{selected_sha}/{filename}"
    if digest_at(root / relative) != selected_sha:
        return {"filename": filename, "sha256": selected_sha,
                "current_sha256": current_sha, "unavailable": "true"}
    return {"filename": filename, "sha256": selected_sha,
            "current_sha256": current_sha, "path": relative}


def pin_for_profile(root: Path, filename: str, current_sha: str,
                    saved_calibration: dict[str, Any] | None) -> str:
    """Seed a new switch pin from its verified previous saved art, if any."""
    if saved_calibration and stock_filename(saved_calibration) == filename:
        old_sha, _ = saved_artwork(root, saved_calibration, current_sha)
        if old_sha:
            return old_sha
    return current_sha


def recorded_preupgrade_choice(root: Path, base: str, name: str,
                               installed_sha: str) -> str:
    """Use a private Installer pre-replacement record, never a guessed image.

    The record must name this already-configured switch and image, match the
    installed new bytes, and point at digest-verified preserved previous bytes.
    A missing record cannot manufacture an old version for a new switch.
    """
    if not re.fullmatch(r"(?:native|custom)_[A-Za-z0-9_-]{1,96}", base):
        return ""
    if not _FILE.fullmatch(name) or not _SHA.fullmatch(installed_sha):
        return ""
    file = root.parent.parent / "switch-vision-faceplate-upgrades.json"
    try:
        if file.is_symlink() or not file.is_file() or file.stat().st_size > 512 * 1024:
            return ""
        payload = json.loads(file.read_text(encoding="utf-8"))
        if not isinstance(payload, dict) or payload.get("schema") != "switch-vision-faceplate-upgrade-record-v1":
            return ""
        entry = payload.get("choices", {}).get(base, {}).get(name, {})
        if not isinstance(entry, dict) or entry.get("after") != installed_sha:
            return ""
        before = entry.get("before")
        if not isinstance(before, str) or not _SHA.fullmatch(before) or before == installed_sha:
            return ""
        choice = verified_choice(root, name, before, installed_sha)
        return before if choice.get("path") == f"faceplate-history/{before}/{name}" else ""
    except (OSError, ValueError, AttributeError, TypeError):
        return ""


_VERSION = re.compile(r"^\d+\.\d+\.\d+$")


def catalog_revisions(root: Path, filename: str) -> list[dict[str, Any]]:
    """Return only manifest-bound, byte-verified artwork+factory geometry pairs."""
    if not _FILE.fullmatch(filename):
        return []
    file = root / "faceplates-old" / "manifest.json"
    try:
        if file.is_symlink() or file.stat().st_size > 1024 * 1024:
            return []
        data = json.loads(file.read_text(encoding="utf-8"))
        if data.get("schema") != 1 or not _VERSION.fullmatch(str(data.get("core_version", ""))):
            return []
        versions = data.get("faceplates", {}).get(filename, [])
        if not isinstance(versions, list) or len(versions) > 3:
            return []
    except (OSError, TypeError, ValueError, AttributeError):
        return []
    verified = []
    for item in versions:
        if not isinstance(item, dict):
            continue
        version = str(item.get("version", ""))
        sha = str(item.get("sha256", ""))
        geo_sha = str(item.get("geometry_sha256", ""))
        if (not _VERSION.fullmatch(version) or not _SHA.fullmatch(sha)
                or not _SHA.fullmatch(geo_sha) or item.get("filename") != filename):
            continue
        latest = item.get("path") == "faceplates/" + filename
        path = ("faceplates/" + filename if latest
                else f"faceplates-old/{version}/{filename}")
        geo_path = ("calibration/" + str(item.get("geometry_path", "")).split("/")[-1]
                    if latest else f"faceplates-old/{version}/{filename[:-4]}.json")
        if item.get("path") != path or item.get("geometry_path") != geo_path:
            continue
        if (not latest and (root / "faceplates-old" / version).is_symlink()):
            continue
        image = root / path
        geometry = root / geo_path
        if digest_at(image) != sha or digest_at(geometry) != geo_sha:
            continue
        try:
            factory = json.loads(geometry.read_text(encoding="utf-8"))
            if (not isinstance(factory, dict) or factory.get("schema") != "switch-vision-interactive-calibration-v1"
                    or factory.get("image", {}).get("file") != "faceplates/" + filename
                    or not isinstance(factory.get("ports"), dict)
                    or not isinstance(factory.get("sfp"), dict)):
                continue
        except (ValueError, OSError, AttributeError):
            continue
        verified.append({"version": version, "filename": filename, "sha256": sha,
                         "geometry_sha256": geo_sha, "path": path,
                         "geometry_path": geo_path, "geometry": factory})
    return verified


def retained_revision(root: Path, filename: str, sha: str,
                      version: str, geometry_sha: str = "") -> dict[str, Any]:
    """Resolve a dropped selected pair preserved locally by Installer.

    Only an exact server-pinned image/version/geometry pair may use this
    installation-local fallback. The shipped selection catalogue stays capped.
    """
    if (not _FILE.fullmatch(filename) or not _SHA.fullmatch(str(sha))
            or not _VERSION.fullmatch(str(version))
            or (geometry_sha and not _SHA.fullmatch(str(geometry_sha)))):
        return {}
    directory = root / "faceplate-history" / "revisions"
    manifest = directory / "manifest.json"
    try:
        if (directory.is_symlink() or manifest.is_symlink()
                or manifest.stat().st_size > 1024 * 1024):
            return {}
        data = json.loads(manifest.read_text(encoding="utf-8"))
        if data.get("schema") != 1:
            return {}
        versions = data.get("faceplates", {}).get(filename, [])
        if not isinstance(versions, list) or len(versions) > 256:
            return {}
        for item in versions:
            if (not isinstance(item, dict) or item.get("version") != version
                    or item.get("filename") != filename
                    or item.get("sha256") != sha
                    or not _SHA.fullmatch(str(item.get("geometry_sha256", "")))
                    or (geometry_sha and item["geometry_sha256"] != geometry_sha)):
                continue
            path = f"faceplate-history/revisions/{version}/{filename}"
            geometry_path = f"faceplate-history/revisions/{version}/{filename[:-4]}.json"
            if item.get("path") != path or item.get("geometry_path") != geometry_path:
                continue
            if (directory.joinpath(version).is_symlink()
                    or digest_at(root / path) != sha
                    or digest_at(root / geometry_path) != item["geometry_sha256"]):
                continue
            factory = json.loads((root / geometry_path).read_text(encoding="utf-8"))
            if (not isinstance(factory, dict)
                    or factory.get("schema") != "switch-vision-interactive-calibration-v1"
                    or factory.get("image", {}).get("file") != "faceplates/" + filename
                    or not isinstance(factory.get("ports"), dict)
                    or not isinstance(factory.get("sfp"), dict)):
                continue
            return {**item, "geometry": factory}
    except (OSError, TypeError, ValueError, AttributeError):
        return {}
    return {}


def revision_choice(root: Path, filename: str, sha: str,
                    current_sha: str, version: str = "") -> dict[str, Any]:
    """Never accept a revision from a browser or unverified manifest."""
    if not _SHA.fullmatch(str(sha)) or not _SHA.fullmatch(str(current_sha)):
        return {}
    for item in reversed(catalog_revisions(root, filename)):
        if item["sha256"] == sha and (not version or item["version"] == version):
            return {**item, "current_sha256": current_sha}
    return {}


def revision_index(root: Path) -> dict[str, list[dict[str, str]]]:
    """Small preview index; full trusted geometry is delivered only for selected art."""
    file = root / "faceplates-old" / "manifest.json"
    try:
        if file.is_symlink() or file.stat().st_size > 1024 * 1024:
            return {}
        data = json.loads(file.read_text(encoding="utf-8"))
        images = data.get("faceplates", {})
        if data.get("schema") != 1 or not isinstance(images, dict) or len(images) > 128:
            return {}
    except (ValueError, TypeError, OSError, AttributeError):
        return {}
    result = {}
    for name in images:
        if not isinstance(name, str) or not _FILE.fullmatch(name):
            continue
        found = catalog_revisions(root, name)
        if found:
            result[name] = [{key: row[key] for key in
                             ("version", "filename", "sha256", "geometry_sha256", "path")}
                            for row in found]
    return result

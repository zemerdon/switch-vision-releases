"""Deterministic Core-release faceplate revisions from local Git history.

A faceplate revision always contains the PNG and its contemporary factory
geometry. No Installer state, filename guesses, or additional version counter.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess

_VERSION = re.compile(r"^\d+\.\d+\.\d+$")


def _git(repo: Path, *arguments: str) -> bytes | None:
    result = subprocess.run(
        ["git", "-C", str(repo), *arguments],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    return result.stdout if result.returncode == 0 else None


def _previous(repo: Path, commit: str, path: str) -> bytes | None:
    return _git(repo, "show", f"{commit}^:{path}")


def _digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _geometry_file(src: Path, filename: str) -> str:
    stem = filename[:-4]
    for candidate in (f"faceplate-{stem}.json", f"faceplate-stock-{stem}.json"):
        if (src / "calibration" / candidate).is_file():
            return candidate
    return ""


def _pair(png: bytes | None, geometry: bytes | None, filename: str) -> bool:
    if not png or not geometry or len(png) > 32 * 1024 * 1024:
        return False
    try:
        item = json.loads(geometry)
        image = item.get("image", {})
        return (isinstance(item, dict) and item.get("schema") == "switch-vision-interactive-calibration-v1"
                and isinstance(image, dict) and image.get("file") == "faceplates/" + filename
                and isinstance(item.get("ports"), dict) and isinstance(item.get("sfp"), dict))
    except (ValueError, AttributeError):
        return False


def generate(repo: Path, release: Path, version: str) -> dict:
    """Build bundled versioned image/geometry pairs from exact Git history.

    Historical revisions get their *outgoing* version from the predecessor
    commit's VERSION; a new worktree image/geometry edit is compared against HEAD.
    A missing/untrusted previous pair is never fabricated.
    """
    src = repo / "src"
    destination = release / "faceplates-old"
    destination.mkdir(parents=True, exist_ok=True)
    catalog: dict[str, list[dict]] = {}
    for image in sorted((src / "faceplates").glob("*.png")):
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,140}\.png", image.name):
            continue
        geometry_name = _geometry_file(src, image.name)
        if not geometry_name:
            continue
        image_path = "src/faceplates/" + image.name
        geometry_path = "src/calibration/" + geometry_name
        current_png = image.read_bytes()
        current_geometry = (src / "calibration" / geometry_name).read_bytes()
        if not _pair(current_png, current_geometry, image.name):
            raise ValueError("Invalid current factory faceplate/geometry pair: " + image.name)
        history = _git(repo, "rev-list", "--reverse", "HEAD", "--", image_path, geometry_path)
        if history is None:
            raise RuntimeError("Local Core history unavailable for faceplate revision build")
        revisions = []
        seen = set()

        def retain(commit: str, old_png: bytes | None, old_geometry: bytes | None,
                   old_version: bytes | None) -> None:
            if not _pair(old_png, old_geometry, image.name) or not old_version:
                return
            old = old_version.decode("ascii", errors="replace").strip()
            if not _VERSION.fullmatch(old):
                raise ValueError("Unversioned historical faceplate revision")
            if old == version:
                return
            key = (_digest(old_png), _digest(old_geometry))
            if key in seen:
                return
            seen.add(key)
            folder = destination / old
            folder.mkdir(parents=True, exist_ok=True)
            filename = image.name
            geometry_output = filename[:-4] + ".json"
            target_png = folder / filename
            target_geometry = folder / geometry_output
            for target, value in ((target_png, old_png), (target_geometry, old_geometry)):
                if target.exists() and target.read_bytes() != value:
                    raise ValueError("Core version identifies conflicting factory faceplate revision")
                target.write_bytes(value)
            revisions.append({
                "version": old, "filename": filename, "sha256": key[0],
                "geometry_sha256": key[1],
                "path": f"faceplates-old/{old}/{filename}",
                "geometry_path": f"faceplates-old/{old}/{geometry_output}",
            })

        for commit in history.decode("ascii").splitlines():
            retain(commit, _previous(repo, commit, image_path),
                   _previous(repo, commit, geometry_path),
                   _previous(repo, commit, "VERSION"))

        head_png = _git(repo, "show", "HEAD:" + image_path)
        head_geometry = _git(repo, "show", "HEAD:" + geometry_path)
        if (head_png != current_png or head_geometry != current_geometry):
            retain("HEAD", head_png, head_geometry, _git(repo, "show", "HEAD:VERSION"))
        latest_key = (_digest(current_png), _digest(current_geometry))
        revisions = [r for r in revisions if (r["sha256"], r["geometry_sha256"]) != latest_key]
        revisions.append({
            "version": version, "filename": image.name, "sha256": latest_key[0],
            "geometry_sha256": latest_key[1], "path": "faceplates/" + image.name,
            "geometry_path": "calibration/" + geometry_name,
        })
        catalog[image.name] = revisions
    data = {"schema": 1, "core_version": version, "faceplates": catalog}
    (destination / "manifest.json").write_text(
        json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return data

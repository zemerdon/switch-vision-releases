#!/usr/bin/env python3
"""Sanitize public attribution metadata before release publication."""
from __future__ import annotations

from pathlib import Path
import argparse
import json
import re
import yaml

PROSE_SUFFIXES = {".md", ".bbcode", ".txt", ".html", ".xml", ".csv"}
SUBMISSION_ID_RE = re.compile(r"(?i)SV[-_]20\d{2}[-_]\d+")
PACKAGE_RE = re.compile(r"(?i)Switch[_ -]Vision[_ -]Contribution[^\s`\"']*")


def _walk_display_names(value: object) -> list[str]:
    names: list[str] = []
    if isinstance(value, dict):
        if "display_name" in value and "public_credit" in value:
            names.append(str(value.get("display_name") or "").strip())
        for child in value.values():
            names.extend(_walk_display_names(child))
    elif isinstance(value, list):
        for child in value:
            names.extend(_walk_display_names(child))
    return names


def collect_private_identities(registry: Path, owner: str) -> set[str]:
    data = yaml.safe_load(registry.read_text(encoding="utf-8")) or {}
    generic = {"", owner.casefold(), "community contributor", "anonymous"}
    identities: set[str] = set()
    for name in _walk_display_names(data):
        if name.casefold() in generic:
            continue
        identities.add(name)
        for token in re.findall(r"[A-Za-z0-9_.@+-]+", name):
            if len(token) >= 4 and token.casefold() not in generic:
                identities.add(token)
    return identities


def sanitize_text(text: str, identities: set[str]) -> str:
    for identity in sorted(identities, key=len, reverse=True):
        text = re.sub(re.escape(identity), "community contributor", text, flags=re.I)
    text = PACKAGE_RE.sub("community submission", text)
    text = SUBMISSION_ID_RE.sub("community validation", text)
    text = re.sub(r"(?i)community contributor['’]s", "community-provided", text)
    text = re.sub(r"(?i)credit\s+`?community contributor`?", "record community validation", text)
    text = re.sub(r"(?i)explicitly credits? community contributor", "uses neutral community attribution", text)
    return text


def sanitize_structured(value: object, identities: set[str], owner: str) -> object:
    if isinstance(value, dict):
        result = {key: sanitize_structured(child, identities, owner) for key, child in value.items()}
        if "display_name" in result and "public_credit" in result:
            name = str(result.get("display_name") or "").strip()
            if name.casefold() != owner.casefold():
                result["display_name"] = "community contributor"
                result["public_credit"] = False
        contributions = result.get("contributions")
        if isinstance(contributions, list):
            for index, row in enumerate(contributions, start=1):
                if isinstance(row, dict) and SUBMISSION_ID_RE.search(str(row.get("id") or "")):
                    row["id"] = f"community-validation-{index}"
        return result
    if isinstance(value, list):
        return [sanitize_structured(child, identities, owner) for child in value]
    if isinstance(value, str):
        return sanitize_text(value, identities)
    return value


def sanitize_registry(path: Path, identities: set[str], owner: str) -> None:
    if path.suffix.lower() == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        data = sanitize_structured(data, identities, owner)
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8", newline="\n")
        return
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    data = sanitize_structured(data, identities, owner)
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8", newline="\n")


def scrub_public_prose(root: Path, identities: set[str]) -> None:
    for path in sorted(root.rglob("*")):
        if not path.is_file() or ".git" in path.parts or path.suffix.lower() not in PROSE_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        updated = sanitize_text(text, identities)
        if updated != text:
            path.write_text(updated, encoding="utf-8", newline="\n")


def sanitize_all_registries(root: Path, identities: set[str], owner: str) -> None:
    for path in sorted(root.rglob("supported_devices.*")):
        if not path.is_file() or ".git" in path.parts or "devices" not in path.parts:
            continue
        if path.suffix.lower() not in {".json", ".yaml", ".yml"}:
            continue
        sanitize_registry(path, identities, owner)


def write_core_release_text(root: Path, version: str, identities: set[str]) -> None:
    entry = f"""## v{version} — Public attribution privacy policy

- Remove contributor and tester identities from public changelog and release-note history unless explicitly approved by the project owner.
- Remove submission identifiers, contribution package names, and submission filenames from public release/history text and structured public contributor metadata.
- Use neutral **Community contributor** wording while preserving technical validation facts.
- Add permanent privacy regression coverage preventing non-approved public attribution from returning.
- No telemetry, device mapping, faceplate, calibration, or runtime behaviour changes.

"""
    for path in (root / "CHANGELOG.md", root / "src/CHANGELOG.md"):
        old = sanitize_text(path.read_text(encoding="utf-8"), identities)
        old = re.sub(rf"^## v{re.escape(version)}.*?(?=^## |\Z)", "", old, flags=re.M | re.S).lstrip()
        path.write_text(entry + old, encoding="utf-8", newline="\n")

    notes = f"""# Switch Vision Core v{version}

This maintenance release applies a general public-attribution privacy policy across Switch Vision release metadata.

Contributor and tester identities are omitted from public changelogs and release notes unless explicitly approved by the project owner. Submission identifiers, contribution package names, and submission filenames are also omitted. Technical validation facts remain intact and use neutral **Community contributor** wording where attribution context is useful.

This release changes privacy/publication policy only; telemetry, device mappings, faceplates, calibration, and runtime behaviour are unchanged.
"""
    for path in (root / "RELEASE_NOTES.md", root / "src/RELEASE_NOTES.md"):
        path.write_text(notes, encoding="utf-8", newline="\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--owner", default="zemerdon")
    parser.add_argument("--core-version")
    args = parser.parse_args()

    root = args.root.resolve()
    registry = root / "src/devices/supported_devices.yaml"
    identities = collect_private_identities(registry, args.owner)
    scrub_public_prose(root, identities)
    sanitize_all_registries(root, identities, args.owner)
    if args.core_version:
        write_core_release_text(root, args.core_version, identities)
    print(f"Sanitized public attribution metadata; neutralized {len(identities)} identity token(s).")


if __name__ == "__main__":
    main()

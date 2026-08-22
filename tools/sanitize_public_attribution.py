#!/usr/bin/env python3
"""Sanitize public attribution metadata before release publication."""
from __future__ import annotations

from pathlib import Path
import argparse
import re
import yaml

TEXT_SUFFIXES = {
    ".md", ".bbcode", ".txt", ".json", ".yaml", ".yml", ".py", ".js",
    ".sh", ".html", ".css", ".xml", ".toml", ".ini", ".cfg", ".csv",
}
SUBMISSION_ID_RE = re.compile(r"(?i)SV-[0-9]{4}-[0-9]+")
PACKAGE_RE = re.compile(r"(?i)Switch[_ -]Vision[_ -]Contribution[^\s`\"']*")


def collect_private_identities(registry: Path, owner: str) -> set[str]:
    data = yaml.safe_load(registry.read_text(encoding="utf-8"))
    generic = {"", owner.casefold(), "community contributor", "anonymous"}
    identities: set[str] = set()
    for item in data.get("devices", []):
        contributor = item.get("contributor") if isinstance(item, dict) else None
        if not isinstance(contributor, dict):
            continue
        name = str(contributor.get("display_name") or "").strip()
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


def neutralize_registry_contributors(registry: Path, owner: str) -> None:
    lines = registry.read_text(encoding="utf-8").splitlines()
    out: list[str] = []
    active = False
    base_indent = 0
    neutral = False
    for line in lines:
        stripped = line.lstrip()
        indent = len(line) - len(stripped)
        if stripped == "contributor:":
            active = True
            base_indent = indent
            neutral = False
            out.append(line)
            continue
        if active and stripped and indent <= base_indent:
            active = False
            neutral = False
        if active and stripped.startswith("display_name:"):
            value = stripped.split(":", 1)[1].strip().strip("\"'")
            if value.casefold() != owner.casefold():
                line = line[:indent] + "display_name: Community contributor"
                neutral = True
        elif active and neutral and stripped.startswith("public_credit:"):
            line = line[:indent] + "public_credit: false"
        out.append(line)
    registry.write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")


def scrub_tree(root: Path, identities: set[str]) -> None:
    for path in sorted(root.rglob("*")):
        if not path.is_file() or ".git" in path.parts or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        updated = sanitize_text(text, identities)
        if updated != text:
            path.write_text(updated, encoding="utf-8", newline="\n")


def write_core_release_text(root: Path, version: str, identities: set[str]) -> None:
    entry = f"""## v{version} — Public attribution privacy policy

- Remove contributor and tester identities from public changelog and release-note history unless explicitly approved by the project owner.
- Remove submission identifiers, contribution package names, and submission filenames from public release/history text and structured public contributor metadata.
- Use neutral **Community contributor** wording while preserving technical validation facts.
- Add a permanent privacy regression so future public releases reject non-approved attribution or private submission references.
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
    scrub_tree(root, identities)
    neutralize_registry_contributors(registry, args.owner)
    if args.core_version:
        write_core_release_text(root, args.core_version, identities)
    print(f"Sanitized public attribution metadata; neutralized {len(identities)} identity token(s).")


if __name__ == "__main__":
    main()

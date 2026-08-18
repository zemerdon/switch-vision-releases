#!/usr/bin/env python3

from hashlib import sha256
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src"
RELEASE = ROOT / "Releases" / "switch-vision-2.2.2"

# build.py intentionally generates these release-only files.
RELEASE_ONLY = {
    "CONTRIBUTING.md",
    "SECURITY.md",
    "manifest.json",
}


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def inventory(root: Path):
    result = {}

    for path in root.rglob("*"):
        if path.is_symlink():
            raise RuntimeError(f"Symlink not permitted: {path}")

        if not path.is_file():
            continue

        if "__pycache__" in path.parts or path.suffix in {".pyc", ".pyo"}:
            raise RuntimeError(f"Python cache material not permitted: {path}")

        rel = path.relative_to(root).as_posix()
        result[rel] = digest(path)

    return result


def main() -> int:
    if not SOURCE.is_dir():
        print(f"Missing source tree: {SOURCE}", file=sys.stderr)
        return 1

    if not RELEASE.is_dir():
        print(f"Missing release tree: {RELEASE}", file=sys.stderr)
        return 1

    source = inventory(SOURCE)
    release = inventory(RELEASE)

    source_names = set(source)
    release_names = set(release)

    unexpected_source = sorted(source_names - release_names)

    unexpected_release = sorted(
        (release_names - source_names) - RELEASE_ONLY
    )

    changed = sorted(
        name
        for name in source_names & release_names
        if name != "manifest.json" and source[name] != release[name]
    )

    errors = []

    if unexpected_source:
        errors.append(
            "Files present only in src/: "
            + ", ".join(unexpected_source)
        )

    if unexpected_release:
        errors.append(
            "Unexpected release-only files: "
            + ", ".join(unexpected_release)
        )

    if changed:
        errors.append(
            "Source/release content differs: "
            + ", ".join(changed)
        )

    actual_release_only = release_names - source_names

    missing_expected = sorted(
        {"CONTRIBUTING.md", "SECURITY.md"} - actual_release_only
    )

    if missing_expected:
        errors.append(
            "Expected generated release files missing: "
            + ", ".join(missing_expected)
        )

    if errors:
        print("Switch Vision Core source/release parity: FAIL")

        for error in errors:
            print(f"- {error}")

        return 1

    print(
        "Switch Vision Core source/release parity: PASS "
        f"({len(source)} source files, {len(release)} release files)"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

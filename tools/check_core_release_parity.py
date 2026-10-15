#!/usr/bin/env python3

from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import faceplate_revision_build  # deterministic build owner for generated pairs

SOURCE = ROOT / "src"

VERSION_FILE = ROOT / "VERSION"
if not VERSION_FILE.is_file():
    raise RuntimeError(f"Missing VERSION file: {VERSION_FILE}")

VERSION = VERSION_FILE.read_text(encoding="utf-8").strip()

if not VERSION:
    raise RuntimeError("VERSION is empty")

RELEASE = ROOT / "Releases" / f"switch-vision-{VERSION}"

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

    generated_archive_names = {name for name in release_names
                               if name.startswith("faceplates-old/")}
    unexpected_release = sorted(
        (release_names - source_names) - RELEASE_ONLY - generated_archive_names
    )

    changed = sorted(
        name
        for name in source_names & release_names
        if name != "manifest.json" and source[name] != release[name]
    )

    errors = []
    # Generated archives are not source files, but every emitted byte must
    # match the exact deterministic revision builder. This is not an exclusion
    # from parity: missing, extra, tampered PNGs, geometry and manifest fail.
    try:
        with TemporaryDirectory(prefix="sv-core-faceplate-parity-") as tmp:
            faceplate_revision_build.generate(ROOT, Path(tmp), VERSION)
            expected_archive = inventory(Path(tmp) / "faceplates-old")
        actual_archive = {
            name[len("faceplates-old/"):]: release[name]
            for name in generated_archive_names
        }
        mismatched = sorted({
            name for name in expected_archive.keys() | actual_archive.keys()
            if expected_archive.get(name) != actual_archive.get(name)
        })
        if mismatched:
            errors.append("Generated faceplate archive differs: " +
                          ", ".join(mismatched[:20]) +
                          (f" (+{len(mismatched)-20} more)" if len(mismatched)>20 else ""))
    except (OSError, RuntimeError, ValueError) as exc:
        errors.append(f"Generated faceplate archive cannot be verified: {exc}")

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

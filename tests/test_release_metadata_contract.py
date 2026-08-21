#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
if not re.fullmatch(r"\d+\.\d+\.\d+", version):
    raise AssertionError(f"VERSION is not an exact semantic version: {version!r}")

release_notes = (ROOT / "RELEASE_NOTES.md").read_text(encoding="utf-8")
changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")

release_heading = next(
    (line.strip() for line in release_notes.splitlines() if line.strip()), ""
)
expected_release_heading = f"# Switch Vision Core v{version}"
assert release_heading == expected_release_heading, (
    "RELEASE_NOTES.md must describe the exact current Core version: "
    f"expected {expected_release_heading!r}, found {release_heading!r}"
)

changelog_heading = next(
    (line.strip() for line in changelog.splitlines() if line.strip()), ""
)
assert re.match(rf"^## v{re.escape(version)}(?:\s|$)", changelog_heading), (
    "CHANGELOG.md must begin with the exact current Core version: "
    f"expected v{version}, found {changelog_heading!r}"
)

print(
    f"Core v{version} release metadata contract: PASS "
    "(VERSION / RELEASE_NOTES.md / CHANGELOG.md)"
)

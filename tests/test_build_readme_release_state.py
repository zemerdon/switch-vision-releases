#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("switch_vision_build", ROOT / "build.py")
assert SPEC is not None and SPEC.loader is not None
BUILD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILD)


def exercise(template: str, expected: str) -> None:
    with tempfile.TemporaryDirectory() as tmp_name:
        tmp = Path(tmp_name)
        readme = tmp / "README.md"
        readme.write_text(template, encoding="utf-8", newline="\n")
        original_root = BUILD.ROOT
        try:
            BUILD.ROOT = tmp
            BUILD.patch_current_release_metadata("9.8.7")
            first = readme.read_text(encoding="utf-8")
            BUILD.patch_current_release_metadata("9.8.7")
            second = readme.read_text(encoding="utf-8")
        finally:
            BUILD.ROOT = original_root
        assert first == second
        assert "### Switch Vision v9.8.7" in first
        assert expected in first


exercise(
    "## Current public Core release\n\n### Switch Vision v1.2.3\n\n**v1.2.3** is the current tested public Switch Vision Core/dashboard release.\n",
    "**v9.8.7** is the current tested public Switch Vision Core/dashboard release.",
)
exercise(
    "## Current Core source version\n\n### Switch Vision v1.2.3\n\n**v1.2.3** is the current tested Switch Vision Core/dashboard source version. Public release status is authoritative on GitHub Releases.\n",
    "**v9.8.7** is the current tested Switch Vision Core/dashboard source version. Public release status is authoritative on GitHub Releases.",
)

with tempfile.TemporaryDirectory() as tmp_name:
    tmp = Path(tmp_name)
    readme = tmp / "README.md"
    readme.write_text(
        "### Switch Vision v1.2.3\n\nUnknown release-state sentence.\n",
        encoding="utf-8",
        newline="\n",
    )
    original_root = BUILD.ROOT
    try:
        BUILD.ROOT = tmp
        try:
            BUILD.patch_current_release_metadata("9.8.7")
        except SystemExit as exc:
            assert str(exc) == "README current-release description not found"
        else:
            raise AssertionError("unknown README release state did not fail closed")
    finally:
        BUILD.ROOT = original_root

build_source = (ROOT / "build.py").read_text(encoding="utf-8")
assert "release_states = {" in build_source
assert "expected exactly one known Core release-state description" in build_source
assert "README release-state descriptions are inconsistent" in build_source

print("Core build README public/source-state contract: PASS")

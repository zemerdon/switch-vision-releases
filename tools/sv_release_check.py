#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
JS_FILES = (
    "src/js/switch-vision.js",
    "src/custom_components/switch_vision/switch-vision-card.js",
    "src/custom_components/switch_vision/switch-vision-panel.js",
    "src/custom_components/switch_vision/switch-vision-dashboard-strategy.js",
)
PYTHON_FILES = (
    "src/custom_components/switch_vision/__init__.py",
    "src/custom_components/switch_vision/config_flow.py",
    "src/devices/generate_supported_devices.py",
)
GENERATED_ROOTS = ("src", "Releases", "tests", "tools")


def run(args: list[str], cwd: Path) -> str:
    proc = subprocess.run(
        args,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if proc.stdout:
        print(proc.stdout, end="" if proc.stdout.endswith("\n") else "\n")
    if proc.returncode:
        raise SystemExit(
            f"Core release check command failed ({proc.returncode}): {' '.join(args)}"
        )
    return proc.stdout or ""


def git_status(root: Path) -> str:
    return subprocess.check_output(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=root,
        text=True,
    )


def validate_version_resource_contract(root: Path, version: str) -> None:
    expected_resource = f"/local/switch-vision/js/switch-vision.js?v={version}"
    component = json.loads(
        (root / "src/custom_components/switch_vision/manifest.json").read_text(
            encoding="utf-8"
        )
    )
    source_manifest = json.loads(
        (root / "src/manifest.json").read_text(encoding="utf-8")
    )
    release_component = json.loads(
        (
            root
            / "Releases"
            / f"switch-vision-{version}"
            / "custom_components"
            / "switch_vision"
            / "manifest.json"
        ).read_text(encoding="utf-8")
    )
    release_manifest = json.loads(
        (
            root / "Releases" / f"switch-vision-{version}" / "manifest.json"
        ).read_text(encoding="utf-8")
    )

    checks = (
        (component.get("version"), version, "source integration version"),
        (source_manifest.get("version"), version, "source package version"),
        (source_manifest.get("resource"), expected_resource, "source resource"),
        (release_component.get("version"), version, "release integration version"),
        (release_manifest.get("version"), version, "release package version"),
        (release_manifest.get("resource"), expected_resource, "release resource"),
    )
    for actual, expected, label in checks:
        if actual != expected:
            raise SystemExit(
                f"Core version/resource contract failed for {label}: "
                f"expected {expected!r}, got {actual!r}"
            )
    print(
        f"Core {version} version/resource contract: PASS ({expected_resource})"
    )


def generated_junk(root: Path) -> list[Path]:
    problems: list[Path] = []
    for relative in GENERATED_ROOTS:
        base = root / relative
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if path.is_dir() and path.name == "__pycache__":
                problems.append(path)
            elif path.is_file() and (
                path.suffix in {".pyc", ".pyo"} or path.name == ".DS_Store"
            ):
                problems.append(path)
    return problems


def reject_generated_junk(root: Path) -> None:
    problems = generated_junk(root)
    if problems:
        shown = ", ".join(str(path.relative_to(root)) for path in problems[:20])
        raise SystemExit(f"Core generated cache/junk material present: {shown}")
    print("Core source hygiene: PASS")


def cleanup_generated_junk(root: Path) -> None:
    for relative in GENERATED_ROOTS:
        base = root / relative
        if not base.exists():
            continue
        for path in sorted(
            (item for item in base.rglob("__pycache__") if item.is_dir()),
            key=lambda item: len(item.parts),
            reverse=True,
        ):
            shutil.rmtree(path, ignore_errors=True)
        for pattern in ("*.pyc", "*.pyo"):
            for path in base.rglob(pattern):
                path.unlink(missing_ok=True)


def compile_python_sources(root: Path) -> None:
    paths = [root / item for item in PYTHON_FILES]
    paths.extend(sorted((root / "tests").glob("*.py")))
    paths.append(root / "tools/sv_release_check.py")
    for path in paths:
        source = path.read_text(encoding="utf-8")
        compile(source, str(path), "exec")
    print(f"Core Python syntax: PASS ({len(paths)} files)")


def run_regressions(root: Path) -> None:
    tests = sorted((root / "tests").glob("test_*.py"))
    if not tests:
        raise SystemExit("Core permanent regression suite is empty")
    for test in tests:
        print(f"=== {test.relative_to(root)} ===")
        run([sys.executable, str(test)], root)
    print(f"Core permanent regression suite: PASS ({len(tests)} tests)")


def remove_ephemeral_build_outputs(root: Path, version: str) -> None:
    paths = (
        root / "Releases" / f"switch-vision-{version}.zip",
        root / "Releases" / f"switch-vision-{version}.zip.sha256",
        root / f"Switch_Vision_v{version}_source.zip",
        root / f"Switch_Vision_v{version}_SHA256SUMS.txt",
    )
    for path in paths:
        path.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the product-owned Switch Vision Core release validation."
    )
    parser.add_argument("--mode", choices=("release",), required=True)
    args = parser.parse_args()
    if args.mode != "release":
        raise SystemExit("unsupported release-check mode")

    root = ROOT
    baseline_status = git_status(root)
    version = (root / "VERSION").read_text(encoding="utf-8").strip()
    if not SEMVER_RE.fullmatch(version):
        raise SystemExit(f"Core VERSION is not exact semantic version: {version!r}")

    reject_generated_junk(root)
    compile_python_sources(root)

    for path in JS_FILES:
        run(["node", "--check", path], root)

    run([sys.executable, "tools/check_core_release_parity.py"], root)
    validate_version_resource_contract(root, version)
    run_regressions(root)

    run([sys.executable, "build.py", "-v", version], root)
    remove_ephemeral_build_outputs(root, version)
    cleanup_generated_junk(root)

    run([sys.executable, "tools/check_core_release_parity.py"], root)
    validate_version_resource_contract(root, version)
    reject_generated_junk(root)

    final_status = git_status(root)
    if final_status != baseline_status:
        print("Core release check changed repository state.", file=sys.stderr)
        print("--- baseline status ---", file=sys.stderr)
        print(baseline_status, end="" if baseline_status.endswith("\n") else "\n", file=sys.stderr)
        print("--- final status ---", file=sys.stderr)
        print(final_status, end="" if final_status.endswith("\n") else "\n", file=sys.stderr)
        return 1

    print(f"Core {version} deterministic release validation: PASS")
    print("SV_RELEASE_CHECK_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

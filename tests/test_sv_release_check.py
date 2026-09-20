#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import re
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENTRY = ROOT / "tools" / "sv_release_check.py"
REQUIREMENTS = ROOT / "tools" / "sv_release_check.requirements.txt"
PIN_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*==[A-Za-z0-9][A-Za-z0-9._+!-]*$")


def load_entrypoint():
    spec = importlib.util.spec_from_file_location("switch_vision_core_release_check", ENTRY)
    if spec is None or spec.loader is None:
        raise AssertionError("could not load Core release-check entrypoint")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    assert ENTRY.is_file()
    assert REQUIREMENTS.is_file()

    source = ENTRY.read_text(encoding="utf-8")
    compile(source, str(ENTRY), "exec")
    for marker in (
        "tools/check_core_release_parity.py",
        "build.py",
        "SV_RELEASE_CHECK_PASS",
        "git_status(root)",
        "reject_generated_junk(root)",
        "cleanup_generated_junk(root)",
        "snapshot_build_outputs(root, version)",
        "restore_build_outputs(baseline_outputs)",
        "node",
        "PYTHONDONTWRITEBYTECODE",
    ):
        assert marker in source, marker

    pins = [
        line.strip()
        for line in REQUIREMENTS.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    assert pins == ["PyYAML==6.0.2"]
    assert all(PIN_RE.fullmatch(line) for line in pins)

    module = load_entrypoint()
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    module.validate_version_resource_contract(ROOT, version)

    # CI deliberately compiles the whole regression suite before executing tests,
    # which creates temporary __pycache__. Hygiene is asserted structurally here
    # and exercised by the release entrypoint itself.
    assert callable(module.reject_generated_junk)
    assert callable(module.cleanup_generated_junk)
    regressions_at = source.index("run_regressions(root)")
    prebuild_cleanup_at = source.index("cleanup_generated_junk(root)", regressions_at)
    snapshot_at = source.index("snapshot_build_outputs(root, version)", regressions_at)
    assert regressions_at < prebuild_cleanup_at < snapshot_at, "release check must clean regression bytecode before the deterministic build"

    with tempfile.TemporaryDirectory(prefix="sv-core-release-output-") as tmp:
        fixture_root = Path(tmp)
        fixture_version = "9.9.9"
        outputs = module.build_output_paths(fixture_root, fixture_version)
        checksum = outputs[1]
        checksum.parent.mkdir(parents=True, exist_ok=True)
        checksum.write_bytes(b"tracked-checksum\n")
        snapshot = module.snapshot_build_outputs(fixture_root, fixture_version)

        outputs[0].write_bytes(b"temporary-zip")
        outputs[2].write_bytes(b"temporary-source-zip")
        outputs[3].write_bytes(b"temporary-private-sums")
        checksum.write_bytes(b"tracked-checksum\n")
        module.restore_build_outputs(snapshot)

        assert checksum.read_bytes() == b"tracked-checksum\n"
        assert not outputs[0].exists()
        assert not outputs[2].exists()
        assert not outputs[3].exists()

        checksum.write_bytes(b"different-checksum\n")
        try:
            module.restore_build_outputs(snapshot)
        except SystemExit as exc:
            assert "changed baseline release artifact" in str(exc)
        else:
            raise AssertionError("release artifact drift was not rejected")
        assert checksum.read_bytes() == b"tracked-checksum\n"

    print("Core product-owned release-check contract: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

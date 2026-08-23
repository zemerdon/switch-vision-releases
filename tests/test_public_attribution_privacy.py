from pathlib import Path
import json
import re
import yaml

ROOT = Path(__file__).resolve().parents[1]
OWNER = "zemerdon"
ALLOWED = {"", OWNER.casefold(), "community contributor", "anonymous"}
SUBMISSION_ID = re.compile(r"(?i)SV[-_]20\d{2}[-_]\d+")
PACKAGE_NAME = re.compile(r"(?i)Switch[_ -]Vision[_ -]Contribution")


def _assert_structured_private_refs_removed(value, path: Path) -> None:
    if isinstance(value, dict):
        for key in value:
            key_text = str(key)
            assert not SUBMISSION_ID.search(key_text), (path, key_text)
            assert not PACKAGE_NAME.search(key_text), (path, key_text)
        if "display_name" in value and "public_credit" in value:
            name = str(value.get("display_name") or "").strip()
            assert name.casefold() in ALLOWED, (path, name)
            if name.casefold() != OWNER.casefold():
                assert value.get("public_credit") is not True, (path, name)
        for child in value.values():
            _assert_structured_private_refs_removed(child, path)
    elif isinstance(value, list):
        for child in value:
            _assert_structured_private_refs_removed(child, path)
    elif isinstance(value, str):
        assert not SUBMISSION_ID.search(value), (path, value)
        assert not PACKAGE_NAME.search(value), (path, value)


def test_all_public_device_registries_are_neutral() -> None:
    registries = [
        path
        for path in ROOT.rglob("supported_devices.*")
        if path.is_file()
        and "devices" in path.parts
        and path.suffix.lower() in {".json", ".yaml", ".yml"}
    ]
    assert registries
    for path in registries:
        if path.suffix.lower() == ".json":
            data = json.loads(path.read_text(encoding="utf-8"))
        else:
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        _assert_structured_private_refs_removed(data, path)


def test_public_release_history_has_no_private_submission_references() -> None:
    paths = [
        ROOT / "CHANGELOG.md",
        ROOT / "RELEASE_NOTES.md",
        ROOT / "src/CHANGELOG.md",
        ROOT / "src/RELEASE_NOTES.md",
    ]
    paths += list((ROOT / "Releases").glob("switch-vision-*/CHANGELOG.md"))
    paths += list((ROOT / "Releases").glob("switch-vision-*/RELEASE_NOTES.md"))
    for path in paths:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        assert not SUBMISSION_ID.search(text), path
        assert not PACKAGE_NAME.search(text), path


if __name__ == "__main__":
    test_all_public_device_registries_are_neutral()
    test_public_release_history_has_no_private_submission_references()
    print("Switch Vision Core public attribution privacy: PASS")

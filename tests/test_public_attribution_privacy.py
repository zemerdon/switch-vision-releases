from pathlib import Path
import re
import yaml

ROOT = Path(__file__).resolve().parents[1]
OWNER = "zemerdon"
ALLOWED = {"", OWNER.casefold(), "community contributor", "anonymous"}
SUBMISSION_ID = re.compile(r"(?i)SV-[0-9]{4}-[0-9]+")
PACKAGE_NAME = re.compile(r"(?i)Switch[_ -]Vision[_ -]Contribution")


def test_public_registry_attribution_is_neutral():
    data = yaml.safe_load((ROOT / "src/devices/supported_devices.yaml").read_text(encoding="utf-8"))
    for item in data.get("devices", []):
        contributor = item.get("contributor") if isinstance(item, dict) else None
        if not isinstance(contributor, dict):
            continue
        name = str(contributor.get("display_name") or "").strip()
        assert name.casefold() in ALLOWED, (item.get("model"), name)
        if name.casefold() != OWNER.casefold():
            assert contributor.get("public_credit") is not True, item.get("model")


def test_public_release_history_has_no_submission_references():
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

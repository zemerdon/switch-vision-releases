from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CARD = ROOT / "src" / "custom_components" / "switch_vision" / "switch-vision-card.js"
MIRROR = ROOT / "src" / "js" / "switch-vision.js"
FACTORY_PROFILE = ROOT / "src" / "calibration" / "faceplate-cisco-3850-12xs.json"
PROFILE = "cisco_3850_12xs"
FILENAME = "cisco-3850-12xs.png"


def _profile_files(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    match = re.search(
        r"const SV_FACEPLATE_PROFILE_FILES = \{(?P<body>.*?)\n\};",
        text,
        re.DOTALL,
    )
    if not match:
        raise AssertionError(f"SV_FACEPLATE_PROFILE_FILES not found in {path}")
    return dict(
        re.findall(
            r'^\s*([A-Za-z0-9_]+):\s*"([^"]+)",?\s*$',
            match.group("body"),
            re.MULTILINE,
        )
    )


def _faceplate_factories(path: Path) -> dict[str, dict]:
    text = path.read_text(encoding="utf-8")
    start_marker = "const SV_FACEPLATE_FACTORY_CALIBRATIONS = "
    end_marker = "\n\nfunction faceplateFactoryCalibrationForFile"
    start = text.find(start_marker)
    if start < 0:
        raise AssertionError(f"factory calibration table not found in {path}")
    start += len(start_marker)
    end = text.find(end_marker, start)
    if end < 0:
        raise AssertionError(f"factory calibration end marker not found in {path}")
    payload = text[start:end].strip()
    if not payload.endswith(";"):
        raise AssertionError(f"factory calibration table malformed in {path}")
    return json.loads(payload[:-1])


def _factory_for_profile(path: Path, profile: str) -> tuple[str | None, dict | None]:
    filename = _profile_files(path).get(profile)
    factory = _faceplate_factories(path).get(filename) if filename else None
    return filename, factory


class C385012XSFactoryBindingTests(unittest.TestCase):
    def test_profile_resolves_to_exact_3850_faceplate_factory(self) -> None:
        expected = json.loads(FACTORY_PROFILE.read_text(encoding="utf-8"))
        for path in (CARD, MIRROR):
            with self.subTest(path=path):
                filename, factory = _factory_for_profile(path, PROFILE)
                self.assertEqual(filename, FILENAME)
                self.assertEqual(factory, expected)
                self.assertEqual(factory["profile"], PROFILE)
                self.assertEqual(factory["model"], "cisco-3850-12xs")
                self.assertEqual(factory["ports"], {})
                self.assertEqual(
                    list(factory["sfp"]),
                    [f"SFP{index}" for index in range(1, 13)],
                )
                self.assertEqual(len(factory["sfp"]), 12)

    def test_mirrored_card_sources_remain_byte_identical(self) -> None:
        self.assertEqual(CARD.read_bytes(), MIRROR.read_bytes())


if __name__ == "__main__":
    unittest.main()

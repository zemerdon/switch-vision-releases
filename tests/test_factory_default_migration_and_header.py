from __future__ import annotations

import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CARD = ROOT / "src" / "js" / "switch-vision.js"
MIRROR = ROOT / "src" / "custom_components" / "switch_vision" / "switch-vision-card.js"
PANEL = ROOT / "src" / "custom_components" / "switch_vision" / "switch-vision-panel.js"


def extract_js_function(source: str, signature: str) -> str:
    start = source.find(signature)
    if start < 0:
        raise AssertionError(f"missing JS function: {signature}")
    brace = source.find("{", start)
    depth = 0
    quote = None
    escape = False
    for pos in range(brace, len(source)):
        char = source[pos]
        if quote is not None:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == quote:
                quote = None
            continue
        if char in {"'", '"', "`"}:
            quote = char
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return source[start:pos + 1]
    raise AssertionError("unterminated JS function")


class FactoryDefaultMigrationAndHeaderTests(unittest.TestCase):
    def test_factory_migration_is_exact_fingerprint_only(self) -> None:
        source = CARD.read_text(encoding="utf-8")
        fn = extract_js_function(source, "function factoryMigrationForStoredCalibration(loaded, recommendation)")
        harness = """
const SV_FACTORY_CALIBRATIONS = {
  legacy: {profile:'legacy', geometry:'old'},
  default_cisco_48_port: {profile:'default_cisco_48_port', geometry:'generic'}
};
const SV_KNOWN_STALE_FACTORY_PROFILES = {
  USWPROMAX24: ['inline'],
  USWPROAGGREGATION: ['default_cisco_48_port']
};
const profileFactories = {inline:{profile:'inline', geometry:'inline'}};
function factoryCalibrationForProfile(profile) { return profileFactories[profile] || null; }
function factoryCalibrationForRecommendation(recommendation) { return recommendation.target || null; }
function calibrationPersistedFingerprint(value) { return JSON.stringify(value); }
function applyCalibrationIdentity(factory, current) { return JSON.parse(JSON.stringify(factory)); }
function ensureCalibrationUi(value) { return value; }
""" + fn + """
function check(value, label) { if (!value) throw new Error(label); }
let migrated = factoryMigrationForStoredCalibration(
  {profile:'legacy', geometry:'old'},
  {model:'Any', profile:'legacy', target:{profile:'legacy', geometry:'new'}}
);
check(migrated && migrated.geometry === 'new', 'same-profile factory migration missing');

migrated = factoryMigrationForStoredCalibration(
  {profile:'legacy', geometry:'old', user_adjustment:1},
  {model:'Any', profile:'legacy', target:{profile:'legacy', geometry:'new'}}
);
check(migrated === null, 'modified calibration was migrated');

migrated = factoryMigrationForStoredCalibration(
  {profile:'inline', geometry:'inline'},
  {model:'USW Pro Max 24', profile:'standard', target:{profile:'standard', geometry:'standard'}}
);
check(migrated && migrated.profile === 'standard', 'reviewed Pro Max migration missing');

migrated = factoryMigrationForStoredCalibration(
  {profile:'inline', geometry:'inline'},
  {model:'Different Model', profile:'standard', target:{profile:'standard', geometry:'standard'}}
);
check(migrated === null, 'unreviewed cross-profile migration was allowed');

migrated = factoryMigrationForStoredCalibration(
  {profile:'default_cisco_48_port', geometry:'generic'},
  {model:'USW Pro Aggregation', profile:'unifi_32sfp', target:{profile:'unifi_32sfp', geometry:'optical'}}
);
check(migrated && migrated.geometry === 'optical', 'reviewed fallback migration missing');
"""
        result = subprocess.run(["node", "-e", harness], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_runtime_persists_only_qualified_factory_migration(self) -> None:
        source = CARD.read_text(encoding="utf-8")
        for marker in (
            "factoryMigrationForStoredCalibration(acceptedCalibration, recommendation)",
            "persistFactoryCalibrationMigration(previousProfile, calibrationValue)",
            'payload.user_topology_authoritative = false;',
            'payload.factory_migrated_from_profile = String(previousProfile || "");',
            "corrected obsolete factory defaults",
        ):
            self.assertIn(marker, source)

    def test_header_contrast_is_independent_of_ha_theme_pairing(self) -> None:
        panel = PANEL.read_text(encoding="utf-8")
        self.assertIn("--sv-panel-header-fg:#eef7ff", panel)
        self.assertIn("--sv-panel-header-bg:#1c242b", panel)
        self.assertIn("background:var(--sv-panel-header-bg);color:var(--sv-panel-header-fg);white-space", panel)
        self.assertIn("background:var(--sv-panel-header-bg);color:var(--sv-panel-header-fg)}", panel)
        self.assertNotIn(".summary{flex:1;min-width:0;border-left:4px solid #3e8fc5;border-radius:8px;padding:9px 12px;background:var(--card-background-color", panel)

    def test_card_sources_remain_identical(self) -> None:
        self.assertEqual(CARD.read_bytes(), MIRROR.read_bytes())


if __name__ == "__main__":
    unittest.main()

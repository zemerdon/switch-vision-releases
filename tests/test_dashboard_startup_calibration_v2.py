from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "src" / "custom_components" / "switch_vision" / "__init__.py"
STRATEGY = ROOT / "src" / "custom_components" / "switch_vision" / "switch-vision-dashboard-strategy.js"
CALIBRATION = ROOT / "src" / "calibration"

backend = BACKEND.read_text(encoding="utf-8")
assert 'if schema_version not in (None, 0, 1, "1", 2, "2"):' in backend

for filename in ("faceplate-unifi-5rj45.json", "faceplate-unifi-8rj45.json"):
    profile = json.loads((CALIBRATION / filename).read_text(encoding="utf-8"))
    assert profile["schema_version"] == 2, filename
    assert profile["status_leds"] == {}, filename

strategy = STRATEGY.read_text(encoding="utf-8")
assert "SWITCH_VISION_RUNTIME_LOOKUP_TIMEOUT_MS = 1000" in strategy
assert "Promise.race([" in strategy
assert "() => resolve(null)" in strategy
assert "SWITCH_VISION_RUNTIME_LOOKUP_TIMEOUT_MS," in strategy
assert "const runtimeVersion = await switchVisionRuntimeVersion(hass);" in strategy

print("Core dashboard startup / calibration v2 contracts: PASS")

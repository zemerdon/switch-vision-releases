from __future__ import annotations

import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CARD = ROOT / "src" / "js" / "switch-vision.js"
CSS = ROOT / "src" / "css" / "switch-vision.css"
BACKEND = ROOT / "src" / "custom_components" / "switch_vision" / "__init__.py"


def extract_js_function(source: str, signature: str) -> str:
    start = source.find(signature)
    if start < 0:
        raise AssertionError(f"JavaScript function not found: {signature}")
    brace = source.find("{", start)
    depth = 0
    quote: str | None = None
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
                return source[start : pos + 1]
    raise AssertionError(f"Closing brace not found for: {signature}")


class UniFiHybridFreshnessTests(unittest.TestCase):
    def test_freshness_rejects_stale_runtime(self) -> None:
        source = CARD.read_text(encoding="utf-8")
        functions = "\n\n".join(
            extract_js_function(source, signature)
            for signature in (
                "function rawUnifiRuntime(config)",
                "function unifiRuntimeFreshness(config)",
                "function unifiRuntime(config)",
            )
        )
        harness = f"""
{functions}
Date.now = () => 200000 * 1000;
function assertTrue(value, label) {{ if (!value) throw new Error(label); }}
function assertFalse(value, label) {{ if (value) throw new Error(label); }}

const fresh = {{
  unifi_refresh_seconds: 30,
  __unifi_runtime: {{
    ports: [],
    freshness: {{ last_success_at: 199990, stale: false, reason: '' }},
    __snapshot_generated_at: 199990
  }}
}};
assertFalse(unifiRuntimeFreshness(fresh).stale, 'fresh runtime marked stale');
assertTrue(unifiRuntime(fresh) !== null, 'fresh runtime rejected');

const failed = {{
  unifi_refresh_seconds: 30,
  __unifi_runtime: {{
    ports: [],
    freshness: {{ last_success_at: 199900, stale: true, reason: 'device_refresh_failed' }},
    __snapshot_generated_at: 200000
  }}
}};
const failedState = unifiRuntimeFreshness(failed);
assertTrue(failedState.stale, 'explicit stale runtime accepted');
assertTrue(failedState.reason === 'device_refresh_failed', 'stale reason lost');
assertTrue(unifiRuntime(failed) === null, 'explicit stale runtime exposed as live');

const aged = {{
  unifi_refresh_seconds: 30,
  __unifi_runtime: {{
    ports: [],
    freshness: {{ last_success_at: 199000, stale: false, reason: '' }},
    __snapshot_generated_at: 199000
  }}
}};
const agedState = unifiRuntimeFreshness(aged);
assertTrue(agedState.stale, 'aged snapshot accepted');
assertTrue(agedState.reason === 'snapshot_age', 'aged snapshot reason missing');
assertTrue(unifiRuntime(aged) === null, 'aged runtime exposed as live');

const producerWindow = {{
  unifi_refresh_seconds: 30,
  __unifi_runtime: {{
    ports: [],
    freshness: {{ last_success_at: 199880, stale: false, reason: '' }},
    __snapshot_generated_at: 199880,
    __snapshot_stale_after_seconds: 180
  }}
}};
assertFalse(unifiRuntimeFreshness(producerWindow).stale, 'producer freshness window ignored');
"""
        result = subprocess.run(
            ["node", "-e", harness], cwd=ROOT, text=True, capture_output=True
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_hybrid_loader_and_warning_contract(self) -> None:
        source = CARD.read_text(encoding="utf-8")
        css = CSS.read_text(encoding="utf-8")
        backend = BACKEND.read_text(encoding="utf-8")
        self.assertIn("hasUnifiBinding()", source)
        self.assertIn("if (!this.hasUnifiBinding() || !this._hass?.callWS) return;", source)
        self.assertIn("__snapshot_generated_at: Number(result?.generated_at || 0)", source)
        self.assertIn("__snapshot_stale_after_seconds: Number(result?.stale_after_seconds || 0)", source)
        self.assertIn('"stale_after_seconds": document.get("stale_after_seconds")', backend)
        self.assertIn("cv-runtime-warning", source)
        self.assertIn(".cv-runtime-warning", css)
        self.assertIn("UniFi telemetry is stale", source)
        self.assertIn("UniFi telemetry is unavailable/stale", source)


if __name__ == "__main__":
    unittest.main()

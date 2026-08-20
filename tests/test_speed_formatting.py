from __future__ import annotations

import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CARD = ROOT / "src" / "js" / "switch-vision.js"


def extract_js_function(source: str, signature: str) -> str:
    start = source.find(signature)
    if start < 0:
        raise AssertionError(f"JavaScript function not found: {signature}")
    brace = source.find("{", start)
    if brace < 0:
        raise AssertionError(f"Opening brace not found for: {signature}")
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


class SpeedFormattingTests(unittest.TestCase):
    def test_fractional_gigabit_speed_is_not_rounded_up(self) -> None:
        source = CARD.read_text(encoding="utf-8")
        function = extract_js_function(source, "function formatSpeedMbps(raw)")
        # formatSpeedMbps delegates input sanitisation to usableValue().  These
        # cases are deliberately valid numeric telemetry, so a tiny identity
        # stub isolates and executes the real formatter without pulling the
        # whole browser card into Node.
        harness = f"""
function usableValue(raw) {{ return raw; }}
{function}
const cases = [
  [1000, '1G'],
  [2500, '2.5G'],
  [5000, '5G'],
  [10000, '10G'],
];
for (const [input, expected] of cases) {{
  const actual = formatSpeedMbps(input);
  if (actual !== expected) {{
    throw new Error(`${{input}} Mbps rendered as ${{actual}}, expected ${{expected}}`);
  }}
}}
"""
        result = subprocess.run(
            ["node", "-e", harness],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()

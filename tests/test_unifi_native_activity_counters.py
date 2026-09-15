#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CARD = ROOT / "src" / "custom_components" / "switch_vision" / "switch-vision-card.js"


def extract_function(source: str, name: str) -> str:
    start = source.find(f"function {name}(")
    if start < 0:
        raise AssertionError(f"missing JavaScript helper: {name}")
    brace = source.find("{", start)
    if brace < 0:
        raise AssertionError(f"opening brace missing for JavaScript helper: {name}")
    depth = 0
    quote = None
    escaped = False
    for index in range(brace, len(source)):
        ch = source[index]
        if quote:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == quote:
                quote = None
            continue
        if ch in {"'", '"', "`"}:
            quote = ch
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return source[start : index + 1]
    raise AssertionError(f"unterminated JavaScript helper: {name}")


class NativeUniFiActivityCounterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = CARD.read_text(encoding="utf-8")

    def test_native_counter_helpers_are_wired_to_activity_and_rate_paths(self) -> None:
        helper = extract_function(self.source, "unifiTrafficCounterSample")
        self.assertIn("traffic.available !== true", helper)
        self.assertIn('direction === "rx" ? "rx_bytes"', helper)
        self.assertIn('direction === "tx" ? "tx_bytes"', helper)
        self.assertIn("traffic.sampled_at", helper)
        self.assertIn("sampledAt * 1000", helper)

        port_reader = extract_function(self.source, "portTrafficCounterSample")
        sfp_reader = extract_function(self.source, "sfpTrafficCounterSample")
        self.assertIn("rawUnifiRuntime(config)", port_reader)
        self.assertIn("unifiAccessPort(config, port)", port_reader)
        self.assertIn("rawUnifiRuntime(config)", sfp_reader)
        self.assertIn("unifiSfpPort(config, port)", sfp_reader)

        port_activity = extract_function(self.source, "testPortActivity")
        port_rates = extract_function(self.source, "portTrafficRates")
        sfp_activity = extract_function(self.source, "testSfpActivity")
        sfp_rates = extract_function(self.source, "sfpTrafficRates")
        self.assertEqual(port_activity.count("portTrafficCounterSample"), 2)
        self.assertEqual(port_rates.count("portTrafficCounterSample"), 2)
        self.assertEqual(sfp_activity.count("sfpTrafficCounterSample"), 2)
        self.assertEqual(sfp_rates.count("sfpTrafficCounterSample"), 2)

    def test_native_counter_sample_uses_producer_timestamp_and_fails_closed(self) -> None:
        helper = extract_function(self.source, "unifiTrafficCounterSample")
        script = helper + r'''
const good = unifiTrafficCounterSample({traffic: {available: true, sampled_at: 1234, rx_bytes: 100, tx_bytes: 250}}, "tx");
const rx = unifiTrafficCounterSample({traffic: {available: true, sampled_at: 1234, rx_bytes: 100, tx_bytes: 250}}, "rx");
const unavailable = unifiTrafficCounterSample({traffic: {available: false, sampled_at: 1234, rx_bytes: 100}}, "rx");
const invalid = unifiTrafficCounterSample({traffic: {available: true, sampled_at: 1234, rx_bytes: -1}}, "rx");
console.log(JSON.stringify({good, rx, unavailable, invalid}));
'''
        result = subprocess.run(
            ["node", "-e", script],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout)
        payload = json.loads(result.stdout.strip())
        self.assertEqual(payload["good"], {"value": 250, "updated": 1234000})
        self.assertEqual(payload["rx"], {"value": 100, "updated": 1234000})
        self.assertIsNone(payload["unavailable"])
        self.assertIsNone(payload["invalid"])


if __name__ == "__main__":
    unittest.main()

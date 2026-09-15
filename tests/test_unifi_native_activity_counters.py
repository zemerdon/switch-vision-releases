#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CARD = ROOT / "src" / "custom_components" / "switch_vision" / "switch-vision-card.js"


def extract_function(source: str, name: str) -> str:
    start = source.find(f"function {name}(")
    if start < 0:
        raise AssertionError(f"missing JavaScript helper: {name}")
    brace = source.find("{", start)
    assert brace >= 0, name
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


def main() -> None:
    source = CARD.read_text(encoding="utf-8")

    helper = extract_function(source, "unifiTrafficCounterSample")
    assert "traffic.available !== true" in helper
    assert 'direction === "rx" ? "rx_bytes"' in helper
    assert 'direction === "tx" ? "tx_bytes"' in helper
    assert "traffic.sampled_at" in helper
    assert "sampledAt * 1000" in helper

    port_reader = extract_function(source, "portTrafficCounterSample")
    sfp_reader = extract_function(source, "sfpTrafficCounterSample")
    assert "rawUnifiRuntime(config)" in port_reader
    assert "unifiAccessPort(config, port)" in port_reader
    assert "rawUnifiRuntime(config)" in sfp_reader
    assert "unifiSfpPort(config, port)" in sfp_reader

    port_activity = extract_function(source, "testPortActivity")
    port_rates = extract_function(source, "portTrafficRates")
    sfp_activity = extract_function(source, "testSfpActivity")
    sfp_rates = extract_function(source, "sfpTrafficRates")
    assert port_activity.count("portTrafficCounterSample") == 2
    assert port_rates.count("portTrafficCounterSample") == 2
    assert sfp_activity.count("sfpTrafficCounterSample") == 2
    assert sfp_rates.count("sfpTrafficCounterSample") == 2

    # Execute the isolated helper so the sample-timestamp and fail-closed
    # semantics are protected by behavior as well as source wiring.
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
    if result.returncode:
        raise AssertionError(result.stdout)
    payload = json.loads(result.stdout.strip())
    assert payload["good"] == {"value": 250, "updated": 1234000}
    assert payload["rx"] == {"value": 100, "updated": 1234000}
    assert payload["unavailable"] is None
    assert payload["invalid"] is None

    print("Core native UniFi snapshot activity counters: PASS")


if __name__ == "__main__":
    main()

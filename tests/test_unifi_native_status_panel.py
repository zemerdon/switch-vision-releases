from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = [
    ROOT / "src/js/switch-vision.js",
    ROOT / "src/custom_components/switch_vision/switch-vision-card.js",
]


def main() -> None:
    for path in FILES:
        text = path.read_text(encoding="utf-8")
        assert "unifi_native_status_fields: true" in text, path
        assert "usableValue(runtime.ip_address)" in text, path
        assert '["model", "ip", "cpu", "memory", "poe", "uptime"]' in text, path
        assert '["model", "ip", "cpu", "memory", "uplink", "uptime"]' in text, path
        assert '["link", "max_speed", "media", "poe", "poe_standard"]' in text, path
        assert '["link", "max_speed", "media"]' in text, path
        assert 'poeSummary = unifiSwitchPoeSummary(runtime)' in text, path
        assert 'function formatUnifiCapabilitySpeed(value)' in text, path
        assert 'function useUnifiNativeStatusFields(config, type, panelNumber = 1)' in text, path
        # The established generic/SNMP rows must not change as a side effect.
        assert 'defaults: ["vlan", "mode", "desc", "link", "rx", "tx"]' in text, path
        assert 'defaults: ["model", "ip", "cpu", "temp", "poe", "uptime", "vendor", "os", "firmware", "serial", "stack", "fans", "psu"]' in text, path
        # UniFi per-port traffic remains explicitly disabled unless a future API
        # genuinely exposes it; this release must not fabricate byte counters.
        assert 'config?.unifi_per_port_traffic !== true' in text, path
    print("UniFi-native status panel regressions: PASS")


if __name__ == "__main__":
    main()

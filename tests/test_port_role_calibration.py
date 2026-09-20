#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
JS = ROOT / "src/js/switch-vision.js"
COMPONENT = ROOT / "src/custom_components/switch_vision/switch-vision-card.js"
REGISTRY = ROOT / "src/devices/supported_devices.yaml"


def main() -> int:
    source = JS.read_text(encoding="utf-8")
    assert source == COMPONENT.read_text(encoding="utf-8"), "card JS copies must remain byte-identical"

    required = [
        'data-cv-field="port-supported-speed"',
        '<label>Port Role',
        'data-cv-field="port-role"',
        'const SV_PORT_ROLES = Object.freeze(["", "lan", "wan", "uplink"]);',
        'function registryPortRoleForGroup(config, group, port)',
        'function effectivePortRole(config, cal, group, port)',
        'editable.item.port_role = normalisePortRole(event.target.value);',
        '"supported_speed", "port_role"',
        'role: formatPortRole(effectivePortRole(config, cal, "rj45", selected.id))',
        'role: formatPortRole(effectivePortRole(config, cal, "sfp", selected.id))',
        '\"model\":\"UDM Pro\"',
        '\"port_roles\":{\"rj45\":{\"9\":\"wan\"}}',
    ]
    for marker in required:
        assert marker in source, f"missing port-role contract marker: {marker}"

    speed_at = source.index('<label>Supported speed')
    role_at = source.index('<label>Port Role', speed_at)
    row_end = source.index('</div>', speed_at)
    assert speed_at < role_at < row_end, "Port Role must sit beside Supported Speed in the Calibration port metadata row"

    data = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    udm = next(item for item in data["devices"] if item["model"] == "UDM Pro")
    assert udm["port_roles"] == {"rj45": {"9": "wan"}}, udm.get("port_roles")

    print("Switch Vision port-role Calibration/registry contract: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

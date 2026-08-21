#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = (ROOT / "src" / "custom_components" / "switch_vision" / "__init__.py").read_text(encoding="utf-8")

assert "from homeassistant.helpers.service import async_register_admin_service" in source
services = {
    "save_calibration": "SAVE_SCHEMA",
    "delete_calibration": "DELETE_SCHEMA",
    "reset_calibrations": "RESET_SCHEMA",
    "reload_calibrations": None,
    "set_ui_density": "UI_DENSITY_SCHEMA",
}
for name, schema in services.items():
    marker = f'async_register_admin_service(hass, DOMAIN, "{name}"'
    assert marker in source, f"{name} is not registered through Home Assistant's admin-service helper"
    assert f'hass.services.async_register(DOMAIN, "{name}"' not in source, f"{name} still has ordinary service registration"
    if schema:
        line = next(line for line in source.splitlines() if marker in line)
        assert f"schema={schema}" in line, f"{name} lost its validation schema"

# Native-header ordering remains separately protected at the WebSocket layer.
ws_marker = "async def websocket_set_native_header_shortcut_order"
pos = source.index(ws_marker)
prefix = source[max(0, pos - 250):pos]
assert "@websocket_api.require_admin" in prefix
print("Core admin-only mutation service contract: PASS")

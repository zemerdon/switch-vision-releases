from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INIT = (ROOT / "src/custom_components/switch_vision/__init__.py").read_text(encoding="utf-8")

for marker in (
    'DELETE_WS_SCHEMA = {',
    '"switch_vision/delete_calibration"',
    'async def _delete_calibration_profile(profile_value: str)',
    'async def websocket_delete_calibration',
    '@websocket_api.require_admin',
    'websocket_api.async_register_command(hass, websocket_delete_calibration)',
    'await _delete_calibration_profile(call.data["profile"])',
    'await _delete_calibration_profile(msg["profile"])',
    '"factory calibration profiles are protected from deletion"',
    '"active calibration profiles are protected from deletion"',
):
    assert marker in INIT, marker

# The service and WebSocket must share one deletion implementation so protection
# rules and event/result semantics cannot drift.
assert INIT.count('async def _delete_calibration_profile(') == 1
assert INIT.count('await _delete_calibration_profile(') == 2

print("Core calibration delete WebSocket contract: PASS")

#!/usr/bin/env python3
"""Core backup restore contract: preserve history without accepting fake pins."""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
source = (root / "src/custom_components/switch_vision/__init__.py").read_text()
assert 'vol.Optional("restore_exact_stock_pin", default=False): bool' in source
service = source.split("async def handle_save(call: ServiceCall)", 1)[1]
service = service.split("async def handle_delete", 1)[0]
assert 'restore_exact_pin = call.data.get("restore_exact_stock_pin", False) is True' in service
assert "if not restore_exact_pin:" in service
assert "calibration.pop(_faceplate_artwork.STOCK_SHA_FIELD, None)" in service
assert "if restore_exact_pin:" in service
assert 'elif artwork_sha:' in service
assert 'imported_pin != artwork_sha' in service
assert 'restored stock faceplate SHA cannot be verified' in service
assert 'async_register_admin_service(hass, DOMAIN, "save_calibration"' in source
print("Core admin-only exact-backup stock SHA contract: PASS")

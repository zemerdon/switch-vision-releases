"""HP 3500yl optical refresh cooldown: per physical port, device-wide busy.

Pure offline tests; absolutely no network access, SNMP GET or SNMP SET.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src/custom_components/switch_vision/hp_optics.py"
spec = importlib.util.spec_from_file_location("hp_optics_cooldown_fixture", SOURCE)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class HpOpticalRefreshCooldownTests(unittest.TestCase):
    def test_different_optical_ports_do_not_share_cooldown(self):
        host = "10.254.22.50"
        busy: set[str] = set()
        last: dict[tuple[str, int], float] = {}
        self.assertIsNone(module.reserve_refresh(host, 49, busy, last, 100.0))
        self.assertEqual(last, {(host, 49): 100.0})
        self.assertEqual(module.reserve_refresh(host, 52, busy, last, 100.1), "busy")
        self.assertEqual(last, {(host, 49): 100.0}, "busy must not advance timestamps")
        busy.remove(host)

        # Clicking A4 immediately after A1 finishes is valid.
        self.assertIsNone(module.reserve_refresh(host, 52, busy, last, 100.1))
        self.assertEqual(last[(host, 52)], 100.1)
        self.assertIn(host, busy)
        busy.remove(host)

        # A1 and A4 each retain their own full 30 seconds, including after
        # a stale or failed command (the production finally releases busy).
        self.assertEqual(module.reserve_refresh(host, 49, busy, last, 100.2), "cooldown")
        self.assertEqual(module.reserve_refresh(host, 52, busy, last, 100.2), "cooldown")
        self.assertEqual(last, {(host, 49): 100.0, (host, 52): 100.1})
        self.assertNotIn(host, busy)
        self.assertIsNone(module.reserve_refresh(host, 49, busy, last, 130.0))
        busy.remove(host)
        self.assertEqual(module.reserve_refresh(host, 52, busy, last, 130.0), "cooldown")
        self.assertIsNone(module.reserve_refresh(host, 52, busy, last, 130.1))

    def test_other_switch_independent_busy_and_port_delay(self):
        busy: set[str] = set()
        last: dict[tuple[str, int], float] = {}
        self.assertIsNone(module.reserve_refresh("10.254.22.50", 49, busy, last, 1.0))
        self.assertIsNone(module.reserve_refresh("10.254.22.51", 49, busy, last, 1.0))
        self.assertEqual(busy, {"10.254.22.50", "10.254.22.51"})
        self.assertEqual(len(last), 2)

    def test_backward_time_does_not_bypass_port_cooldown(self):
        busy: set[str] = set()
        last: dict[tuple[str, int], float] = {}
        host = "10.254.22.50"
        self.assertIsNone(module.reserve_refresh(host, 49, busy, last, 101.0))
        busy.remove(host)
        self.assertEqual(module.reserve_refresh(host, 49, busy, last, 99.0), "cooldown")
        self.assertEqual(last[(host, 49)], 101.0)

    def test_authorization_and_device_guards_remain_in_front(self):
        backend = (ROOT / "src/custom_components/switch_vision/__init__.py").read_text()
        function = backend.split("async def websocket_refresh_hp_optics(", 1)[1].split(
            "websocket_api.async_register_command(hass, websocket_get_hp_optics_settings)", 1
        )[0]
        self.assertLess(function.index("_hp_optics_settings()"),
                        function.index("trusted_target("))
        self.assertLess(function.index("trusted_target("),
                        function.index("reserve_refresh("))
        self.assertIn("@websocket_api.require_admin", backend.split(
            "async def websocket_refresh_hp_optics(", 1
        )[0][-180:])
        self.assertIn("finally:", function)
        self.assertIn("hp_optics_busy.discard(host)", function)
        self.assertIn("timeout=30.0", function)
        self.assertIn('hp_optics_last_by_port', backend)
        self.assertNotIn('hp_optics_last.get(host', function)


if __name__ == "__main__":
    unittest.main()

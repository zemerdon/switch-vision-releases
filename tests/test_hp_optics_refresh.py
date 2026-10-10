#!/usr/bin/env python3
"""Offline functional DOM-only refresh tests: no SNMP packets are sent."""
import asyncio
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "src/custom_components/switch_vision/hp_optics.py"
spec = importlib.util.spec_from_file_location("hp_optics_test", MODULE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

MODEL = "HP J8693A Switch 3500yl-48G"
CARDS = [{"member": "LAB3500", "switch_ip": "10.254.22.50", "switch_model": MODEL}]
assert module.supported_model(MODEL)
assert module.trusted_target(CARDS, "10.254.22.50", "LAB3500", 49) == "10.254.22.50"
for host, member, port in [("10.254.22.60", "LAB3500", 49), ("10.254.22.50", "Other", 49), ("10.254.22.50", "LAB3500", 2), ("127.0.0.1", "LAB3500", 49)]:
    try:
        module.trusted_target(CARDS, host, member, port)
    except ValueError:
        pass
    else:
        raise AssertionError("Unapproved host/member/port passed the binding guard")


class FakeAgent:
    def __init__(self, dom=1, after=110, rx=-7223, tx=-2111, sys_descr="HP ProCurve Switch 3500yl-48G (J8693A)"):
        self.sys_descr = sys_descr
        self.dom = dom
        self.after = after
        self.rx = rx
        self.tx = tx
        self.sets = []
        self.tick_reads = 0

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass

    async def get(self, oid):
        if oid == module.SYS_DESCR:
            return self.sys_descr
        if oid == module.IF_DESCR + ".49":
            return "A1"
        if oid == module.oid(module.DOM, 49):
            return str(self.dom)
        if oid == module.oid(module.TIME_TICKS, 49):
            self.tick_reads += 1
            return "100" if self.tick_reads == 1 else str(self.after)
        if oid == module.oid(module.TX, 49):
            return str(self.tx)
        if oid == module.oid(module.RX, 49):
            return str(self.rx)
        raise AssertionError("Unexpected OID " + oid)

    async def set_integer(self, oid, value):
        self.sets.append((oid, value))


async def check():
    agent = FakeAgent()
    result = await module.refresh_dom("10.254.22.50", 49, "dedicated-write", lambda *_: agent)
    assert result == {"status": "ok", "port": 49, "tx_dbm": "-2.111", "rx_dbm": "-7.223"}
    assert agent.sets == [(module.oid(module.UPDATE, 49), 1)]
    for wrong_identity in ["HP ProCurve Switch 3500yl-48G (J8694A)", "HP Switch 2530-48G (J8693A)", "Other vendor 3500yl-48G"]:
        agent = FakeAgent(sys_descr=wrong_identity)
        try:
            await module.refresh_dom("10.254.22.50", 49, "dedicated-write", lambda *_: agent)
        except ValueError:
            pass
        else:
            raise AssertionError("Non-J8693A/3500yl live identity was allowed to issue an SNMP SET")
        assert not agent.sets
    for prohibited in [0, 2, 3, 4, None]:
        agent = FakeAgent(dom=prohibited)
        try:
            await module.refresh_dom("10.254.22.50", 49, "dedicated-write", lambda *_: agent)
        except ValueError:
            pass
        else:
            raise AssertionError("Non-DOM port sent a SET")
        assert not agent.sets, prohibited
    stale = FakeAgent(after=100)
    result = await module.refresh_dom("10.254.22.50", 49, "dedicated-write", lambda *_: stale)
    assert result["status"] == "stale" and len(stale.sets) == 1
    for value in [module.MISSING, -110000, "nan"]:
        agent = FakeAgent(rx=value)
        try:
            await module.refresh_dom("10.254.22.50", 49, "dedicated-write", lambda *_: agent)
        except ValueError:
            pass
        else:
            raise AssertionError("Missing power accepted")
    print("HP_3500YL_DOM_READ_CHECK_THEN_FIXED_SET_PASS")


asyncio.run(check())
source = (ROOT / "src/custom_components/switch_vision/__init__.py").read_text()
card = (ROOT / "src/custom_components/switch_vision/switch-vision-card.js").read_text()
assert "@websocket_api.require_admin" in source
assert '"switch_vision/refresh_hp_optics"' in source
assert '"switch_vision/get_hp_optics_settings"' in source
assert '"switch_vision/set_hp_optics_settings"' in source
assert 'write_community_configured' in source
assert 'hp_optics_busy' in source and 'hp_optics_last' in source
assert 'type: "switch_vision/refresh_hp_optics"' in card
assert 'port_db: "PORT dB"' in card
assert 'this.refreshHpOpticsForPort(sfpLogicalPort(this.config, id));' in card
assert 'if (type === "sfp" && !calibrationActive)' in card
assert 'if (type === "sfp" && !calibrationActive) this.refreshHpOpticsForPort(Number(selectedId));' not in card
assert 'port_db: hpOpticalDbValue(config, sfpLogicalPort(config, selected.id))' in card
assert 'port_db: selected.hp_optics_sfp === true ? hpOpticalDbValue(config, selected.id) : "—"' in card
assert '...(type === "sfp" && hp3500ylOpticalPilot(this.config) ? { hp_optics_sfp: true } : {})' in card
# Ordinary copper clicks have no HP optical-origin marker, so cannot display a stale SFP reading.
print("HP_OPTICS_CARD_AND_ADMIN_SETTINGS_CONTRACT_PASS")

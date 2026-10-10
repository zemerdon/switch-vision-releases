"""Explicit, model-bound HP 3500yl optical DOM refresh.

The optical data is read-only; the *refresh trigger* is an SNMP SET and
must never be sent for a VCT, unknown transceiver or unregistered host.
"""
from __future__ import annotations

import asyncio
import ipaddress
import re
from typing import Any, Callable


SUPPORTED_MODELS = frozenset({"J8693A", "HP J8693A Switch 3500yl-48G", "HP J8693A 3500yl-48G", "3500yl-48G"})
PREFIX = "1.3.6.1.4.1.11.2.14.11.5.1.82.1.1.1.1"
SYS_DESCR = "1.3.6.1.2.1.1.1.0"
IF_DESCR = "1.3.6.1.2.1.2.2.1.2"
DOM = 9
UPDATE = 10
TX = 14
RX = 15
TIME_TICKS = 64
MISSING = -99999999
MIN_COOLDOWN_SECONDS = 30


def supported_model(value: Any) -> bool:
    model = str(value or "").strip()
    return model in SUPPORTED_MODELS


def trusted_target(cards: list[dict[str, Any]], host: str, member: str, index: int) -> str:
    """Bind a browser selection to exactly one generated, reviewed HP card."""
    try:
        ip = ipaddress.ip_address(host)
    except ValueError as exc:
        raise ValueError("Target must be a configured numeric IPv4 address.") from exc
    if ip.version != 4 or not ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast:
        raise ValueError("Target is not a supported private IPv4 switch.")
    if type(index) is not int or not (45 <= index <= 52):
        raise ValueError("Port index is outside the HP 3500yl physical range.")
    if not member or len(member) > 128:
        raise ValueError("Missing switch identity.")
    matching = [
        card for card in cards
        if isinstance(card, dict)
        and str(card.get("switch_ip") or "") == host
        and str(card.get("member") or card.get("selected_switch") or "") == member
        and supported_model(card.get("switch_model"))
    ]
    if len(matching) != 1:
        raise ValueError("No unique registered HP 3500yl matches this selected switch.")
    # Ports 45-48 may be optical only when their dual-purpose SFP is populated.
    # Rear optional module positions 49-52 are also subject to the live DOM check.
    return str(ip)


def power_dbm(raw: Any) -> str:
    try:
        value = int(str(raw))
    except (ValueError, TypeError) as exc:
        raise ValueError("Optical power is unavailable.") from exc
    if value == MISSING or not (-100000 <= value <= 40000):
        raise ValueError("Optical power is unavailable.")
    return f"{value / 1000:.3f}"


def oid(column: int, port: int) -> str:
    return f"{PREFIX}.{column}.{port}"


def assert_dom(value: Any) -> None:
    try:
        dom = int(str(value))
    except (ValueError, TypeError) as exc:
        raise ValueError("The port did not report valid diagnostic capabilities.") from exc
    if dom != 1:
        raise ValueError("Refresh denied: transceiver is not DOM(1); VCT and other diagnostics are prohibited.")


def assert_device(sys_descr: Any) -> None:
    text = str(sys_descr or "")
    if not re.search(r"(?i)(3500\s*yl|J8693A)", text):
        raise ValueError("Live SNMP identity is not the supported HP 3500yl.")


def assert_optical(if_descr: Any) -> None:
    value = str(if_descr or "").strip()
    if not value or len(value) > 256:
        raise ValueError("Selected interface does not have a valid live SNMP description.")


async def refresh_dom(
    host: str,
    port: int,
    write_community: str,
    snmp_factory: Callable[..., Any] | None = None,
) -> dict[str, Any]:
    """Validate identity + DOM using SNMP GET, then one fixed, narrow SET.

    A caller must check configuration, HA authorization, generated switch
    identity and rate limiting before calling this function.
    """
    if not write_community or len(write_community) > 256:
        raise ValueError("Dedicated SNMP write credentials are not configured.")
    if snmp_factory is None:
        snmp_factory = SnmpV2Agent
    async with snmp_factory(host, write_community) as agent:
        assert_device(await agent.get(SYS_DESCR))
        assert_optical(await agent.get(f"{IF_DESCR}.{port}"))
        assert_dom(await agent.get(oid(DOM, port)))
        # Only the numeric TruthValue for DOM update is ever written. Never
        # offer an arbitrary OID/value or re-purpose this path for VCT.
        before = await agent.get(oid(TIME_TICKS, port))
        await agent.set_integer(oid(UPDATE, port), 1)
        # Reverify DOM *after* the operation and never display stale values.
        assert_dom(await agent.get(oid(DOM, port)))
        changed = False
        for attempt in range(4):
            after = await agent.get(oid(TIME_TICKS, port))
            try:
                changed = int(str(after)) != int(str(before))
            except (ValueError, TypeError):
                changed = False
            if changed:
                break
            if attempt < 3:
                await asyncio.sleep(0.25 * (attempt + 1))
        if not changed:
            return {"status": "stale", "port": port, "message": "Optical diagnostics have not reported a new timestamp."}
        tx = power_dbm(await agent.get(oid(TX, port)))
        rx = power_dbm(await agent.get(oid(RX, port)))
        return {"status": "ok", "port": port, "tx_dbm": tx, "rx_dbm": rx}


class SnmpV2Agent:
    """Bounded per-request SNMPv2c client; no arbitrary user-selected OIDs."""

    def __init__(self, host: str, community: str) -> None:
        self.host = host
        self.community = community
        self.engine: Any = None
        self.target: Any = None

    async def __aenter__(self) -> "SnmpV2Agent":
        from pysnmp.hlapi.v3arch.asyncio import SnmpEngine, UdpTransportTarget
        self.engine = SnmpEngine()
        self.target = await UdpTransportTarget.create((self.host, 161), timeout=2.0, retries=0)
        return self

    async def __aexit__(self, *_exc: object) -> None:
        if self.engine is not None:
            self.engine.close_dispatcher()

    async def _request(self, command: str, target_oid: str, value: int | None = None) -> str:
        from pysnmp.hlapi.v3arch.asyncio import (
            CommunityData, ContextData, ObjectIdentity, ObjectType, get_cmd, set_cmd,
        )
        from pysnmp.proto.rfc1902 import Integer
        binding = ObjectType(ObjectIdentity(target_oid))
        if command == "set":
            binding = ObjectType(ObjectIdentity(target_oid), Integer(value))
        method = get_cmd if command == "get" else set_cmd
        error, error_status, _index, result = await asyncio.wait_for(
            method(
                self.engine, CommunityData(self.community, mpModel=1),
                self.target, ContextData(), binding, lookupMib=False,
            ),
            timeout=5.0,
        )
        if error or error_status or not result:
            raise RuntimeError("SNMP optical diagnostic operation failed.")
        return str(result[0][1])

    async def get(self, target_oid: str) -> str:
        return await self._request("get", target_oid)

    async def set_integer(self, target_oid: str, value: int) -> None:
        if not (target_oid.startswith(PREFIX + ".10.") and value == 1):
            raise ValueError("SNMP write command outside the fixed DOM allowlist.")
        await self._request("set", target_oid, value)

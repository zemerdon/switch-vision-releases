"""Source-executed parallel Supervisor reads for the Native app-status UI."""

import ast
import asyncio
import logging
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src/custom_components/switch_vision/__init__.py"
tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
names = {
    "_addon_slug_value",
    "_resolve_switch_vision_app_slug",
    "async_switch_vision_app_states",
}
nodes = [
    node for node in tree.body
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    and node.name in names
]
assert {node.name for node in nodes} == names

class SupervisorError(Exception):
    pass

class SupervisorNotFoundError(SupervisorError):
    pass

current_client = [None]

def get_supervisor_client(_hass):
    if current_client[0] is None:
        raise RuntimeError("Supervisor unavailable")
    return current_client[0]

environment = {
    "asyncio": asyncio,
    "_LOGGER": logging.getLogger("switch_vision_app_status_contract"),
    "DATA_ADDONS_LIST": "installed_addons",
    "DISCOVERY_APP_SLUG": "switch_vision_discovery",
    "INSTALLER_APP_SLUG": "switch_vision_installer",
    "SNMP2MQTT_APP_SLUG": "switch_vision_snmp2mqtt",
    "UNIFI2MQTT_APP_SLUG": "switch_vision_unifi2mqtt",
    "get_supervisor_client": get_supervisor_client,
    "SupervisorError": SupervisorError,
    "SupervisorNotFoundError": SupervisorNotFoundError,
}
module = ast.Module(
    body=[ast.ImportFrom(
        module="__future__", names=[ast.alias(name="annotations")], level=0,
    )] + nodes,
    type_ignores=[],
)
exec(compile(ast.fix_missing_locations(module), str(SOURCE), "exec"), environment)
get_states = environment["async_switch_vision_app_states"]

base_slugs = [
    "switch_vision_discovery", "switch_vision_installer",
    "switch_vision_snmp2mqtt", "switch_vision_unifi2mqtt",
]
repo_slug = "abcdef_" + base_slugs[0]
hass = SimpleNamespace(data={
    "installed_addons": [{"slug": repo_slug}] + [
        SimpleNamespace(slug=slug) for slug in base_slugs[1:]
    ],
})

async def verify():
    # Missing client retains four discoverable navigation targets, no I/O.
    current_client[0] = None
    absent = await get_states(hass)
    assert list(absent) == ["discovery", "installer", "snmp2mqtt", "unifi2mqtt"]
    assert absent["discovery"]["slug"] == repo_slug
    assert all(not state["installed"] for state in absent.values())

    # A barrier makes serial fetching fail: all four reads must be in flight.
    started = set()
    release = asyncio.Event()
    async def addon_info(slug):
        started.add(slug)
        if len(started) == 4:
            release.set()
        await asyncio.wait_for(release.wait(), timeout=2)
        if slug == "switch_vision_installer":
            raise SupervisorNotFoundError("not installed")
        if slug == "switch_vision_snmp2mqtt":
            raise SupervisorError("transient API error")
        return SimpleNamespace(
            ingress=True, ingress_panel=True, available=True,
            state=SimpleNamespace(value="started"),
        )

    current_client[0] = SimpleNamespace(addons=SimpleNamespace(addon_info=addon_info))
    states = await get_states(hass)
    assert len(started) == 4
    assert states["discovery"]["slug"] == repo_slug
    assert states["discovery"]["installed"] is True
    assert states["discovery"]["state"] == "started"
    assert states["discovery"]["panel_path"] == "/" + repo_slug
    assert states["unifi2mqtt"]["available"] is True
    assert states["unifi2mqtt"]["ingress_panel"] is True
    assert states["installer"]["installed"] is False
    assert states["snmp2mqtt"]["installed"] is False
    assert "state" not in states["installer"]
    assert "state" not in states["snmp2mqtt"]

    # Unexpected exceptions must still fail closed instead of being mistaken
    # for an uninstalled app.
    async def unexpected(slug):
        if slug == repo_slug:
            raise ValueError("invalid Supervisor response")
        return SimpleNamespace(ingress=False, ingress_panel=False, available=True)
    current_client[0] = SimpleNamespace(addons=SimpleNamespace(addon_info=unexpected))
    try:
        await get_states(hass)
    except ValueError as error:
        assert str(error) == "invalid Supervisor response"
    else:
        raise AssertionError("Unexpected Supervisor error was swallowed")

asyncio.run(verify())
print("Core parallel Supervisor app-state retrieval contracts: PASS")

#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INIT = ROOT / "src/custom_components/switch_vision/__init__.py"
FLOW = ROOT / "src/custom_components/switch_vision/config_flow.py"
TEST = ROOT / "tests/test_sidebar_header_contracts.py"


def patch(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise SystemExit(f"Expected migration marker not found in {path}: {old[:100]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8", newline="\n")


patch(
    INIT,
    '''    show_hub_in_sidebar = sidebar_master and bool(\n        entry.options.get(CONF_SHOW_HUB_IN_SIDEBAR, DEFAULT_OPTIONS[CONF_SHOW_HUB_IN_SIDEBAR])\n    )\n    show_installer_in_sidebar = sidebar_master and bool(\n        entry.options.get(CONF_SHOW_INSTALLER_IN_SIDEBAR, DEFAULT_OPTIONS[CONF_SHOW_INSTALLER_IN_SIDEBAR])\n    )\n''',
    '''    app_states = await async_switch_vision_app_states(hass)\n    hub_preference = (\n        bool(entry.options[CONF_SHOW_HUB_IN_SIDEBAR])\n        if CONF_SHOW_HUB_IN_SIDEBAR in entry.options\n        else bool(app_states.get("discovery", {}).get("ingress_panel", True))\n    )\n    installer_preference = (\n        bool(entry.options[CONF_SHOW_INSTALLER_IN_SIDEBAR])\n        if CONF_SHOW_INSTALLER_IN_SIDEBAR in entry.options\n        else bool(app_states.get("installer", {}).get("ingress_panel", True))\n    )\n    show_hub_in_sidebar = sidebar_master and hub_preference\n    show_installer_in_sidebar = sidebar_master and installer_preference\n''',
)

patch(
    FLOW,
    '''                    default=self._value(CONF_SHOW_HUB_IN_SIDEBAR),\n''',
    '''                    default=(\n                        bool(self.config_entry.options[CONF_SHOW_HUB_IN_SIDEBAR])\n                        if CONF_SHOW_HUB_IN_SIDEBAR in self.config_entry.options\n                        else bool(discovery.get("ingress_panel", True))\n                    ),\n''',
)
patch(
    FLOW,
    '''                    default=self._value(CONF_SHOW_INSTALLER_IN_SIDEBAR),\n''',
    '''                    default=(\n                        bool(self.config_entry.options[CONF_SHOW_INSTALLER_IN_SIDEBAR])\n                        if CONF_SHOW_INSTALLER_IN_SIDEBAR in self.config_entry.options\n                        else bool(installer.get("ingress_panel", True))\n                    ),\n''',
)

text = TEST.read_text(encoding="utf-8")
needle = "assert 'Not installed' in STRINGS\n"
addition = '''assert 'CONF_SHOW_HUB_IN_SIDEBAR in entry.options' in INIT\nassert 'get("ingress_panel", True)' in INIT\nassert 'CONF_SHOW_INSTALLER_IN_SIDEBAR in self.config_entry.options' in FLOW\nassert 'discovery.get("ingress_panel", True)' in FLOW\nassert 'installer.get("ingress_panel", True)' in FLOW\n'''
if addition not in text:
    if needle not in text:
        raise SystemExit("sidebar migration regression marker missing")
    text = text.replace(needle, addition + needle, 1)
    TEST.write_text(text, encoding="utf-8", newline="\n")

print("Applied Core 2.4.4 sidebar preference migration safeguards")

#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
COMP = SRC / "custom_components" / "switch_vision"
INIT = COMP / "__init__.py"
PANEL = COMP / "switch-vision-panel.js"
TEST = ROOT / "tests" / "test_sidebar_header_contracts.py"
OLD = "2.4.4"
NEW = "2.4.5"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, text: str) -> None:
    path.write_text(text.replace("\r\n", "\n").replace("\r", "\n"), encoding="utf-8", newline="\n")


def replace_once(path: Path, old: str, new: str) -> None:
    text = read(path)
    if old not in text:
        raise SystemExit(f"Expected marker missing in {path}: {old[:160]!r}")
    write(path, text.replace(old, new, 1))


def replace_section(path: Path, start: str, end: str, replacement: str) -> None:
    text = read(path)
    a = text.find(start)
    if a < 0:
        raise SystemExit(f"Start marker missing in {path}: {start!r}")
    b = text.find(end, a)
    if b < 0:
        raise SystemExit(f"End marker missing in {path}: {end!r}")
    write(path, text[:a] + replacement + text[b:])


# ---------------------------------------------------------------------------
# Version metadata and user-facing release notes.
# ---------------------------------------------------------------------------
write(ROOT / "VERSION", NEW + "\n")
for manifest in (SRC / "manifest.json", COMP / "manifest.json"):
    payload = json.loads(read(manifest))
    payload["version"] = NEW
    write(manifest, json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

for path in (
    INIT,
    PANEL,
    COMP / "switch-vision-card.js",
    COMP / "switch-vision-dashboard-strategy.js",
    SRC / "js" / "switch-vision.js",
):
    text = read(path)
    if OLD not in text:
        raise SystemExit(f"Current version marker missing in {path}")
    write(path, text.replace(OLD, NEW))

examples = SRC / "examples"
for path in sorted(examples.iterdir()):
    if path.is_file():
        text = read(path)
        if OLD in text:
            write(path, text.replace(OLD, NEW))
for path in sorted(examples.glob(f"*{OLD}*")):
    path.rename(path.with_name(path.name.replace(OLD, NEW)))

changelog_entry = '''## v2.4.5 — Native dashboard shortcut editor hotfix\n\n- Fix Native dashboard shortcut navigation by using Home Assistant's current history + `location-changed` navigation contract.\n- Resolve repository-prefixed Supervisor app slugs so installed Switch Vision apps are no longer incorrectly shown as **Not installed**.\n- Use the resolved Supervisor slug for Hub, Installer, and app-configuration shortcut destinations.\n- Replace drag-and-drop shortcut ordering with an explicit Customize editor containing show/hide checkboxes plus Up/Down ordering controls.\n- Stage Customize changes until **Done**, add **Cancel**, and expose Customize only to Home Assistant administrators.\n- Preserve telemetry, calibration geometry, Activity LED behavior, device mappings, Discovery generation, and saved shortcut preferences.\n\n'''
for path in (ROOT / "CHANGELOG.md", SRC / "CHANGELOG.md"):
    text = read(path)
    if "## v2.4.5" not in text:
        write(path, changelog_entry + text)

notes = '''# Switch Vision Core v2.4.5 — Native dashboard shortcut editor hotfix\n\n- Fixes **Switch Vision Settings** and other Native dashboard shortcuts so they navigate through Home Assistant's supported SPA navigation contract.\n- Detects repository-installed Switch Vision apps by their real Supervisor slug, including repository prefixes.\n- Uses the real installed app slug for Hub, Installer, and app Configuration destinations.\n- Replaces drag-and-drop customization with a clear checkbox + Up/Down shortcut editor.\n- Customize changes are staged until **Done**; **Cancel** discards them.\n- Customize is shown only to Home Assistant administrators.\n- Does not change switch telemetry, calibration geometry, Discovery generation, supported-device mappings, or Activity LED behavior.\n\nAfter updating Core through Switch Vision Installer, restart Home Assistant Core when requested and hard-refresh the browser so the new integration and Native panel JavaScript are loaded.\n'''
write(ROOT / "RELEASE_NOTES.md", notes)
write(SRC / "RELEASE_NOTES.md", notes)
for path in (ROOT / "README.md", SRC / "README.md"):
    text = read(path)
    text = text.replace("### Switch Vision v2.4.4", "### Switch Vision v2.4.5", 1)
    text = text.replace("**v2.4.4** is the current tested public Switch Vision Core/dashboard release.", "**v2.4.5** is the current tested public Switch Vision Core/dashboard release.", 1)
    write(path, text)

# ---------------------------------------------------------------------------
# Backend: resolve actual repository-prefixed Supervisor slugs and persist the
# complete shortcut editor state through the existing admin-only WebSocket.
# ---------------------------------------------------------------------------
replace_once(
    INIT,
    "from homeassistant.components.hassio.handler import get_supervisor_client\n",
    "from homeassistant.components.hassio.const import DATA_ADDONS_LIST\nfrom homeassistant.components.hassio.handler import get_supervisor_client\n",
)

replace_once(
    INIT,
    '''SET_NATIVE_HEADER_ORDER_WS_SCHEMA = {\n    vol.Required("type"): "switch_vision/set_native_header_shortcut_order",\n    vol.Required("order"): [vol.In(NATIVE_HEADER_SHORTCUT_IDS)],\n}\n''',
    '''SET_NATIVE_HEADER_ORDER_WS_SCHEMA = {\n    vol.Required("type"): "switch_vision/set_native_header_shortcut_order",\n    vol.Required("order"): [vol.In(NATIVE_HEADER_SHORTCUT_IDS)],\n    vol.Optional("shortcuts"): {vol.In(NATIVE_HEADER_SHORTCUT_IDS): bool},\n}\n''',
)

replace_once(
    INIT,
    '''UNIFI2MQTT_APP_SLUG = "switch_vision_unifi2mqtt"\n\nCONF_SHOW_UNIFI_INTEGRATION''',
    '''UNIFI2MQTT_APP_SLUG = "switch_vision_unifi2mqtt"\n\nNATIVE_HEADER_SHORTCUT_OPTION_KEYS = {\n    "hub": CONF_NATIVE_HEADER_SHORTCUT_HUB,\n    "switch_vision_settings": CONF_NATIVE_HEADER_SHORTCUT_SWITCH_VISION_SETTINGS,\n    "discovery_settings": CONF_NATIVE_HEADER_SHORTCUT_DISCOVERY_SETTINGS,\n    "installer": CONF_NATIVE_HEADER_SHORTCUT_INSTALLER,\n    "installer_settings": CONF_NATIVE_HEADER_SHORTCUT_INSTALLER_SETTINGS,\n    "snmp2mqtt_settings": CONF_NATIVE_HEADER_SHORTCUT_SNMP2MQTT_SETTINGS,\n    "unifi2mqtt_settings": CONF_NATIVE_HEADER_SHORTCUT_UNIFI2MQTT_SETTINGS,\n}\n\nCONF_SHOW_UNIFI_INTEGRATION''',
)

new_app_state = '''def _addon_slug_value(addon: Any) -> str:\n    """Extract an installed Supervisor app slug from model or dict data."""\n    if isinstance(addon, dict):\n        return str(addon.get("slug") or "").strip()\n    return str(getattr(addon, "slug", "") or "").strip()\n\n\ndef _resolve_switch_vision_app_slug(hass: HomeAssistant, base_slug: str) -> str:\n    """Resolve a repository-prefixed installed slug from Supervisor's live list."""\n    installed = hass.data.get(DATA_ADDONS_LIST) or []\n    slugs = [slug for slug in (_addon_slug_value(addon) for addon in installed) if slug]\n    if base_slug in slugs:\n        return base_slug\n    suffix = f"_{base_slug}"\n    matches = sorted({slug for slug in slugs if slug.endswith(suffix)}, key=lambda value: (len(value), value))\n    if matches:\n        if len(matches) > 1:\n            _LOGGER.warning("Multiple installed Supervisor apps match %s; using %s", base_slug, matches[0])\n        return matches[0]\n    return base_slug\n\n\nasync def async_switch_vision_app_states(hass: HomeAssistant) -> dict[str, dict[str, Any]]:\n    """Return safe installed/ingress state for Switch Vision managed apps."""\n    specs = {\n        "discovery": DISCOVERY_APP_SLUG,\n        "installer": INSTALLER_APP_SLUG,\n        "snmp2mqtt": SNMP2MQTT_APP_SLUG,\n        "unifi2mqtt": UNIFI2MQTT_APP_SLUG,\n    }\n    states: dict[str, dict[str, Any]] = {}\n    try:\n        client = get_supervisor_client(hass)\n    except (KeyError, RuntimeError):\n        client = None\n\n    for key, base_slug in specs.items():\n        slug = _resolve_switch_vision_app_slug(hass, base_slug)\n        state = {\n            "base_slug": base_slug,\n            "slug": slug,\n            "installed": False,\n            "ingress": False,\n            "ingress_panel": False,\n            "available": False,\n            "panel_path": f"/{slug}",\n            "config_path": f"/config/app/{slug}/config",\n        }\n        states[key] = state\n        if client is None:\n            continue\n        try:\n            info = await client.addons.addon_info(slug)\n        except SupervisorNotFoundError:\n            continue\n        except SupervisorError as err:\n            _LOGGER.debug("Could not read Switch Vision app %s state: %s", slug, err)\n            continue\n        state.update(\n            {\n                "installed": True,\n                "ingress": bool(getattr(info, "ingress", False)),\n                "ingress_panel": bool(getattr(info, "ingress_panel", False)),\n                "available": bool(getattr(info, "available", True)),\n                "state": str(getattr(getattr(info, "state", None), "value", getattr(info, "state", "")) or ""),\n            }\n        )\n    return states\n\n\n'''
replace_section(
    INIT,
    "async def async_switch_vision_app_states(hass: HomeAssistant) -> dict[str, dict[str, Any]]:\n",
    "async def _sync_switch_vision_app_ingress_panel(\n",
    new_app_state,
)

replace_once(
    INIT,
    '''async def _sync_switch_vision_app_ingress_panel(\n    hass: HomeAssistant, slug: str, show_in_sidebar: bool\n) -> bool:\n    """Apply one supported Supervisor ingress-panel preference if installed."""\n    try:\n        client = get_supervisor_client(hass)\n        info = await client.addons.addon_info(slug)\n''',
    '''async def _sync_switch_vision_app_ingress_panel(\n    hass: HomeAssistant, slug: str, show_in_sidebar: bool\n) -> bool:\n    """Apply one supported Supervisor ingress-panel preference if installed."""\n    slug = _resolve_switch_vision_app_slug(hass, slug)\n    try:\n        client = get_supervisor_client(hass)\n        info = await client.addons.addon_info(slug)\n''',
)

replace_once(
    INIT,
    '''            apps[key] = {\n                "installed": bool(state.get("installed", False)),\n                "ingress": bool(state.get("ingress", False)),\n                "available": bool(state.get("available", False)),\n            }\n''',
    '''            apps[key] = {\n                "installed": bool(state.get("installed", False)),\n                "ingress": bool(state.get("ingress", False)),\n                "available": bool(state.get("available", False)),\n                "slug": str(state.get("slug") or ""),\n                "panel_path": str(state.get("panel_path") or ""),\n                "config_path": str(state.get("config_path") or ""),\n            }\n''',
)

old_handler_start = '''    @websocket_api.websocket_command(SET_NATIVE_HEADER_ORDER_WS_SCHEMA)\n    @websocket_api.require_admin\n    @websocket_api.async_response\n    async def websocket_set_native_header_shortcut_order(hass: HomeAssistant, connection, msg):\n'''
new_handler = '''    @websocket_api.websocket_command(SET_NATIVE_HEADER_ORDER_WS_SCHEMA)\n    @websocket_api.require_admin\n    @websocket_api.async_response\n    async def websocket_set_native_header_shortcut_order(hass: HomeAssistant, connection, msg):\n        """Persist Native dashboard shortcut visibility and ordering."""\n        requested = [str(value) for value in msg.get("order", [])]\n        order = []\n        for shortcut in requested:\n            if shortcut in NATIVE_HEADER_SHORTCUT_IDS and shortcut not in order:\n                order.append(shortcut)\n        order.extend(shortcut for shortcut in NATIVE_HEADER_SHORTCUT_IDS if shortcut not in order)\n\n        requested_shortcuts = msg.get("shortcuts")\n        requested_shortcuts = requested_shortcuts if isinstance(requested_shortcuts, dict) else {}\n\n        entries = hass.config_entries.async_entries(DOMAIN)\n        if not entries:\n            connection.send_error(msg["id"], "not_configured", "Switch Vision integration is not configured")\n            return\n        entry = entries[0]\n        options = dict(entry.options)\n        options[CONF_NATIVE_HEADER_SHORTCUT_ORDER] = order\n        for shortcut_id, enabled in requested_shortcuts.items():\n            option_key = NATIVE_HEADER_SHORTCUT_OPTION_KEYS.get(str(shortcut_id))\n            if option_key:\n                options[option_key] = bool(enabled)\n        hass.config_entries.async_update_entry(entry, options=options)\n        native_header = _native_header_settings(entry)\n        hass.data.setdefault(DOMAIN, {})[DATA_NATIVE_HEADER_SETTINGS] = native_header\n        hass.bus.async_fire(EVENT_UI_SETTINGS_UPDATED)\n        connection.send_result(\n            msg["id"],\n            {"order": native_header["order"], "shortcuts": native_header["shortcuts"]},\n        )\n\n'''
replace_section(
    INIT,
    old_handler_start,
    "    websocket_api.async_register_command(hass, websocket_get_app_states)\n",
    new_handler,
)

# ---------------------------------------------------------------------------
# Native panel: supported HA navigation + checkbox/Up/Down editor.
# ---------------------------------------------------------------------------
replace_once(
    PANEL,
    '''    this._shortcutAvailability = { discovery: false, installer: false, snmp2mqtt: false, unifi2mqtt: false };\n    this._customizingShortcuts = false;\n    this._draggedShortcutId = null;\n''',
    '''    this._shortcutAppStates = { discovery: {}, installer: {}, snmp2mqtt: {}, unifi2mqtt: {} };\n    this._customizingShortcuts = false;\n    this._shortcutDraft = null;\n    this._shortcutEditorError = "";\n''',
)

replace_once(
    PANEL,
    '''        .shortcut:hover,.shortcut:focus-visible{background:var(--primary-color,#2b8cc4);outline:none}.shortcut[disabled]{opacity:.45;cursor:not-allowed}.shortcut.dragging{opacity:.45}.shortcut.customizing{cursor:grab;border:1px dashed rgba(127,180,220,.75)}\n        .shortcut-tools{display:flex;gap:8px;align-items:center;flex:0 0 auto}.shortcut-tools button{font-size:12px;padding:7px 9px}.shortcut-hint{font-size:12px;opacity:.72;white-space:nowrap}\n''',
    '''        .shortcut:hover,.shortcut:focus-visible{background:var(--primary-color,#2b8cc4);outline:none}.shortcut[disabled]{opacity:.45;cursor:not-allowed}\n        .shortcut-tools{display:flex;gap:8px;align-items:center;flex:0 0 auto}.shortcut-tools button{font-size:12px;padding:7px 9px}\n        .shortcut-row.editing{display:block;overflow:visible}.shortcut-editor{display:grid;gap:6px;min-width:min(720px,100%);padding:10px;border:1px solid rgba(127,180,220,.28);border-radius:10px;background:var(--card-background-color,#1c242b)}\n        .shortcut-editor-title{font-size:13px;font-weight:700;margin-bottom:2px}.shortcut-edit-row{display:grid;grid-template-columns:minmax(220px,1fr) auto;gap:10px;align-items:center;padding:6px 7px;border-radius:7px;background:var(--secondary-background-color,#27323a)}\n        .shortcut-edit-label{display:flex;align-items:center;gap:9px;min-width:0}.shortcut-edit-label input{width:17px;height:17px;margin:0;flex:0 0 auto}.shortcut-edit-name{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.shortcut-edit-status{font-size:11px;opacity:.65;margin-left:4px}.shortcut-move{display:flex;gap:5px}.shortcut-move button{min-width:38px;padding:5px 8px}.shortcut-editor-actions{display:flex;justify-content:flex-end;gap:7px;margin-top:3px}.shortcut-editor-error{font-size:12px;color:var(--error-color,#db4437)}\n''',
)
replace_once(
    PANEL,
    '''        @media(max-width:650px){.page{padding:8px 8px 28px}.compact-head{gap:7px}.summary{font-size:13px;padding:8px 9px}.version{font-size:11px;padding:4px 7px}button{padding:7px 9px}.menu-toggle{padding:0}.shortcut-row{gap:6px}.shortcut{font-size:11px;padding:6px 8px}}\n''',
    '''        @media(max-width:650px){.page{padding:8px 8px 28px}.compact-head{gap:7px}.summary{font-size:13px;padding:8px 9px}.version{font-size:11px;padding:4px 7px}button{padding:7px 9px}.menu-toggle{padding:0}.shortcut-row{gap:6px}.shortcut{font-size:11px;padding:6px 8px}.shortcut-edit-row{grid-template-columns:1fr auto}.shortcut-edit-name{max-width:180px}}\n''',
)

panel_methods = '''  _shortcutDefinitions() {\n    const baseSlugs = {\n      discovery: "switch_vision_discovery",\n      installer: "switch_vision_installer",\n      snmp2mqtt: "switch_vision_snmp2mqtt",\n      unifi2mqtt: "switch_vision_unifi2mqtt"\n    };\n    const stateFor = (key) => this._shortcutAppStates?.[key] || {};\n    const panelPath = (key) => stateFor(key).panel_path || `/${baseSlugs[key]}`;\n    const configPath = (key) => stateFor(key).config_path || `/config/app/${baseSlugs[key]}/config`;\n    return {\n      hub: { label: "Switch Vision Hub", app: "discovery", path: panelPath("discovery") },\n      switch_vision_settings: { label: "Switch Vision Settings", path: "/config/integrations/integration/switch_vision" },\n      discovery_settings: { label: "Discovery Settings", app: "discovery", path: configPath("discovery") },\n      installer: { label: "Switch Vision Installer", app: "installer", path: panelPath("installer") },\n      installer_settings: { label: "Installer Settings", app: "installer", path: configPath("installer") },\n      snmp2mqtt_settings: { label: "SNMP2MQTT Settings", app: "snmp2mqtt", path: configPath("snmp2mqtt") },\n      unifi2mqtt_settings: { label: "UniFi2MQTT Settings", app: "unifi2mqtt", path: configPath("unifi2mqtt") }\n    };\n  }\n\n  _navigate(path) {\n    if (!path) return;\n    const current = `${window.location.pathname}${window.location.search}${window.location.hash}`;\n    const currentState = window.history.state && typeof window.history.state === "object" ? window.history.state : {};\n    const state = currentState.root ? { root: true, from: current } : { from: current };\n    window.history.pushState(state, "", path);\n    window.dispatchEvent(new CustomEvent("location-changed", { detail: { replace: false } }));\n  }\n\n  async _refreshShortcutAvailability() {\n    if (!this._hass) return;\n    const blank = { installed: false, ingress: false, available: false, slug: "", panel_path: "", config_path: "" };\n    const next = { discovery: { ...blank }, installer: { ...blank }, snmp2mqtt: { ...blank }, unifi2mqtt: { ...blank } };\n    try {\n      const result = await this._hass.callWS({ type: "switch_vision/get_app_states" });\n      const apps = result?.apps && typeof result.apps === "object" ? result.apps : {};\n      for (const key of Object.keys(next)) next[key] = { ...blank, ...(apps[key] || {}) };\n    } catch (error) {\n      console.warn("Switch Vision could not read app availability", error);\n    }\n    this._shortcutAppStates = next;\n    this._renderShortcuts();\n  }\n\n  _normalizedShortcutOrder(defs) {\n    const raw = Array.isArray(this._nativeHeader.order) ? this._nativeHeader.order : [];\n    const order = [];\n    for (const id of raw) if (defs[id] && !order.includes(id)) order.push(id);\n    for (const id of Object.keys(defs)) if (!order.includes(id)) order.push(id);\n    return order;\n  }\n\n  _renderShortcuts() {\n    const root = this.shadowRoot.getElementById("shortcut-row");\n    if (!root) return;\n    root.replaceChildren();\n    root.classList.toggle("editing", this._customizingShortcuts);\n    if (!this._showDashboardHeader) { root.hidden = true; return; }\n    const defs = this._shortcutDefinitions();\n\n    if (this._customizingShortcuts) {\n      this._renderShortcutEditor(root, defs);\n      root.hidden = false;\n      return;\n    }\n\n    const enabled = this._nativeHeader.shortcuts || {};\n    const order = this._normalizedShortcutOrder(defs);\n    let rendered = 0;\n    for (const id of order) {\n      const def = defs[id];\n      if (!def || enabled[id] === false) continue;\n      const installed = !def.app || this._shortcutAppStates?.[def.app]?.installed === true;\n      if (!installed) continue;\n      const button = document.createElement("button");\n      button.type = "button";\n      button.className = "shortcut";\n      button.dataset.shortcutId = id;\n      button.textContent = def.label;\n      button.title = def.label;\n      button.addEventListener("click", () => this._navigate(def.path));\n      root.appendChild(button);\n      rendered += 1;\n    }\n\n    const isAdmin = this._hass?.user?.is_admin === true;\n    if (isAdmin) {\n      const tools = document.createElement("span");\n      tools.className = "shortcut-tools";\n      const customize = document.createElement("button");\n      customize.type = "button";\n      customize.className = "secondary";\n      customize.textContent = "Customize";\n      customize.addEventListener("click", () => this._beginShortcutCustomization());\n      tools.appendChild(customize);\n      root.appendChild(tools);\n    }\n    root.hidden = rendered === 0 && !isAdmin;\n  }\n\n  _beginShortcutCustomization() {\n    if (this._hass?.user?.is_admin !== true) return;\n    const defs = this._shortcutDefinitions();\n    this._shortcutDraft = {\n      order: this._normalizedShortcutOrder(defs),\n      shortcuts: Object.fromEntries(Object.keys(defs).map((id) => [id, this._nativeHeader.shortcuts?.[id] !== false]))\n    };\n    this._shortcutEditorError = "";\n    this._customizingShortcuts = true;\n    this._renderShortcuts();\n  }\n\n  _renderShortcutEditor(root, defs) {\n    const draft = this._shortcutDraft || { order: this._normalizedShortcutOrder(defs), shortcuts: {} };\n    const editor = document.createElement("div");\n    editor.className = "shortcut-editor";\n\n    const title = document.createElement("div");\n    title.className = "shortcut-editor-title";\n    title.textContent = "Customize shortcuts";\n    editor.appendChild(title);\n\n    for (let index = 0; index < draft.order.length; index += 1) {\n      const id = draft.order[index];\n      const def = defs[id];\n      if (!def) continue;\n      const installed = !def.app || this._shortcutAppStates?.[def.app]?.installed === true;\n\n      const row = document.createElement("div");\n      row.className = "shortcut-edit-row";\n\n      const label = document.createElement("label");\n      label.className = "shortcut-edit-label";\n      const checkbox = document.createElement("input");\n      checkbox.type = "checkbox";\n      checkbox.checked = draft.shortcuts[id] !== false;\n      checkbox.disabled = !installed;\n      checkbox.addEventListener("change", () => { draft.shortcuts[id] = checkbox.checked; });\n      label.appendChild(checkbox);\n      const name = document.createElement("span");\n      name.className = "shortcut-edit-name";\n      name.textContent = def.label;\n      label.appendChild(name);\n      if (!installed) {\n        const status = document.createElement("span");\n        status.className = "shortcut-edit-status";\n        status.textContent = "Not installed";\n        label.appendChild(status);\n      }\n      row.appendChild(label);\n\n      const move = document.createElement("span");\n      move.className = "shortcut-move";\n      const up = document.createElement("button");\n      up.type = "button";\n      up.className = "secondary";\n      up.textContent = "↑";\n      up.title = `Move ${def.label} up`;\n      up.setAttribute("aria-label", up.title);\n      up.disabled = index === 0;\n      up.addEventListener("click", () => this._moveShortcut(id, -1));\n      move.appendChild(up);\n      const down = document.createElement("button");\n      down.type = "button";\n      down.className = "secondary";\n      down.textContent = "↓";\n      down.title = `Move ${def.label} down`;\n      down.setAttribute("aria-label", down.title);\n      down.disabled = index === draft.order.length - 1;\n      down.addEventListener("click", () => this._moveShortcut(id, 1));\n      move.appendChild(down);\n      row.appendChild(move);\n      editor.appendChild(row);\n    }\n\n    if (this._shortcutEditorError) {\n      const error = document.createElement("div");\n      error.className = "shortcut-editor-error";\n      error.textContent = this._shortcutEditorError;\n      editor.appendChild(error);\n    }\n\n    const actions = document.createElement("div");\n    actions.className = "shortcut-editor-actions";\n    const cancel = document.createElement("button");\n    cancel.type = "button";\n    cancel.className = "secondary";\n    cancel.textContent = "Cancel";\n    cancel.addEventListener("click", () => this._cancelShortcutCustomization());\n    actions.appendChild(cancel);\n    const done = document.createElement("button");\n    done.type = "button";\n    done.textContent = "Done";\n    done.addEventListener("click", () => void this._saveShortcutCustomization());\n    actions.appendChild(done);\n    editor.appendChild(actions);\n    root.appendChild(editor);\n  }\n\n  _moveShortcut(id, delta) {\n    const draft = this._shortcutDraft;\n    if (!draft || !Array.isArray(draft.order)) return;\n    const index = draft.order.indexOf(id);\n    const target = index + delta;\n    if (index < 0 || target < 0 || target >= draft.order.length) return;\n    [draft.order[index], draft.order[target]] = [draft.order[target], draft.order[index]];\n    this._renderShortcuts();\n  }\n\n  _cancelShortcutCustomization() {\n    this._shortcutDraft = null;\n    this._shortcutEditorError = "";\n    this._customizingShortcuts = false;\n    this._renderShortcuts();\n  }\n\n  async _saveShortcutCustomization() {\n    if (!this._shortcutDraft || this._hass?.user?.is_admin !== true) return;\n    try {\n      const result = await this._hass.callWS({\n        type: "switch_vision/set_native_header_shortcut_order",\n        order: [...this._shortcutDraft.order],\n        shortcuts: { ...this._shortcutDraft.shortcuts }\n      });\n      this._nativeHeader.order = Array.isArray(result?.order) ? result.order : [...this._shortcutDraft.order];\n      this._nativeHeader.shortcuts = result?.shortcuts && typeof result.shortcuts === "object"\n        ? { ...result.shortcuts }\n        : { ...this._shortcutDraft.shortcuts };\n      this._shortcutDraft = null;\n      this._shortcutEditorError = "";\n      this._customizingShortcuts = false;\n      this._renderShortcuts();\n    } catch (error) {\n      console.warn("Switch Vision could not save shortcut customization", error);\n      this._shortcutEditorError = `Could not save shortcut changes: ${String(error)}`;\n      this._renderShortcuts();\n    }\n  }\n\n'''
replace_section(PANEL, "  _shortcutDefinitions() {\n", "  _updateRuntimeVersion(result) {\n", panel_methods)

# ---------------------------------------------------------------------------
# Permanent regression source updated for the hotfix. The larger audit cycle
# will separately wire all permanent tests into the permanent CI workflow.
# ---------------------------------------------------------------------------
test = '''from pathlib import Path\n\nROOT = Path(__file__).resolve().parents[1]\nINIT = (ROOT / "src/custom_components/switch_vision/__init__.py").read_text(encoding="utf-8")\nFLOW = (ROOT / "src/custom_components/switch_vision/config_flow.py").read_text(encoding="utf-8")\nPANEL = (ROOT / "src/custom_components/switch_vision/switch-vision-panel.js").read_text(encoding="utf-8")\nSTRINGS = (ROOT / "src/custom_components/switch_vision/strings.json").read_text(encoding="utf-8")\n\nfor marker in (\n    'CONF_SHOW_ALL_SWITCH_VISION_SIDEBAR_ITEMS',\n    'CONF_SHOW_HUB_IN_SIDEBAR',\n    'CONF_SHOW_INSTALLER_IN_SIDEBAR',\n    'AddonsOptions(ingress_panel=bool(show_in_sidebar))',\n    'switch_vision/set_native_header_shortcut_order',\n    'DATA_NATIVE_HEADER_SETTINGS',\n    'DATA_ADDONS_LIST',\n    '_resolve_switch_vision_app_slug',\n    'slug.endswith(suffix)',\n    '"panel_path": f"/{slug}"',\n    '"config_path": f"/config/app/{slug}/config"',\n    'NATIVE_HEADER_SHORTCUT_OPTION_KEYS',\n):\n    assert marker in INIT, marker\n\nfor marker in (\n    'sidebar_hub_not_installed',\n    'sidebar_installer_not_installed',\n    'shortcut_snmp2mqtt_not_installed',\n    'read_only',\n    'vol.Required("native_header")',\n):\n    assert marker in FLOW, marker\n\nfor marker in (\n    'Switch Vision Hub',\n    '/config/integrations/integration/switch_vision',\n    'location-changed',\n    'shortcut-editor',\n    'checkbox.type = "checkbox"',\n    '_moveShortcut(id, -1)',\n    '_moveShortcut(id, 1)',\n    'Cancel',\n    'Done',\n    'set_native_header_shortcut_order',\n    'this._hass?.user?.is_admin === true',\n    'panel_path',\n    'config_path',\n):\n    assert marker in PANEL, marker\n\nassert 'hass-navigate' not in PANEL\nassert 'dragstart' not in PANEL\nassert '.draggable' not in PANEL\nassert 'event.clientX < rect.left + rect.width / 2' not in PANEL\nassert 'type: "supervisor/api"' not in PANEL\nassert 'CONF_SHOW_HUB_IN_SIDEBAR in entry.options' in INIT\nassert 'get("ingress_panel", True)' in INIT\nassert 'CONF_SHOW_INSTALLER_IN_SIDEBAR in self.config_entry.options' in FLOW\nassert 'discovery.get("ingress_panel", True)' in FLOW\nassert 'installer.get("ingress_panel", True)' in FLOW\nassert 'Not installed' in STRINGS\nassert INIT.index("NATIVE_HEADER_SHORTCUT_IDS = (") < INIT.index("SET_NATIVE_HEADER_ORDER_WS_SCHEMA = {")\nassert 'switch_vision/get_app_states' in INIT\nassert 'websocket_get_app_states' in INIT\nassert 'sidebar_master and lovelace_preference' in INIT\nassert 'saved.pop(synthetic_key, None)' in FLOW\nassert 'switch_vision/get_app_states' in PANEL\nprint('Core 2.4.5 sidebar/header contracts: PASS')\n'''
write(TEST, test)

print("Prepared Switch Vision Core v2.4.5 Native header usability hotfix")

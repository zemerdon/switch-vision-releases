const PANEL_VERSION = "2.4.4";
const CARD_MODULE_URL = `/api/switch_vision/switch-vision-card.js?v=${PANEL_VERSION}`;
const NATIVE_CARD_TYPE = `switch-vision-3650-v${PANEL_VERSION.replace(/[^0-9a-z]+/gi, "-").toLowerCase()}`;

class SwitchVisionPanel extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._hass = null;
    this._panel = null;
    this._cards = [];
    this._loaded = false;
    this._loading = false;
    this._lastModified = null;
    this._lastShowCalibrationButtons = null;
    this._showDashboardHeader = true;
    this._nativeHeader = { enabled: true, show_summary: true, show_refresh: true, show_version: true, order: [], shortcuts: {} };
    this._shortcutAvailability = { discovery: false, installer: false, snmp2mqtt: false, unifi2mqtt: false };
    this._customizingShortcuts = false;
    this._draggedShortcutId = null;
    this._lastNativeHeaderSignature = null;
    this._pollTimer = null;
    this._loadSequence = 0;
    this._activeLoadId = 0;
    this._visibilityHandler = () => {
      if (!document.hidden) this._checkForUpdate(true);
      this._schedulePoll();
    };
  }

  set hass(value) {
    this._hass = value;
    for (const card of this._cards) card.hass = value;
    if (this.isConnected && !this._loaded && !this._loading) this._load();
  }

  get hass() { return this._hass; }

  set panel(value) {
    this._panel = value;
    if (this.isConnected && !this._loaded && !this._loading) this._load();
  }

  connectedCallback() {
    if (!this.shadowRoot.getElementById("cards")) this._renderShell();
    document.addEventListener("visibilitychange", this._visibilityHandler);
    window.addEventListener("focus", this._visibilityHandler);
    if (this._hass && !this._loading) {
      if (!this._loaded) this._load();
      else void this._checkForUpdate(true);
    }
    this._schedulePoll();
  }

  disconnectedCallback() {
    document.removeEventListener("visibilitychange", this._visibilityHandler);
    window.removeEventListener("focus", this._visibilityHandler);
    if (this._pollTimer) clearTimeout(this._pollTimer);
    this._pollTimer = null;
    this._activeLoadId = ++this._loadSequence;
    this._loading = false;
    const refreshButton = this.shadowRoot.getElementById("refresh");
    if (refreshButton) {
      refreshButton.disabled = false;
      refreshButton.textContent = "Refresh";
    }
  }

  _renderShell() {
    this.shadowRoot.innerHTML = `
      <style>
        :host{display:block;min-height:100%;background:var(--primary-background-color,#11161b);color:var(--primary-text-color,#e8eef3);font-family:var(--paper-font-body1_-_font-family,Arial,sans-serif)}
        .page{max-width:1280px;margin:0 auto;padding:10px 16px 40px}
        .native-header{margin:0 0 12px}.native-header[hidden]{display:none!important}
        .shortcut-row{display:flex;align-items:center;gap:8px;margin:0 0 8px;overflow-x:auto;padding:1px 0 3px;scrollbar-width:thin}
        .shortcut-row[hidden]{display:none!important}.shortcut{flex:0 0 auto;white-space:nowrap;background:var(--secondary-background-color,#34414a);font-size:12px;padding:7px 10px}
        .shortcut:hover,.shortcut:focus-visible{background:var(--primary-color,#2b8cc4);outline:none}.shortcut[disabled]{opacity:.45;cursor:not-allowed}.shortcut.dragging{opacity:.45}.shortcut.customizing{cursor:grab;border:1px dashed rgba(127,180,220,.75)}
        .shortcut-tools{display:flex;gap:8px;align-items:center;flex:0 0 auto}.shortcut-tools button{font-size:12px;padding:7px 9px}.shortcut-hint{font-size:12px;opacity:.72;white-space:nowrap}
        .compact-head{display:flex;align-items:center;gap:12px;margin:0;min-height:38px}
        .compact-head.header-hidden{margin:0;min-height:0}
        .compact-head.header-hidden .summary,.compact-head.header-hidden #refresh,.compact-head.header-hidden .version{display:none}
        .compact-head.header-hidden .menu-toggle{margin:0 0 8px}
        .menu-toggle{display:none;align-items:center;justify-content:center;flex:0 0 40px;width:40px;height:40px;padding:0;border-radius:10px;background:transparent;color:var(--primary-text-color,#e8eef3);font-size:27px;font-weight:400;line-height:1}
        .menu-toggle:hover,.menu-toggle:focus-visible{background:var(--secondary-background-color,rgba(127,127,127,.18));outline:none}
        .summary{flex:1;min-width:0;border-left:4px solid #3e8fc5;border-radius:8px;padding:9px 12px;background:var(--card-background-color,#1c242b);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
        .version{font-size:12px;border:1px solid rgba(127,180,220,.45);border-radius:999px;padding:5px 9px;white-space:nowrap}
        button{border:0;border-radius:8px;padding:8px 11px;background:var(--primary-color,#2b8cc4);color:#fff;font-weight:600;cursor:pointer}button.secondary{background:var(--secondary-background-color,#34414a)}button:disabled{opacity:.55;cursor:default}
        .error,.empty{border-radius:8px;padding:10px 13px;margin:0 0 10px;background:var(--card-background-color,#1c242b);box-shadow:var(--ha-card-box-shadow,0 2px 8px rgba(0,0,0,.22))}.error{border-left:4px solid #d26a5c}.empty{border-left:4px solid #d4a64e}
        [hidden]{display:none!important}
        .cards{display:grid;grid-template-columns:minmax(0,1fr);gap:18px}.cards.headers-hidden{gap:2px}.card-wrap{min-width:0}
        details{margin-top:16px;background:var(--card-background-color,#1c242b);border-radius:10px;padding:11px 14px}summary{cursor:pointer;font-weight:600}.advanced-actions{display:flex;gap:10px;flex-wrap:wrap;margin:12px 0}
        .meta{font-family:monospace;white-space:pre-wrap;word-break:break-word;background:#0d1216;padding:12px;border-radius:8px;max-height:320px;overflow:auto}
        @media(max-width:870px){.menu-toggle{display:flex}}
        @media(max-width:650px){.page{padding:8px 8px 28px}.compact-head{gap:7px}.summary{font-size:13px;padding:8px 9px}.version{font-size:11px;padding:4px 7px}button{padding:7px 9px}.menu-toggle{padding:0}.shortcut-row{gap:6px}.shortcut{font-size:11px;padding:6px 8px}}
      </style>
      <div class="page">
        <div id="native-header" class="native-header">
          <div id="shortcut-row" class="shortcut-row"></div>
          <div id="compact-head" class="compact-head">
            <button id="menu-toggle" class="menu-toggle" title="Open Home Assistant menu" aria-label="Open Home Assistant menu" type="button">☰</button>
            <div id="summary" class="summary">Loading generated switch configuration…</div>
            <button id="refresh" title="Refresh dashboard" aria-label="Refresh dashboard">Refresh</button>
            <span id="version" class="version">v${PANEL_VERSION}</span>
          </div>
        </div>

        <section id="dashboard-view">
          <div id="message"></div>
          <div id="cards" class="cards"></div>
          <details id="details"><summary>Advanced</summary><div class="advanced-actions"><button id="reload" class="secondary">Reload frontend modules</button></div><div id="meta" class="meta">No dashboard details loaded yet.</div></details>
        </section>

      </div>`;
    this.shadowRoot.getElementById("menu-toggle").addEventListener("click", () => this._toggleHomeAssistantMenu());
    this.shadowRoot.getElementById("refresh").addEventListener("click", () => this._load(true));
    this.shadowRoot.getElementById("reload").addEventListener("click", () => window.location.reload());


  }

  _toggleHomeAssistantMenu() {
    this.dispatchEvent(new CustomEvent("hass-toggle-menu", {
      bubbles: true,
      composed: true,
      detail: {}
    }));
  }

  _loadIsCurrent(loadId) {
    return this.isConnected && loadId === this._activeLoadId;
  }

  _applyDashboardHeaderVisibility(result) {
    const legacyConfigured = result?.show_dashboard_header ?? this.panel?.config?.show_dashboard_header;
    const incoming = result?.native_header || this.panel?.config?.native_header || {};
    this._nativeHeader = {
      enabled: incoming.enabled ?? (legacyConfigured !== false),
      show_summary: incoming.show_summary !== false,
      show_refresh: incoming.show_refresh !== false,
      show_version: incoming.show_version !== false,
      order: Array.isArray(incoming.order) ? incoming.order.map(String) : [],
      shortcuts: incoming.shortcuts && typeof incoming.shortcuts === "object" ? { ...incoming.shortcuts } : {}
    };
    this._showDashboardHeader = this._nativeHeader.enabled !== false;
    const wholeHeader = this.shadowRoot.getElementById("native-header");
    if (wholeHeader) wholeHeader.hidden = !this._showDashboardHeader;
    const summary = this.shadowRoot.getElementById("summary");
    const refresh = this.shadowRoot.getElementById("refresh");
    const version = this.shadowRoot.getElementById("version");
    if (summary) summary.hidden = this._nativeHeader.show_summary === false;
    if (refresh) refresh.hidden = this._nativeHeader.show_refresh === false;
    if (version) version.hidden = this._nativeHeader.show_version === false;
    this._lastNativeHeaderSignature = JSON.stringify(this._nativeHeader);
    this._renderShortcuts();
  }

  _shortcutDefinitions() {
    return {
      hub: { label: "Switch Vision Hub", app: "discovery", path: "/app/switch_vision_discovery" },
      switch_vision_settings: { label: "Switch Vision Settings", path: "/config/integrations/integration/switch_vision" },
      discovery_settings: { label: "Discovery Settings", app: "discovery", path: "/config/app/switch_vision_discovery/config" },
      installer: { label: "Switch Vision Installer", app: "installer", path: "/app/switch_vision_installer" },
      installer_settings: { label: "Installer Settings", app: "installer", path: "/config/app/switch_vision_installer/config" },
      snmp2mqtt_settings: { label: "SNMP2MQTT Settings", app: "snmp2mqtt", path: "/config/app/switch_vision_snmp2mqtt/config" },
      unifi2mqtt_settings: { label: "UniFi2MQTT Settings", app: "unifi2mqtt", path: "/config/app/switch_vision_unifi2mqtt/config" }
    };
  }

  _navigate(path) {
    this.dispatchEvent(new CustomEvent("hass-navigate", {
      bubbles: true, composed: true, detail: { navigate: path }
    }));
  }

  async _refreshShortcutAvailability() {
    if (!this._hass) return;
    const next = { discovery: false, installer: false, snmp2mqtt: false, unifi2mqtt: false };
    try {
      const result = await this._hass.callWS({ type: "switch_vision/get_app_states" });
      const apps = result?.apps && typeof result.apps === "object" ? result.apps : {};
      for (const key of Object.keys(next)) next[key] = apps[key]?.installed === true;
    } catch (error) {
      console.warn("Switch Vision could not read app availability", error);
    }
    this._shortcutAvailability = next;
    this._renderShortcuts();
  }

  _renderShortcuts() {
    const root = this.shadowRoot.getElementById("shortcut-row");
    if (!root) return;
    root.replaceChildren();
    if (!this._showDashboardHeader) { root.hidden = true; return; }
    const defs = this._shortcutDefinitions();
    const enabled = this._nativeHeader.shortcuts || {};
    const order = Array.isArray(this._nativeHeader.order) && this._nativeHeader.order.length
      ? this._nativeHeader.order
      : Object.keys(defs);
    const rendered = [];
    for (const id of order) {
      const def = defs[id];
      if (!def || enabled[id] === false) continue;
      const installed = !def.app || this._shortcutAvailability[def.app] === true;
      if (!installed) continue;
      const button = document.createElement("button");
      button.type = "button";
      button.className = `shortcut${this._customizingShortcuts ? " customizing" : ""}`;
      button.dataset.shortcutId = id;
      button.textContent = def.label;
      button.title = this._customizingShortcuts ? "Drag to reorder" : def.label;
      button.draggable = this._customizingShortcuts;
      button.addEventListener("click", (event) => {
        if (this._customizingShortcuts) { event.preventDefault(); return; }
        this._navigate(def.path);
      });
      button.addEventListener("dragstart", () => { this._draggedShortcutId = id; button.classList.add("dragging"); });
      button.addEventListener("dragend", () => { this._draggedShortcutId = null; button.classList.remove("dragging"); });
      button.addEventListener("dragover", (event) => {
        if (!this._customizingShortcuts || !this._draggedShortcutId || this._draggedShortcutId === id) return;
        event.preventDefault();
        const dragged = root.querySelector(`[data-shortcut-id="${this._draggedShortcutId}"]`);
        if (!dragged || dragged === button) return;
        const rect = button.getBoundingClientRect();
        const before = event.clientX < rect.left + rect.width / 2;
        root.insertBefore(dragged, before ? button : button.nextSibling);
      });
      root.appendChild(button);
      rendered.push(id);
    }
    if (rendered.length) {
      const tools = document.createElement("span");
      tools.className = "shortcut-tools";
      if (this._customizingShortcuts) {
        const hint = document.createElement("span");
        hint.className = "shortcut-hint";
        hint.textContent = "Drag shortcuts, then Done";
        tools.appendChild(hint);
      }
      const customize = document.createElement("button");
      customize.type = "button";
      customize.className = "secondary";
      customize.textContent = this._customizingShortcuts ? "Done" : "Customize";
      customize.addEventListener("click", () => this._toggleShortcutCustomization());
      tools.appendChild(customize);
      root.appendChild(tools);
    }
    root.hidden = rendered.length === 0;
  }

  async _toggleShortcutCustomization() {
    if (!this._customizingShortcuts) {
      this._customizingShortcuts = true;
      this._renderShortcuts();
      return;
    }
    const root = this.shadowRoot.getElementById("shortcut-row");
    const visibleOrder = root ? [...root.querySelectorAll("button.shortcut")].map(button => button.dataset.shortcutId).filter(Boolean) : [];
    const fullOrder = Array.isArray(this._nativeHeader.order) ? [...this._nativeHeader.order] : [];
    const visibleSet = new Set(visibleOrder);
    const mergedOrder = [...visibleOrder, ...fullOrder.filter(id => !visibleSet.has(id))];
    try {
      const result = await this._hass.callWS({ type: "switch_vision/set_native_header_shortcut_order", order: mergedOrder });
      this._nativeHeader.order = Array.isArray(result?.order) ? result.order : mergedOrder;
    } catch (error) {
      console.warn("Switch Vision could not save shortcut order", error);
    } finally {
      this._customizingShortcuts = false;
      this._renderShortcuts();
    }
  }

  _updateRuntimeVersion(result) {
    const runtimeVersion = result?.runtime_version || this.panel?.config?.runtime_version || PANEL_VERSION;
    const versionBadge = this.shadowRoot.getElementById("version");
    if (versionBadge) versionBadge.textContent = `v${runtimeVersion}`;
  }

  _commitEmptyDashboard(result, summaryText, messageHtml) {
    const cardsRoot = this.shadowRoot.getElementById("cards");
    const summary = this.shadowRoot.getElementById("summary");
    const message = this.shadowRoot.getElementById("message");
    cardsRoot.replaceChildren();
    this._cards = [];
    message.className = "empty";
    message.innerHTML = messageHtml;
    summary.textContent = summaryText;
    this._lastModified = result?.modified || null;
    this._lastShowCalibrationButtons = result?.show_calibration_buttons !== false;
    this._loaded = true;
    this._showMeta(result || {});
  }

  async _load(force = false) {
    if (!this._hass || this._loading || !this.isConnected) return;
    const loadId = ++this._loadSequence;
    this._activeLoadId = loadId;
    this._loading = true;

    const refreshButton = this.shadowRoot.getElementById("refresh");
    const summary = this.shadowRoot.getElementById("summary");
    const message = this.shadowRoot.getElementById("message");
    const cardsRoot = this.shadowRoot.getElementById("cards");
    const hadCards = this._cards.length > 0 && cardsRoot.children.length > 0;
    const previousSummary = summary.innerHTML;

    refreshButton.disabled = true;
    refreshButton.textContent = "Refreshing…";
    if (hadCards) {
      summary.textContent = "Refreshing generated switch configuration…";
    } else {
      summary.textContent = "Loading generated switch configuration…";
      message.replaceChildren();
      message.className = "";
    }

    try {
      const result = await this._hass.callWS({ type: "switch_vision/get_dashboard_panel", refresh: !!force });
      if (!this._loadIsCurrent(loadId)) return;
      this._updateRuntimeVersion(result);
      this._applyDashboardHeaderVisibility(result);
      void this._refreshShortcutAvailability();
      cardsRoot.classList.toggle("headers-hidden", result?.show_card_headers === false);

      if (!result.exists) {
        this._commitEmptyDashboard(
          result,
          "No switch cards loaded",
          `<b>No switches are ready to display yet.</b><br>Run Discovery with dashboard-card generation enabled.`
        );
        return;
      }

      const configs = Array.isArray(result.cards) ? result.cards : [];
      if (!configs.length) {
        this._commitEmptyDashboard(
          result,
          "No switch cards loaded",
          `<b>The generated dashboard contains no Switch Vision cards.</b><br>Run Discovery again or use the generated YAML manually while troubleshooting.`
        );
        return;
      }

      // Always import the release-specific module. Home Assistant keeps custom
      // elements alive during SPA navigation, and the stable manual-YAML tag may
      // still point at an older release in the same browser session. The module
      // registers a versioned native-panel alias that cannot collide with it.
      await import(CARD_MODULE_URL);
      if (!customElements.get(NATIVE_CARD_TYPE)) {
        throw new Error(`Switch Vision ${PANEL_VERSION} card renderer did not register ${NATIVE_CARD_TYPE}`);
      }
      if (!this._loadIsCurrent(loadId)) return;

      // Build the complete replacement away from the visible dashboard. A bad
      // card config or failed module import therefore cannot remove working cards.
      const stagedRoot = document.createDocumentFragment();
      const stagedCards = [];
      for (const config of configs) {
        const card = document.createElement(NATIVE_CARD_TYPE);
        card._globalShowCardHeaders = result?.show_card_headers !== false;
        card.setConfig({
          ...config,
          show_card_header: result?.show_card_headers !== false,
          type: "custom:switch-vision-3650"
        });
        card.hass = this._hass;
        const wrap = document.createElement("div");
        wrap.className = "card-wrap";
        wrap.appendChild(card);
        stagedRoot.appendChild(wrap);
        stagedCards.push(card);
      }

      if (!this._loadIsCurrent(loadId)) return;
      cardsRoot.replaceChildren(stagedRoot);
      this._cards = stagedCards;

      const updated = result.modified ? new Date(result.modified * 1000).toLocaleString() : "Unknown";
      summary.innerHTML = `<b>${configs.length} switch card${configs.length === 1 ? "" : "s"} loaded</b> &bull; Last generated ${this._escape(updated)}`;
      message.replaceChildren();
      message.className = "";
      this._lastModified = result.modified || null;
      this._lastShowCalibrationButtons = result.show_calibration_buttons !== false;
      this._loaded = true;
      this._showMeta(result);
    } catch (error) {
      if (!this._loadIsCurrent(loadId)) return;
      message.className = "error";
      if (hadCards) {
        summary.innerHTML = previousSummary;
        message.innerHTML = `<b>Dashboard refresh failed; the existing switch cards remain active.</b><br>${this._escape(String(error))}<br><br>The next automatic poll will retry.`;
      } else {
        message.innerHTML = `<b>Switch dashboard could not be loaded.</b><br>${this._escape(String(error))}<br><br>The generated dashboard YAML remains available as a manual fallback.`;
        summary.textContent = "Dashboard update failed";
      }
    } finally {
      if (loadId === this._activeLoadId) {
        this._loading = false;
        refreshButton.disabled = false;
        refreshButton.textContent = "Refresh";
        this._schedulePoll();
      }
    }
  }

  _schedulePoll() {
    if (this._pollTimer) clearTimeout(this._pollTimer);
    this._pollTimer = null;
    if (!this.isConnected || document.hidden) return;
    this._pollTimer = setTimeout(() => this._checkForUpdate(false), 5000);
  }

  async _checkForUpdate(forceVisible = false) {
    if (!this._hass || this._loading || document.hidden) {
      this._schedulePoll();
      return;
    }
    try {
      const result = await this._hass.callWS({ type: "switch_vision/get_dashboard_panel", refresh: false });
      const modified = result && result.modified ? Number(result.modified) : null;
      const showCalibrationButtons = result && result.show_calibration_buttons !== false;
      const headerSignature = JSON.stringify(result?.native_header || {});
      const optionChanged = (this._lastShowCalibrationButtons !== null && showCalibrationButtons !== this._lastShowCalibrationButtons)
        || (this._lastNativeHeaderSignature !== null && headerSignature !== this._lastNativeHeaderSignature);
      if (!this._loaded || optionChanged || (modified && this._lastModified && modified !== this._lastModified) || (modified && !this._lastModified)) {
        await this._load(true);
      } else if (forceVisible && result) {
        this._showMeta(result);
      }
    } catch (error) {
      // Keep the existing dashboard visible; the next poll will retry.
    } finally {
      this._schedulePoll();
    }
  }

  _showMeta(result) {
    const meta = this.shadowRoot.getElementById("meta");
    meta.textContent = JSON.stringify({
      runtime_version: result.runtime_version || this.panel?.config?.runtime_version || PANEL_VERSION,
      asset_revision: result.asset_revision || this.panel?.config?.asset_revision || null,
      source: result.path,
      modified: result.modified ? new Date(result.modified * 1000).toISOString() : null,
      card_count: result.card_count,
      warnings: result.warnings || [],
      show_calibration_buttons: result.show_calibration_buttons !== false,
      manual_yaml_fallback: true,
      native_header: result.native_header || this._nativeHeader
    }, null, 2);
  }

  _escape(value) {
    return String(value).replace(/[&<>'"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;","'":"&#39;",'"':"&quot;"}[c]));
  }
}

SwitchVisionPanel.switchVisionVersion = PANEL_VERSION;

if (!customElements.get("switch-vision-panel")) {
  customElements.define("switch-vision-panel", SwitchVisionPanel);
}

// Community dashboard strategies may be created after an integration upgrade
// while an older stable panel element is still alive in Home Assistant's SPA.
// Give each release a versioned alias so the dashboard host can always use the
// renderer shipped with the current integration without disturbing the stable
// sidebar custom-panel tag.
const VERSIONED_PANEL_TYPE = `switch-vision-panel-v${PANEL_VERSION.replace(/[^0-9a-z]+/gi, "-").toLowerCase()}`;
if (!customElements.get(VERSIONED_PANEL_TYPE)) {
  class SwitchVisionVersionedPanel extends SwitchVisionPanel {}
  SwitchVisionVersionedPanel.switchVisionVersion = PANEL_VERSION;
  customElements.define(VERSIONED_PANEL_TYPE, SwitchVisionVersionedPanel);
}

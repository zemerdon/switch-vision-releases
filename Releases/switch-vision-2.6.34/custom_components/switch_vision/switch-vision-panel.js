const PANEL_VERSION = "2.6.34";
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
    this._shortcutAppStates = { discovery: {}, installer: {}, snmp2mqtt: {}, unifi2mqtt: {} };
    this._customizingShortcuts = false;
    this._shortcutDraft = null;
    this._shortcutEditorError = "";
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
        .shortcut:hover,.shortcut:focus-visible{background:var(--primary-color,#2b8cc4);outline:none}.shortcut[disabled]{opacity:.45;cursor:not-allowed}
        .shortcut-tools{display:flex;gap:8px;align-items:center;flex:0 0 auto}.shortcut-tools button{font-size:12px;padding:7px 9px}
        .shortcut-row.editing{display:block;overflow:visible}.shortcut-editor{display:grid;gap:6px;min-width:min(720px,100%);padding:10px;border:1px solid rgba(127,180,220,.28);border-radius:10px;background:var(--card-background-color,#1c242b)}
        .shortcut-editor-title{font-size:13px;font-weight:700;margin-bottom:2px}.shortcut-edit-row{display:grid;grid-template-columns:minmax(220px,1fr) auto;gap:10px;align-items:center;padding:6px 7px;border-radius:7px;background:var(--secondary-background-color,#27323a)}
        .shortcut-edit-label{display:flex;align-items:center;gap:9px;min-width:0}.shortcut-edit-label input{width:17px;height:17px;margin:0;flex:0 0 auto}.shortcut-edit-name{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.shortcut-edit-status{font-size:11px;opacity:.65;margin-left:4px}.shortcut-move{display:flex;gap:5px}.shortcut-move button{min-width:38px;padding:5px 8px}.shortcut-editor-actions{display:flex;justify-content:flex-end;gap:7px;margin-top:3px}.shortcut-editor-error{font-size:12px;color:var(--error-color,#db4437)}
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
        .meta{font-family:monospace;white-space:pre-wrap;word-break:break-word;background:#0d1216;color:#e8eef3;padding:12px;border-radius:8px;max-height:320px;overflow:auto}
        @media(max-width:870px){.menu-toggle{display:flex}}
        @media(max-width:650px){.page{padding:8px 8px 28px}.compact-head{gap:7px}.summary{font-size:13px;padding:8px 9px}.version{font-size:11px;padding:4px 7px}button{padding:7px 9px}.menu-toggle{padding:0}.shortcut-row{gap:6px}.shortcut{font-size:11px;padding:6px 8px}.shortcut-edit-row{grid-template-columns:1fr auto}.shortcut-edit-name{max-width:180px}}
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
    const baseSlugs = {
      discovery: "switch_vision_discovery",
      installer: "switch_vision_installer",
      snmp2mqtt: "switch_vision_snmp2mqtt",
      unifi2mqtt: "switch_vision_unifi2mqtt"
    };
    const stateFor = (key) => this._shortcutAppStates?.[key] || {};
    const panelPath = (key) => stateFor(key).panel_path || `/${baseSlugs[key]}`;
    const configPath = (key) => stateFor(key).config_path || `/config/app/${baseSlugs[key]}/config`;
    return {
      hub: { label: "Switch Vision Hub", app: "discovery", path: panelPath("discovery") },
      maintenance: { label: "Maintenance", app: "discovery", path: `${panelPath("discovery")}?view=maintenance` },
      switch_vision_settings: { label: "Switch Vision Settings", path: "/config/integrations/integration/switch_vision" },
      discovery_settings: { label: "Discovery Settings", app: "discovery", path: configPath("discovery") },
      installer: { label: "Switch Vision Installer", app: "installer", path: panelPath("installer") },
      installer_settings: { label: "Installer Settings", app: "installer", path: configPath("installer") },
      snmp2mqtt_settings: { label: "SNMP2MQTT Settings", app: "snmp2mqtt", path: configPath("snmp2mqtt") },
      unifi2mqtt_settings: { label: "UniFi2MQTT Settings", app: "unifi2mqtt", path: configPath("unifi2mqtt") }
    };
  }

  _navigate(path) {
    if (!path) return;
    const current = `${window.location.pathname}${window.location.search}${window.location.hash}`;
    const currentState = window.history.state && typeof window.history.state === "object" ? window.history.state : {};
    const state = currentState.root ? { root: true, from: current } : { from: current };
    window.history.pushState(state, "", path);
    window.dispatchEvent(new CustomEvent("location-changed", { detail: { replace: false } }));
  }

  async _refreshShortcutAvailability() {
    if (!this._hass) return;
    const blank = { installed: false, ingress: false, available: false, slug: "", panel_path: "", config_path: "" };
    const next = { discovery: { ...blank }, installer: { ...blank }, snmp2mqtt: { ...blank }, unifi2mqtt: { ...blank } };
    try {
      const result = await this._hass.callWS({ type: "switch_vision/get_app_states" });
      const apps = result?.apps && typeof result.apps === "object" ? result.apps : {};
      for (const key of Object.keys(next)) next[key] = { ...blank, ...(apps[key] || {}) };
    } catch (error) {
      console.warn("Switch Vision could not read app availability", error);
    }
    this._shortcutAppStates = next;
    this._renderShortcuts();
  }

  _normalizedShortcutOrder(defs) {
    const raw = Array.isArray(this._nativeHeader.order) ? this._nativeHeader.order : [];
    const order = [];
    for (const id of raw) if (defs[id] && !order.includes(id)) order.push(id);
    for (const id of Object.keys(defs)) if (!order.includes(id)) order.push(id);
    return order;
  }

  _renderShortcuts() {
    const root = this.shadowRoot.getElementById("shortcut-row");
    if (!root) return;
    root.replaceChildren();
    root.classList.toggle("editing", this._customizingShortcuts);
    if (!this._showDashboardHeader) { root.hidden = true; return; }
    const defs = this._shortcutDefinitions();

    if (this._customizingShortcuts) {
      this._renderShortcutEditor(root, defs);
      root.hidden = false;
      return;
    }

    const enabled = this._nativeHeader.shortcuts || {};
    const order = this._normalizedShortcutOrder(defs);
    let rendered = 0;
    for (const id of order) {
      const def = defs[id];
      if (!def || enabled[id] === false) continue;
      const installed = !def.app || this._shortcutAppStates?.[def.app]?.installed === true;
      if (!installed) continue;
      const button = document.createElement("button");
      button.type = "button";
      button.className = "shortcut";
      button.dataset.shortcutId = id;
      button.textContent = def.label;
      button.title = def.label;
      button.addEventListener("click", () => this._navigate(def.path));
      root.appendChild(button);
      rendered += 1;
    }

    const isAdmin = this._hass?.user?.is_admin === true;
    if (isAdmin) {
      const tools = document.createElement("span");
      tools.className = "shortcut-tools";
      const customize = document.createElement("button");
      customize.type = "button";
      customize.className = "secondary";
      customize.textContent = "Customize";
      customize.addEventListener("click", () => this._beginShortcutCustomization());
      tools.appendChild(customize);
      root.appendChild(tools);
    }
    root.hidden = rendered === 0 && !isAdmin;
  }

  _beginShortcutCustomization() {
    if (this._hass?.user?.is_admin !== true) return;
    const defs = this._shortcutDefinitions();
    this._shortcutDraft = {
      order: this._normalizedShortcutOrder(defs),
      shortcuts: Object.fromEntries(Object.keys(defs).map((id) => [id, this._nativeHeader.shortcuts?.[id] !== false]))
    };
    this._shortcutEditorError = "";
    this._customizingShortcuts = true;
    this._renderShortcuts();
  }

  _renderShortcutEditor(root, defs) {
    const draft = this._shortcutDraft || { order: this._normalizedShortcutOrder(defs), shortcuts: {} };
    const editor = document.createElement("div");
    editor.className = "shortcut-editor";

    const title = document.createElement("div");
    title.className = "shortcut-editor-title";
    title.textContent = "Customize shortcuts";
    editor.appendChild(title);

    for (let index = 0; index < draft.order.length; index += 1) {
      const id = draft.order[index];
      const def = defs[id];
      if (!def) continue;
      const installed = !def.app || this._shortcutAppStates?.[def.app]?.installed === true;

      const row = document.createElement("div");
      row.className = "shortcut-edit-row";

      const label = document.createElement("label");
      label.className = "shortcut-edit-label";
      const checkbox = document.createElement("input");
      checkbox.type = "checkbox";
      checkbox.checked = draft.shortcuts[id] !== false;
      checkbox.disabled = !installed;
      checkbox.addEventListener("change", () => { draft.shortcuts[id] = checkbox.checked; });
      label.appendChild(checkbox);
      const name = document.createElement("span");
      name.className = "shortcut-edit-name";
      name.textContent = def.label;
      label.appendChild(name);
      if (!installed) {
        const status = document.createElement("span");
        status.className = "shortcut-edit-status";
        status.textContent = "Not installed";
        label.appendChild(status);
      }
      row.appendChild(label);

      const move = document.createElement("span");
      move.className = "shortcut-move";
      const up = document.createElement("button");
      up.type = "button";
      up.className = "secondary";
      up.textContent = "↑";
      up.title = `Move ${def.label} up`;
      up.setAttribute("aria-label", up.title);
      up.disabled = index === 0;
      up.addEventListener("click", () => this._moveShortcut(id, -1));
      move.appendChild(up);
      const down = document.createElement("button");
      down.type = "button";
      down.className = "secondary";
      down.textContent = "↓";
      down.title = `Move ${def.label} down`;
      down.setAttribute("aria-label", down.title);
      down.disabled = index === draft.order.length - 1;
      down.addEventListener("click", () => this._moveShortcut(id, 1));
      move.appendChild(down);
      row.appendChild(move);
      editor.appendChild(row);
    }

    if (this._shortcutEditorError) {
      const error = document.createElement("div");
      error.className = "shortcut-editor-error";
      error.textContent = this._shortcutEditorError;
      editor.appendChild(error);
    }

    const actions = document.createElement("div");
    actions.className = "shortcut-editor-actions";
    const cancel = document.createElement("button");
    cancel.type = "button";
    cancel.className = "secondary";
    cancel.textContent = "Cancel";
    cancel.addEventListener("click", () => this._cancelShortcutCustomization());
    actions.appendChild(cancel);
    const done = document.createElement("button");
    done.type = "button";
    done.textContent = "Done";
    done.addEventListener("click", () => void this._saveShortcutCustomization());
    actions.appendChild(done);
    editor.appendChild(actions);
    root.appendChild(editor);
  }

  _moveShortcut(id, delta) {
    const draft = this._shortcutDraft;
    if (!draft || !Array.isArray(draft.order)) return;
    const index = draft.order.indexOf(id);
    const target = index + delta;
    if (index < 0 || target < 0 || target >= draft.order.length) return;
    [draft.order[index], draft.order[target]] = [draft.order[target], draft.order[index]];
    this._renderShortcuts();
  }

  _cancelShortcutCustomization() {
    this._shortcutDraft = null;
    this._shortcutEditorError = "";
    this._customizingShortcuts = false;
    this._renderShortcuts();
  }

  async _saveShortcutCustomization() {
    if (!this._shortcutDraft || this._hass?.user?.is_admin !== true) return;
    try {
      const result = await this._hass.callWS({
        type: "switch_vision/set_native_header_shortcut_order",
        order: [...this._shortcutDraft.order],
        shortcuts: { ...this._shortcutDraft.shortcuts }
      });
      this._nativeHeader.order = Array.isArray(result?.order) ? result.order : [...this._shortcutDraft.order];
      this._nativeHeader.shortcuts = result?.shortcuts && typeof result.shortcuts === "object"
        ? { ...result.shortcuts }
        : { ...this._shortcutDraft.shortcuts };
      this._shortcutDraft = null;
      this._shortcutEditorError = "";
      this._customizingShortcuts = false;
      this._renderShortcuts();
    } catch (error) {
      console.warn("Switch Vision could not save shortcut customization", error);
      this._shortcutEditorError = `Could not save shortcut changes: ${String(error)}`;
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

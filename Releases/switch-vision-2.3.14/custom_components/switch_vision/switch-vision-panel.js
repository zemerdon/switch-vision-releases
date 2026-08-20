const PANEL_VERSION = "2.3.14";
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
        .compact-head{display:flex;align-items:center;gap:12px;margin:0 0 10px;min-height:38px}
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
        @media(max-width:650px){.page{padding:8px 8px 28px}.compact-head{gap:7px}.summary{font-size:13px;padding:8px 9px}.version{font-size:11px;padding:4px 7px}button{padding:7px 9px}.menu-toggle{padding:0}}
      </style>
      <div class="page">
        <div id="compact-head" class="compact-head">
          <button id="menu-toggle" class="menu-toggle" title="Open Home Assistant menu" aria-label="Open Home Assistant menu" type="button">☰</button>
          <div id="summary" class="summary">Loading generated switch configuration…</div>
          <button id="refresh" title="Refresh dashboard" aria-label="Refresh dashboard">Refresh</button>
          <span id="version" class="version">v${PANEL_VERSION}</span>
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
    const configured = result?.show_dashboard_header ?? this.panel?.config?.show_dashboard_header;
    this._showDashboardHeader = configured !== false;
    const header = this.shadowRoot.getElementById("compact-head");
    if (header) header.classList.toggle("header-hidden", !this._showDashboardHeader);
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
      const optionChanged = this._lastShowCalibrationButtons !== null && showCalibrationButtons !== this._lastShowCalibrationButtons;
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
      manual_yaml_fallback: true
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

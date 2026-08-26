(() => {
"use strict";
const SWITCH_VISION_DASHBOARD_VERSION = "2.6.9";
function switchVisionPanelModuleUrl(version) {
  return `/api/switch_vision/switch-vision-panel.js?v=${encodeURIComponent(version)}`;
}

function switchVisionVersionedPanelType(version) {
  return `switch-vision-panel-v${String(version).replace(/[^0-9a-z]+/gi, "-").toLowerCase()}`;
}
const SWITCH_VISION_DASHBOARD_CARD = "switch-vision-native-dashboard";
const SWITCH_VISION_STRATEGY = "switch-vision";
const SWITCH_VISION_RUNTIME_LOOKUP_TIMEOUT_MS = 1000;

async function switchVisionRuntimeVersion(hass) {
  if (!hass || typeof hass.callWS !== "function") {
    return SWITCH_VISION_DASHBOARD_VERSION;
  }

  let timerId = null;
  try {
    const runtime = await Promise.race([
      hass.callWS({
        type: "switch_vision/get_dashboard_panel",
        refresh: false,
      }),
      new Promise((resolve) => {
        timerId = setTimeout(
          () => resolve(null),
          SWITCH_VISION_RUNTIME_LOOKUP_TIMEOUT_MS,
        );
      }),
    ]);
    if (runtime?.runtime_version) return String(runtime.runtime_version);
  } catch (_error) {
    // A disconnected or overloaded Home Assistant websocket must not prevent
    // Lovelace from constructing the dashboard. The delegated panel can retry
    // normally after the client connection recovers.
  } finally {
    if (timerId !== null) clearTimeout(timerId);
  }

  return SWITCH_VISION_DASHBOARD_VERSION;
}

class SwitchVisionNativeDashboardCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._hass = null;
    this._config = {};
    this._panelHost = null;
    this._loadPromise = null;
  }

  setConfig(config) {
    this._config = config && typeof config === "object" ? { ...config } : {};
    this._syncPanelConfig();
  }

  set hass(value) {
    this._hass = value;
    if (this._panelHost) this._panelHost.hass = value;
    if (this.isConnected) void this._ensurePanel();
  }

  get hass() {
    return this._hass;
  }

  connectedCallback() {
    if (!this.shadowRoot.firstChild) {
      const style = document.createElement("style");
      style.textContent = `:host{display:block;width:100%;min-height:100vh}#mount{display:block;width:100%;min-height:100vh}`;
      const mount = document.createElement("div");
      mount.id = "mount";
      this.shadowRoot.append(style, mount);
    }
    void this._ensurePanel();
  }

  disconnectedCallback() {
    // The delegated panel owns and clears its own visibility/focus/poll timers.
    // Drop our reference so returning to the dashboard creates a clean host.
    this._panelHost = null;
    this._loadPromise = null;
  }

  getCardSize() {
    return 1;
  }

  _runtimeVersion() {
    return String(this._config?.runtime_version || SWITCH_VISION_DASHBOARD_VERSION);
  }

  _panelConfig() {
    const runtimeVersion = this._runtimeVersion();
    return {
      automatic_dashboard: true,
      version: runtimeVersion,
      runtime_version: runtimeVersion,
      asset_revision: runtimeVersion,
      manual_yaml_fallback: true,
      dashboard_strategy: true,
      ...this._config,
    };
  }

  _syncPanelConfig() {
    if (!this._panelHost) return;
    this._panelHost.panel = {
      title: "Switch Vision",
      config: this._panelConfig(),
    };
  }

  async _ensurePanel() {
    if (this._panelHost || !this.isConnected) return;
    const runtimeVersion = this._runtimeVersion();
    const panelType = switchVisionVersionedPanelType(runtimeVersion);
    if (!this._loadPromise) {
      this._loadPromise = import(switchVisionPanelModuleUrl(runtimeVersion));
    }
    try {
      await this._loadPromise;
      if (!this.isConnected || this._panelHost) return;
      if (!customElements.get(panelType)) {
        throw new Error(`Switch Vision ${runtimeVersion} panel renderer was not registered`);
      }
      const panel = document.createElement(panelType);
      panel.panel = {
        title: "Switch Vision",
        config: this._panelConfig(),
      };
      if (this._hass) panel.hass = this._hass;
      this.shadowRoot.getElementById("mount").replaceChildren(panel);
      this._panelHost = panel;
    } catch (error) {
      if (!this.isConnected) return;
      const mount = this.shadowRoot.getElementById("mount");
      if (mount) {
        const message = document.createElement("ha-alert");
        message.alertType = "error";
        message.textContent = `Switch Vision dashboard could not load: ${String(error)}`;
        mount.replaceChildren(message);
      }
    }
  }
}

if (!customElements.get(SWITCH_VISION_DASHBOARD_CARD)) {
  customElements.define(SWITCH_VISION_DASHBOARD_CARD, SwitchVisionNativeDashboardCard);
}

class SwitchVisionDashboardStrategy extends HTMLElement {
  static noEditor = true;
  static registryDependencies = [];

  static getCreateSuggestions(_hass) {
    return {
      title: "Switch Vision",
      icon: "switch-vision:logo",
    };
  }

  static async generate(config, hass) {
    // Keep runtime-version discovery bounded. During Home Assistant startup a
    // client may be processing thousands of restored state events; waiting
    // indefinitely for an auxiliary websocket response can make Lovelace mark
    // the whole strategy as a configuration error. Fall back to this resource
    // version and let the delegated panel retry once the connection recovers.
    const runtimeVersion = await switchVisionRuntimeVersion(hass);
    return {
      title: config?.title || "Switch Vision",
      views: [
        {
          title: "Switch Vision",
          path: "switch-vision",
          type: "panel",
          cards: [
            {
              type: `custom:${SWITCH_VISION_DASHBOARD_CARD}`,
              dashboard_strategy: true,
              runtime_version: runtimeVersion,
            },
          ],
        },
      ],
    };
  }
}

const strategyElement = `ll-strategy-dashboard-${SWITCH_VISION_STRATEGY}`;
const legacyStrategyElement = `ll-strategy-${SWITCH_VISION_STRATEGY}`;

// Home Assistant 2026.5+ resolves custom dashboard strategies using the
// ll-strategy-dashboard-* tag and still checks the legacy ll-strategy-* tag.
// Register both with distinct constructors so either loader path can resolve.
if (!customElements.get(strategyElement)) {
  customElements.define(strategyElement, SwitchVisionDashboardStrategy);
}
if (!customElements.get(legacyStrategyElement)) {
  class SwitchVisionLegacyDashboardStrategy extends SwitchVisionDashboardStrategy {}
  customElements.define(legacyStrategyElement, SwitchVisionLegacyDashboardStrategy);
}

window.customStrategies = window.customStrategies || [];
if (!window.customStrategies.some(
  (item) => item?.type === SWITCH_VISION_STRATEGY && item?.strategyType === "dashboard"
)) {
  window.customStrategies.push({
    type: SWITCH_VISION_STRATEGY,
    strategyType: "dashboard",
    name: "Switch Vision",
    description: "Live Switch Vision dashboard generated from the current Discovery output.",
    documentationURL: "https://switch-vision.zemerdon.com",
  });
}

// Visible only in the browser console and useful when troubleshooting the HA
// Community dashboard picker. Do not expose configuration or entity data.
console.info(
  `[Switch Vision ${SWITCH_VISION_DASHBOARD_VERSION}] dashboard strategy registered`,
  {
    current: Boolean(customElements.get(strategyElement)),
    legacy: Boolean(customElements.get(legacyStrategyElement)),
  },
);
})();

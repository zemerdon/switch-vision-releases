const PANEL_VERSION = "2.3.10";
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
    this._activeView = "dashboard";
    this._profileItems = [];
    this._selectedProfiles = new Set();
    this._profilesLoading = false;
    this._profilesLoaded = false;
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
        .hub-nav{display:flex;gap:8px;margin:0 0 12px}
        .hub-nav button{background:var(--secondary-background-color,#34414a)}
        .hub-nav button.active{background:var(--primary-color,#2b8cc4)}
        [hidden]{display:none!important}
        .cards{display:grid;grid-template-columns:minmax(0,1fr);gap:18px}.cards.headers-hidden{gap:2px}.card-wrap{min-width:0}
        .profiles-head{display:flex;align-items:center;gap:10px;margin-bottom:10px}
        .profiles-head .profiles-summary{flex:1}
        .profiles-toolbar{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin:0 0 10px}
        .profiles-toolbar .selection-summary{margin-right:auto;font-size:13px;opacity:.9}
        .profiles-root{display:grid;gap:10px}
        .profile-select{display:flex;align-items:center;gap:7px;margin-bottom:8px;font-size:12px}
        .profile-select input{width:16px;height:16px}
        .profile-card{background:var(--card-background-color,#1c242b);border-radius:10px;padding:13px 14px;box-shadow:var(--ha-card-box-shadow,0 2px 8px rgba(0,0,0,.22))}
        .profile-card.is-active{border-left:4px solid #46a36f}
        .profile-card.is-stale{border-left:4px solid #d26a5c}
        .profile-card.is-duplicate{border-left:4px solid #d4a64e}
        .profile-title{display:flex;align-items:center;gap:8px;flex-wrap:wrap;font-weight:700}
        .profile-badges{display:flex;gap:6px;flex-wrap:wrap}
        .profile-badge{font-size:11px;font-weight:700;border-radius:999px;padding:3px 7px;background:var(--secondary-background-color,#34414a)}
        .profile-badge.active{background:#2f7d4d}
        .profile-badge.warning{background:#886c20}
        .profile-badge.danger{background:#91483f}
        .profile-summary-line{margin-top:7px;font-size:13px;opacity:.9}
        .profile-details{margin-top:9px;padding-top:9px;border-top:1px solid rgba(127,127,127,.22);font-size:12px;line-height:1.55}
        .profile-details code{word-break:break-all}
        .profile-actions{display:flex;gap:8px;justify-content:flex-end;margin-top:11px}
        .profile-actions button.danger{background:#91483f}
        .profile-actions button:disabled{opacity:.45;cursor:not-allowed}
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
        <div class="hub-nav">
          <button id="view-dashboard" class="active" type="button">Dashboard</button>
          <button id="view-profiles" type="button">Calibration Profiles</button>
        </div>

        <section id="dashboard-view">
          <div id="message"></div>
          <div id="cards" class="cards"></div>
          <details id="details"><summary>Advanced</summary><div class="advanced-actions"><button id="reload" class="secondary">Reload frontend modules</button></div><div id="meta" class="meta">No dashboard details loaded yet.</div></details>
        </section>

        <section id="profiles-view" hidden>
          <div class="profiles-head">
            <div id="profiles-summary" class="profiles-summary">Calibration profiles have not been loaded yet.</div>
            <button id="refresh-profiles" type="button">Refresh Profiles</button>
          </div>
          <div id="profiles-message"></div>
          <div class="profiles-toolbar">
            <span id="profile-selection-summary" class="selection-summary">0 selected</span>
            <button id="select-stale-profiles" class="secondary" type="button">Select Stale</button>
            <button id="clean-stale-profiles" class="danger" type="button">Clean Stale Profiles</button>
            <button id="clear-profile-selection" class="secondary" type="button">Clear Selection</button>
            <button id="delete-selected-profiles" class="danger" type="button" disabled>Delete Selected</button>
          </div>
          <div id="profiles-root" class="profiles-root"></div>
        </section>
      </div>`;
    this.shadowRoot.getElementById("menu-toggle").addEventListener("click", () => this._toggleHomeAssistantMenu());
    this.shadowRoot.getElementById("refresh").addEventListener("click", () => this._load(true));
    this.shadowRoot.getElementById("reload").addEventListener("click", () => window.location.reload());
    this.shadowRoot.getElementById("view-dashboard").addEventListener("click", () => this._setView("dashboard"));
    this.shadowRoot.getElementById("view-profiles").addEventListener("click", () => this._setView("profiles"));
    this.shadowRoot.getElementById("refresh-profiles").addEventListener("click", () => this._loadProfiles(true));

    this.shadowRoot.getElementById("select-stale-profiles").addEventListener("click", () => {
      this._selectedProfiles = new Set(
        this._profileItems
          .filter((item) => item.stale === true && item.active !== true && item.scope !== "factory")
          .map((item) => String(item.profile || "").trim())
          .filter(Boolean)
      );
      this._renderProfiles();
    });

    this.shadowRoot.getElementById("clean-stale-profiles").addEventListener("click", () => {
      this._selectedProfiles = new Set(
        this._profileItems
          .filter((item) => item.stale === true && item.active !== true && item.scope !== "factory")
          .map((item) => String(item.profile || "").trim())
          .filter(Boolean)
      );

      this._renderProfiles();

      if (!this._selectedProfiles.size) {
        const message = this.shadowRoot.getElementById("profiles-message");
        if (message) {
          message.className = "";
          message.textContent = "No stale calibration profiles found.";
        }
        return;
      }

      void this._deleteSelectedProfiles();
    });

    this.shadowRoot.getElementById("clear-profile-selection").addEventListener("click", () => {
      this._selectedProfiles.clear();
      this._renderProfiles();
    });

    this.shadowRoot.getElementById("delete-selected-profiles").addEventListener("click", () => {
      void this._deleteSelectedProfiles();
    });
  }

  _setView(view) {
    const nextView = view === "profiles" ? "profiles" : "dashboard";
    this._activeView = nextView;

    const dashboardView = this.shadowRoot.getElementById("dashboard-view");
    const profilesView = this.shadowRoot.getElementById("profiles-view");
    const dashboardButton = this.shadowRoot.getElementById("view-dashboard");
    const profilesButton = this.shadowRoot.getElementById("view-profiles");

    if (dashboardView) dashboardView.hidden = nextView !== "dashboard";
    if (profilesView) profilesView.hidden = nextView !== "profiles";
    if (dashboardButton) dashboardButton.classList.toggle("active", nextView === "dashboard");
    if (profilesButton) profilesButton.classList.toggle("active", nextView === "profiles");

    if (nextView === "profiles" && !this._profilesLoaded) {
      void this._loadProfiles(false);
    }
  }

  async _loadProfiles(force = false) {
    if (!this._hass || this._profilesLoading) return;

    const refreshButton = this.shadowRoot.getElementById("refresh-profiles");
    const summary = this.shadowRoot.getElementById("profiles-summary");
    const message = this.shadowRoot.getElementById("profiles-message");

    this._profilesLoading = true;

    if (refreshButton) {
      refreshButton.disabled = true;
      refreshButton.textContent = "Refreshing…";
    }

    if (summary) {
      summary.textContent = force
        ? "Refreshing calibration profiles…"
        : "Loading calibration profiles…";
    }

    if (message) {
      message.replaceChildren();
      message.className = "";
    }

    try {
      const result = await this._hass.callWS({
        type: "switch_vision/list_calibrations"
      });

      this._profileItems = Array.isArray(result?.items)
        ? result.items
        : [];

      this._profileResult = result || {};
      this._profilesLoaded = true;

      if (summary) {
        const count = this._profileItems.length;
        summary.textContent =
          `${count} saved calibration profile${count === 1 ? "" : "s"}`;
      }

      this._renderProfiles();
    } catch (error) {
      this._profilesLoaded = false;

      if (summary) {
        summary.textContent = "Calibration profiles unavailable";
      }

      if (message) {
        message.className = "error";
        message.innerHTML =
          `<b>Calibration profiles could not be loaded.</b><br>${this._escape(String(error))}`;
      }
    } finally {
      this._profilesLoading = false;

      if (refreshButton) {
        refreshButton.disabled = false;
        refreshButton.textContent = "Refresh Profiles";
      }
    }
  }

  _updateProfileSelectionSummary() {
    const summary = this.shadowRoot.getElementById("profile-selection-summary");
    if (!summary) return;

    const count = this._selectedProfiles.size;
    summary.textContent = `${count} selected`;

    const deleteButton = this.shadowRoot.getElementById("delete-selected-profiles");
    if (deleteButton) {
      deleteButton.disabled = count === 0;
    }
  }

  _renderProfiles() {
    const root = this.shadowRoot.getElementById("profiles-root");
    const summary = this.shadowRoot.getElementById("profiles-summary");
    if (!root) return;

    const items = Array.isArray(this._profileItems)
      ? this._profileItems
      : [];

    const selectableProfiles = new Set(
      items
        .filter((item) => item.active !== true && item.scope !== "factory")
        .map((item) => String(item.profile || "").trim())
        .filter(Boolean)
    );

    for (const profile of [...this._selectedProfiles]) {
      if (!selectableProfiles.has(profile)) {
        this._selectedProfiles.delete(profile);
      }
    }

    this._updateProfileSelectionSummary();

    if (!items.length) {
      root.innerHTML = `<div class="empty"><b>No saved calibration profiles.</b></div>`;
      if (summary) summary.textContent = "0 saved calibration profiles";
      return;
    }

    const activeCount = items.filter((item) => item.active === true).length;
    const staleCount = items.filter((item) => item.stale === true).length;
    const duplicateCount = items.filter(
      (item) => item.duplicate_faceplate_content === true
    ).length;

    if (summary) {
      const parts = [
        `${items.length} saved`,
        `${activeCount} active`
      ];
      if (staleCount) parts.push(`${staleCount} missing faceplate`);
      if (duplicateCount) parts.push(`${duplicateCount} duplicate-content`);
      summary.textContent = parts.join(" · ");
    }

    root.innerHTML = items.map((item, index) => {
      const badges = [];
      const protectedProfile =
        item.active === true || item.scope === "factory";

      badges.push(
        `<span class="profile-badge">${this._escape(
          String(item.scope || "other").toUpperCase()
        )}</span>`
      );

      if (item.active === true) {
        badges.push(`<span class="profile-badge active">ACTIVE</span>`);
      } else {
        badges.push(`<span class="profile-badge">UNUSED</span>`);
      }

      if (item.stale === true) {
        badges.push(
          `<span class="profile-badge danger">MISSING FACEPLATE</span>`
        );
      }

      if (item.duplicate_faceplate_content === true) {
        badges.push(
          `<span class="profile-badge warning">DUPLICATE FACEPLATE</span>`
        );
      }

      const classes = ["profile-card"];
      if (item.active === true) classes.push("is-active");
      if (item.stale === true) classes.push("is-stale");
      else if (item.duplicate_faceplate_content === true) {
        classes.push("is-duplicate");
      }

      const faceplate = String(item.faceplate || "__default__");
      const model = String(item.model || "Unknown model");
      const baseProfile = String(item.base_profile || "");
      const profile = String(item.profile || "");
      const sha = String(item.faceplate_sha256 || "");
      const duplicates = Array.isArray(item.duplicate_faceplates)
        ? item.duplicate_faceplates
        : [];

      const duplicateText = duplicates.length > 1
        ? `<div><b>Same image content:</b> ${duplicates
            .map((name) => this._escape(name))
            .join(", ")}</div>`
        : "";

      const fingerprintText = sha
        ? `<div><b>SHA-256:</b> <code>${this._escape(sha)}</code></div>`
        : "";

      const copyTargets = items
        .map((candidate, targetIndex) => ({
          candidate,
          targetIndex
        }))
        .filter(({ candidate }) =>
          String(candidate.profile || "").trim() !== profile &&
          candidate.scope !== "factory" &&
          candidate.stale !== true &&
          String(candidate.base_profile || "") === baseProfile
        );

      const copyOptions = copyTargets
        .map(({ candidate, targetIndex }) => {
          const targetFaceplate =
            String(candidate.faceplate || "__default__");
          const active =
            candidate.active === true ? " · ACTIVE" : "";

          return `<option value="${targetIndex}">${
            this._escape(targetFaceplate + active)
          }</option>`;
        })
        .join("");

      return `
        <article class="${classes.join(" ")}">
          <label class="profile-select">
            <input
              type="checkbox"
              data-select-profile="${index}"
              ${protectedProfile ? "disabled" : ""}
              ${this._selectedProfiles.has(profile) ? "checked" : ""}
            >
            ${item.scope === "factory"
              ? "Factory profile protected"
              : (item.active === true ? "Active profile protected" : "Select profile")}
          </label>

          <div class="profile-title">
            <span>${this._escape(baseProfile || profile)}</span>
            <span class="profile-badges">${badges.join("")}</span>
          </div>

          <div class="profile-summary-line">
            ${this._escape(model)}
            · ${Number(item.port_count || 0)} RJ45
            · ${Number(item.sfp_count || 0)} SFP/uplink
            · Faceplate: ${this._escape(faceplate)}
          </div>

          <div class="profile-details">
            <div><b>Internal profile:</b> <code>${this._escape(profile)}</code></div>
            <div><b>Base profile:</b> <code>${this._escape(baseProfile)}</code></div>
            <div><b>Faceplate exists:</b> ${item.faceplate_exists === false ? "No" : "Yes"}</div>
            ${duplicateText}
            ${fingerprintText}
          </div>

          <div class="profile-actions">
            <button
              type="button"
              class="secondary"
              data-export-profile="${index}"
            >Export Profile</button>

            ${item.scope !== "factory" && item.stale !== true ? `
              <button
                type="button"
                class="secondary"
                data-import-profile="${index}"
              >Import Into Profile</button>
              <input
                type="file"
                accept="application/json,.json"
                data-import-file="${index}"
                hidden
              >
            ` : ""}

            ${copyTargets.length ? `
              <select data-copy-target="${index}">
                <option value="">Copy to…</option>
                ${copyOptions}
              </select>
              <button
                type="button"
                class="secondary"
                data-copy-profile="${index}"
              >Copy Profile</button>
            ` : ""}

            <button
              type="button"
              class="danger"
              data-delete-profile="${index}"
              ${protectedProfile ? "disabled" : ""}
              title="${item.scope === "factory"
                ? "Factory profiles are protected from deletion"
                : (item.active === true
                  ? "Active profiles are protected from deletion"
                  : "Delete this saved calibration profile")}"
            >${item.scope === "factory"
              ? "Factory — Protected"
              : (item.active === true ? "Active — Protected" : "Delete Profile")}</button>
          </div>
        </article>`;
    }).join("");

    root.querySelectorAll("[data-import-profile]").forEach((button) => {
      button.addEventListener("click", () => {
        const index = Number.parseInt(
          button.dataset.importProfile || "",
          10
        );

        if (!Number.isInteger(index)) return;

        const input = root.querySelector(
          `[data-import-file="${index}"]`
        );

        if (input) input.click();
      });
    });

    root.querySelectorAll("[data-import-file]").forEach((input) => {
      input.addEventListener("change", () => {
        const index = Number.parseInt(
          input.dataset.importFile || "",
          10
        );

        const file = input.files?.[0] || null;
        input.value = "";

        if (!Number.isInteger(index) || !file) return;

        void this._importProfile(index, file);
      });
    });

    root.querySelectorAll("[data-export-profile]").forEach((button) => {
      button.addEventListener("click", () => {
        const index = Number.parseInt(
          button.dataset.exportProfile || "",
          10
        );

        if (!Number.isInteger(index)) return;
        void this._exportProfile(index);
      });
    });

    root.querySelectorAll("[data-copy-profile]").forEach((button) => {
      button.addEventListener("click", () => {
        const sourceIndex = Number.parseInt(
          button.dataset.copyProfile || "",
          10
        );

        if (!Number.isInteger(sourceIndex)) return;

        const select = root.querySelector(
          `[data-copy-target="${sourceIndex}"]`
        );

        const targetIndex = Number.parseInt(
          select?.value || "",
          10
        );

        if (!Number.isInteger(targetIndex)) return;

        void this._copyProfile(
          sourceIndex,
          targetIndex
        );
      });
    });

    root.querySelectorAll("[data-select-profile]").forEach((checkbox) => {
      checkbox.addEventListener("change", () => {
        const index = Number.parseInt(
          checkbox.dataset.selectProfile || "",
          10
        );

        if (!Number.isInteger(index)) return;

        const item = this._profileItems[index];
        if (!item || item.active === true || item.scope === "factory") {
          checkbox.checked = false;
          return;
        }

        const profile = String(item.profile || "").trim();
        if (!profile) {
          checkbox.checked = false;
          return;
        }

        if (checkbox.checked) {
          this._selectedProfiles.add(profile);
        } else {
          this._selectedProfiles.delete(profile);
        }

        this._updateProfileSelectionSummary();
      });
    });

    root.querySelectorAll("[data-delete-profile]").forEach((button) => {
      button.addEventListener("click", () => {
        const index = Number.parseInt(
          button.dataset.deleteProfile || "",
          10
        );

        if (!Number.isInteger(index)) return;
        void this._deleteProfile(index);
      });
    });
  }

  async _importProfile(index, file) {
    if (!this._hass || this._profilesLoading || !file) return;

    const target = this._profileItems[index];
    const message =
      this.shadowRoot.getElementById("profiles-message");

    if (
      !target ||
      target.scope === "factory" ||
      target.stale === true
    ) {
      if (message) {
        message.className = "error";
        message.textContent =
          "Import rejected: unsafe destination profile.";
      }
      return;
    }

    const targetProfile =
      String(target.profile || "").trim();

    const targetBase =
      String(target.base_profile || "").trim();

    const targetFaceplate =
      String(target.faceplate || "__default__");

    if (!targetProfile || !targetBase) return;

    const maxBytes = 2 * 1024 * 1024;

    if (file.size > maxBytes) {
      if (message) {
        message.className = "error";
        message.textContent =
          "Import rejected: profile file exceeds 2 MB.";
      }
      return;
    }

    this._profilesLoading = true;

    try {
      const raw = JSON.parse(await file.text());

      if (
        !raw ||
        typeof raw !== "object" ||
        Array.isArray(raw)
      ) {
        throw new Error(
          "Profile file must contain one JSON object."
        );
      }

      const schemaVersion =
        Number(raw.schema_version || 0);

      if (
        schemaVersion &&
        ![1, 2].includes(schemaVersion)
      ) {
        throw new Error(
          `Unsupported schema_version ${schemaVersion}.`
        );
      }

      if (
        raw.transfer_type &&
        raw.transfer_type !==
          "switch-vision-faceplate-profile-v2"
      ) {
        throw new Error(
          "Unsupported Switch Vision transfer type."
        );
      }

      if (
        raw.schema &&
        raw.schema !==
          "switch-vision-interactive-calibration-v1"
      ) {
        throw new Error(
          "Unsupported calibration schema."
        );
      }

      const targetResult =
        await this._hass.callWS({
          type: "switch_vision/get_calibration",
          profile: targetProfile
        });

      if (
        targetResult?.exists !== true ||
        !targetResult?.calibration
      ) {
        throw new Error(
          "Destination calibration no longer exists."
        );
      }

      const targetCalibration =
        targetResult.calibration;

      const sourceModel =
        String(raw.model || "").trim();

      const targetModel =
        String(
          targetCalibration.model ||
          target.model ||
          ""
        ).trim();

      if (
        sourceModel &&
        targetModel &&
        sourceModel !== targetModel
      ) {
        throw new Error(
          `Model mismatch: ${sourceModel} → ${targetModel}`
        );
      }

      const requiredFaceplate =
        String(
          raw.required_faceplate ||
          raw.ui?.faceplate?.file ||
          "__default__"
        ).trim();

      const duplicateFaceplates =
        Array.isArray(target.duplicate_faceplates)
          ? target.duplicate_faceplates
          : [];

      const faceplateMatches =
        requiredFaceplate === targetFaceplate ||
        duplicateFaceplates.includes(requiredFaceplate);

      const sourceProfile =
        String(raw.source_profile || "unknown");

      const faceplateWarning =
        faceplateMatches
          ? ""
          : "\n\nWARNING: The exported profile references a different faceplate filename.";

      const activeWarning =
        target.active === true
          ? "\n\nWARNING: This destination profile is currently ACTIVE."
          : "";

      const confirmed = window.confirm(
        "Import calibration profile?\n\n" +
        "FILE SOURCE:\n" +
        sourceProfile + "\n" +
        "Model: " + (sourceModel || "unspecified") + "\n" +
        "Required faceplate: " + requiredFaceplate + "\n\n" +
        "DESTINATION:\n" +
        targetProfile + "\n" +
        "Faceplate: " + targetFaceplate +
        faceplateWarning +
        activeWarning + "\n\n" +
        "The destination calibration will be overwritten.\n" +
        "Destination identity and faceplate will be preserved."
      );

      if (!confirmed) {
        this._profilesLoading = false;
        return;
      }

      const imported = JSON.parse(
        JSON.stringify(raw)
      );

      delete imported.transfer_type;
      delete imported.source_scope;
      delete imported.source_profile;
      delete imported.source_base_profile;
      delete imported.required_faceplate;
      delete imported.faceplate_included;

      delete imported.profile_name;
      delete imported.profile_scope;
      delete imported.base_profile_name;

      imported.ui = imported.ui || {};

      imported.ui.faceplate = JSON.parse(
        JSON.stringify(
          targetCalibration.ui?.faceplate || {
            show: true,
            source: "custom",
            file: targetFaceplate
          }
        )
      );

      imported.base_profile_name = targetBase;

      if (targetCalibration.profile !== undefined) {
        imported.profile =
          targetCalibration.profile;
      }

      if (targetCalibration.management !== undefined) {
        imported.management = JSON.parse(
          JSON.stringify(
            targetCalibration.management
          )
        );
      }

      if (targetCalibration.stack !== undefined) {
        imported.stack = JSON.parse(
          JSON.stringify(
            targetCalibration.stack
          )
        );
      }

      await this._hass.callService(
        "switch_vision",
        "save_calibration",
        {
          profile: targetProfile,
          calibration: imported,
          mirror_to_base: false
        }
      );

      this._profilesLoading = false;
      this._profilesLoaded = false;

      await this._loadProfiles(true);

      if (message) {
        message.className = "";
        message.textContent =
          `Imported profile into ${targetProfile}`;
      }
    } catch (error) {
      this._profilesLoading = false;

      if (message) {
        message.className = "error";
        message.innerHTML =
          `<b>Import Profile failed.</b><br>${
            this._escape(String(error))
          }`;
      }
    }
  }

  async _exportProfile(index) {
    if (!this._hass || this._profilesLoading) return;

    const item = this._profileItems[index];
    if (!item) return;

    const profile =
      String(item.profile || "").trim();

    const baseProfile =
      String(item.base_profile || "").trim();

    const faceplate =
      String(item.faceplate || "__default__");

    const scope =
      String(item.scope || "");

    const message =
      this.shadowRoot.getElementById("profiles-message");

    if (!profile) return;

    try {
      const result = await this._hass.callWS({
        type: "switch_vision/get_calibration",
        profile
      });

      if (
        result?.exists !== true ||
        !result?.calibration
      ) {
        throw new Error(
          "Calibration profile no longer exists."
        );
      }

      const payload = JSON.parse(
        JSON.stringify(result.calibration)
      );

      payload.schema_version = 2;
      payload.transfer_type =
        "switch-vision-faceplate-profile-v2";
      payload.generated_by =
        `Switch Vision v${PANEL_VERSION}`;

      payload.source_scope = scope;
      payload.source_profile = profile;
      payload.source_base_profile = baseProfile;
      payload.required_faceplate = faceplate;
      payload.faceplate_included = false;

      delete payload.profile_name;
      delete payload.profile_scope;
      delete payload.base_profile_name;

      const safeName = profile
        .replace(/[^A-Za-z0-9_.-]+/g, "-")
        .replace(/^-+|-+$/g, "")
        .slice(0, 120) || "profile";

      const blob = new Blob(
        [JSON.stringify(payload, null, 2) + "\n"],
        { type: "application/json" }
      );

      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");

      link.href = url;
      link.download =
        `switch-vision-profile-${safeName}.json`;

      document.body.appendChild(link);
      link.click();
      link.remove();

      URL.revokeObjectURL(url);

      if (message) {
        message.className = "";
        message.textContent =
          `Exported calibration profile: ${profile}`;
      }
    } catch (error) {
      if (message) {
        message.className = "error";
        message.innerHTML =
          `<b>Export Profile failed.</b><br>${
            this._escape(String(error))
          }`;
      }
    }
  }

  async _copyProfile(sourceIndex, targetIndex) {
    if (!this._hass || this._profilesLoading) return;

    const source = this._profileItems[sourceIndex];
    const target = this._profileItems[targetIndex];

    if (!source || !target || sourceIndex === targetIndex) return;

    const sourceProfile =
      String(source.profile || "").trim();

    const targetProfile =
      String(target.profile || "").trim();

    const sourceBase =
      String(source.base_profile || "").trim();

    const targetBase =
      String(target.base_profile || "").trim();

    const message =
      this.shadowRoot.getElementById("profiles-message");

    if (
      !sourceProfile ||
      !targetProfile ||
      sourceBase !== targetBase ||
      target.scope === "factory" ||
      target.stale === true
    ) {
      if (message) {
        message.className = "error";
        message.textContent =
          "Copy Profile rejected: invalid source or destination.";
      }
      return;
    }

    const sourceFaceplate =
      String(source.faceplate || "__default__");

    const targetFaceplate =
      String(target.faceplate || "__default__");

    const activeWarning =
      target.active === true
        ? "\n\nWARNING: The destination profile is currently ACTIVE."
        : "";

    const confirmed = window.confirm(
      "Copy calibration profile?\n\n" +
      "SOURCE:\n" +
      sourceProfile + "\n" +
      "Faceplate: " + sourceFaceplate + "\n\n" +
      "DESTINATION:\n" +
      targetProfile + "\n" +
      "Faceplate: " + targetFaceplate +
      activeWarning + "\n\n" +
      "The destination calibration will be overwritten.\n" +
      "Its faceplate identity will be preserved."
    );

    if (!confirmed) return;

    this._profilesLoading = true;

    try {
      const [sourceResult, targetResult] =
        await Promise.all([
          this._hass.callWS({
            type: "switch_vision/get_calibration",
            profile: sourceProfile
          }),
          this._hass.callWS({
            type: "switch_vision/get_calibration",
            profile: targetProfile
          })
        ]);

      if (
        sourceResult?.exists !== true ||
        !sourceResult?.calibration ||
        targetResult?.exists !== true ||
        !targetResult?.calibration
      ) {
        throw new Error(
          "Source or destination calibration no longer exists."
        );
      }

      const copied = JSON.parse(
        JSON.stringify(sourceResult.calibration)
      );

      const targetCalibration =
        targetResult.calibration;

      copied.ui = copied.ui || {};

      copied.ui.faceplate = JSON.parse(
        JSON.stringify(
          targetCalibration?.ui?.faceplate || {
            show: true,
            source: "custom",
            file: targetFaceplate
          }
        )
      );

      copied.base_profile_name = targetBase;

      await this._hass.callService(
        "switch_vision",
        "save_calibration",
        {
          profile: targetProfile,
          calibration: copied,
          mirror_to_base: false
        }
      );

      this._profilesLoading = false;
      this._profilesLoaded = false;

      await this._loadProfiles(true);

      if (message) {
        message.className = "";
        message.textContent =
          `Copied ${sourceProfile} → ${targetProfile}`;
      }
    } catch (error) {
      this._profilesLoading = false;

      if (message) {
        message.className = "error";
        message.innerHTML =
          `<b>Copy Profile failed.</b><br>${
            this._escape(String(error))
          }`;
      }
    }
  }

  async _deleteSelectedProfiles() {
    if (!this._hass || this._profilesLoading || !this._selectedProfiles.size) {
      return;
    }

    const message = this.shadowRoot.getElementById("profiles-message");

    const selectedItems = this._profileItems.filter((item) => {
      const profile = String(item.profile || "").trim();
      return profile && this._selectedProfiles.has(profile);
    });

    if (!selectedItems.length) {
      this._selectedProfiles.clear();
      this._updateProfileSelectionSummary();
      return;
    }

    const protectedItems = selectedItems.filter(
      (item) => item.active === true || item.scope === "factory"
    );

    if (protectedItems.length) {
      if (message) {
        message.className = "error";
        message.innerHTML =
          "<b>Bulk deletion stopped.</b><br>" +
          "One or more selected profiles are active or factory profiles and are protected.";
      }

      this._renderProfiles();
      return;
    }

    const profiles = selectedItems
      .map((item) => String(item.profile || "").trim())
      .filter(Boolean);

    const list = profiles
      .map((profile) => `• ${profile}`)
      .join("\n");

    const confirmed = window.confirm(
      `Delete ${profiles.length} calibration profile${profiles.length === 1 ? "" : "s"}?\n\n` +
      `Profiles:\n${list}\n\n` +
      "This cannot be undone."
    );

    if (!confirmed) return;

    this._profilesLoading = true;

    try {
      for (const profile of profiles) {
        await this._hass.callService(
          "switch_vision",
          "delete_calibration",
          { profile }
        );
      }

      this._selectedProfiles.clear();
      this._profilesLoaded = false;

      if (message) {
        message.className = "";
        message.textContent =
          `Deleted ${profiles.length} calibration profile${profiles.length === 1 ? "" : "s"}.`;
      }

      this._profilesLoading = false;
      await this._loadProfiles(true);
    } catch (error) {
      this._profilesLoading = false;

      if (message) {
        message.className = "error";
        message.innerHTML =
          `<b>Bulk calibration profile deletion failed.</b><br>${this._escape(String(error))}`;
      }

      await this._loadProfiles(true);
    }
  }

  async _deleteProfile(index) {
    const item = this._profileItems[index];
    if (!item || this._profilesLoading) return;

    const message = this.shadowRoot.getElementById("profiles-message");
    const profile = String(item.profile || "").trim();
    const faceplate = String(item.faceplate || "__default__").trim();

    if (!profile) return;

    // UI buttons are disabled for active profiles, but keep a second
    // programmatic guard here as well.
    if (item.active === true || item.scope === "factory") {
      if (message) {
        message.className = "error";
        message.innerHTML = item.scope === "factory"
          ? "<b>Factory profiles are protected from deletion.</b>"
          : "<b>Active profiles are protected from deletion.</b>";
      }
      return;
    }

    const confirmed = window.confirm(
      "Delete this calibration profile?\n\n" +
      "Internal profile:\n" + profile + "\n\n" +
      "Faceplate:\n" + faceplate + "\n\n" +
      "This removes the saved calibration profile and cannot be undone."
    );

    if (!confirmed) return;

    try {
      await this._hass.callService(
        "switch_vision",
        "delete_calibration",
        { profile }
      );

      if (message) {
        message.className = "";
        message.textContent = `Deleted calibration profile: ${profile}`;
      }

      this._profilesLoaded = false;
      await this._loadProfiles(true);
    } catch (error) {
      if (message) {
        message.className = "error";
        message.innerHTML =
          `<b>Calibration profile deletion failed.</b><br>${this._escape(String(error))}`;
      }
    }
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

// Switch Vision sidebar icon set. Generated from brand/sidebar.svg.
window.customIconsets = window.customIconsets || {};
window.customIconsets["switch-vision"] = async (iconName) => {
  if (iconName !== "logo") return { path: "", viewBox: "0 0 906 906" };
  return { path: "M 862 526 L 683 305 L 436 302 L 415 349 L 573 534 L 544 593 L 448 658 L 141 661 L 9 828 L 55 862 L 592 864 L 854 579 Z M 887 38 L 812 7 L 340 6 L 50 290 L 38 363 L 230 581 L 480 584 L 489 531 L 339 373 L 335 319 L 437 224 L 775 214 L 887 88 Z", viewBox: "0 0 906 906" };
};

// Calibration SFP port-manager extension.
//
// The renderer intentionally remains the canonical src/js/switch-vision.js
// build artifact. This globally loaded bootstrap augments the card prototype
// after registration so Core's canonical/runtime JS parity is preserved.
(() => {
  const PATCH_FLAG = Symbol.for("switchVision.calibrationSfpPortManager.v1");
  const ROOT_FLAG = Symbol.for("switchVision.calibrationSfpPortManager.root.v1");
  const CAL_REF = Symbol.for("switchVision.calibrationSfpPortManager.calibration.v1");

  const escapeHtml = (value) => String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");

  const logicalSfpNumber = (key) => {
    const nums = String(key ?? "").match(/\d+/g) || [];
    const number = Number(nums.at(-1) || 0);
    return Number.isInteger(number) && number > 0 ? number : 0;
  };

  const sfpKeys = (cal) => Object.keys(cal?.sfp && typeof cal.sfp === "object" ? cal.sfp : {});

  const sfpKeyForNumber = (cal, number) => {
    const wanted = Number(number);
    if (!(wanted > 0)) return null;
    return sfpKeys(cal).find((key) => logicalSfpNumber(key) === wanted) || null;
  };

  const selectedSfpKey = (card, cal) => {
    const rawTarget = String(card?.config?.calibration_target || "").trim();
    const targetMatch = rawTarget.match(/^sfp:(\d+)$/i);
    if (targetMatch) return sfpKeyForNumber(cal, Number(targetMatch[1]));
    const selected = card?.config?.selected_interface;
    if (String(selected?.type || "").toLowerCase() === "sfp") {
      return sfpKeyForNumber(cal, Number(selected.id));
    }
    return null;
  };

  const nextSfpNumber = (cal) => {
    const numbers = sfpKeys(cal).map(logicalSfpNumber).filter((number) => number > 0);
    return numbers.length ? Math.max(...numbers) + 1 : 1;
  };

  const sfpCollision = (cal, ignoreKey = null) => {
    const seen = new Map();
    for (const key of sfpKeys(cal)) {
      if (ignoreKey !== null && key === ignoreKey) continue;
      const number = logicalSfpNumber(key);
      if (!(number > 0)) continue;
      if (seen.has(number)) return { number, first: seen.get(number), second: key };
      seen.set(number, key);
    }
    return null;
  };

  const collisionForNumber = (cal, number, ignoreKey = null) => sfpKeys(cal).find((key) => (
    key !== ignoreKey && logicalSfpNumber(key) === Number(number)
  )) || null;

  const cloneSfp = (cal, sourceKey, newKey, offsetX = 12, offsetY = 0) => {
    cal.sfp = cal.sfp && typeof cal.sfp === "object" ? cal.sfp : {};
    const source = cal.sfp?.[String(sourceKey)] || Object.values(cal.sfp)[0] || {
      center: [1710, 246],
      hitbox: [94, 48]
    };
    const copy = JSON.parse(JSON.stringify(source));
    for (const part of ["center", "number", "led_left", "led_right"]) {
      if (!Array.isArray(copy[part])) continue;
      copy[part][0] = Math.round((Number(copy[part][0]) + offsetX) * 10) / 10;
      copy[part][1] = Math.round((Number(copy[part][1]) + offsetY) * 10) / 10;
    }
    delete copy.display_name;
    cal.sfp[String(newKey)] = copy;
  };

  const setStatus = (card, message, error = false) => {
    if (typeof card?.setCalibrationSaveStatus === "function") {
      card.setCalibrationSaveStatus(String(message), error === true);
    }
  };

  const finishEdit = (card, message, error = false) => {
    setStatus(card, message, error);
    if (!error && typeof card?.markCalibrationDirty === "function") card.markCalibrationDirty();
    if (typeof card?.render === "function") card.render();
    if (typeof card?.clearCalibrationSaveStatusSoon === "function") card.clearCalibrationSaveStatusSoon();
  };

  const normalizeSfpKey = (value) => String(value ?? "").trim().toUpperCase();

  const validateSfpKey = (key) => {
    if (!key) return "SFP key cannot be blank";
    if (key.length > 32) return "SFP key must be 32 characters or fewer";
    if (!/^[A-Z0-9][A-Z0-9._\/-]*$/.test(key)) {
      return "SFP key may contain letters, numbers, dot, underscore, slash and hyphen";
    }
    if (!(logicalSfpNumber(key) > 0)) return "SFP key must contain a positive uplink number";
    return "";
  };

  const collisionMessage = (collision) => (
    `SFP key collision: ${collision.first} and ${collision.second} both resolve to uplink ${collision.number}`
  );

  const handleSfpAction = (card, event) => {
    const actionButton = event.target?.closest?.("[data-cv-action]");
    if (!actionButton || !card.shadowRoot?.contains(actionButton)) return;
    const action = String(actionButton.dataset.cvAction || "");
    const cal = card[CAL_REF] || (typeof card.calibrationData === "function" ? card.calibrationData() : null);
    if (!cal || typeof cal !== "object") return;

    const selectedKey = selectedSfpKey(card, cal);
    const duplicateSfp = action === "duplicate-port" && Boolean(selectedKey);
    if (!["add-sfp-port", "rename-sfp-port"].includes(action) && !duplicateSfp) return;

    event.preventDefault();
    event.stopPropagation();
    event.stopImmediatePropagation();

    if (action === "add-sfp-port" || duplicateSfp) {
      const number = nextSfpNumber(cal);
      const newKey = `SFP${number}`;
      const sourceKey = selectedKey || sfpKeys(cal).at(-1) || null;
      cloneSfp(cal, sourceKey, newKey, action === "add-sfp-port" ? 12 : 0, 0);
      card.config = {
        ...card.config,
        calibration_target: `sfp:${number}`,
        calibration_part: "center",
        selected_interface: { type: "sfp", id: number },
        selected_port: null
      };
      finishEdit(card, `${action === "add-sfp-port" ? "Added" : "Duplicated"} SFP uplink ${newKey}`);
      return;
    }

    if (action === "rename-sfp-port") {
      if (!selectedKey) {
        finishEdit(card, "Select one SFP/uplink before renaming its key", true);
        return;
      }
      const input = card.shadowRoot?.querySelector('[data-cv-field="sfp-key"]');
      const nextKey = normalizeSfpKey(input?.value);
      const validationError = validateSfpKey(nextKey);
      if (validationError) {
        finishEdit(card, validationError, true);
        return;
      }
      if (nextKey === selectedKey) {
        finishEdit(card, `SFP key is already ${selectedKey}`, false);
        return;
      }
      if (Object.prototype.hasOwnProperty.call(cal.sfp || {}, nextKey)) {
        finishEdit(card, `SFP key ${nextKey} already exists`, true);
        return;
      }
      const number = logicalSfpNumber(nextKey);
      const conflictingKey = collisionForNumber(cal, number, selectedKey);
      if (conflictingKey) {
        finishEdit(card, collisionMessage({ number, first: conflictingKey, second: nextKey }), true);
        return;
      }

      const renamed = {};
      for (const [key, value] of Object.entries(cal.sfp || {})) {
        renamed[key === selectedKey ? nextKey : key] = value;
      }
      cal.sfp = renamed;
      card.config = {
        ...card.config,
        calibration_target: `sfp:${number}`,
        selected_interface: { type: "sfp", id: number },
        selected_port: null
      };
      finishEdit(card, `Renamed SFP key ${selectedKey} → ${nextKey}`);
    }
  };

  const install = (CardClass) => {
    const proto = CardClass?.prototype;
    if (!proto || proto[PATCH_FLAG]) return;
    Object.defineProperty(proto, PATCH_FLAG, { value: true, configurable: false });

    if (typeof proto.calibrationControls === "function") {
      const originalCalibrationControls = proto.calibrationControls;
      proto.calibrationControls = function patchedCalibrationControls(cal) {
        let html = originalCalibrationControls.call(this, cal);
        const portCount = Object.keys(cal?.ports || {}).length;
        const uplinkCount = sfpKeys(cal).length;
        const selectedKey = selectedSfpKey(this, cal);
        const addRj45 = '<button type="button" data-cv-action="add-port">Add port</button>';
        const addButtons = '<button type="button" data-cv-action="add-port">Add RJ45</button>\n        <button type="button" data-cv-action="add-sfp-port">Add SFP</button>';
        html = html.replace(addRj45, addButtons);
        html = html.replace(
          '<button type="button" data-cv-action="duplicate-port">Duplicate port</button>',
          '<button type="button" data-cv-action="duplicate-port">Duplicate selected</button>'
        );
        html = html.replace(
          `<span class="cv-cal-current">${portCount} visual ports</span>`,
          `<span class="cv-cal-current">${portCount} RJ45 · ${uplinkCount} SFP</span>`
        );

        // Use the literal rendered RJ45 control as the insertion anchor so the
        // extension remains independent from the renderer's lexical helpers.
        html = html.replace(
          /(<button type="button" data-cv-action="rename-port"[^>]*>Renumber<\/button>)\s*<span class="cv-cal-row-divider" aria-hidden="true"><\/span>\s*<label>Display name/,
          `$1\n        <span class="cv-cal-row-divider" aria-hidden="true"></span>\n        <label>SFP key<input class="cv-cal-input" data-cv-field="sfp-key" type="text" maxlength="32" value="${escapeHtml(selectedKey || "")}" placeholder="SFP5 or G3/TE3" ${selectedKey ? "" : "disabled"}></label>\n        <button type="button" data-cv-action="rename-sfp-port" ${selectedKey ? "" : "disabled"}>Rename SFP</button>\n        <span class="cv-cal-row-divider" aria-hidden="true"></span>\n        <label>Display name`
        );
        return html;
      };
    }

    if (typeof proto.attachCalibrationControlHandlers === "function") {
      const originalAttachHandlers = proto.attachCalibrationControlHandlers;
      proto.attachCalibrationControlHandlers = function patchedAttachCalibrationControlHandlers(cal) {
        this[CAL_REF] = cal;
        const result = originalAttachHandlers.call(this, cal);
        const root = this.shadowRoot;
        if (root && !root[ROOT_FLAG]) {
          Object.defineProperty(root, ROOT_FLAG, { value: true, configurable: false });
          root.addEventListener("click", (event) => handleSfpAction(this, event), true);
        }
        return result;
      };
    }

    if (typeof proto.saveCalibrationProfile === "function") {
      const originalSaveCalibrationProfile = proto.saveCalibrationProfile;
      proto.saveCalibrationProfile = async function patchedSaveCalibrationProfile(cal, ...args) {
        const collision = sfpCollision(cal);
        if (collision) {
          const message = collisionMessage(collision);
          setStatus(this, message, true);
          throw new Error(message);
        }
        return originalSaveCalibrationProfile.call(this, cal, ...args);
      };
    }
  };

  const installForElement = (element) => {
    const tag = String(element?.tagName || "").toLowerCase();
    if (!tag.startsWith("switch-vision-3650")) return;
    install(element.constructor);
  };

  // The stable public card is always registered by the renderer. Patching its
  // prototype also covers a fresh native versioned subclass via inheritance.
  customElements.whenDefined("switch-vision-3650").then(() => {
    install(customElements.get("switch-vision-3650"));
    for (const element of document.querySelectorAll("switch-vision-3650")) installForElement(element);
  }).catch(() => {});

  // Home Assistant can keep an older stable custom element alive across an
  // in-browser integration update. Watch for versioned native card instances
  // so the current renderer subclass is patched even in that stale-tag case.
  const observer = new MutationObserver((records) => {
    for (const record of records) {
      for (const added of record.addedNodes) {
        if (!(added instanceof Element)) continue;
        const stack = [added];
        while (stack.length) {
          const node = stack.pop();
          installForElement(node);
          for (const child of node.children || []) stack.push(child);
        }
      }
    }
  });
  const startObserver = () => {
    if (document.documentElement) observer.observe(document.documentElement, { childList: true, subtree: true });
  };
  if (document.documentElement) startObserver();
  else window.addEventListener("DOMContentLoaded", startObserver, { once: true });
})();

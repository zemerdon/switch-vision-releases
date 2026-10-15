"""Read-only, provenance-checked stock artwork version binding.

Core saves the current stock SHA with each future user Calibration save.
Installer preserves prior *verified* stock PNG bytes outside the replaceable
faceplates directory. Legacy profiles may use its first retained original.
No profile is reset automatically, and no renderer/geometry is rewritten.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
import re
from typing import Any

_SHA = re.compile(r"^[0-9a-f]{64}$")
_FILE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,140}\.png$")
_MAX_BYTES = 32 * 1024 * 1024
STOCK_SHA_FIELD = "stock_faceplate_sha256"


def stock_filename(calibration: dict[str, Any]) -> str:
    ui = calibration.get("ui")
    ui = ui if isinstance(ui, dict) else {}
    faceplate = ui.get("faceplate")
    faceplate = faceplate if isinstance(faceplate, dict) else {}
    selected = str(faceplate.get("file") or "default").strip()
    source = str(faceplate.get("source") or "default").strip().lower()
    if source not in ("", "default", "custom"):
        return ""
    img = calibration.get("image")
    img = img if isinstance(img, dict) else {}
    filename = str(img.get("file") or "")
    if filename.startswith("faceplates/"):
        filename = filename[len("faceplates/"):]
    if not _FILE.fullmatch(filename):
        return ""
    if selected in ("", "default", "__default__"):
        return filename
    # The existing 3850/other factory profiles may select their bundled
    # filename as a 'custom' visual even though the pixels remain stock.
    return filename if selected == filename else ""


def digest_at(path: Path) -> str:
    if not path.is_file() or path.is_symlink():
        return ""
    try:
        if path.stat().st_size > _MAX_BYTES:
            return ""
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return ""


def current_stock_sha(root: Path, calibration: dict[str, Any],
                      stock_assets: dict[str, Any]) -> str:
    name = stock_filename(calibration)
    expected = stock_assets.get("faceplates", {}).get(name) if name else ""
    if not isinstance(expected, str) or not _SHA.fullmatch(expected):
        return ""
    actual = digest_at(root / "faceplates" / name)
    return actual if actual == expected else ""


def saved_artwork(root: Path, calibration: dict[str, Any],
                  current_sha: str) -> tuple[str, str]:
    """Return saved SHA and verified historical preview path, if possible.

    The filename is *never* versioned. The previous bytes live in an
    independent managed history area, not the stock catalogue.
    """
    name = stock_filename(calibration)
    if not name or not _SHA.fullmatch(current_sha):
        return "", ""
    saved = calibration.get(STOCK_SHA_FIELD)
    if saved is not None:
        if not isinstance(saved, str) or not _SHA.fullmatch(saved):
            return "", ""
        if saved == current_sha:
            return saved, ""
        relative = f"faceplate-history/{saved}/{name}"
    else:
        # Legacy profiles predate Core's server-owned save-time hash. The
        # installer records the earliest verified installed stock art when
        # it first replaces a PNG; never guess old bytes from a filename.
        relative = f"faceplate-history/legacy/{name}"
    history_root = root / "faceplate-history"
    if history_root.is_symlink() or (root / "faceplate-history" / relative.split("/")[1]).is_symlink():
        return "", ""
    historical = digest_at(root / relative)
    if not historical or historical == current_sha:
        return "", ""
    if saved is not None and historical != saved:
        return "", ""
    if saved is None and digest_at(history_root / historical / name) != historical:
        # The legacy alias is trustworthy only with its content-addressed
        # companion, both retained from an installer-verified old stock PNG.
        return "", ""
    return historical, relative

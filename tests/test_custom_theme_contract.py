from __future__ import annotations

import ast
from pathlib import Path
from types import SimpleNamespace
from typing import Any


class _Invalid(Exception):
    pass


vol = SimpleNamespace(Invalid=_Invalid)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "src/custom_components/switch_vision/__init__.py").read_text(encoding="utf-8")

tree = ast.parse(SOURCE)


def literal_assignment(name: str):
    node = next(
        item for item in tree.body
        if isinstance(item, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == name for target in item.targets)
    )
    return ast.literal_eval(node.value)


color_keys = literal_assignment("MANAGEMENT_THEME_COLOR_KEYS")
assert len(color_keys) >= 40
for key in (
    "page", "card", "surface_input", "text", "muted", "field_label",
    "accent", "heading", "warn", "ok", "bad", "link",
    "button_primary_bg", "button_secondary_bg", "button_danger_bg",
):
    assert key in color_keys, key

helpers = [
    node for node in tree.body
    if isinstance(node, ast.FunctionDef)
    and node.name in {"_normalise_custom_themes", "_normalise_management_theme_selected"}
]
namespace: dict[str, Any] = {
    "Any": Any,
    "vol": vol,
    "MAX_CUSTOM_THEMES": 20,
    "MAX_CUSTOM_THEME_NAME_LENGTH": 64,
    "MAX_CUSTOM_THEME_ID_LENGTH": 64,
    "MANAGEMENT_THEME_COLOR_KEYS": color_keys,
    "MANAGEMENT_BUILTIN_THEME_IDS": ("switch-vision", "cisco-classic", "cisco-nexus", "unifi"),
}
exec(compile(ast.Module(body=helpers, type_ignores=[]), "<custom-theme>", "exec"), namespace)

normalise_themes = namespace["_normalise_custom_themes"]
normalise_selected = namespace["_normalise_management_theme_selected"]
colors = {key: "#123456" for key in color_keys}
theme = {"id": "lab_theme", "name": "Lab Theme", "colors": colors}
assert normalise_themes([theme]) == [theme]
assert normalise_selected("switch-vision", [theme]) == "switch-vision"
assert normalise_selected("custom:lab_theme", [theme]) == "custom:lab_theme"

for invalid in (
    [{"id": "", "name": "Bad", "colors": colors}],
    [{"id": "bad/id", "name": "Bad", "colors": colors}],
    [{"id": "one", "name": "", "colors": colors}],
    [{"id": "one", "name": "Bad", "colors": {**colors, "page": "red"}}],
    [{"id": "one", "name": "Bad", "colors": {key: "#123456" for key in color_keys if key != "page"}}],
):
    try:
        normalise_themes(invalid)
    except vol.Invalid:
        pass
    else:
        raise AssertionError(f"invalid theme accepted: {invalid!r}")

for marker in (
    '"management_theme": (',
    'CONF_MANAGEMENT_THEME_SELECTED',
    'CONF_CUSTOM_THEMES',
    '"schema_version": 2',
    '"management_theme": {',
    '"selected": selected_theme',
    '"custom_themes": custom_themes',
):
    assert marker in SOURCE, marker

print("Core custom management theme contract: PASS")

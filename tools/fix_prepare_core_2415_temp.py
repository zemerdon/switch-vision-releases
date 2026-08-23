from pathlib import Path

path = Path("tools/prepare_core_2415_temp.py")
text = path.read_text(encoding="utf-8")
old = "    rows = makeRows(values, fields, STATUS_PANEL_ROW_DEFS.sfp.labels);\\n  }''',"
new = "    rows = makeRows(values, fields, STATUS_PANEL_ROW_DEFS.sfp.labels);\\n''',"
count = text.count(old)
if count != 1:
    raise SystemExit(f"expected one SFP replacement-tail target, found {count}")
path.write_text(text.replace(old, new, 1), encoding="utf-8", newline="\n")
# This committed touch occurs after the corrected temporary workflow reached main,
# ensuring the next pull_request synchronize run executes the fixer first.
print("Core 2.4.15 preparer syntax-tail fix applied")

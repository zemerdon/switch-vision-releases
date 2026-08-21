#!/usr/bin/env python3
"""Temporary review-only guard patch; delete before final review."""
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "build.py"
text = path.read_text(encoding="utf-8")
old = '''        if model not in compact_8x2_visual_models:\n            if item.get("profile") == "cisco_3560cg_8pc":\n'''
new = '''        if item is not None and model not in compact_8x2_visual_models:\n            if item.get("profile") == "cisco_3560cg_8pc":\n'''
if new not in text:
    if text.count(old) != 1:
        raise SystemExit(f"build.py: compact-profile guard target count={text.count(old)}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8", newline="\n")
print("SV-2026-000002 validator null guard applied")

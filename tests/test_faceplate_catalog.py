#!/usr/bin/env python3
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
data=json.loads((root/"src/faceplates/catalog.json").read_text(encoding="utf-8"))
assert data["schema"]=="switch-vision-faceplate-catalog-v1"
labels={row["filename"]:row["display_name"] for row in data["faceplates"]}
shipped={p.name for p in (root/"src/faceplates").glob("*.png")}
assert set(labels)==shipped and len(labels)==len(data["faceplates"])
assert labels["unifi-24-rj45-2sfp-inline.png"]=="UniFi 24-Port · 2 × SFP · Inline"
assert labels["unifi-4-rj45-12sfp.png"]=="UniFi 4-Port · 12 × SFP"
for rel in ("src/js/switch-vision.js","src/custom_components/switch_vision/switch-vision-card.js"):
    text=(root/rel).read_text(encoding="utf-8")
    assert "const shippedLabels =" not in text
    assert 'kind === "faceplates" && SV_SHIPPED_FACEPLATE_LABELS[file]' in text
print(f"Faceplate catalog contract: PASS ({len(labels)} faceplates)")

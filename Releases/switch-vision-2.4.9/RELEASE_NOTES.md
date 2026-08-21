# Switch Vision Core v2.4.9

Core 2.4.9 adds truthful exact-model UniFi API-port mapping from Support My Switch contribution `SV-2026-000002` by **bignick8t3**.

`US 48` is added with its verified 48 RJ45 + four optical layout. `US XG 16` is recognised with its real optical-first API order (SFP+ 1–12, RJ45 13–16), and `USW Pro Aggregation` is recognised as 32 optical ports (28 × 10G SFP+ plus 4 × 25G SFP28). XG16 and Pro Aggregation remain dashboard-disabled until verified faceplates exist rather than falling back to inaccurate generic geometry.

The release also preserves maximum capability separately from negotiated speed, adds Nick's independent evidence to existing UniFi models without over-promoting them, and restores the newer validated Zyxel XS1930-10 contributor evidence into the authoritative Core registry before Discovery synchronization. Existing UniFi models without explicit API maps keep their previous sequential mapping behaviour.

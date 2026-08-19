# Switch Vision Core v2.3.7 — Accurate multi-gigabit speed labels

Switch Vision Core v2.3.7 corrects generic human-readable link-speed formatting for multi-gigabit Ethernet ports.

A genuine 2.5 Gbit/s link could previously be displayed as `3G` because the presentation layer rounded Gbit/s values to the nearest whole number. Real-hardware reports from multiple contributors confirmed that the underlying SNMP speed data was correct and that the fault was in Switch Vision Core's display formatting.

The formatter now preserves meaningful Ethernet rates:

- 10 Mbps → `10M`
- 100 Mbps → `100M`
- 1,000 Mbps → `1G`
- 2,500 Mbps → `2.5G`
- 5,000 Mbps → `5G`
- 10,000 Mbps → `10G`
- 25,000 Mbps → `25G`
- 40,000 Mbps → `40G`
- 100,000 Mbps → `100G`

This is a generic Core correction and is not tied to a particular switch vendor.

The change affects human-readable speed labels only. Numeric link-speed values used for activity and utilisation calculations remain numeric and are not derived from the formatted display string.

This release does not change physical-port mappings, Discovery classification, faceplate selection, or calibration data.

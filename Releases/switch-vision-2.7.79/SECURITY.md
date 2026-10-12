# Security policy

Switch Vision uses read-only SNMP v2c and stores generated network-management evidence locally in Home Assistant. Discovery configuration exports and Support My Switch bundles can contain sensitive infrastructure information.

## Reporting a security issue

Do not post credentials, private network data, unredacted support bundles, or exploit details publicly.

Report security concerns privately to:

```text
switch-vision@zemerdon.com
```

Include the affected version, component, impact, reproduction steps, and the minimum evidence needed to investigate. Remove SNMP communities, passwords, tokens, public IP addresses, MAC addresses, hostnames, VLAN names, and interface descriptions unless they are essential to the report.

## Safe operation

- Use a dedicated read-only SNMP community.
- Restrict UDP/161 access to trusted management hosts.
- Store Discovery configuration exports securely.
- Review Support My Switch archives before sharing.
- Do not send a contribution marked **REVIEW REQUIRED** without inspecting the privacy report.
- Keep Home Assistant, Switch Vision, Discovery, and SNMP2MQTT updated together when release notes require it.

# Switch Vision Core v2.4.14

Core 2.4.14 adds Experimental exact-model UniFi API contracts for UDM Pro Max and USW Pro XG 24 PoE using privacy-processed community real-hardware validation.

UDM Pro Max is represented as eight 1G RJ45 ports, one 2.5G-capable RJ45 port, and two 10G SFP+ ports with no PoE output capability. USW Pro XG 24 PoE is represented as eight 2.5G-capable RJ45 ports, sixteen 10G-capable RJ45 ports, and two 25G SFP28 ports, with 802.3bt Type 4 PoE capability on all 24 copper ports.

Maximum connector capability remains separate from negotiated link speed. The validated hardware includes 10G-capable copper negotiating at lower rates and 25G SFP28 links negotiating at both 10G and 25G. UniFi port detail is retained while unavailable per-port traffic is not synthesized.

Both exact models remain Experimental until rendered physical alignment, port selection, PoE presentation, and optical-position behaviour are validated on contributor hardware. Public release metadata remains anonymous and contains no private submission identifiers, package names, filenames, or contributor identities.

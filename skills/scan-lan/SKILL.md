---
name: scan-lan
description: ARP-scan the LAN, save the results, and compare them with the network definition to find new, missing or changed devices.
---

# Scan the LAN

## Scripts

`np.py` is at `${CLAUDE_PLUGIN_ROOT}/scripts/np.py`. If that variable is unset because the skill was loaded from a catalogue, use a local clone of `https://github.com/danielrosehill/Network-Playbook`, and `scripts/np.py` there.

## Steps

1. Run `np.py scan`, adding `--iface` or `--cidr` if needed. It uses `arp-scan` with non-interactive sudo, then falls back to the neighbour table, and adds mDNS and reverse DNS. If it reports method `ip-neigh`, tell the user that coverage is partial, and offer `sudo arp-scan` for them to run.
2. Run `np.py diff`.
3. Report `new`, `changed` and `missing` as short lists. Identify new hosts from vendor, mDNS and reverse DNS, and ask the user only about what stays unknown.
4. Add confirmed devices to `network.json` with `source: scan` and today's `last_verified`. Put unresolved hosts in `open_questions`.

## Notes

Repeat from a wired port where possible, and once per VLAN that the machine can reach. Read the last section of `references/probes.md` for what a scan misses. Sends ARP and mDNS traffic on the local network only; needs root for `arp-scan`.

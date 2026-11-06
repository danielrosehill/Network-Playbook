---
name: probe-infrastructure
description: Read-only probe of router, DHCP, servers, Tailscale, Cloudflare tunnels, public IP and DNS into the network definition.
---

# Probe the infrastructure

Fill the logical half of `network.json` from live systems. Use read-only access only.

## Scripts

`np.py` is at `${CLAUDE_PLUGIN_ROOT}/scripts/np.py`. If that variable is unset because the skill was loaded from a catalogue, use a local clone of `https://github.com/danielrosehill/Network-Playbook`, and `scripts/np.py` there.

## Steps

1. Read `references/probes.md` and `references/definition-format.md`.
2. Ask which systems exist and how to reach them, unless the definition already says. Use whatever credentials and tools the user already has, and keep the secrets out of the definition.
3. Probe in this order: router (subnets, DHCP range, reservations, ARP table, port forwards), switches and APs, servers, Tailscale, Cloudflare, public IP and DNS.
4. Write results as NetBox-style records: IPs go on interfaces, and every device gets `source: probe` and `last_verified`.
5. Reconcile conflicts: live evidence beats the old record. If two live sources disagree, add an `open_questions` entry.
6. Run `np.py validate` and report errors and gaps.

## Notes

Fields ending `_ref` say where a secret is stored, for example "password manager: Home Wi-Fi". `np.py` rejects anything that looks like a stored secret.

# Network Playbook

Agent skills that document a home network well enough to rebuild it after a move. The test of success: you can unplug everything, carry it to a new address, and put it back together from the printout.

One definition, `network.json`, produces two outputs:

- **PDF playbook** (Typst), to print and follow: move-out checks, rebuild steps, topology, DHCP range and reservations, port maps of each device, cable schedule, fallback plans, remote access and DNS.
- **Machine JSON**, for an agent helping with the rebuild: the same facts plus ordered steps, each with a check.

## Skills

| Skill | Job |
|---|---|
| `setup-site` | Create the workspace for a location |
| `scan-lan` | ARP and mDNS sweep, compared with the definition |
| `probe-infrastructure` | Read-only probe of router, DHCP, servers, Tailscale, Cloudflare, public IP, DNS |
| `document-hardware` | Photos and notes into port maps, cable schedule and layout |
| `build-playbook` | Render the dated PDF and JSON, save to Google Drive |
| `update-playbook` | Find drift, record it, reissue |
| `rebuild-network` | Walk through reassembly at a new location |

## Methods

The format borrows from people who move working systems for a living: PACE fallback plans and jump kits from military signals, TIA-606 identifiers, input-list-style cable schedules and stage plots from touring, Read-Do checklists from aviation, NetBox's data model and NIST's reconstitution step. See `references/documentation-standards.md`. These are adaptations, not claims of compliance.

## Data

Your data stays outside the plugin, by default in `~/.claude-user-data/network-playbook/`. Set `NETWORK_PLAYBOOK_HOME` to move it. Secrets are never stored: `*_ref` fields say where each one is kept, and the validator rejects anything that looks like a credential.

## Requirements

Python 3 and [Typst](https://typst.app) 0.14 or later. `arp-scan` (needs root) and `avahi-browse` are recommended for scanning.

## Install

```bash
/plugin marketplace add danielrosehill/Claude-Code-Plugins
/plugin install network-playbook@danielrosehill
```

`examples/example-site/network.json` is a fictional, complete definition. Formerly `lan-manager-plugin`.

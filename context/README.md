# LAN Memory — Schema

Structured knowledge store for the local network. Grows over time as Claude learns about devices and services.

Note: the entire `context/` directory is gitignored — add device/service details freely, this plugin's memory stays local.

## Files

- `network.md` — subnets, gateway, DNS, DHCP ranges, VLANs, WAN entry points
- `devices/<slug>.md` — one file per physical/virtual host
- `services/<slug>.md` — one file per service (may be hosted on one or more devices)

Slug = lowercase, hyphenated, stable identifier (e.g. `ubuntuvm`, `jellyfin`, `home-assistant`).

Two legacy files are preserved for now: `lan-guide.md` and `services.md`. New information should go into the structured `devices/` and `services/` layout.

## Device frontmatter schema

```yaml
---
hostname: ubuntuvm
ip: 10.0.0.20
ipv6:
mac:
os: Ubuntu 24.04
kernel:
hardware: Proxmox VM (host: proxmox)
ssh_alias: ubuntuvm
role: general-purpose Linux VM for self-hosted services
status: active        # active | offline | retired | unknown
last_verified: 2026-04-19
---
```

Followed by free-form notes: services hosted, quirks, credentials-location hints (never credentials themselves), links to related device/service files.

## Service frontmatter schema

```yaml
---
name: Jellyfin
host: 10.0.0.4
internal_port: 8096
external_port: 32400
protocol: http
container: true
reverse_proxy: cloudflared -> media.example.com
auth: Cloudflare Access
status: active
last_verified: 2026-04-19
---
```

Followed by notes: install method, config path, related services, known issues.

## Update rules

1. **Edit in place** — don't create duplicate entries for a renamed/moved host. Update the existing file and bump `last_verified`.
2. **Never store secrets** — SSH keys, passwords, API tokens. Point to where they live, don't inline them.
3. **Flag stale data** when you can't verify — set `status: unknown` and leave a `## Stale:` note with the date rather than deleting.
4. **Cross-link** — devices link to services they host; services link back to their host devices.

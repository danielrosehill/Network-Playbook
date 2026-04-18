# LAN Manager

This plugin is a dual-purpose tool for Daniel's local network:

1. **Operational launchpad** — base for network sysadmin tasks (scans, device ops).
2. **Persistent LAN memory** — a structured knowledge store of devices, services, OSes, ports, and network topology that accumulates over time.

## Memory layout

```
context/
  network.md          subnet, gateway, DNS, DHCP, VLANs
  devices/<host>.md   one file per device (frontmatter + notes)
  services/<svc>.md   one file per service (frontmatter + notes)
```

Each device and service file uses YAML frontmatter for structured fields so it stays greppable and machine-readable. See `context/README.md` for the schema.

## How to use the memory

- **Before acting** on a LAN task, read the relevant `context/devices/*.md` and `context/services/*.md` for what we already know.
- **After learning something new** about the LAN — a new device, a port discovery, an OS version, a service move — update the appropriate file. Prefer editing existing entries over creating duplicates.
- **When memory conflicts with reality** (e.g. a port probe returns something different from the file), trust the live evidence, update the file, and record the correction date in the entry.
- The `/lan-remember`, `/lan-recall`, and `/lan-verify` commands are the primary entry points for memory operations.

## Authority & staleness

Memory entries are historical snapshots. Treat them as hints, not guarantees. If a user is about to act on memory (SSH somewhere, hit a port), verify reachability first when cheap to do so.

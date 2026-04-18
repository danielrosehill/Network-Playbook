## LAN Manager Plugin

A Claude Code plugin that turns your LAN into a working memory: devices, services, OSes, ports, and topology, all captured in a structured, greppable knowledge store that grows as you and Claude discover things together.

This repo is a **public template**. Install it, then either keep memory local (the `context/` directory is gitignored) or fork/clone it privately and commit your own inventory into that private copy.

---

## Install

```bash
/plugin marketplace add https://github.com/danielrosehill/Claude-Code-Plugins
/plugin install lan-manager@danielrosehill
```

## Quick start

```bash
# Seed the network overview
cp context/network.md.example context/network.md
# Edit context/network.md with your subnet / gateway / DNS

# Record your first device
/lan-remember the firewall is opnsense at 10.0.0.1, runs cloudflared

# Sweep the LAN and reconcile with memory
/lan-scan

# Look something up later
/lan-recall jellyfin

# Re-check what's on disk against reality
/lan-verify jellyfin
```

## How memory is laid out

```
context/
  network.md              subnet, gateway, DNS, WAN entry points
  devices/<slug>.md       one file per host (YAML frontmatter + notes)
  services/<slug>.md      one file per service (YAML frontmatter + notes)
```

Schema and field definitions are in `context/README.md`. Example templates are committed as `_example.md` in each directory — everything else in `context/devices/`, `context/services/`, and `context/network.md` is gitignored so a private install can't accidentally leak topology to the public template.

## Commands

| Command | Purpose |
|---------|---------|
| `/lan-remember <desc>` | Record a new device or service observation into memory |
| `/lan-recall <query>` | Look up hosts/services by slug, IP, port, or keyword |
| `/lan-verify <slug>` | Probe the live network and reconcile memory with reality |
| `/lan-scan [subnet]` | ARP/nmap sweep, matched against existing memory |

## Design principles

- **Public template, private data.** The template ships with empty inventory; your real data stays in the gitignored `context/` tree or in a private clone.
- **Structured over narrative.** YAML frontmatter for machine-grep, prose for human notes.
- **Trust live evidence.** When memory and reality disagree, update memory.
- **Never store secrets.** Point to where they live (vault entry, key path); never inline them.

## Author

**Daniel Rosehill**
[danielrosehill.com](https://danielrosehill.com) | [public@danielrosehill.com](mailto:public@danielrosehill.com)

[![Claude Code](https://img.shields.io/badge/Claude%20Code-Project-8A2BE2)](https://claude.ai/claude-code)

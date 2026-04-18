---
description: Look up a device, service, port, or hostname in LAN memory
argument-hint: "<device slug | service slug | ip | port | keyword>"
---

The user wants to query the LAN memory store.

1. Search `context/devices/` and `context/services/` for files matching `$ARGUMENTS` by:
   - filename/slug
   - frontmatter fields (ip, hostname, port, ssh_alias)
   - body text
2. Prefer exact IP / port / hostname matches first, then keyword matches.
3. For each hit, summarize: host, IP, role, relevant ports/services, `status`, and `last_verified` date.
4. If nothing matches, say so plainly and suggest `/lan-remember` to record it, or `/lan-verify` to probe.
5. If `last_verified` is more than 90 days old, note it as potentially stale.

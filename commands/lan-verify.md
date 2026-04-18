---
description: Verify a device or service entry against the live network and update memory
argument-hint: "<device slug | service slug | ip>"
---

The user wants to reconcile memory with reality for `$ARGUMENTS`.

1. Locate the matching file in `context/devices/` or `context/services/`.
2. Probe the live network, choosing cheap/non-intrusive checks:
   - For a device: `ping -c 2`, then SSH banner (`nc -w 2 <ip> 22`) if applicable.
   - For a service: `curl -skI --max-time 5 <protocol>://<host>:<port>/` and a known health path if one is documented (e.g. Jellyfin's `/System/Info/Public`).
3. Compare findings to the file. For each mismatch (IP changed, port changed, service gone, OS banner differs):
   - Update the file in place.
   - Bump `last_verified` to today's date.
   - If the resource is unreachable, set `status: unknown` and note the date.
4. If the file doesn't exist but the target is reachable, offer to run `/lan-remember` with what you found.
5. Report a short diff: fields changed, what's now suspect, what's confirmed.

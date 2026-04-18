---
description: Run an ARP/nmap sweep of the LAN and reconcile findings with memory
argument-hint: "[subnet, e.g. 10.0.0.0/24]"
---

The user wants a fresh sweep of the LAN, with results reconciled against `context/`.

1. Determine target subnet: use `$ARGUMENTS` if provided, else read `context/network.md`'s `Primary subnet`, else fall back to the subnet of the local interface.
2. Run discovery (choose what's available, least intrusive first):
   - `arp-scan --localnet` (needs sudo) or `arp -an`
   - `nmap -sn <subnet>` for ping sweep
   - For interesting hosts, optional `nmap --top-ports 50 <host>` — ask before running a broader port scan.
3. For each live host:
   - Match to an existing `context/devices/*.md` by IP or MAC.
   - If matched and fields differ, update and bump `last_verified`.
   - If unmatched, suggest `/lan-remember` for that host.
4. Summarize: known-and-present, known-but-missing, unknown-and-new.
5. Do **not** persist raw scan output into the git-tracked tree.

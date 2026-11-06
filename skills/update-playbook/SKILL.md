---
name: update-playbook
description: Keep the network documentation current by rescanning, re-probing, recording changes and reissuing the playbook.
---

# Update the playbook

## Scripts

`np.py` is at `${CLAUDE_PLUGIN_ROOT}/scripts/np.py`. If that variable is unset because the skill was loaded from a catalogue, use a local clone of `https://github.com/danielrosehill/Network-Playbook`, and `scripts/np.py` there.

## Steps

1. If the user stated a change ("the NAS moved to port 6"), record it, then go to step 4.
2. Otherwise run `scan-lan` and re-run the parts of `probe-infrastructure` that can change without notice: DHCP reservations, Tailscale nodes, tunnels, public IP, DNS.
3. List the differences and which are real changes. Treat devices that are only asleep as unconfirmed, not removed.
4. Update `network.json`, set `last_verified` on what you confirmed, and add a `changelog` entry with the date.
5. Check that rebuild steps still match. A moved port means editing the steps that name it.
6. Report anything with an old `last_verified` or a PACE route that has never been tested.
7. If anything changed, run `build-playbook`. If nothing changed, say so and don't issue a new copy.

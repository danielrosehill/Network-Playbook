---
name: rebuild-network
description: Reassemble a network at a new location from its playbook JSON, step by step, checking each stage. Use on "we've moved".
---

# Rebuild the network

Work from the newest `releases/*.json`, or the file the user provides. Its `_meta.agent_instructions` apply.

## Scripts

`np.py` is at `${CLAUDE_PLUGIN_ROOT}/scripts/np.py`. If that variable is unset because the skill was loaded from a catalogue, use a local clone of `https://github.com/danielrosehill/Network-Playbook`, and `scripts/np.py` there.

## Steps

1. Create a new site with `setup-site` and copy the definition into it, so the old site stays as a record.
2. Before the move, walk `rebuild.move_out` as Do-Confirm: the user does the work, then you confirm each line.
3. Bring up `rebuild.jump_kit` first.
4. Go through `rebuild.phases` in order as Read-Do. Give one step at a time, run or ask for its `verify` check, and record the result. Do not cross a `pause_point` with a failed check.
5. If a step fails, stop and diagnose. Use the `pace` plans if internet or admin access is lost.
6. Handle what changes at a new address: provider handoff, public IP, DNS records with `depends_on_public_ip`, port forwards, dynamic DNS.
7. Run `rebuild.reconstitution` in full, including a fresh `scan-lan` and `np.py diff`.
8. Write every difference back to the new site's `network.json`, then run `build-playbook`.

## Notes

Ask before any step that changes router, DNS or tunnel configuration; the user may be cut off from the network it serves.

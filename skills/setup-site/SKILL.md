---
name: setup-site
description: Create the persistent workspace for documenting a home network site, outside the plugin. Use on "set up network playbook".
---

# Set up a site

A site is one physical location, such as "Apartment 2". A move means a new site, so the old one stays as a record.

## Scripts

`np.py` is at `${CLAUDE_PLUGIN_ROOT}/scripts/np.py`. If that variable is unset because the skill was loaded from a catalogue, use a local clone of `https://github.com/danielrosehill/Network-Playbook`, and `scripts/np.py` there.

## Steps

1. Run `np.py path` and tell the user where data will live.
2. Ask for the site name if it wasn't given, then run `np.py init <slug> --name "<name>"`.
3. In `config.json` at the data root, set `publish.drive_folder` to where finished playbooks go. Set `footer_line` if the user wants a closing line on every PDF.
4. Point the user at `scan-lan`, `probe-infrastructure` and `document-hardware`.

## Data storage

```
<data dir>/config.json
<data dir>/sites/<slug>/network.json   the definition, the single source of truth
                       photos/         cabinet and hardware photos
                       scans/          raw scan results
                       releases/       dated PDF and JSON pairs
```

The data dir is the first of: `$NETWORK_PLAYBOOK_HOME`, `$CLAUDE_USER_DATA/network-playbook`, `~/.claude-user-data/network-playbook`, the XDG `claude-plugins` root.

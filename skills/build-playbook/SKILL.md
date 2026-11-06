---
name: build-playbook
description: Render the network definition to a dated printable Typst PDF and agent-readable JSON, then save both to Google Drive.
---

# Build the playbook

Both outputs come from `network.json`, so they can't disagree.

## Scripts

`np.py` is at `${CLAUDE_PLUGIN_ROOT}/scripts/np.py`. If that variable is unset because the skill was loaded from a catalogue, use a local clone of `https://github.com/danielrosehill/Network-Playbook`, and `scripts/np.py` there.

## Steps

1. Read `references/documentation-standards.md`.
2. Author or refresh the `rebuild` section so it fits this network: `move_out`, `jump_kit`, `phases` and `reconstitution`. Write `pace` plans for `internet` and `admin_access`. Ask the user what their real fallbacks are; do not invent them.
3. Run `np.py validate`. Fix errors. Report `readiness_gaps`, which print on the PDF cover until closed.
4. Add a `changelog` entry, then run `np.py build`. It writes `Network-Playbook-<site>-<date>.pdf` and `.json` to `releases/`.
5. View the PDF pages as images. Check the topology and every port map before calling it done.
6. Upload both files to `publish.drive_folder` with the agent's Drive tool or `rclone`, titled "Network setup at <site>, <date>". Read back the folder listing to confirm they arrived. Keep older dated copies.

## Notes

The PDF needs `typst`. The first build fetches the `cntopo` package from Typst Universe.

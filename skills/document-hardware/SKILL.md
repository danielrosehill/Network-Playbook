---
name: document-hardware
description: Turn photos and notes of a network cabinet into port maps, cable schedule and layout. Use on "here's a photo of the switch".
---

# Document the hardware

Capture what no probe can see: which socket is which, and what plugs into what.

## Scripts

`np.py` is at `${CLAUDE_PLUGIN_ROOT}/scripts/np.py`. If that variable is unset because the skill was loaded from a catalogue, use a local clone of `https://github.com/danielrosehill/Network-Playbook`, and `scripts/np.py` there.

## Inputs

Photos of the cabinet, faceplates and labels, plus the user's notes on how things connect.

## Steps

1. Read `references/documentation-standards.md`.
2. Copy each photo into the site's `photos/` folder with a descriptive name and add it to `photos[]`. Attach it to devices through `devices[].photos`.
3. For each device, record every physical port: `label` as printed, `face`, `row`, `position` counted left to right as seen by someone facing that side, `use`, and `os_name` if known. Set `source: photo`.
4. Read only what is legible in the photo. For anything unreadable or ambiguous, ask the user or add to `open_questions`. Never guess a port order: the point of this document is that the guess is not needed.
5. Map OS interface names to physical sockets when you can test it, for example by having the user unplug one cable while you watch link state.
6. Record each connection in `cables[]` with a cable number (`C001`, `C002` and so on), in patch order. Tell the user to label both ends.
7. Record where things physically go in `plot[]`.
8. Run `np.py validate`.

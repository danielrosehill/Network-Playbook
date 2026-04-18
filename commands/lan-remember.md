---
description: Record a device or service observation into LAN memory under context/
argument-hint: "<free-form description of the device or service>"
---

The user wants to save a new observation into the LAN memory store.

1. Parse `$ARGUMENTS` to decide whether this is a **device** (a host) or a **service** (a process on a host). If ambiguous, ask once.
2. Derive a slug: lowercase, hyphenated, stable (hostname for devices; service name for services).
3. Check whether `context/devices/<slug>.md` or `context/services/<slug>.md` already exists.
   - If yes → **edit in place**, update frontmatter fields, append to notes, bump `last_verified` to today's date.
   - If no → create it using the schema in `context/devices/_example.md` or `context/services/_example.md`.
4. Populate only fields you have evidence for. Leave others blank or `unknown` rather than guessing.
5. If the observation implies a relationship (service X runs on device Y), cross-link both files.
6. Never write secrets (passwords, keys, tokens). If the user pastes one, refuse and tell them to store the pointer only.
7. Report back: path written, fields set, any gaps worth filling on a later pass.

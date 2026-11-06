# Documentation standards used by this plugin

These methods come from fields that rebuild working systems in new places under pressure. Apply them when writing or updating a definition. This plugin **borrows** them; it does not claim compliance with any standard. TIA-606 and the AVIXA documents are paid standards, and only secondary summaries of them were read (2026-11-06).

| Method | From | Rule in this plugin | Where it lands |
|---|---|---|---|
| PACE | Military signal planning (FM 6-02, per CISA) | Give every critical path four routes in order: Primary, Alternate, Contingency, Emergency. State when to switch. A route never tested counts as unproven: test by disabling the primary. | `pace.internet`, `pace.admin_access` |
| Jump TOC | Military command post moves (FM 3-09.70) | A small element moves first and keeps things running while the main body moves. Name the smallest device set that gives internet and admin access. | `rebuild.jump_kit` |
| Administration identifiers | ANSI/TIA-606 | Give every cabinet, port and cable a unique identifier, numbered top-down, with `panel:port` written using a colon. Label both ends of each cable and show the far end at each port. A single cabinet is the small end of TIA's administration classes. | `cables[].id`, `<device>:<interface>` |
| Input list / patch sheet | Live sound | One table row per connection, in patch order, using exact numbers. Keep a one-to-one patch where possible, so switch port N matches panel port N. Keep spares next to related ports. | Cable schedule, `cables[]` |
| Stage plot | Live sound | Where things go is a separate view from what connects to what. | `plot[]`, topology page |
| Read-Do / Do-Confirm | Aviation checklists (Boorman, via Gawande) | Rebuild steps are Read-Do. Move-out checks are Do-Confirm. Every phase ends at a named pause point. Aim for 5 to 9 steps per phase, which is a rule of thumb. Mark the steps most dangerous to skip as `killer`. | `rebuild.phases`, `rebuild.move_out` |
| Source-of-truth model | NetBox (DCIM/IPAM) | Site, rack, device, interface, then IP. Addresses belong to interfaces, not devices. Cables join two interfaces. Prefixes hold IP ranges. Use NetBox's vocabulary so the file feels familiar and can be mapped into NetBox later. | `network.json` shape |
| Reconstitution | NIST SP 800-34 | Recovery ends only after it is validated, not when things appear to work. | `rebuild.reconstitution` |

## Writing rules

- **Write for someone tired, holding a cable, with no internet.** Each step is one physical action and names the exact port and cable: "Connect firewall LAN 1 to switch port 1 with C002."
- **Every step has a check** with an expected result. Prefer a command when one exists.
- **Dependency order:** internet, then LAN and Wi-Fi, then servers, then remote access and DNS.
- **Mark what a new address breaks:** set `depends_on_public_ip` on DNS records and list port forwards and dynamic DNS.
- **Separate facts from guesses:** every device has `source` (`scan`, `probe`, `photo`, `user`, `inferred`) and `last_verified`. Unresolved points go in `open_questions`, which print on the cover.

## Sources

- [CISA/NCSWIC PACE plan](https://cybersecurity.gov/sites/default/files/2023-05/23_0426_ncswic_PACE-Plan_508.pdf)
- [FM 3-09.70 excerpt, jump TOC](https://www.globalsecurity.org/military/library/policy/army/fm/3-09-70/ch3.htm)
- [TIA-606 study guide](https://open-exam-prep.com/study-guides/bicsi-inst2-copper/standards-and-code-compliance/pathways-spaces-admin); [TIA-606-D summary](https://www.akcp.com/2025/04/07/data-center-cable-labeling-standards/)
- [Input list](https://www.daysheets.com/glossary/input-list); [Ferguson on stage plots and input lists](https://bluecupmusic.com/wp-content/uploads/2020/11/ferguson-stage-plots-input-lists.pdf); [How to prepare for a tour](https://soundgirls.org/?p=5241)
- [AVIXA standards](https://avixa.org/standards/current-standards)
- [Checklist Manifesto notes](https://www.stevegrossi.com/on/the-checklist-manifesto)
- [NetBox docs mirror](https://netbox.rc.umass.edu/static/docs)
- [NIST SP 800-34 mirror](https://corpora.tika.apache.org/base/docs/govdocs1/662/662094.pdf)

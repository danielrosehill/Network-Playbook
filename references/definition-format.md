# Definition format (`network.json`, schema_version 1)

`examples/example-site/network.json` is a complete worked example. `np.py validate` checks it. Field names follow NetBox where one exists.

| Key | Holds |
|---|---|
| `site` | `name`, `slug`, `address`, `summary` |
| `racks[]` | Cabinets: `id`, `name`, `location` |
| `devices[]` | `id`, `name`, `role` (`ont`, `modem`, `router`, `firewall`, `switch`, `ap`, `server`, `nas`, `vm`, `client`), `make`, `model`, `rack`, `os`, `hosted_on`, `admin {url, credential_ref}`, `photos[]`, `notes`, `source`, `last_verified`, `interfaces[]` |
| `devices[].interfaces[]` | `id`, `label` (as printed), `type` (`rj45`, `sfp`, `wifi`, `virtual`), `face` (`front`, `rear`), `row`, `position` (left to right, from 1), `use` (`wan`, `uplink`, `trunk`, `lan`, `mgmt`, `spare`), `os_name`, `mac`, `ip_addresses[]` |
| `ip_addresses[]` | `address`, `prefix`, `assignment` (`static`, `reservation`, `dhcp`), `dns_name` |
| `cables[]` | `id`, `a {device, interface}`, `b {device, interface}`, `type`, `colour`, `length`, `notes` |
| `prefixes[]` | `id`, `name`, `cidr`, `vlan`, `gateway`, `dns[]`, `domain`, `ip_ranges[] {kind, start, end, server, lease}` |
| `wireless[]` | `ssid`, `bands`, `prefix`, `password_ref`, `aps[]` |
| `internet` | `provider {name, support, account_ref}`, `circuits[] {id, name, type, handoff, device, interface, addressing, credential_ref}`, `public_ip {address, kind, observed}` |
| `pace` | `internet` and `admin_access`, each with `primary`, `alternate`, `contingency`, `emergency` as `{method, switch_when, last_tested}` |
| `services[]` | `id`, `name`, `host`, `port`, `url` |
| `remote_access` | `tailscale {tailnet, nodes[] {name, ip, device, subnet_routes[], exit_node}}`, `cloudflare_tunnels[] {name, id, connector, routes[] {hostname, service}}`, `port_forwards[] {external, protocol, target, notes}`, `ddns[] {hostname, provider, updater}` |
| `dns` | `resolver {device, upstreams[]}`, `overrides[] {host, ip}`, `zones[] {name, registrar, nameservers[], records[] {type, name, value, depends_on_public_ip}}` |
| `photos[]` | `id`, `file` (relative to the site folder), `caption` |
| `plot[]` | `item`, `location` |
| `rebuild` | `jump_kit[]`, `move_out[]`, `phases[] {id, title, pause_point, steps[] {id, action, killer, depends_on[], verify {command, check, expected}}}`, `reconstitution[]` |
| `open_questions[]`, `changelog[] {date, summary}` | Unknowns, and history |

**Secrets never go in this file.** A key that looks like a credential is rejected unless it ends in `_ref`, which says where the secret is kept.

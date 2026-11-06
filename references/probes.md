# Read-only probes

Run only what the network has, and only reads. Record the `source` and today's date as `last_verified`. Never copy a secret into the definition.

## Router or firewall
This is the best single source: DHCP range, reservations, interfaces, VLANs, ARP table for every subnet, port forwards, DNS overrides.
- **OPNsense:** REST API with a read-only key, or SSH. Reservations and ranges are in `/conf/config.xml`; `ifconfig -a` gives OS interface names and MACs; `arp -an` gives the neighbour table. Redact `config.xml` before keeping any of it, as it holds hashes and keys.
- **Other routers:** export the config or read the admin pages. Ask the user for a screenshot if there is no API.

## UniFi and other managed switches or APs
Use the controller API or UI for device list, switch port table, uplinks and client-to-port mapping. This gives real cabling evidence.

## Servers (over SSH)
```bash
hostnamectl; ip -j addr; ip -j route; cat /etc/resolv.conf
docker ps --format '{{.Names}}\t{{.Image}}\t{{.Ports}}'
virsh list --all 2>/dev/null; systemctl list-units --type=service --state=running --no-pager
```

## Tailscale
`tailscale status --json` gives nodes, IPs, exit node. Advertised routes are under `Peer[].PrimaryRoutes`. Also run `tailscale serve status`.

## Cloudflare
With an API token that can read the account: `GET /accounts/{id}/cfd_tunnel`, `GET /accounts/{id}/cfd_tunnel/{tunnel}/configurations` for hostnames and targets, `GET /zones` and `GET /zones/{id}/dns_records`. On the connector host, `cloudflared tunnel list` also works.

## Public IP and DNS
- `curl -s https://api.ipify.org` gives the public IP. Compare with the router's WAN address: if they differ, or the WAN is in `100.64.0.0/10`, the connection is behind CGNAT and port forwards will not work.
- `dig +short <hostname>` for each record; `dig NS <zone>` for nameservers; `whois <domain>` for the registrar.
- Set `depends_on_public_ip` on any record whose value equals the public IP.

## What a scan cannot see
ARP stops at the subnet boundary and sees only awake devices. Mesh systems can answer for many IPs (`proxy_arp_suspect`), and phones use randomised MACs (`locally_administered_mac`). Treat the router's tables as authoritative; a scan only confirms them.

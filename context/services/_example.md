---
name: Example Service
host: 10.0.0.10
internal_port: 8096
external_port: 32400
protocol: http
container: true
reverse_proxy: none                 # or e.g. "cloudflared -> example.mydomain.com"
auth: none                          # or "Cloudflare Access", "basic", "SSO", etc.
status: active                      # active | offline | retired | unknown
last_verified: 2026-01-01
---

# Example Service

What this service does and why it runs on the LAN.

## Host
- [example-host](../devices/_example.md)

## Access
- LAN: `http://10.0.0.10:32400`
- External: (if exposed) `https://example.mydomain.com`

## Install / config
- Install method (apt, Docker compose, Helm, etc.)
- Config path on host
- Backup location / strategy

## Related services
- Links to other services this one depends on or talks to.

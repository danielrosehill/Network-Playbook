---
hostname: example-host
ip: 10.0.0.10
ipv6:
mac:
os: Ubuntu 24.04
kernel:
hardware: Physical or VM description
ssh_alias: example
role: what this device does on the LAN
status: active        # active | offline | retired | unknown
last_verified: 2026-01-01
---

# example-host

One-paragraph summary of what this device is and why it exists on the network.

## Services hosted
- [example-service](../services/_example.md)

## Quirks
- Anything odd about this device (power sensitivity, flaky NIC, known reboot schedule).

## Credentials
- Never store passwords or keys here. Note where they live instead (e.g. "SSH key in ~/.ssh/id_ed25519, vault entry 'example-host'").

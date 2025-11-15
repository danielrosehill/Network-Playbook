# Context Directory

This directory contains documentation about the LAN setup and services.

## Public Context Files
- **lan-guide.md** - Overview of LAN resources and devices
- **services.md** - Service-specific documentation

## Protected Context (gitignored)
The `context/protected/` subdirectory is gitignored and contains sensitive information:
- Specific device details that shouldn't be public
- Camera configurations (IPs, credentials structure, RTSP/ONVIF info)
- Any other sensitive network information

**Note:** The entire `context/` directory is gitignored, so add information here freely. This README is just documentation of the pattern.

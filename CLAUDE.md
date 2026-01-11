# RegenNexus MCP - Claude Code Project Guide

## Project Overview
RegenNexus MCP is a thin MCP (Model Context Protocol) wrapper around RegenNexus UAP, enabling AI agents to control hardware devices. This is the **first hardware/IoT MCP server** in the official MCP Registry.

**Version**: 0.1.1 | **License**: MIT

## Published Locations
- **PyPI**: https://pypi.org/project/regennexus-mcp/
- **MCP Registry**: `io.github.ReGenNow/regennexus-mcp`
- **GitHub**: https://github.com/ReGenNow/regennexus-mcp

## PyPI Credentials
Stored in `/Volumes/Fast/ReGenNexus-UAP/CLAUDE.md` (not pushed to GitHub).

## MCP Registry Publishing
The mcp-publisher CLI is built from source:
```bash
cd /tmp && git clone https://github.com/modelcontextprotocol/registry.git mcp-registry
cd mcp-registry && make publisher
./bin/mcp-publisher login github
./bin/mcp-publisher publish server.json
```

## Key Files
- `server.json` - MCP Registry manifest (required for registry listing)
- `mcp.json` - Alternative manifest format
- `pyproject.toml` - Package metadata
- `src/regennexus_mcp/` - Source code
- `icon-*.png` - Optimized icons (48, 64, 128, 256px)

## Available Tools (Free Tier - 17 tools)
### GPIO
- gpio_write, gpio_read, pwm_write

### Sensors
- read_sensor

### I2C/Serial
- i2c_scan, serial_send, serial_read

### Robotics
- robot_arm_move, gripper_control

### Device Management
- list_devices, device_info, camera_capture

### Mesh Networking
- list_nodes, ping_node, send_to_node, broadcast_message, find_by_capability

## Development Commands
```bash
# Build package
python3 -m build

# Upload to PyPI
TWINE_USERNAME=__token__ TWINE_PASSWORD='pypi-...' python3 -m twine upload dist/*

# Publish to MCP Registry
/tmp/mcp-registry/bin/mcp-publisher publish server.json

# Test locally
pip install -e .[local]
regennexus-mcp
```

## Version Bumping Checklist
When releasing a new version:
1. Update `pyproject.toml` version
2. Update `server.json` version (both top-level and in packages)
3. Rebuild: `python3 -m build`
4. Upload to PyPI
5. Publish to MCP Registry

## Registry Requirements
- Description must be <= 100 characters
- Name format: `io.github.{org}/{repo}` (case-sensitive!)
- Transport must be object: `{"type": "stdio"}`
- PyPI packages need version specified
- README must contain: `<!-- mcp-name: io.github.ReGenNow/regennexus-mcp -->`

## Work Log

### 2026-01-11: Initial Release v0.1.1
- Created regennexus-mcp package as thin wrapper around RegenNexus UAP
- Added 17 free tier tools (GPIO, sensors, robotics, mesh networking)
- Created optimized icons (48, 64, 128, 256px) from 1024px logo
- Published to PyPI v0.1.0, then v0.1.1 with MCP name tag
- Registered on official MCP Registry as first hardware/IoT server
- Fixed server.json schema issues (transport object, version, namespace case)

### Related: RegenNexus UAP
The main UAP codebase is at `/Volumes/Fast/ReGenNexus-UAP` with 70+ tools in the premium version.
Mesh network tested successfully with Xavier-AGX at 192.168.68.75 (7.34ms latency).

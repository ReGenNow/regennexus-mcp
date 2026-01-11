# RegenNexus MCP Server

<img src="logo.png" alt="RegenNexus Logo" width="64" height="64">

MCP (Model Context Protocol) server adapter for [RegenNexus UAP](https://github.com/ReGenNow/ReGenNexus) - enabling AI-controlled hardware.

This package exposes RegenNexus hardware capabilities as MCP tools, allowing Claude Code, Claude Desktop, and other MCP-compatible AI clients to control physical devices.

## Features

- **Hardware Control**: GPIO, PWM, robotic arms, sensors, cameras
- **Mesh Networking**: Discover and communicate with nodes over LAN (UDP/WebSocket)
- **Serial/I2C**: Communicate with microcontrollers and sensors
- **Two Connection Modes**: Local (direct import) or Remote (HTTP API)
- **Auto-Discovery**: Automatically detects installed RegenNexus and mesh nodes
- **MCP Compatible**: Works with Claude, Codex, Gemini, and any MCP client

## Installation

```bash
# MCP server only (for remote UAP connection)
pip install regennexus-mcp

# With local UAP support
pip install regennexus-mcp[local]

# With remote API support
pip install regennexus-mcp[remote]

# Everything
pip install regennexus-mcp[all]
```

## Quick Start

### 1. Configure Claude Code

Add to your Claude Code MCP settings:

```json
{
  "mcpServers": {
    "regennexus": {
      "command": "regennexus-mcp"
    }
  }
}
```

### 2. Use with Claude

Once configured, Claude can control hardware:

```
User: "List all connected devices"
Claude: [calls list_devices tool]

User: "Turn on GPIO pin 18"
Claude: [calls gpio_write with pin=18, value=1]

User: "Move the robot arm to position [0, 45, -30, 0, 60, 0, 0]"
Claude: [calls robot_arm_move with positions]
```

## Configuration

Configure via environment variables:

```bash
# Connection mode: auto, local, or remote
REGENNEXUS_MODE=auto

# Remote mode settings
REGENNEXUS_ENDPOINT=https://your-uap-server.com
REGENNEXUS_API_KEY=your-api-key

# Local mode settings
REGENNEXUS_CONFIG=/path/to/regennexus-config.yaml

# Logging
REGENNEXUS_LOG_LEVEL=INFO
```

### Claude Code Config with Environment

```json
{
  "mcpServers": {
    "regennexus": {
      "command": "regennexus-mcp",
      "env": {
        "REGENNEXUS_MODE": "local",
        "REGENNEXUS_LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

## Available Tools (Free Tier)

These tools are provided by the `regennexus` package (open source):

### GPIO & Basic I/O

| Tool | Description |
|------|-------------|
| `gpio_write` | Set a GPIO pin to HIGH (1) or LOW (0) |
| `gpio_read` | Read the current state of a GPIO pin |
| `pwm_write` | Set PWM duty cycle (0-100%) for motors, LEDs, servos |

### Sensors & I2C

| Tool | Description |
|------|-------------|
| `read_sensor` | Read value from a sensor (temperature, humidity, etc.) |
| `i2c_scan` | Scan I2C bus for connected devices |

### Serial Communication

| Tool | Description |
|------|-------------|
| `serial_send` | Send data over serial port (UART) |
| `serial_read` | Read data from serial port |

### Robotics

| Tool | Description |
|------|-------------|
| `robot_arm_move` | Move a robotic arm to specified joint positions |
| `gripper_control` | Open or close a robotic gripper |

### Device Management

| Tool | Description |
|------|-------------|
| `list_devices` | List all connected hardware devices |
| `device_info` | Get device details (CPU, memory, IP, temperature) |

### Camera

| Tool | Description |
|------|-------------|
| `camera_capture` | Capture a single image from a camera |

### Mesh Network

| Tool | Description |
|------|-------------|
| `list_nodes` | List all nodes in the mesh network |
| `ping_node` | Ping a node and measure network latency |
| `send_to_node` | Send a message/command to a specific node |
| `broadcast_message` | Broadcast a message to all nodes |
| `find_by_capability` | Find nodes with a specific capability |

Premium tools with additional capabilities are available separately.

## Connection Modes

### Local Mode (Recommended)

Requires `regennexus` package installed on the same machine. Directly imports UAP modules for minimal latency. **No API server needed.**

```bash
pip install regennexus-mcp[local]
REGENNEXUS_MODE=local regennexus-mcp
```

This is the recommended mode for most users.

### Remote Mode (Advanced)

Connects to a UAP instance running as a service via HTTP API. Requires UAP API server to be running (`regen server`).

```bash
# On the UAP server machine:
regen server --port 8080

# On the Claude Code machine:
pip install regennexus-mcp[remote]
REGENNEXUS_MODE=remote \
REGENNEXUS_ENDPOINT=http://uap-server:8080 \
regennexus-mcp
```

### Auto Mode (Default)

Tries local first, falls back to remote if UAP not installed.

```bash
regennexus-mcp  # Auto-detects best mode
```

## Running Standalone

```bash
# Run MCP server
regennexus-mcp

# Or via Python
python -m regennexus_mcp
```

## Architecture

```
Claude Code (MCP Client)
        │
        ▼
regennexus-mcp (This Package)
        │
        ├── Local Mode: Direct import
        │       │
        │       ▼
        │   regennexus (UAP)
        │
        └── Remote Mode: HTTP API
                │
                ▼
            UAP Service
```

## Development

```bash
# Clone
git clone https://github.com/regennow/regennexus-mcp
cd regennexus-mcp

# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/
ruff check src/
```

## Related Projects

- [RegenNexus UAP](https://github.com/ReGenNow/ReGenNexus) - Universal Adapter Protocol
- [MCP Specification](https://modelcontextprotocol.io/) - Model Context Protocol

## License

MIT License

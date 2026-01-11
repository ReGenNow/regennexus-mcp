"""
RegenNexus MCP Server - Public MCP adapter for RegenNexus UAP.

This package exposes RegenNexus UAP hardware control as MCP tools
for Claude Code, Claude Desktop, and other MCP-compatible AI clients.

In local mode, it uses the existing MCPServer from regennexus.bridges.mcp_bridge
which provides the free tier hardware tools:
- gpio_write
- robot_arm_move
- gripper_control
- read_sensor
- list_devices

Premium tools are available separately.

Usage:
    # Run as MCP server
    regennexus-mcp

    # Or via Python
    python -m regennexus_mcp
"""

__version__ = "0.1.0"

from .server import MCPServer
from .bridge import UAPBridge, LocalBridge, RemoteBridge

__all__ = ["MCPServer", "UAPBridge", "LocalBridge", "RemoteBridge", "__version__"]

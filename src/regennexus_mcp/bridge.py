"""
UAP Bridge - Connection layer between MCP server and RegenNexus UAP.

Supports two modes:
- Local: Direct Python import using existing mcp_bridge.py from regennexus
- Remote: HTTP/WebSocket API (for remote UAP instances)

The local mode leverages the existing MCPServer implementation in regennexus,
which provides the free tier tools. Premium tools are available separately.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from .config import ConnectionMode, MCPConfig

logger = logging.getLogger(__name__)


class UAPBridge(ABC):
    """Abstract base class for UAP connection."""

    @abstractmethod
    async def connect(self) -> bool:
        """Connect to UAP. Returns True if successful."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from UAP."""
        pass

    @abstractmethod
    def get_mcp_server(self) -> Any:
        """Get the underlying MCP server instance."""
        pass


class LocalBridge(UAPBridge):
    """
    Local UAP bridge using direct Python imports.

    This uses the existing MCPServer from regennexus.bridges.mcp_bridge,
    which provides the free tier hardware control tools.

    Requires: pip install regennexus
    """

    def __init__(self, config: MCPConfig):
        self.config = config
        self._mcp_server = None
        self._connected = False

    async def connect(self) -> bool:
        """Initialize local UAP MCP server."""
        try:
            from regennexus.bridges.mcp_bridge import create_hardware_mcp_server

            # Create the MCP server with pre-configured hardware tools
            self._mcp_server = create_hardware_mcp_server()
            self._connected = True

            logger.info("Connected to local UAP - using regennexus.bridges.mcp_bridge")
            return True

        except ImportError as e:
            logger.error(f"regennexus not installed: {e}")
            logger.info("Install with: pip install regennexus")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize UAP MCP server: {e}")
            return False

    async def disconnect(self) -> None:
        """Cleanup."""
        self._connected = False
        self._mcp_server = None

    def get_mcp_server(self) -> Any:
        """Get the UAP MCPServer instance."""
        return self._mcp_server


class RemoteBridge(UAPBridge):
    """
    Remote UAP bridge using HTTP/WebSocket API.

    For connecting to UAP running on another machine or as a service.

    NOTE: Remote mode requires UAP API server to be running.
    Most users should use local mode (pip install regennexus).
    """

    def __init__(self, config: MCPConfig):
        self.config = config
        self._session = None
        self._connected = False
        self._mcp_server = None

    async def connect(self) -> bool:
        """Connect to remote UAP API."""
        if not self.config.endpoint:
            logger.error("REGENNEXUS_ENDPOINT not set for remote mode")
            logger.info("Hint: Use REGENNEXUS_MODE=local if UAP is installed locally")
            return False

        try:
            import aiohttp

            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.timeout / 1000),
                headers=self._get_headers(),
            )

            # Test connection
            async with self._session.get(f"{self.config.endpoint}/health") as resp:
                if resp.status == 200:
                    self._connected = True
                    logger.info(f"Connected to remote UAP at {self.config.endpoint}")

                    # Create a proxy MCP server for remote mode
                    self._mcp_server = RemoteMCPServerProxy(
                        self._session,
                        self.config.endpoint,
                    )
                    return True
                else:
                    logger.error(f"UAP health check failed: {resp.status}")
                    return False

        except ImportError:
            logger.error("aiohttp required for remote mode: pip install regennexus-mcp[remote]")
            return False
        except Exception as e:
            logger.error(f"Failed to connect to remote UAP: {e}")
            return False

    async def disconnect(self) -> None:
        """Close remote connection."""
        if self._session:
            await self._session.close()
            self._session = None
        self._connected = False
        self._mcp_server = None

    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers with auth."""
        headers = {"Content-Type": "application/json"}
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        return headers

    def get_mcp_server(self) -> Any:
        """Get the remote MCP server proxy."""
        return self._mcp_server


class RemoteMCPServerProxy:
    """
    Proxy that forwards MCP requests to remote UAP API.

    Implements the same interface as regennexus MCPServer.
    """

    def __init__(self, session: Any, endpoint: str):
        self._session = session
        self._endpoint = endpoint
        self.name = "regennexus-remote"
        self.version = "0.1.0"

    async def handle_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Forward MCP message to remote UAP."""
        method = message.get("method", "")
        params = message.get("params", {})
        msg_id = message.get("id")

        # Handle notifications
        if "id" not in message:
            return None

        try:
            if method == "initialize":
                return self._success_response(msg_id, {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}, "resources": {}},
                    "serverInfo": {"name": self.name, "version": self.version},
                })

            elif method == "tools/list":
                # Get tools from remote
                tools = await self._get_remote_tools()
                return self._success_response(msg_id, {"tools": tools})

            elif method == "tools/call":
                result = await self._call_remote_tool(
                    params.get("name"),
                    params.get("arguments", {}),
                )
                return self._success_response(msg_id, {
                    "content": [{"type": "text", "text": str(result)}]
                })

            elif method == "ping":
                return self._success_response(msg_id, {})

            else:
                return self._error_response(msg_id, -32601, f"Method not found: {method}")

        except Exception as e:
            return self._error_response(msg_id, -32603, str(e))

    async def _get_remote_tools(self) -> List[Dict]:
        """Fetch tool list from remote UAP."""
        # For now, return standard hardware tools
        # In future, could query remote for available tools
        return [
            {
                "name": "gpio_write",
                "description": "Set a GPIO pin to HIGH (1) or LOW (0)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "device_id": {"type": "string"},
                        "pin": {"type": "integer"},
                        "value": {"type": "integer", "enum": [0, 1]},
                    },
                    "required": ["device_id", "pin", "value"],
                },
            },
            {
                "name": "robot_arm_move",
                "description": "Move a robotic arm to specified joint positions",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "device_id": {"type": "string"},
                        "positions": {"type": "array", "items": {"type": "number"}},
                        "duration": {"type": "number"},
                    },
                    "required": ["device_id", "positions"],
                },
            },
            {
                "name": "gripper_control",
                "description": "Open or close a robotic gripper",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "device_id": {"type": "string"},
                        "action": {"type": "string", "enum": ["open", "close"]},
                        "force": {"type": "number"},
                    },
                    "required": ["device_id", "action"],
                },
            },
            {
                "name": "read_sensor",
                "description": "Read value from a sensor",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "device_id": {"type": "string"},
                        "sensor_type": {"type": "string"},
                    },
                    "required": ["device_id", "sensor_type"],
                },
            },
            {
                "name": "list_devices",
                "description": "List all connected hardware devices",
                "inputSchema": {"type": "object", "properties": {}},
            },
        ]

    async def _call_remote_tool(self, tool_name: str, arguments: Dict) -> Dict:
        """Execute tool on remote UAP via /send endpoint."""
        device_id = arguments.get("device_id", "*")

        async with self._session.post(
            f"{self._endpoint}/send",
            json={
                "target": device_id,
                "intent": "command",
                "content": {"tool": tool_name, "arguments": arguments},
            },
        ) as resp:
            return await resp.json()

    async def run_stdio(self) -> None:
        """Run stdio server (delegates to main server loop)."""
        # This is handled by the main server.py
        pass

    def _success_response(self, msg_id: Any, result: Dict) -> Dict:
        return {"jsonrpc": "2.0", "id": msg_id, "result": result}

    def _error_response(self, msg_id: Any, code: int, message: str) -> Dict:
        return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": code, "message": message}}


def create_bridge(config: MCPConfig) -> UAPBridge:
    """
    Create appropriate bridge based on configuration.

    Auto mode tries local first, falls back to remote.
    """
    if config.mode == ConnectionMode.LOCAL:
        return LocalBridge(config)

    if config.mode == ConnectionMode.REMOTE:
        return RemoteBridge(config)

    # Auto mode: try local first
    if config.mode == ConnectionMode.AUTO:
        # Check if regennexus is installed
        try:
            import regennexus
            logger.info("regennexus found, using local mode")
            return LocalBridge(config)
        except ImportError:
            pass

        # Check if remote endpoint is configured
        if config.endpoint:
            logger.info("Using remote mode")
            return RemoteBridge(config)

        # Default to local (will fail gracefully if not installed)
        logger.info("Defaulting to local mode")
        return LocalBridge(config)

    return LocalBridge(config)

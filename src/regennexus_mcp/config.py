"""
Configuration loader for RegenNexus MCP Server.

Supports environment variables and .env files.
"""

import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class ConnectionMode(Enum):
    """Connection mode to UAP."""
    AUTO = "auto"      # Try local first, fall back to remote
    LOCAL = "local"    # Direct import (requires regennexus installed)
    REMOTE = "remote"  # HTTP/WebSocket API


@dataclass
class MCPConfig:
    """MCP Server configuration."""

    # Connection mode
    mode: ConnectionMode = ConnectionMode.AUTO

    # Remote mode settings
    endpoint: Optional[str] = None
    api_key: Optional[str] = None
    ws_endpoint: Optional[str] = None
    timeout: int = 60000  # milliseconds

    # Local mode settings
    config_path: Optional[str] = None

    # Server settings
    server_name: str = "regennexus-mcp"
    server_version: str = "0.1.0"

    # Logging
    log_level: str = "INFO"
    log_format: str = "text"  # "text" or "json"

    # Mesh networking
    enable_mesh: bool = False
    mesh_port: int = 5353
    node_id: str = "mcp-server"

    @classmethod
    def from_env(cls) -> "MCPConfig":
        """Load configuration from environment variables."""

        # Parse mode
        mode_str = os.getenv("REGENNEXUS_MODE", "auto").lower()
        try:
            mode = ConnectionMode(mode_str)
        except ValueError:
            logger.warning(f"Invalid mode '{mode_str}', using 'auto'")
            mode = ConnectionMode.AUTO

        return cls(
            mode=mode,
            endpoint=os.getenv("REGENNEXUS_ENDPOINT"),
            api_key=os.getenv("REGENNEXUS_API_KEY"),
            ws_endpoint=os.getenv("REGENNEXUS_WS"),
            timeout=int(os.getenv("REGENNEXUS_TIMEOUT", "60000")),
            config_path=os.getenv("REGENNEXUS_CONFIG"),
            server_name=os.getenv("REGENNEXUS_SERVER_NAME", "regennexus-mcp"),
            log_level=os.getenv("REGENNEXUS_LOG_LEVEL", "INFO"),
            log_format=os.getenv("REGENNEXUS_LOG_FORMAT", "text"),
            enable_mesh=os.getenv("REGENNEXUS_MESH", "").lower() in ("true", "1", "yes"),
            mesh_port=int(os.getenv("REGENNEXUS_MESH_PORT", "5353")),
            node_id=os.getenv("REGENNEXUS_NODE_ID", "mcp-server"),
        )


def load_dotenv():
    """Load .env file if present."""
    try:
        from dotenv import load_dotenv as _load_dotenv
        _load_dotenv()
    except ImportError:
        # python-dotenv not installed, skip
        pass


def setup_logging(config: MCPConfig):
    """Configure logging based on config."""
    import sys

    level = getattr(logging, config.log_level.upper(), logging.INFO)

    if config.log_format == "json":
        fmt = '{"time": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}'
    else:
        fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    logging.basicConfig(
        level=level,
        format=fmt,
        stream=sys.stderr,  # Log to stderr, keep stdout for MCP
    )

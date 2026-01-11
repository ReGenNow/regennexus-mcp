"""
MCP Server wrapper for RegenNexus.

This is a thin wrapper that uses the existing MCPServer from
regennexus.bridges.mcp_bridge for the actual MCP protocol handling.

The regennexus package provides the free tier hardware tools:
- gpio_write, robot_arm_move, gripper_control, read_sensor, list_devices

Premium tools are available separately.
"""

import asyncio
import json
import logging
import sys
import threading
import queue
from typing import Any, Dict, Optional

from .bridge import create_bridge
from .config import MCPConfig, load_dotenv, setup_logging

logger = logging.getLogger(__name__)


class MCPServer:
    """
    MCP Server wrapper for RegenNexus UAP.

    In local mode, this delegates to regennexus.bridges.mcp_bridge.MCPServer
    which provides the free tier tool implementations.

    In remote mode, this proxies requests to a remote UAP API.
    """

    def __init__(self, config: Optional[MCPConfig] = None):
        self.config = config or MCPConfig.from_env()
        self.bridge = create_bridge(self.config)
        self._uap_server = None
        self._initialized = False

    async def initialize(self) -> bool:
        """Initialize connection to UAP and get the MCPServer instance."""
        if await self.bridge.connect():
            self._uap_server = self.bridge.get_mcp_server()
            self._initialized = self._uap_server is not None
            return self._initialized
        return False

    async def handle_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Handle incoming MCP JSON-RPC message.

        Delegates to the UAP's MCPServer which has the tool implementations.
        """
        if not self._uap_server:
            msg_id = message.get("id")
            if msg_id is None:
                return None
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32603, "message": "UAP not connected"},
            }

        # Delegate to UAP's MCPServer
        return await self._uap_server.handle_message(message)

    async def run_stdio(self) -> None:
        """
        Run MCP server over stdio.

        This is the standard transport for Claude Code/Desktop integration.
        """
        logger.info("Starting RegenNexus MCP server on stdio")

        # Initialize UAP connection first
        if not await self.initialize():
            logger.error("Failed to initialize UAP connection")
            logger.info("Make sure regennexus is installed: pip install regennexus")
            return

        logger.info("UAP MCPServer initialized with free tier tools")

        # Thread-safe queue for stdin
        input_queue: queue.Queue = queue.Queue()
        stop_event = threading.Event()

        def stdin_reader():
            """Read stdin in separate thread."""
            try:
                while not stop_event.is_set():
                    try:
                        line = sys.stdin.readline()
                        if line:
                            input_queue.put(line)
                        elif line == "":
                            input_queue.put(None)  # EOF
                            break
                    except Exception as e:
                        logger.error(f"Stdin error: {e}")
                        input_queue.put(None)
                        break
            except Exception as e:
                logger.error(f"Stdin reader error: {e}")
                input_queue.put(None)

        # Start reader thread
        reader = threading.Thread(target=stdin_reader, daemon=True)
        reader.start()

        try:
            while True:
                try:
                    # Get input with timeout
                    try:
                        line = await asyncio.get_event_loop().run_in_executor(
                            None, lambda: input_queue.get(timeout=0.1)
                        )
                    except queue.Empty:
                        continue

                    if line is None:
                        break  # EOF

                    line = line.strip()
                    if not line:
                        continue

                    message = json.loads(line)
                    response = await self.handle_message(message)

                    if response:
                        sys.stdout.write(json.dumps(response) + "\n")
                        sys.stdout.flush()

                except json.JSONDecodeError as e:
                    logger.debug(f"JSON decode error: {e}")
                except Exception as e:
                    logger.error(f"Server error: {e}")
                    break

        finally:
            stop_event.set()
            await self.bridge.disconnect()


async def run_server():
    """Main entry point for running the MCP server."""
    load_dotenv()
    config = MCPConfig.from_env()
    setup_logging(config)

    server = MCPServer(config)
    await server.run_stdio()


def main():
    """CLI entry point."""
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logging.error(f"Server error: {e}")
        sys.exit(1)

"""Tests for MCP server wrapper."""

import pytest
from regennexus_mcp.server import MCPServer
from regennexus_mcp.config import MCPConfig, ConnectionMode


@pytest.fixture
def config():
    """Create test config."""
    return MCPConfig(mode=ConnectionMode.LOCAL)


def test_server_creation(config):
    """Test server can be created."""
    server = MCPServer(config)
    assert server is not None
    assert server.config == config


def test_config_from_env():
    """Test config loads from environment."""
    config = MCPConfig.from_env()
    assert config.mode == ConnectionMode.AUTO  # Default


def test_connection_modes():
    """Test connection mode enum."""
    assert ConnectionMode.AUTO.value == "auto"
    assert ConnectionMode.LOCAL.value == "local"
    assert ConnectionMode.REMOTE.value == "remote"


@pytest.mark.asyncio
async def test_handle_message_without_init(config):
    """Test handling message before UAP init returns error."""
    server = MCPServer(config)
    # Don't initialize - should return error

    response = await server.handle_message({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list",
        "params": {}
    })

    assert response["id"] == 1
    assert "error" in response
    assert response["error"]["code"] == -32603


@pytest.mark.asyncio
async def test_notification_no_response(config):
    """Test notifications don't get responses."""
    server = MCPServer(config)

    response = await server.handle_message({
        "jsonrpc": "2.0",
        "method": "notifications/initialized",
        "params": {}
    })

    # Notifications should return None (no response)
    assert response is None

#!/usr/bin/env python3
"""
Tests for the MCP (Model Context Protocol) client module
"""

import os
import sys
import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from davincimcp.utils.config import Config
from davincimcp.core.resolve_controller import ResolveController
from davincimcp.core.mcp.mcp_client import MCPClient


class TestMCPClient:
    """Tests for the MCPClient class"""

    def test_initialization(self):
        """Test basic initialization of MCPClient"""
        # Mock config
        config = MagicMock(spec=Config)
        config.get.side_effect = lambda key, default=None: {
            "mcp_enabled": True,
        }.get(key, default)
        config.anthropic_api_key = "test_key"
        
        # Mock imports
        with patch("davincimcp.core.mcp.mcp_client.Anthropic") as mock_anthropic:
            # Initialize client
            client = MCPClient(config)
            
            assert client.enabled is True
            assert client.initialized is False
            assert client.exit_stack is None
            assert client.session is None
            
            # Check Anthropic client initialized with key
            mock_anthropic.assert_called_once_with(api_key="test_key")
    
    def test_initialization_disabled(self):
        """Test initialization with MCP disabled"""
        # Mock config
        config = MagicMock(spec=Config)
        config.get.side_effect = lambda key, default=None: {
            "mcp_enabled": False,
        }.get(key, default)
        
        client = MCPClient(config)
        
        assert client.enabled is False
        assert client.initialized is False
    
    def test_initialization_no_api_key(self):
        """Test initialization without API key"""
        # Mock config
        config = MagicMock(spec=Config)
        config.get.side_effect = lambda key, default=None: {
            "mcp_enabled": True,
        }.get(key, default)
        config.anthropic_api_key = None
        
        # Mock imports
        with patch("davincimcp.core.mcp.mcp_client.Anthropic") as mock_anthropic:
            # Initialize client
            client = MCPClient(config)
            
            assert client.enabled is True
            assert client.anthropic is None
            mock_anthropic.assert_not_called()
    
    def test_get_script_type(self):
        """Test script type detection"""
        # Mock config
        config = MagicMock(spec=Config)
        config.get.return_value = False  # Disable MCP to avoid import errors
        
        client = MCPClient(config)
        
        # Test Python files
        assert client._get_script_type("script.py") == "python"
        assert client._get_script_type("script.pyw") == "python"
        
        # Test Node.js files
        assert client._get_script_type("script.js") == "node"
        assert client._get_script_type("script.mjs") == "node"
        
        # Test unknown extension
        with patch("builtins.open", MagicMock(side_effect=Exception())):
            assert client._get_script_type("script.txt") is None
    
    @pytest.mark.asyncio
    async def test_connect_to_server(self):
        """Test connecting to an MCP server"""
        # Mock config
        config = MagicMock(spec=Config)
        config.get.side_effect = lambda key, default=None: {
            "mcp_enabled": True,
        }.get(key, default)
        config.anthropic_api_key = "test_key"
        
        # Mock imports and server connection
        with patch("davincimcp.core.mcp.mcp_client.Anthropic") as mock_anthropic, \
             patch("davincimcp.core.mcp.mcp_client.StdioServerParameters") as mock_params, \
             patch("davincimcp.core.mcp.mcp_client.stdio_client") as mock_stdio, \
             patch("davincimcp.core.mcp.mcp_client.ClientSession") as mock_session, \
             patch.object(MCPClient, "_get_script_type", return_value="python"):
            
            # Mock anthropic client
            mock_anthropic_instance = MagicMock()
            mock_anthropic.return_value = mock_anthropic_instance
            
            # Mock connection
            mock_connection = MagicMock()
            mock_context_manager = MagicMock()
            mock_context_manager.__aenter__ = AsyncMock(return_value=mock_connection)
            mock_context_manager.__aexit__ = AsyncMock(return_value=False)
            mock_stdio.return_value = mock_context_manager
            
            # Mock session
            mock_session_instance = MagicMock()
            mock_session_instance.initialize = AsyncMock()
            mock_session_instance.list_resources = AsyncMock(return_value=[])
            mock_session_instance.list_tools = AsyncMock(return_value=[])
            mock_session_instance.capabilities = ["tools"]
            mock_session.return_value = mock_session_instance
            
            # Initialize client
            client = MCPClient(config)
            client.anthropic = mock_anthropic_instance
            
            # Connect to server
            result = await client.connect_to_server("/path/to/server.py")
            
            assert result is True
            assert client.initialized is True
            assert client.session is mock_session_instance
            mock_session_instance.initialize.assert_called_once()
            mock_session_instance.list_resources.assert_called_once()
            mock_session_instance.list_tools.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_connect_to_server_disabled(self):
        """Test connecting to server when MCP is disabled"""
        # Mock config
        config = MagicMock(spec=Config)
        config.get.side_effect = lambda key, default=None: {
            "mcp_enabled": False,
        }.get(key, default)
        
        client = MCPClient(config)
        
        result = await client.connect_to_server("/path/to/server.py")
        
        assert result is False
        assert client.initialized is False
    
    @pytest.mark.asyncio
    async def test_connect_to_server_no_anthropic(self):
        """Test connecting to server without Anthropic client"""
        # Mock config
        config = MagicMock(spec=Config)
        config.get.side_effect = lambda key, default=None: {
            "mcp_enabled": True,
        }.get(key, default)
        
        client = MCPClient(config)
        client.anthropic = None
        
        result = await client.connect_to_server("/path/to/server.py")
        
        assert result is False
        assert client.initialized is False
    
    @pytest.mark.asyncio
    async def test_disconnect(self):
        """Test disconnecting from an MCP server"""
        # Mock config
        config = MagicMock(spec=Config)
        config.get.return_value = False  # Disable MCP to avoid import errors
        
        client = MCPClient(config)
        client.initialized = True
        client.exit_stack = MagicMock()
        client.exit_stack.aclose = AsyncMock()
        
        result = await client.disconnect()
        
        assert result is True
        assert client.initialized is False
        assert client.exit_stack is None
        assert client.session is None
        client.exit_stack.aclose.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_query(self):
        """Test processing a query with MCP"""
        # Mock config
        config = MagicMock(spec=Config)
        config.get.side_effect = lambda key, default=None: {
            "mcp_enabled": True,
        }.get(key, default)
        
        # Mock session and Anthropic
        with patch("davincimcp.core.mcp.mcp_client.Anthropic"):
            client = MCPClient(config)
            client.initialized = True
            client.session = MagicMock()
            
            # Mock Anthropic message response
            mock_message = MagicMock()
            mock_message.content = [MagicMock(text="Test response")]
            
            # Mock Anthropic client
            client.anthropic = MagicMock()
            client.anthropic.messages.create = AsyncMock(return_value=mock_message)
            
            # Process query
            result = await client.process_query("Test query")
            
            assert result == "Test response"
            client.anthropic.messages.create.assert_called_once_with(
                model="claude-3-sonnet-20240229",
                max_tokens=1024,
                system="You are an AI assistant that helps with video editing in DaVinci Resolve.",
                messages=[
                    {"role": "user", "content": "Test query"}
                ]
            )
    
    @pytest.mark.asyncio
    async def test_process_query_not_initialized(self):
        """Test processing a query when not connected to a server"""
        # Mock config
        config = MagicMock(spec=Config)
        config.get.return_value = False  # Disable MCP to avoid import errors
        
        client = MCPClient(config)
        client.initialized = False
        
        result = await client.process_query("Test query")
        
        assert "Error: Not connected to MCP server" in result
    
    @pytest.mark.asyncio
    async def test_process_query_no_anthropic(self):
        """Test processing a query without Anthropic client"""
        # Mock config
        config = MagicMock(spec=Config)
        config.get.return_value = False  # Disable MCP to avoid import errors
        
        client = MCPClient(config)
        client.initialized = True
        client.session = MagicMock()
        client.anthropic = None
        
        result = await client.process_query("Test query")
        
        assert "Error: Anthropic client not initialized" in result 
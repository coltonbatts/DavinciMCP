#!/usr/bin/env python3
"""
Tests for the MCP (Model Context Protocol) handler module
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
from davincimcp.core.mcp.mcp_handler import MCPHandler


class TestMCPHandler:
    """Tests for the MCPHandler class"""

    def test_initialization(self):
        """Test basic initialization of MCPHandler"""
        # Mock config
        config = MagicMock(spec=Config)
        config.get.side_effect = lambda key, default=None: {
            "mcp_enabled": True,
            "mcp_server_script": "/path/to/server.py",
            "mcp_server_capabilities": ["resources", "tools"]
        }.get(key, default)
        
        handler = MCPHandler(config)
        
        assert handler.enabled is True
        assert handler.server_script == "/path/to/server.py"
        assert handler.server_capabilities == ["resources", "tools"]
        assert handler.server_process is None
        assert handler.initialized is False
    
    def test_initialization_disabled(self):
        """Test initialization with MCP disabled"""
        # Mock config
        config = MagicMock(spec=Config)
        config.get.side_effect = lambda key, default=None: {
            "mcp_enabled": False,
            "mcp_server_script": "/path/to/server.py",
            "mcp_server_capabilities": ["resources", "tools"]
        }.get(key, default)
        
        handler = MCPHandler(config)
        
        assert handler.enabled is False
        assert handler.server_script == "/path/to/server.py"
        assert handler.server_capabilities == ["resources", "tools"]
    
    def test_get_script_type_python(self):
        """Test script type detection for Python files"""
        config = MagicMock(spec=Config)
        handler = MCPHandler(config)
        
        # Test Python file extensions
        with patch("pathlib.Path") as mock_path:
            mock_path.return_value.suffix = ".py"
            result = handler._get_script_type(mock_path.return_value)
            assert result == "python"
            
            mock_path.return_value.suffix = ".pyw"
            result = handler._get_script_type(mock_path.return_value)
            assert result == "python"
    
    def test_get_script_type_node(self):
        """Test script type detection for Node.js files"""
        config = MagicMock(spec=Config)
        handler = MCPHandler(config)
        
        # Test Node.js file extensions
        with patch("pathlib.Path") as mock_path:
            mock_path.return_value.suffix = ".js"
            result = handler._get_script_type(mock_path.return_value)
            assert result == "node"
            
            mock_path.return_value.suffix = ".mjs"
            result = handler._get_script_type(mock_path.return_value)
            assert result == "node"
    
    def test_get_script_type_shebang(self):
        """Test script type detection using shebang"""
        config = MagicMock(spec=Config)
        handler = MCPHandler(config)
        
        # Use a path for mocking
        mock_path = Path("test_script.ext")
        
        # Mock the open function to return a file-like object with shebang
        python_shebang = "#!/usr/bin/env python3\n"
        node_shebang = "#!/usr/bin/env node\n"
        
        # Test Python shebang
        with patch("builtins.open", MagicMock(return_value=MagicMock(__enter__=lambda x: MagicMock(readline=lambda: python_shebang)))):
            result = handler._get_script_type(mock_path)
            assert result == "python"
        
        # Test Node.js shebang
        with patch("builtins.open", MagicMock(return_value=MagicMock(__enter__=lambda x: MagicMock(readline=lambda: node_shebang)))):
            result = handler._get_script_type(mock_path)
            assert result == "node"
    
    def test_get_script_type_unknown(self):
        """Test script type detection for unknown file types"""
        config = MagicMock(spec=Config)
        handler = MCPHandler(config)
        
        # Test unknown extension
        with patch("pathlib.Path") as mock_path:
            mock_path.return_value.suffix = ".txt"
            
            # Mock the open function to return a file-like object without a shebang
            with patch("builtins.open", MagicMock(return_value=MagicMock(__enter__=lambda x: MagicMock(readline=lambda: "Not a shebang")))):
                result = handler._get_script_type(mock_path.return_value)
                assert result is None
    
    @pytest.mark.asyncio
    async def test_start_server(self):
        """Test starting the MCP server"""
        # Mock config
        config = MagicMock(spec=Config)
        config.get.side_effect = lambda key, default=None: {
            "mcp_enabled": True,
            "mcp_server_script": "/path/to/server.py",
            "mcp_server_capabilities": ["resources", "tools"]
        }.get(key, default)
        
        handler = MCPHandler(config)
        
        # Mock path exists
        with patch("pathlib.Path") as mock_path, \
             patch("os.path.exists", return_value=True), \
             patch.object(handler, "_get_script_type", return_value="python"), \
             patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_create_process:
                
            mock_path.return_value.exists.return_value = True
            mock_process = MagicMock()
            mock_process.pid = 12345
            mock_create_process.return_value = mock_process
            
            result = await handler.start_server()
            
            assert result is True
            assert handler.initialized is True
            assert handler.server_process is mock_process
            mock_create_process.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_start_server_disabled(self):
        """Test starting the server when MCP is disabled"""
        # Mock config
        config = MagicMock(spec=Config)
        config.get.side_effect = lambda key, default=None: {
            "mcp_enabled": False,
            "mcp_server_script": "/path/to/server.py",
            "mcp_server_capabilities": ["resources", "tools"]
        }.get(key, default)
        
        handler = MCPHandler(config)
        
        result = await handler.start_server()
        
        assert result is False
        assert handler.initialized is False
    
    @pytest.mark.asyncio
    async def test_stop_server(self):
        """Test stopping the MCP server"""
        # Mock config
        config = MagicMock(spec=Config)
        handler = MCPHandler(config)
        
        # Mock server process
        mock_process = MagicMock()
        mock_process.wait = AsyncMock()
        mock_process.terminate = MagicMock()
        mock_process.pid = 12345
        handler.server_process = mock_process
        handler.initialized = True
        
        result = await handler.stop_server()
        
        assert result is True
        assert handler.server_process is None
        assert handler.initialized is False
        mock_process.terminate.assert_called_once()
        mock_process.wait.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_stop_server_timeout(self):
        """Test stopping the server with timeout"""
        # Mock config
        config = MagicMock(spec=Config)
        handler = MCPHandler(config)
        
        # Mock server process
        mock_process = MagicMock()
        mock_process.wait = AsyncMock(side_effect=asyncio.TimeoutError())
        mock_process.terminate = MagicMock()
        mock_process.kill = MagicMock()
        mock_process.pid = 12345
        handler.server_process = mock_process
        handler.initialized = True
        
        result = await handler.stop_server()
        
        assert result is True
        assert handler.server_process is None
        assert handler.initialized is False
        mock_process.terminate.assert_called_once()
        mock_process.kill.assert_called_once()
    
    def test_is_running(self):
        """Test is_running method"""
        # Mock config
        config = MagicMock(spec=Config)
        handler = MCPHandler(config)
        
        # No process
        assert handler.is_running() is False
        
        # Running process
        mock_process = MagicMock()
        mock_process.returncode = None
        handler.server_process = mock_process
        
        assert handler.is_running() is True
        
        # Stopped process
        mock_process.returncode = 0
        assert handler.is_running() is False
    
    def test_get_capabilities(self):
        """Test get_capabilities method"""
        # Mock config
        config = MagicMock(spec=Config)
        config.get.side_effect = lambda key, default=None: {
            "mcp_enabled": True,
            "mcp_server_script": "/path/to/server.py",
            "mcp_server_capabilities": ["resources", "tools"]
        }.get(key, default)
        
        handler = MCPHandler(config)
        
        capabilities = handler.get_capabilities()
        assert capabilities == ["resources", "tools"] 
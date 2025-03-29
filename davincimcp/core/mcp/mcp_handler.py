#!/usr/bin/env python3
"""
mcp_handler.py - Model Context Protocol (MCP) Handler

This module provides the MCPHandler class for managing Model Context Protocol
interactions and server management.
"""

import os
import sys
import logging
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple, Union

from davincimcp.utils.config import Config
from davincimcp.utils.exceptions import ConfigError

# Logger for this module
logger = logging.getLogger(__name__)

class MCPHandler:
    """
    Handler for Model Context Protocol (MCP) operations
    
    Manages server processes and client connections for Model Context Protocol.
    """
    
    def __init__(self, config: Config):
        """
        Initialize the MCP Handler
        
        Args:
            config: Config instance with MCP settings
        """
        self.config = config
        self.enabled = config.get("mcp_enabled", False)
        self.server_script = config.get("mcp_server_script", "")
        self.server_capabilities = config.get("mcp_server_capabilities", [])
        self.server_process = None
        self.initialized = False
        
        logger.info(f"MCP Handler initialized (enabled: {self.enabled})")
        
        if self.enabled and not self.server_script:
            logger.warning("MCP is enabled but no server script is configured")
    
    async def start_server(self) -> bool:
        """
        Start the MCP server process
        
        Returns:
            bool: True if server started successfully
        """
        if not self.enabled:
            logger.warning("MCP is not enabled. Cannot start server.")
            return False
            
        if not self.server_script:
            logger.error("No MCP server script configured")
            return False
            
        # Check if server script exists
        script_path = Path(self.server_script)
        if not script_path.exists():
            logger.error(f"MCP server script does not exist: {self.server_script}")
            return False
            
        # Detect script type
        script_type = self._get_script_type(script_path)
        if not script_type:
            logger.error(f"Unsupported script type for MCP server: {script_path}")
            return False
            
        try:
            # Start server process
            logger.info(f"Starting MCP server: {script_path}")
            
            if script_type == "python":
                cmd = [sys.executable, str(script_path)]
            elif script_type == "node":
                cmd = ["node", str(script_path)]
            else:
                logger.error(f"Unsupported script type: {script_type}")
                return False
                
            # Start process with pipe communication
            self.server_process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            logger.info(f"MCP server started with PID: {self.server_process.pid}")
            self.initialized = True
            return True
            
        except Exception as e:
            logger.error(f"Error starting MCP server: {str(e)}")
            self.initialized = False
            return False
    
    async def stop_server(self) -> bool:
        """
        Stop the MCP server process
        
        Returns:
            bool: True if server stopped successfully
        """
        if not self.server_process:
            logger.warning("No MCP server process to stop")
            return False
            
        try:
            logger.info(f"Stopping MCP server (PID: {self.server_process.pid})")
            self.server_process.terminate()
            
            try:
                # Wait for process to terminate with timeout
                await asyncio.wait_for(self.server_process.wait(), timeout=5.0)
                logger.info("MCP server stopped gracefully")
            except asyncio.TimeoutError:
                # Force kill if timeout
                logger.warning("MCP server did not terminate gracefully, killing process")
                self.server_process.kill()
                await self.server_process.wait()
            
            self.server_process = None
            self.initialized = False
            return True
            
        except Exception as e:
            logger.error(f"Error stopping MCP server: {str(e)}")
            return False
    
    def _get_script_type(self, script_path: Path) -> Optional[str]:
        """
        Determine the type of script (python or node)
        
        Args:
            script_path (Path): Path to the script
            
        Returns:
            Optional[str]: 'python', 'node', or None if unknown
        """
        # Check extension
        ext = script_path.suffix.lower()
        if ext in ['.py', '.pyw']:
            return "python"
        elif ext in ['.js', '.mjs']:
            return "node"
            
        # Check for shebang
        try:
            with open(script_path, 'r') as f:
                first_line = f.readline().strip()
                if first_line.startswith('#!'):
                    if 'python' in first_line:
                        return "python"
                    elif 'node' in first_line:
                        return "node"
        except Exception:
            pass
            
        # Unknown script type
        return None
    
    def is_running(self) -> bool:
        """
        Check if the MCP server is running
        
        Returns:
            bool: True if server is running
        """
        if self.server_process is None:
            return False
            
        return self.server_process.returncode is None
    
    def get_capabilities(self) -> List[str]:
        """
        Get the configured capabilities for the MCP server
        
        Returns:
            List[str]: List of capabilities
        """
        return self.server_capabilities 
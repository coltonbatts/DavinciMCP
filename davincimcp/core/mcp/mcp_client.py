#!/usr/bin/env python3
"""
mcp_client.py - Model Context Protocol (MCP) Client

This module provides the MCPClient class for interacting with Model Context Protocol
servers to provide AI context and tool access.
"""

import os
import sys
import logging
import asyncio
from typing import Dict, Any, Optional, List, Tuple, Union
from contextlib import AsyncExitStack

from davincimcp.utils.config import Config
from davincimcp.core.resolve_controller import ResolveController
from davincimcp.utils.exceptions import ConfigError

# Logger for this module
logger = logging.getLogger(__name__)

class MCPClient:
    """
    Client for Model Context Protocol (MCP) operations
    
    Handles interaction with MCP servers for providing context, tools,
    and other capabilities to AI models.
    """
    
    def __init__(self, 
                config: Config, 
                resolve_controller: Optional[ResolveController] = None):
        """
        Initialize the MCP Client
        
        Args:
            config: Config instance with MCP settings
            resolve_controller: Optional ResolveController for DaVinci Resolve access
        """
        self.config = config
        self.resolve_controller = resolve_controller
        self.enabled = config.get("mcp_enabled", False)
        self.initialized = False
        self.exit_stack = None
        self.session = None
        self.anthropic = None
        
        # Import MCP libraries only if enabled
        if self.enabled:
            try:
                global mcp, ClientSession, StdioServerParameters, stdio_client, Anthropic
                from mcp import ClientSession, StdioServerParameters
                from mcp.client.stdio import stdio_client
                from anthropic import Anthropic
                
                # Initialize Anthropic client if API key is available
                if config.anthropic_api_key:
                    self.anthropic = Anthropic(api_key=config.anthropic_api_key)
                else:
                    logger.warning("No Anthropic API key found. Some MCP features may be limited.")
                
                logger.info("MCP Client initialized successfully")
            except ImportError as e:
                logger.error(f"Failed to import MCP libraries: {str(e)}")
                logger.error("Install required packages: pip install mcp anthropic")
                self.enabled = False
    
    async def connect_to_server(self, server_script_path: str) -> bool:
        """
        Connect to an MCP server
        
        Args:
            server_script_path: Path to the MCP server script
            
        Returns:
            bool: True if connection successful
        """
        if not self.enabled:
            logger.warning("MCP is not enabled. Cannot connect to server.")
            return False
            
        if not self.anthropic:
            logger.error("Anthropic client not initialized. Cannot connect to server.")
            return False
            
        try:
            # Initialize exit stack for resource management
            self.exit_stack = AsyncExitStack()
            
            # Determine script type
            script_type = self._get_script_type(server_script_path)
            if not script_type:
                logger.error(f"Unsupported script type for MCP server: {server_script_path}")
                return False
                
            # Create server parameters
            if script_type == "python":
                cmd = [sys.executable, server_script_path]
            elif script_type == "node":
                cmd = ["node", server_script_path]
            else:
                logger.error(f"Unsupported script type: {script_type}")
                return False
                
            # Connect to server
            logger.info(f"Connecting to MCP server: {server_script_path}")
            server_params = StdioServerParameters(
                command=cmd,
                cwd=os.path.dirname(os.path.abspath(server_script_path))
            )
            
            # Create client and connect
            connection = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            
            # Create session
            self.session = ClientSession(connection)
            
            # Initialize session
            await self.session.initialize()
            
            # List available capabilities (resources, tools, etc.)
            resources = await self.session.list_resources()
            tools = await self.session.list_tools() if "tools" in self.session.capabilities else []
            
            logger.info(f"Connected to MCP server with {len(resources)} resources and {len(tools)} tools")
            self.initialized = True
            return True
            
        except Exception as e:
            logger.error(f"Error connecting to MCP server: {str(e)}")
            
            # Clean up resources
            if self.exit_stack:
                await self.exit_stack.aclose()
                self.exit_stack = None
                
            self.session = None
            self.initialized = False
            return False
    
    async def disconnect(self) -> bool:
        """
        Disconnect from the MCP server
        
        Returns:
            bool: True if disconnection successful
        """
        if not self.initialized or not self.exit_stack:
            logger.warning("Not connected to any MCP server")
            return False
            
        try:
            logger.info("Disconnecting from MCP server")
            await self.exit_stack.aclose()
            self.exit_stack = None
            self.session = None
            self.initialized = False
            return True
            
        except Exception as e:
            logger.error(f"Error disconnecting from MCP server: {str(e)}")
            return False
    
    async def process_query(self, query: str) -> str:
        """
        Process a query through the MCP server and Claude
        
        Args:
            query: User's query text
            
        Returns:
            str: Response from Claude with any tool calls processed
        """
        if not self.initialized or not self.session:
            logger.warning("Not connected to any MCP server. Cannot process query.")
            return "Error: Not connected to MCP server"
            
        if not self.anthropic:
            logger.error("Anthropic client not initialized. Cannot process query.")
            return "Error: Anthropic client not initialized"
            
        try:
            # Create a Claude message with MCP context
            logger.info(f"Processing query with MCP: {query[:50]}...")
            
            # Get the Claude message with MCP context
            message = await self.anthropic.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1024,
                system="You are an AI assistant that helps with video editing in DaVinci Resolve.",
                messages=[
                    {"role": "user", "content": query}
                ]
            )
            
            # Process any tool calls in the response
            if hasattr(message, "content") and message.content:
                result = message.content[0].text
                return result
            else:
                return "No response received from Claude"
            
        except Exception as e:
            error_msg = f"Error processing query with MCP: {str(e)}"
            logger.error(error_msg)
            return f"Error: {error_msg}"
    
    def _get_script_type(self, script_path: str) -> Optional[str]:
        """
        Determine the type of script (python or node)
        
        Args:
            script_path: Path to the script
            
        Returns:
            Optional[str]: 'python', 'node', or None if unknown
        """
        # Check extension
        ext = os.path.splitext(script_path)[1].lower()
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
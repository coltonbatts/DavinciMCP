#!/usr/bin/env python3
"""
client_example.py - Example MCP Client for DaVinci Resolve

This script demonstrates how to use the MCP client to connect to a Resolve server
and interact with it through Anthropic's Claude.
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to sys.path to import davincimcp modules
sys.path.append(str(Path(__file__).parent.parent.parent))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)
logger = logging.getLogger("resolve-mcp-client")

# Load environment variables
load_dotenv()

# Import DavinciMCP libraries
from davincimcp.utils.config import Config
from davincimcp.core.resolve_controller import ResolveController
from davincimcp.core.mcp.mcp_client import MCPClient


async def interactive_session(client: MCPClient):
    """
    Run an interactive session with the MCP client
    
    Args:
        client: Initialized MCPClient instance
    """
    print("\n===== DaVinci Resolve MCP Interactive Session =====")
    print("Type 'exit' or 'quit' to end the session.")
    print("Example commands:")
    print("- Tell me about my current project")
    print("- Cut the clip at the current position")
    print("- Add a cross dissolve transition that's 1.5 seconds")
    print("=====================================================\n")
    
    while True:
        try:
            # Get user input
            user_input = input("\nEnter a command (or 'exit' to quit): ").strip()
            
            # Check for exit command
            if user_input.lower() in ['exit', 'quit']:
                print("Exiting session...")
                break
                
            # Process query with MCP
            print("Processing...")
            response = await client.process_query(user_input)
            
            # Display response
            print("\nResponse:")
            print(response)
            
        except KeyboardInterrupt:
            print("\nSession interrupted. Exiting...")
            break
        except Exception as e:
            logger.error(f"Error during interactive session: {str(e)}")
            print(f"\nError: {str(e)}")


async def main():
    """Main entry point"""
    # Initialize configuration
    config = Config()
    
    # Check for required keys
    if not config.anthropic_api_key:
        logger.error("Anthropic API key not found. Set ANTHROPIC_API_KEY in your .env file.")
        sys.exit(1)
        
    # Initialize Resolve controller
    controller = ResolveController()
    
    # Try to connect to Resolve (optional, still works without Resolve)
    resolve_connected = controller.connect()
    if not resolve_connected:
        logger.warning("Could not connect to DaVinci Resolve. Some features will be limited.")
    
    # Initialize MCP client
    client = MCPClient(config, controller)
    
    # Get server script path - use environment variable or default example
    server_script = config.get("mcp_server_script")
    if not server_script:
        # Use the included example server
        server_script = str(Path(__file__).parent / "resolve_server.py")
        logger.info(f"No MCP server script configured, using example: {server_script}")
    
    # Connect to MCP server
    logger.info(f"Connecting to MCP server: {server_script}")
    connected = await client.connect_to_server(server_script)
    
    if not connected:
        logger.error("Failed to connect to MCP server. Exiting.")
        sys.exit(1)
    
    try:
        # Run interactive session
        await interactive_session(client)
    finally:
        # Disconnect from server
        logger.info("Disconnecting from MCP server...")
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main()) 
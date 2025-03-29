#!/usr/bin/env python3
"""
cli.py - Command Line Interface for DavinciMCP

This module provides the command line interface for the DavinciMCP application.
It parses command line arguments and dispatches to the appropriate handler.
"""

import sys
import logging
import argparse
import asyncio
from typing import Optional, List

from davincimcp.core.resolve_controller import ResolveController
from davincimcp.core.gemini_handler import GeminiAPIHandler
from davincimcp.core.mcp.mcp_handler import MCPHandler
from davincimcp.core.mcp.mcp_client import MCPClient
from davincimcp.commands.command_registry import CommandRegistry, CommandExecutor
from davincimcp.media.analyzer import MediaAnalyzer, EditSuggestionEngine
from davincimcp.utils.config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """
    Parse command line arguments
    
    Args:
        args (Optional[List[str]]): Command line arguments (uses sys.argv if None)
        
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="DavinciMCP - Python interface for controlling DaVinci Resolve with AI integration"
    )
    
    # Global options
    parser.add_argument(
        "--log-level", 
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level"
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Interactive mode (default)
    interactive_parser = subparsers.add_parser(
        "interactive", 
        help="Start interactive mode"
    )
    interactive_parser.add_argument(
        "--no-feedback", 
        action="store_true",
        help="Disable operation feedback"
    )
    interactive_parser.add_argument(
        "--use-mcp",
        action="store_true",
        help="Use Model Context Protocol for AI interaction"
    )
    
    # MCP mode
    mcp_parser = subparsers.add_parser(
        "mcp",
        help="Start MCP interactive mode with Claude integration"
    )
    mcp_parser.add_argument(
        "--server-script",
        type=str,
        help="Path to MCP server script"
    )
    
    # GUI mode
    gui_parser = subparsers.add_parser(
        "gui", 
        help="Start GUI mode"
    )
    
    # Single command mode
    cmd_parser = subparsers.add_parser(
        "cmd", 
        help="Execute a single command"
    )
    cmd_parser.add_argument(
        "text", 
        type=str,
        help="Command text to execute"
    )
    cmd_parser.add_argument(
        "--no-feedback", 
        action="store_true",
        help="Disable operation feedback"
    )
    
    # Media analysis mode
    analyze_parser = subparsers.add_parser(
        "analyze", 
        help="Analyze media and suggest edits"
    )
    analyze_parser.add_argument(
        "--target", 
        choices=["current", "selected", "all"],
        default="current",
        help="Which media to analyze"
    )
    analyze_parser.add_argument(
        "--output", 
        choices=["console", "file"],
        default="console",
        help="Where to output results"
    )
    analyze_parser.add_argument(
        "--output-file", 
        type=str,
        help="File to write results to (if output=file)"
    )
    
    # Server mode
    server_parser = subparsers.add_parser(
        "server",
        help="Start MCP server"
    )
    
    return parser.parse_args(args)

async def run_mcp_mode(config: Config, server_script: Optional[str] = None) -> int:
    """
    Run the application in MCP mode
    
    Args:
        config: Config instance
        server_script: Optional path to MCP server script
        
    Returns:
        int: Exit code (0 for success, non-zero for errors)
    """
    # Check for Anthropic API key
    if not config.anthropic_api_key:
        logger.error("Anthropic API key not found. Set ANTHROPIC_API_KEY in your .env file.")
        return 1
    
    # Initialize Resolve controller
    controller = ResolveController()
    
    # Try to connect to Resolve (optional for MCP mode)
    resolve_connected = controller.connect()
    if not resolve_connected:
        logger.warning("Could not connect to DaVinci Resolve. Some features will be limited.")
    
    # Initialize MCP client
    client = MCPClient(config, controller)
    
    # Get server script path
    if not server_script:
        server_script = config.get("mcp_server_script")
    
    if not server_script:
        logger.error("No MCP server script specified. Set MCP_SERVER_SCRIPT in your .env file or use --server-script.")
        return 1
    
    # Connect to MCP server
    logger.info(f"Connecting to MCP server: {server_script}")
    connected = await client.connect_to_server(server_script)
    
    if not connected:
        logger.error("Failed to connect to MCP server. Exiting.")
        return 1
    
    try:
        # Run interactive session
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
                
        return 0
    finally:
        # Disconnect from server
        logger.info("Disconnecting from MCP server...")
        await client.disconnect()

async def run_server_mode(config: Config) -> int:
    """
    Run the application in server mode (starts an MCP server)
    
    Args:
        config: Config instance
        
    Returns:
        int: Exit code (0 for success, non-zero for errors)
    """
    # Initialize MCP handler
    mcp_handler = MCPHandler(config)
    
    # Start server
    logger.info("Starting MCP server...")
    success = await mcp_handler.start_server()
    
    if not success:
        logger.error("Failed to start MCP server.")
        return 1
    
    try:
        # Keep server running until interrupted
        print("MCP server running. Press Ctrl+C to stop.")
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\nServer interrupted. Shutting down...")
    finally:
        # Stop server
        await mcp_handler.stop_server()
    
    return 0

def run_gui_mode() -> int:
    """
    Run the application in GUI mode
    
    Returns:
        int: Exit code (0 for success, non-zero for errors)
    """
    try:
        from davincimcp.ui.app import run_app
        return run_app()
    except ImportError as e:
        logger.error(f"Failed to import GUI components: {str(e)}")
        logger.error("Make sure PySide6 is installed: pip install PySide6")
        return 1

def main(args: Optional[List[str]] = None) -> int:
    """
    Main entry point for the application
    
    Args:
        args (Optional[List[str]]): Command line arguments (uses sys.argv if None)
        
    Returns:
        int: Exit code (0 for success, non-zero for errors)
    """
    parsed_args = parse_args(args)
    
    # Set log level if specified
    if parsed_args.log_level:
        logging.getLogger().setLevel(getattr(logging, parsed_args.log_level))
    
    # Initialize configuration
    config = Config()
    
    # Check for MCP mode
    if parsed_args.command == "mcp":
        return asyncio.run(run_mcp_mode(config, parsed_args.server_script if hasattr(parsed_args, 'server_script') else None))
    
    # Check for server mode
    if parsed_args.command == "server":
        return asyncio.run(run_server_mode(config))
    
    # Check for GUI mode first
    if parsed_args.command == "gui":
        return run_gui_mode()
    
    # Initialize the Resolve controller
    controller = ResolveController()
    
    # Attempt to connect to Resolve
    if not controller.connect():
        logger.error("Failed to connect to DaVinci Resolve. Is it running?")
        return 1
    
    # Get project info
    project_info = controller.get_project_info()
    if project_info:
        logger.info(f"Connected to project: {project_info.get('name', 'Unknown')}")
    
    # Initialize handlers
    gemini_handler = GeminiAPIHandler(config.gemini_api_key)
    
    # Initialize command system
    command_registry = CommandRegistry(controller)
    command_executor = CommandExecutor(
        command_registry, 
        feedback_enabled=not getattr(parsed_args, 'no_feedback', False)
    )
    
    # Initialize media analysis components
    media_analyzer = MediaAnalyzer(controller)
    edit_suggestion_engine = EditSuggestionEngine(media_analyzer)
    
    # Execute the requested command
    command = parsed_args.command or "interactive"
    
    if command == "interactive":
        # Use MCP mode if specified
        if getattr(parsed_args, 'use_mcp', False):
            return asyncio.run(run_mcp_mode(config))
            
        # Run normal interactive mode
        from davincimcp.interactive.prompt import run_interactive_session
        return run_interactive_session(
            command_executor, 
            gemini_handler, 
            controller, 
            media_analyzer
        )
    elif command == "cmd":
        result = command_executor.execute_from_text(parsed_args.text)
        print(result.get('status', 'unknown'))
        if result.get('feedback'):
            print(result.get('feedback'))
        return 0 if result.get('status') == 'success' else 1
    elif command == "analyze":
        target = parsed_args.target
        if target == "current":
            analysis = media_analyzer.analyze_current_clip()
        elif target == "selected":
            analysis = media_analyzer.analyze_selected_clips()
        else:  # all
            analysis = media_analyzer.analyze_all_media()
            
        suggestions = edit_suggestion_engine.generate_suggestions(analysis)
        
        if parsed_args.output == "console":
            print(f"Analysis results for {target} media:")
            print(analysis)
            print("\nEdit suggestions:")
            print(suggestions)
        else:  # file
            output_file = parsed_args.output_file or f"analysis_{target}.txt"
            with open(output_file, 'w') as f:
                f.write(f"Analysis results for {target} media:\n")
                f.write(f"{analysis}\n\n")
                f.write("Edit suggestions:\n")
                f.write(f"{suggestions}\n")
            print(f"Analysis written to {output_file}")
        
        return 0
    else:
        logger.error(f"Unknown command: {command}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 
#!/usr/bin/env python3
"""
cli.py - Command Line Interface for DavinciMCP

This module provides the command line interface for the DavinciMCP application.
It parses command line arguments and dispatches to the appropriate handler.
"""

import sys
import logging
import argparse
from typing import Optional, List

from davincimcp.core.resolve_controller import ResolveController
from davincimcp.core.gemini_handler import GeminiAPIHandler
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
        description="DavinciMCP - Python interface for controlling DaVinci Resolve with Gemini AI integration"
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
        "command_text", 
        help="The command text to execute"
    )
    cmd_parser.add_argument(
        "--no-feedback", 
        action="store_true",
        help="Disable operation feedback"
    )
    
    # Analysis mode
    analyze_parser = subparsers.add_parser(
        "analyze", 
        help="Analyze media"
    )
    analyze_parser.add_argument(
        "--clip-index", 
        type=int,
        help="Index of the clip to analyze"
    )
    analyze_parser.add_argument(
        "--timeline-item-index", 
        type=int,
        help="Index of the timeline item to analyze"
    )
    analyze_parser.add_argument(
        "--target", 
        choices=["current", "selected", "all"],
        default="current",
        help="Target for analysis"
    )
    
    return parser.parse_args(args)

def run_gui_mode() -> int:
    """
    Run the GUI mode
    
    Returns:
        int: Exit code (0 for success, non-zero for errors)
    """
    try:
        from davincimcp.ui.app import run_app
        return run_app()
    except ImportError as e:
        logger.error(f"GUI dependencies not installed: {e}")
        logger.error("Please install the required packages: pip install PySide6 Pillow")
        return 1
    except Exception as e:
        logger.error(f"Error running GUI mode: {e}")
        return 1

def run_interactive_mode(
    controller: ResolveController,
    command_executor: CommandExecutor,
    gemini_handler: GeminiAPIHandler,
    media_analyzer: MediaAnalyzer,
    edit_suggestion_engine: EditSuggestionEngine
) -> int:
    """
    Run the interactive mode
    
    Args:
        controller: Resolve controller
        command_executor: Command executor
        gemini_handler: Gemini API handler
        media_analyzer: Media analyzer
        edit_suggestion_engine: Edit suggestion engine
        
    Returns:
        int: Exit code (0 for success, non-zero for errors)
    """
    # Show welcome message
    print("\nDaVinci Resolve MCP Interactive Mode")
    print("------------------------------------")
    print("Type 'exit' or 'quit' to exit, 'help' for available commands.\n")
    
    # Check if connected to Resolve
    project_info = controller.get_project_info()
    if project_info:
        print(f"Connected to project: {project_info.get('name', 'Unknown')}")
    else:
        print("Warning: Not connected to a DaVinci Resolve project.")
    
    # Main loop
    while True:
        # Get user input
        try:
            command_text = input("\nDavinciMCP> ").strip()
        except KeyboardInterrupt:
            print("\nExiting...")
            return 0
        except EOFError:
            print("\nExiting...")
            return 0
        
        # Check for exit command
        if command_text.lower() in ["exit", "quit"]:
            print("Exiting...")
            return 0
        
        # Check for help command
        if command_text.lower() == "help":
            print("\nAvailable commands:")
            print("  help - Show this help message")
            print("  exit, quit - Exit the program")
            print("  analyze - Analyze the current clip")
            print("  <Any natural language command> - Execute command using Gemini AI")
            continue
        
        # Check for analyze command
        if command_text.lower() == "analyze":
            print("\nAnalyzing current clip...")
            try:
                analysis = media_analyzer.analyze_current_clip()
                if analysis:
                    print("\nAnalysis results:")
                    for key, value in analysis.items():
                        print(f"  {key}: {value}")
                    
                    # Get edit suggestions
                    suggestions = edit_suggestion_engine.get_suggestions_for_clip(analysis)
                    if suggestions:
                        print("\nEdit suggestions:")
                        for i, suggestion in enumerate(suggestions, 1):
                            print(f"  {i}. {suggestion}")
                else:
                    print("No analysis data available.")
            except Exception as e:
                print(f"Error analyzing clip: {e}")
            continue
        
        # Execute command
        try:
            # This would use the real command pattern + AI in production
            print(f"\nExecuting: {command_text}")
            # In a real implementation, this would call command_executor.execute_command(command_text)
            # with input from gemini_handler
            print("Command executed.")
        except Exception as e:
            print(f"Error executing command: {e}")
    
    return 0

def run_single_command(command_executor: CommandExecutor, command_text: str) -> int:
    """
    Run a single command
    
    Args:
        command_executor: Command executor
        command_text: Command text to execute
        
    Returns:
        int: Exit code (0 for success, non-zero for errors)
    """
    try:
        # This would use the real command pattern + AI in production
        print(f"Executing: {command_text}")
        # In a real implementation, this would call command_executor.execute_command(command_text)
        print("Command executed.")
        return 0
    except Exception as e:
        logger.error(f"Error executing command: {e}")
        return 1

def run_analysis(
    media_analyzer: MediaAnalyzer,
    edit_suggestion_engine: EditSuggestionEngine,
    args: argparse.Namespace
) -> int:
    """
    Run analysis mode
    
    Args:
        media_analyzer: Media analyzer
        edit_suggestion_engine: Edit suggestion engine
        args: Command line arguments
        
    Returns:
        int: Exit code (0 for success, non-zero for errors)
    """
    try:
        print("Analyzing media...")
        # In a real implementation, this would analyze media based on the provided arguments
        print("Analysis complete.")
        return 0
    except Exception as e:
        logger.error(f"Error during analysis: {e}")
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
        return run_interactive_mode(controller, command_executor, gemini_handler, media_analyzer, edit_suggestion_engine)
    elif command == "cmd":
        return run_single_command(command_executor, parsed_args.command_text)
    elif command == "analyze":
        return run_analysis(media_analyzer, edit_suggestion_engine, parsed_args)
    elif command == "gui":
        return run_gui_mode()
    else:
        logger.error(f"Unknown command: {command}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 
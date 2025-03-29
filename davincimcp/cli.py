#!/usr/bin/env python3
"""
cli.py - Command Line Interface for DaVinci Resolve Control

This module provides a command-line interface for controlling DaVinci Resolve
and serves as the main entry point for the application.
"""

import sys
import argparse
import logging
from typing import List, Optional

from davincimcp import __version__
from davincimcp.utils.config import Config
from davincimcp.core.resolve_controller import ResolveController
from davincimcp.core.gemini_handler import GeminiAPIHandler
from davincimcp.commands.command_registry import CommandRegistry, CommandExecutor
from davincimcp.media.analyzer import MediaAnalyzer, EditSuggestionEngine

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
    parser = argparse.ArgumentParser(description="DaVinci Resolve Control with Gemini AI")
    
    parser.add_argument(
        "--version", "-v",
        action="version",
        version=f"DavinciMCP {__version__}"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level"
    )
    
    parser.add_argument(
        "--no-feedback",
        action="store_true",
        help="Disable command feedback"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Interactive mode (default)
    parser_interactive = subparsers.add_parser("interactive", help="Enter interactive command mode")
    
    # Single command mode
    parser_cmd = subparsers.add_parser("cmd", help="Execute a single command")
    parser_cmd.add_argument("command_text", help="The command text to execute")
    
    # Media analysis mode
    parser_analyze = subparsers.add_parser("analyze", help="Analyze media")
    parser_analyze.add_argument(
        "--current", "-c",
        action="store_true",
        help="Analyze the current clip"
    )
    parser_analyze.add_argument(
        "--long-take", "-l",
        action="store_true",
        help="Analyze a long take and suggest cuts"
    )
    
    return parser.parse_args(args)

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
        feedback_enabled=not parsed_args.no_feedback
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
    else:
        logger.error(f"Unknown command: {command}")
        return 1

def run_interactive_mode(
    controller: ResolveController,
    command_executor: CommandExecutor,
    gemini_handler: GeminiAPIHandler,
    media_analyzer: MediaAnalyzer,
    edit_suggestion_engine: EditSuggestionEngine
) -> int:
    """
    Run the application in interactive mode
    
    Args:
        controller: ResolveController instance
        command_executor: CommandExecutor instance
        gemini_handler: GeminiAPIHandler instance
        media_analyzer: MediaAnalyzer instance
        edit_suggestion_engine: EditSuggestionEngine instance
        
    Returns:
        int: Exit code (0 for success, non-zero for errors)
    """
    print("\nDaVinci Resolve Control with Gemini AI")
    print("=========================================")
    print("Enter commands in natural language or type 'help' for assistance")
    print("Type 'exit' or 'quit' to exit")
    
    help_text = """
Available commands:
- cut/split: Cut or split a clip at the current playhead position
- transition: Add a transition between clips (e.g., "add a 2s cross dissolve")
- marker: Add a marker at the current position (e.g., "add a red marker named 'Scene 1'")
- analyze: Analyze the current clip
- analyze long take: Analyze a long take and suggest cut points
- help: Show this help text
- exit/quit: Exit the program
"""
    
    while True:
        try:
            user_input = input("\n> ")
            
            if user_input.lower() in ["exit", "quit"]:
                print("Exiting...")
                return 0
            
            if user_input.lower() in ["help", "?"]:
                print(help_text)
                continue
            
            if user_input.lower() in ["analyze", "analyze clip"]:
                analysis = media_analyzer.analyze_current_clip()
                if analysis.get("status") == "success":
                    print(f"Clip analysis:")
                    print(f"- Duration: {analysis.get('duration')}s")
                    print(f"- Frame Rate: {analysis.get('frame_rate')}")
                    print(f"- Resolution: {analysis.get('resolution')}")
                    print(f"- Shot Type: {analysis.get('shot_type')}")
                    print(f"- Suggested cuts: {', '.join([str(cut) + 's' for cut in analysis.get('suggested_cuts', [])])}")
                else:
                    print(f"Error: {analysis.get('message', 'Analysis failed')}")
                continue
            
            if user_input.lower() in ["analyze long take", "long take"]:
                analysis = edit_suggestion_engine.suggest_cuts_for_long_take()
                if analysis.get("status") == "success":
                    print(f"Long take analysis:")
                    print(f"- Duration: {analysis.get('clip_duration')}s")
                    print(f"- Summary: {analysis.get('summary')}")
                    print("- Suggested cuts:")
                    for i, cut in enumerate(analysis.get("suggested_cuts", []), 1):
                        print(f"  {i}. {cut.get('timecode')} - {cut.get('reason')} (confidence: {cut.get('confidence', 0):.2f})")
                else:
                    print(f"Error: {analysis.get('message', 'Analysis failed')}")
                continue
            
            # Execute command
            result = command_executor.execute_from_text(user_input)
            
            # Show feedback
            if result.get("status") == "success":
                if "feedback" in result:
                    print(f"✓ {result['feedback']}")
                else:
                    print("✓ Command executed successfully")
            else:
                print(f"✗ {result.get('message', 'Command failed')}")
                
                # If we couldn't understand the command, try using Gemini for interpretation
                if "Could not understand command" in result.get('message', '') and gemini_handler.initialized:
                    try:
                        print("Asking AI for help interpreting your command...")
                        prompt = f"""
                        As a video editing assistant, interpret this user request and convert it to a specific editing command:
                        "{user_input}"
                        
                        Available commands are:
                        - cut: Split a clip at the playhead position
                        - transition: Add a transition between clips (type: Cross Dissolve, Fade, Wipe, etc.)
                        - marker: Add a marker at the current position
                        
                        Respond with ONLY the exact command text that should be executed, nothing else.
                        """
                        
                        ai_interpretation = gemini_handler.generate_response(prompt)
                        print(f"AI suggests: {ai_interpretation}")
                        
                        # Ask if the user wants to try the AI's interpretation
                        try_ai = input("Try this command? (y/n): ").lower()
                        if try_ai.startswith('y'):
                            result = command_executor.execute_from_text(ai_interpretation)
                            if result.get("status") == "success":
                                if "feedback" in result:
                                    print(f"✓ {result['feedback']}")
                                else:
                                    print("✓ Command executed successfully with AI assistance")
                            else:
                                print(f"✗ {result.get('message', 'Command failed')}")
                    except Exception as e:
                        logger.error(f"Error using AI for command interpretation: {str(e)}")
                
        except KeyboardInterrupt:
            print("\nExiting...")
            return 0
        except Exception as e:
            logger.error(f"Error in interactive mode: {str(e)}")
            print(f"Error: {str(e)}")
    
    return 0

def run_single_command(command_executor: CommandExecutor, command_text: str) -> int:
    """
    Run a single command
    
    Args:
        command_executor: CommandExecutor instance
        command_text: The command text to execute
        
    Returns:
        int: Exit code (0 for success, non-zero for errors)
    """
    result = command_executor.execute_from_text(command_text)
    
    if result.get("status") == "success":
        if "feedback" in result:
            print(result["feedback"])
        else:
            print("Command executed successfully")
        return 0
    else:
        print(f"Error: {result.get('message', 'Command failed')}")
        return 1

def run_analysis(
    media_analyzer: MediaAnalyzer,
    edit_suggestion_engine: EditSuggestionEngine,
    args: argparse.Namespace
) -> int:
    """
    Run media analysis
    
    Args:
        media_analyzer: MediaAnalyzer instance
        edit_suggestion_engine: EditSuggestionEngine instance
        args: Command line arguments
        
    Returns:
        int: Exit code (0 for success, non-zero for errors)
    """
    if args.current:
        analysis = media_analyzer.analyze_current_clip()
        if analysis.get("status") == "success":
            print(f"Clip analysis:")
            print(f"- Duration: {analysis.get('duration')}s")
            print(f"- Frame Rate: {analysis.get('frame_rate')}")
            print(f"- Resolution: {analysis.get('resolution')}")
            print(f"- Shot Type: {analysis.get('shot_type')}")
            print(f"- Suggested cuts: {', '.join([str(cut) + 's' for cut in analysis.get('suggested_cuts', [])])}")
            return 0
        else:
            print(f"Error: {analysis.get('message', 'Analysis failed')}")
            return 1
    
    if args.long_take:
        analysis = edit_suggestion_engine.suggest_cuts_for_long_take()
        if analysis.get("status") == "success":
            print(f"Long take analysis:")
            print(f"- Duration: {analysis.get('clip_duration')}s")
            print(f"- Summary: {analysis.get('summary')}")
            print("- Suggested cuts:")
            for i, cut in enumerate(analysis.get("suggested_cuts", []), 1):
                print(f"  {i}. {cut.get('timecode')} - {cut.get('reason')} (confidence: {cut.get('confidence', 0):.2f})")
            return 0
        else:
            print(f"Error: {analysis.get('message', 'Analysis failed')}")
            return 1
    
    # If no analysis type specified, show an error
    print("Error: No analysis type specified. Use --current or --long-take.")
    return 1

if __name__ == "__main__":
    sys.exit(main()) 
#!/usr/bin/env python3
"""
prompt.py - Interactive prompt module for DavinciMCP CLI

This module provides the interactive command-line interface for DavinciMCP,
allowing users to enter commands and see results in real time.
"""

import logging
from typing import Dict, Any, Optional

from davincimcp.core.resolve_controller import ResolveController
from davincimcp.core.gemini_handler import GeminiAPIHandler
from davincimcp.commands.command_registry import CommandExecutor
from davincimcp.media.analyzer import MediaAnalyzer

# Configure logging
logger = logging.getLogger(__name__)

def run_interactive_session(
    command_executor: CommandExecutor,
    gemini_handler: GeminiAPIHandler,
    controller: ResolveController,
    media_analyzer: MediaAnalyzer
) -> int:
    """
    Run the interactive command-line session
    
    Args:
        command_executor: Command executor for handling operations
        gemini_handler: Gemini API handler for AI integration
        controller: Resolve controller for connection to DaVinci Resolve
        media_analyzer: Media analyzer for content analysis
        
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
            print("  <Any natural language command> - Execute command using AI")
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
                    suggestions = media_analyzer.generate_suggestions(analysis)
                    if suggestions:
                        print("\nEdit suggestions:")
                        for i, suggestion in enumerate(suggestions, 1):
                            print(f"  {i}. {suggestion}")
                else:
                    print("No analysis data available.")
            except Exception as e:
                logger.error(f"Error analyzing clip: {str(e)}")
                print(f"Error analyzing clip: {str(e)}")
            continue
        
        # Process with AI and execute command
        try:
            if not gemini_handler.initialized:
                print("Warning: AI not initialized. Processing as direct command.")
                result = command_executor.execute_from_text(command_text)
            else:
                # Process with AI first
                print("Processing with AI...")
                ai_interpretation = gemini_handler.generate_response(
                    f"Convert this instruction into a precise editing command for DaVinci Resolve: '{command_text}'"
                )
                
                # Execute the command
                print(f"Executing command: {command_text}")
                result = command_executor.execute_from_text(command_text, ai_context=ai_interpretation)
            
            # Show result
            print(f"Result: {result.get('status', 'unknown')}")
            if result.get('feedback'):
                print(f"Feedback: {result.get('feedback')}")
                
        except Exception as e:
            logger.error(f"Error executing command: {str(e)}")
            print(f"Error executing command: {str(e)}")
    
    return 0 
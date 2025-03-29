#!/usr/bin/env python3
"""
Basic Editing Example

This example demonstrates how to use DavinciMCP for basic editing operations:
1. Connecting to DaVinci Resolve
2. Setting up a command executor
3. Executing basic editing commands (cut, transition)
"""

import os
import sys
import logging
from pathlib import Path

# Add parent directory to path to import DavinciMCP modules
sys.path.append(str(Path(__file__).parent.parent))

from config import Config
from resolve_control import ResolveController
from command_pattern import CommandRegistry, CommandExecutor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """
    Main function to demonstrate basic editing capabilities
    """
    logger.info("Starting Basic Editing Example")
    
    # Initialize configuration
    config = Config()
    
    # Connect to DaVinci Resolve
    controller = ResolveController()
    if not controller.connect():
        logger.error("Failed to connect to DaVinci Resolve. Is it running?")
        sys.exit(1)
    
    # Set up command system
    command_registry = CommandRegistry(controller)
    command_executor = CommandExecutor(
        command_registry, 
        feedback_enabled=True
    )
    
    # Get project info
    project_info = controller.get_project_info()
    if project_info:
        logger.info(f"Connected to project: {project_info.get('name')}")
        logger.info(f"Timeline count: {project_info.get('timeline_count')}")
    
    # Example 1: Execute a cut command
    print("\nExample 1: Executing a cut at the current playhead position")
    result = command_executor.execute_from_text("cut at current position")
    print(f"Result: {result.get('status')}")
    if result.get('feedback'):
        print(f"Feedback: {result.get('feedback')}")
    
    # Example 2: Add a transition
    print("\nExample 2: Adding a cross dissolve transition")
    result = command_executor.execute_from_text("add a cross dissolve transition that's 1.5 seconds")
    print(f"Result: {result.get('status')}")
    if result.get('feedback'):
        print(f"Feedback: {result.get('feedback')}")
    
    # Example 3: Try an invalid command
    print("\nExample 3: Trying an invalid command")
    result = command_executor.execute_from_text("do something impossible")
    print(f"Result: {result.get('status')}")
    if result.get('message'):
        print(f"Message: {result.get('message')}")
    
    logger.info("Basic Editing Example completed")

if __name__ == "__main__":
    main() 
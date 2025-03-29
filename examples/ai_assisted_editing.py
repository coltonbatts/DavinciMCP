#!/usr/bin/env python3
"""
AI-Assisted Editing Example

This example demonstrates how to use DavinciMCP with Gemini AI for intelligent editing:
1. Connecting to Gemini API
2. Analyzing media with AI assistance
3. Using NLP for complex editing operations
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path to import DavinciMCP modules
sys.path.append(str(Path(__file__).parent.parent))

from config import Config
from resolve_control import ResolveController, GeminiAPIHandler
from command_pattern import CommandRegistry, CommandExecutor
from media_analysis import MediaAnalyzer, EditSuggestionEngine

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """
    Main function to demonstrate AI-assisted editing
    """
    logger.info("Starting AI-Assisted Editing Example")
    
    # Initialize configuration
    config = Config()
    
    # Check for Gemini API key
    if not config.gemini_api_key:
        logger.error("Gemini API key not found. Set GEMINI_API_KEY in your .env file.")
        sys.exit(1)
    
    # Connect to DaVinci Resolve
    controller = ResolveController()
    if not controller.connect():
        logger.error("Failed to connect to DaVinci Resolve. Is it running?")
        sys.exit(1)
    
    # Initialize Gemini API handler
    gemini_handler = GeminiAPIHandler(config.gemini_api_key)
    if not gemini_handler.initialized:
        logger.error("Failed to initialize Gemini API.")
        sys.exit(1)
    
    # Initialize media analysis components
    media_analyzer = MediaAnalyzer(controller)
    edit_suggestion_engine = EditSuggestionEngine(media_analyzer)
    
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
    
    # Example 1: Analyze a clip with AI
    print("\nExample 1: Analyzing current clip with AI")
    
    # Get clip analysis
    analysis = media_analyzer.analyze_current_clip()
    
    # Use Gemini to interpret the analysis
    if analysis.get("status") == "success":
        prompt = f"""
        As a video editing assistant, analyze this clip data and provide 3 specific editing suggestions:
        
        Clip Data:
        - Duration: {analysis.get('duration')}s
        - Frame Rate: {analysis.get('frame_rate')}
        - Resolution: {analysis.get('resolution')}
        - Shot Type: {analysis.get('shot_type')}
        - Brightness: {analysis.get('brightness')}
        - Movement: {analysis.get('movement')}
        
        Provide 3 specific editing suggestions based on this analysis.
        """
        
        ai_suggestions = gemini_handler.generate_response(prompt)
        print("AI Editing Suggestions:")
        print(ai_suggestions)
    
    # Example 2: Analyze a long take and suggest cuts
    print("\nExample 2: Analyzing a long take and suggesting cuts")
    
    long_take_analysis = edit_suggestion_engine.suggest_cuts_for_long_take()
    if long_take_analysis.get("status") == "success":
        # Format the cut suggestions for AI
        cuts_info = "\n".join([
            f"- Cut at {cut.get('timecode')}: {cut.get('reason')} (confidence: {cut.get('confidence'):.2f})"
            for cut in long_take_analysis.get('suggested_cuts', [])
        ])
        
        prompt = f"""
        As a professional editor, review these suggested cuts for a {long_take_analysis.get('clip_duration')}s long take:
        
        {cuts_info}
        
        Provide your professional opinion on:
        1. Which cuts should be prioritized
        2. Any potential pacing issues
        3. A recommendation for the editing approach
        Keep your response concise and focused on actionable editing advice.
        """
        
        ai_opinion = gemini_handler.generate_response(prompt)
        print("AI Professional Editing Opinion:")
        print(ai_opinion)
    
    # Example 3: Translate complex editing request to specific commands
    print("\nExample 3: Translating complex editing request to specific commands")
    
    complex_request = "Create a montage sequence from the selected clips with cross dissolves between shots"
    
    prompt = f"""
    As a video editing assistant, translate this request into a series of specific DaVinci Resolve editing commands:
    "{complex_request}"
    
    Break this down into a step-by-step sequence of simple commands that could be executed by an editing program.
    Focus on practical implementation details.
    """
    
    ai_translation = gemini_handler.generate_response(prompt)
    print("AI Command Translation:")
    print(ai_translation)
    
    logger.info("AI-Assisted Editing Example completed")

if __name__ == "__main__":
    main() 
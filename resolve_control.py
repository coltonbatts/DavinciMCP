#!/usr/bin/env python3
"""
resolve_control.py - DaVinci Resolve Control Script

This script provides an interface to control DaVinci Resolve via its Python API.
It includes connection handling, Gemini API integration, and MCP operations.

Usage:
    python resolve_control.py

Requirements:
    - DaVinci Resolve installed with Developer/Scripting/Modules available
    - Python virtual environment (recommended)
    - Configuration in .env file (see .env.example)
"""

# Version is defined in __init__.py

import sys
import os
import logging
import google.generativeai as genai
from typing import Optional, Dict, Any, Union, List

# Import local modules
from config import Config
from command_pattern import CommandRegistry, CommandExecutor
from media_analysis import MediaAnalyzer, EditSuggestionEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load configuration
config = Config()

# Add DaVinci Resolve modules path to system path
if not config.append_resolve_modules_to_path():
    logger.error("Failed to add Resolve modules path to system path")
    sys.exit(1)

try:
    import DaVinciResolveScript as bmd
    logger.info("Successfully imported DaVinciResolveScript module")
except ImportError as e:
    logger.error(f"Failed to import DaVinciResolveScript module: {e}")
    logger.error(f"Please ensure DaVinci Resolve is installed and the path is correct: {config.resolve_modules_path}")
    sys.exit(1)

class ResolveController:
    """
    Class to manage connections and operations with DaVinci Resolve
    """
    def __init__(self):
        self.resolve = None
        self.project_manager = None
        self.current_project = None
        self.connected = False

    def connect(self) -> bool:
        """
        Establish connection to DaVinci Resolve
        
        Returns:
            bool: True if connection is successful, False otherwise
        """
        try:
            # Initialize the connection to Resolve
            self.resolve = bmd.scriptapp("Resolve")
            if self.resolve is None:
                logger.error("Unable to connect to DaVinci Resolve. Is the application running?")
                return False
            
            logger.info("Successfully connected to DaVinci Resolve")
            
            # Get the Project Manager
            self.project_manager = self.resolve.GetProjectManager()
            if self.project_manager is None:
                logger.error("Unable to get Project Manager")
                return False
                
            logger.info("Successfully accessed Project Manager")
            
            # Get the current project
            self.current_project = self.project_manager.GetCurrentProject()
            if self.current_project is None:
                logger.warning("No project is currently open in DaVinci Resolve")
            else:
                project_name = self.current_project.GetName()
                logger.info(f"Current project: {project_name}")
            
            self.connected = True
            return True
            
        except Exception as e:
            logger.error(f"Error connecting to DaVinci Resolve: {str(e)}")
            self.connected = False
            return False

    def get_project_info(self) -> Dict[str, Any]:
        """
        Get information about the current project
        
        Returns:
            Dict[str, Any]: Project information
        """
        if not self.connected or self.current_project is None:
            logger.error("Not connected to Resolve or no project open")
            return {}
            
        try:
            return {
                "name": self.current_project.GetName(),
                "timeline_count": self.current_project.GetTimelineCount(),
                # Add more project info as needed
            }
        except Exception as e:
            logger.error(f"Error getting project info: {str(e)}")
            return {}
    
    def get_current_timeline(self):
        """
        Get the current timeline
        
        Returns:
            Timeline object or None if no timeline is available
        """
        if not self.connected or self.current_project is None:
            logger.error("Not connected to Resolve or no project open")
            return None
            
        try:
            timeline = self.current_project.GetCurrentTimeline()
            if timeline is None:
                logger.warning("No timeline is currently active")
            return timeline
        except Exception as e:
            logger.error(f"Error getting current timeline: {str(e)}")
            return None
    
    def get_media_pool(self):
        """
        Get the media pool
        
        Returns:
            MediaPool object or None if not available
        """
        if not self.connected or self.current_project is None:
            logger.error("Not connected to Resolve or no project open")
            return None
            
        try:
            media_pool = self.current_project.GetMediaPool()
            if media_pool is None:
                logger.warning("Unable to access Media Pool")
            return media_pool
        except Exception as e:
            logger.error(f"Error getting media pool: {str(e)}")
            return None

class GeminiAPIHandler:
    """
    Class for Gemini API operations
    Handles AI-assisted operations using Google's Generative AI
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.initialized = False
        self.model = None
        self.generation_config = None
        if api_key:
            self.initialize(api_key)
        else:
            logger.info("Gemini API Handler created but not initialized (needs API key)")
    
    def initialize(self, api_key: str) -> bool:
        """
        Initialize the Gemini API connection
        
        Args:
            api_key (str): The API key for authentication
            
        Returns:
            bool: True if initialization is successful
        """
        try:
            self.api_key = api_key
            genai.configure(api_key=self.api_key)
            
            # Set default model to Gemini Pro
            self.model = genai.GenerativeModel('gemini-pro')
            
            # Default generation config
            self.generation_config = {
                "temperature": config.get("gemini_temperature", 0.7),
                "top_p": 0.9,
                "top_k": 40,
                "max_output_tokens": config.get("gemini_max_tokens", 1024),
            }
            
            self.initialized = True
            logger.info("Gemini API successfully initialized")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini API: {str(e)}")
            self.initialized = False
            return False
    
    def generate_response(self, prompt: str) -> str:
        """
        Generate a response using the Gemini API
        
        Args:
            prompt (str): The input prompt
            
        Returns:
            str: The generated response
        """
        if not self.initialized:
            logger.warning("Gemini API not initialized")
            return "Error: API not initialized"
            
        try:
            logger.info(f"Processing prompt: {prompt[:50]}...")
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            error_msg = f"Error generating response from Gemini API: {str(e)}"
            logger.error(error_msg)
            return f"Error: {error_msg}"
    
    def generate_with_config(self, 
                           prompt: str, 
                           temperature: Optional[float] = None, 
                           max_output_tokens: Optional[int] = None) -> str:
        """
        Generate a response with custom configuration
        
        Args:
            prompt (str): The input prompt
            temperature (float, optional): Controls randomness (0.0-1.0)
            max_output_tokens (int, optional): Maximum length of response
            
        Returns:
            str: The generated response
        """
        if not self.initialized:
            logger.warning("Gemini API not initialized")
            return "Error: API not initialized"
        
        try:
            # Create a custom generation config
            generation_config = self.generation_config.copy()
            if temperature is not None:
                generation_config["temperature"] = max(0.0, min(1.0, temperature))
            if max_output_tokens is not None:
                generation_config["max_output_tokens"] = max_output_tokens
                
            logger.info(f"Processing prompt with custom config: {prompt[:50]}...")
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            return response.text
            
        except Exception as e:
            error_msg = f"Error generating response with custom config: {str(e)}"
            logger.error(error_msg)
            return f"Error: {error_msg}"
            
    def chat_session(self, messages: List[Dict[str, str]]) -> str:
        """
        Handle a multi-turn conversation with Gemini
        
        Args:
            messages (List[Dict[str, str]]): List of conversation messages
                Each message should have 'role' (user/model) and 'content' keys
                
        Returns:
            str: The response from Gemini
        """
        if not self.initialized:
            logger.warning("Gemini API not initialized")
            return "Error: API not initialized"
            
        try:
            logger.info(f"Processing chat session with {len(messages)} messages")
            
            # Convert to the format needed by Gemini API
            chat = self.model.start_chat(history=[])
            
            # Add messages
            response = None
            for msg in messages:
                if msg["role"] == "user":
                    response = chat.send_message(msg["content"])
                    
            if response:
                return response.text
            else:
                return "No response generated from chat session"
                
        except Exception as e:
            error_msg = f"Error in chat session: {str(e)}"
            logger.error(error_msg)
            return f"Error: {error_msg}"


class MCPOperationsHandler:
    """
    Handler for MCP (Media Control Protocol) operations
    This will be implemented in the future to handle specialized media control operations
    """
    
    def __init__(self, resolve_controller: ResolveController):
        self.resolve_controller = resolve_controller
        logger.info("MCP Operations Handler initialized")
    
    def execute_command(self, command: str, params: Dict[str, Any] = None) -> Union[bool, Dict[str, Any]]:
        """
        Execute an MCP command
        
        Args:
            command (str): The command to execute
            params (Dict[str, Any], optional): Command parameters
            
        Returns:
            Union[bool, Dict[str, Any]]: Result of the command execution
        """
        if params is None:
            params = {}
            
        # Placeholder for actual implementation
        logger.info(f"MCP command executed: {command}")
        return {"status": "success", "message": f"Executed {command}"}


def main():
    """
    Main function to initialize and demonstrate the Resolve connection and NLP control
    """
    logger.info("Starting DaVinci Resolve Control Script")
    
    # Initialize the Resolve controller
    controller = ResolveController()
    
    # Attempt to connect to Resolve
    if not controller.connect():
        logger.error("Failed to connect to DaVinci Resolve. Exiting.")
        sys.exit(1)
    
    # Initialize handlers and analyzers
    gemini_handler = GeminiAPIHandler(config.gemini_api_key)
    mcp_handler = MCPOperationsHandler(controller)
    
    # Initialize media analysis components
    media_analyzer = MediaAnalyzer(controller)
    edit_suggestion_engine = EditSuggestionEngine(media_analyzer)
    
    # Initialize command system
    command_registry = CommandRegistry(controller)
    command_executor = CommandExecutor(
        command_registry, 
        feedback_enabled=config.get("feedback_enabled", True)
    )
    
    # Demonstrate getting project info
    project_info = controller.get_project_info()
    if project_info:
        logger.info(f"Project info: {project_info}")
    
    # Demonstrate NLP command execution
    if gemini_handler.initialized:
        # Process user input with NLP
        print("\nEnter commands in natural language (or type 'exit' to quit):")
        
        while True:
            user_input = input("> ")
            if user_input.lower() in ['exit', 'quit']:
                break
                
            # Execute command from natural language
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
                if "Could not understand command" in result.get('message', ''):
                    try:
                        prompt = f"""
                        As a video editing assistant, interpret this user request and convert it to a specific editing command:
                        "{user_input}"
                        
                        Available commands are:
                        - cut: Split a clip at the playhead position
                        - transition: Add a transition between clips (type: Cross Dissolve, Fade, Wipe, etc.)
                        
                        Respond with ONLY the exact command text that should be executed, nothing else.
                        """
                        
                        ai_interpretation = gemini_handler.generate_response(prompt)
                        print(f"AI suggests: {ai_interpretation}")
                        
                        # Try executing the AI's interpretation
                        if ai_interpretation and len(ai_interpretation) < 100:  # Sanity check
                            print("Trying AI's interpretation...")
                            result = command_executor.execute_from_text(ai_interpretation)
                            if result.get("status") == "success":
                                if "feedback" in result:
                                    print(f"✓ {result['feedback']}")
                                else:
                                    print("✓ Command executed successfully with AI assistance")
                    except Exception as e:
                        logger.error(f"Error using AI for command interpretation: {str(e)}")
    else:
        logger.warning("Gemini API not initialized. NLP command processing unavailable.")
        print("Gemini API key not provided. Set GEMINI_API_KEY in your .env file to enable NLP commands.")
    
    # Demonstrate media analysis
    try:
        print("\nAnalyzing current clip...")
        analysis = media_analyzer.analyze_current_clip()
        if analysis.get("status") == "success":
            print(f"Clip duration: {analysis.get('duration')}s, Frame rate: {analysis.get('frame_rate')}")
            print(f"Suggested cuts at: {', '.join([str(cut) + 's' for cut in analysis.get('suggested_cuts', [])])}")
        
        # Demonstrate long take analysis
        print("\nAnalyzing long take...")
        long_take_analysis = edit_suggestion_engine.suggest_cuts_for_long_take()
        if long_take_analysis.get("status") == "success":
            print(f"Analysis summary: {long_take_analysis.get('summary')}")
            for i, cut in enumerate(long_take_analysis.get('suggested_cuts', []), 1):
                print(f"Cut {i}: {cut.get('timecode')} - {cut.get('reason')} (confidence: {cut.get('confidence', 0):.2f})")
    except Exception as e:
        logger.error(f"Error in media analysis: {str(e)}")
    
    logger.info("DaVinci Resolve Control Script completed successfully")


if __name__ == "__main__":
    main()


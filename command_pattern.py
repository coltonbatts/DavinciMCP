#!/usr/bin/env python3
"""
command_pattern.py - Command Pattern Implementation for DaVinci Resolve Control

Implements the command pattern to translate NLP intents into specific Resolve operations.
Provides a framework for adding new commands and mapping natural language to operations.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable

logger = logging.getLogger(__name__)

class Command(ABC):
    """Abstract base class for all commands"""
    
    @abstractmethod
    def execute(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute the command
        
        Args:
            params (Dict[str, Any], optional): Command parameters
            
        Returns:
            Dict[str, Any]: Result of the command execution
        """
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """
        Get a description of the command
        
        Returns:
            str: Description of the command
        """
        pass
    
    def get_feedback(self, result: Dict[str, Any]) -> str:
        """
        Get feedback about the command execution
        
        Args:
            result (Dict[str, Any]): Result of the command execution
            
        Returns:
            str: Feedback message
        """
        return f"Command executed with result: {result}"


class CutCommand(Command):
    """Command to cut/split a clip at the current playhead position"""
    
    def __init__(self, resolve_controller):
        self.resolve_controller = resolve_controller
    
    def execute(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        if params is None:
            params = {}
            
        try:
            # Implementation would use resolve_controller to perform a cut
            # Example (not actual implementation):
            # timeline = self.resolve_controller.current_project.GetCurrentTimeline()
            # timeline.Split()
            
            # Placeholder for actual implementation
            logger.info("Executing cut command")
            return {"status": "success", "message": "Cut performed at playhead position"}
        except Exception as e:
            logger.error(f"Error executing cut command: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def get_description(self) -> str:
        return "Cut/split the clip at the current playhead position"
    
    def get_feedback(self, result: Dict[str, Any]) -> str:
        if result.get("status") == "success":
            return "Cut performed at the current position"
        else:
            return f"Error performing cut: {result.get('message', 'Unknown error')}"


class AddTransitionCommand(Command):
    """Command to add a transition between clips"""
    
    def __init__(self, resolve_controller):
        self.resolve_controller = resolve_controller
    
    def execute(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        if params is None:
            params = {}
        
        transition_type = params.get("type", "Cross Dissolve")
        duration = params.get("duration", 1.0)  # seconds
        
        try:
            # Implementation would use resolve_controller to add a transition
            # Example (not actual implementation):
            # timeline = self.resolve_controller.current_project.GetCurrentTimeline()
            # timeline.AddTransition(transition_type, duration)
            
            # Placeholder for actual implementation
            logger.info(f"Adding {transition_type} transition with duration {duration}s")
            return {
                "status": "success", 
                "message": f"Added {transition_type} transition",
                "transition_type": transition_type,
                "duration": duration
            }
        except Exception as e:
            logger.error(f"Error adding transition: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def get_description(self) -> str:
        return "Add a transition between clips"
    
    def get_feedback(self, result: Dict[str, Any]) -> str:
        if result.get("status") == "success":
            return f"Added {result.get('transition_type', 'transition')} with duration {result.get('duration', '1.0')}s"
        else:
            return f"Error adding transition: {result.get('message', 'Unknown error')}"


class CommandRegistry:
    """Registry for all available commands"""
    
    def __init__(self, resolve_controller):
        self.resolve_controller = resolve_controller
        self.commands: Dict[str, Command] = {}
        self.nlp_matchers: Dict[str, List[str]] = {}
        self._register_commands()
    
    def _register_commands(self):
        """Register all available commands"""
        # Register Cut command
        cut_cmd = CutCommand(self.resolve_controller)
        self.commands["cut"] = cut_cmd
        self.nlp_matchers["cut"] = [
            "cut", "split", "slice", "divide", 
            "separate clip", "split clip", "cut clip"
        ]
        
        # Register Add Transition command
        transition_cmd = AddTransitionCommand(self.resolve_controller)
        self.commands["transition"] = transition_cmd
        self.nlp_matchers["transition"] = [
            "add transition", "transition", "dissolve", 
            "cross dissolve", "fade", "wipe"
        ]
        
        # Add more commands as needed
    
    def get_command(self, command_id: str) -> Optional[Command]:
        """
        Get a command by its ID
        
        Args:
            command_id (str): Command identifier
            
        Returns:
            Optional[Command]: The command object or None if not found
        """
        return self.commands.get(command_id)
    
    def match_nlp_intent(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Match natural language text to a command and extract parameters
        
        Args:
            text (str): Natural language text
            
        Returns:
            Optional[Dict[str, Any]]: Dictionary with command_id and params if matched
        """
        text = text.lower().strip()
        
        for command_id, phrases in self.nlp_matchers.items():
            for phrase in phrases:
                if phrase in text:
                    # Extract parameters based on the command
                    params = self._extract_params(command_id, text)
                    return {
                        "command_id": command_id,
                        "params": params
                    }
        
        return None
    
    def _extract_params(self, command_id: str, text: str) -> Dict[str, Any]:
        """
        Extract parameters from text based on the command
        
        Args:
            command_id (str): Command identifier
            text (str): Natural language text
            
        Returns:
            Dict[str, Any]: Extracted parameters
        """
        params = {}
        
        # Different extraction logic based on command type
        if command_id == "transition":
            # Extract transition type
            transition_types = {
                "cross dissolve": "Cross Dissolve",
                "fade": "Fade",
                "wipe": "Wipe",
                "push": "Push",
                "slide": "Slide"
            }
            
            for key, value in transition_types.items():
                if key in text:
                    params["type"] = value
                    break
            
            # Extract duration
            import re
            duration_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:s|sec|second)', text)
            if duration_match:
                params["duration"] = float(duration_match.group(1))
        
        # Add more parameter extraction for other commands
        
        return params


class CommandExecutor:
    """Executes commands and manages feedback"""
    
    def __init__(self, registry: CommandRegistry, feedback_enabled: bool = True):
        self.registry = registry
        self.feedback_enabled = feedback_enabled
        self.history: List[Dict[str, Any]] = []
    
    def execute_from_text(self, text: str) -> Dict[str, Any]:
        """
        Execute a command from natural language text
        
        Args:
            text (str): Natural language command
            
        Returns:
            Dict[str, Any]: Result of the command execution
        """
        match_result = self.registry.match_nlp_intent(text)
        
        if not match_result:
            result = {
                "status": "error",
                "message": "Could not understand command",
                "original_text": text
            }
            self.history.append(result)
            return result
        
        command_id = match_result["command_id"]
        params = match_result["params"]
        
        command = self.registry.get_command(command_id)
        if not command:
            result = {
                "status": "error",
                "message": f"Command '{command_id}' not found",
                "original_text": text
            }
            self.history.append(result)
            return result
        
        # Execute the command
        result = command.execute(params)
        
        # Add feedback if enabled
        if self.feedback_enabled:
            result["feedback"] = command.get_feedback(result)
        
        # Add to history
        self.history.append({
            "command_id": command_id,
            "params": params,
            "result": result,
            "original_text": text
        })
        
        return result
    
    def get_last_feedback(self) -> Optional[str]:
        """
        Get feedback from the last executed command
        
        Returns:
            Optional[str]: Feedback message or None if no commands executed
        """
        if not self.history:
            return None
        
        last_command = self.history[-1]
        result = last_command.get("result", {})
        
        if "feedback" in result:
            return result["feedback"]
        
        command_id = last_command.get("command_id")
        if command_id:
            command = self.registry.get_command(command_id)
            if command:
                return command.get_feedback(result)
        
        return None 
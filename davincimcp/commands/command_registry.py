#!/usr/bin/env python3
"""
command_registry.py - Command Registry and Executor

This module provides the CommandRegistry and CommandExecutor classes
for registering, looking up, and executing commands.
"""

import logging
import re
from typing import Dict, Any, List, Optional

from davincimcp.commands.command_base import Command
from davincimcp.commands.editing_commands import CutCommand, AddTransitionCommand, SetMarkerCommand

# Logger for this module
logger = logging.getLogger(__name__)

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
        
        # Register Set Marker command
        marker_cmd = SetMarkerCommand(self.resolve_controller)
        self.commands["marker"] = marker_cmd
        self.nlp_matchers["marker"] = [
            "add marker", "set marker", "create marker", "marker", "mark position"
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
            duration_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:s|sec|second)', text)
            if duration_match:
                params["duration"] = float(duration_match.group(1))
        
        elif command_id == "marker":
            # Extract marker name
            name_match = re.search(r'(?:named|called|name)\s+[\'"]?([a-zA-Z0-9 ]+)[\'"]?', text)
            if name_match:
                params["name"] = name_match.group(1).strip()
            
            # Extract marker color
            colors = ["blue", "green", "red", "yellow", "purple", "cyan", "magenta", "white", "black"]
            for color in colors:
                if color in text:
                    params["color"] = color.capitalize()
                    break
        
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
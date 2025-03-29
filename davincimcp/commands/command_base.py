#!/usr/bin/env python3
"""
command_base.py - Command Base Classes

This module provides the base classes for the command pattern implementation.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any

# Logger for this module
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
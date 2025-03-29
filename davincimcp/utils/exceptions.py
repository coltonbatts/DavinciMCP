"""
Exceptions module for DavinciMCP.

This module defines all exceptions raised by the DavinciMCP package.
Having a centralized exception hierarchy makes error handling more consistent.
"""

from typing import Optional, Any


class DavinciMCPError(Exception):
    """Base exception for all errors in the DavinciMCP package."""
    
    def __init__(self, message: str = "An error occurred in DavinciMCP", *args: Any) -> None:
        """
        Initialize the exception.
        
        Args:
            message: The error message
            *args: Additional arguments to pass to the base Exception class
        """
        self.message = message
        super().__init__(message, *args)
    
    def __str__(self) -> str:
        """Return the string representation of the error."""
        return self.message


class ConnectionError(DavinciMCPError):
    """Exception raised for errors when connecting to DaVinci Resolve."""
    
    def __init__(self, message: str = "Failed to connect to DaVinci Resolve", *args: Any) -> None:
        super().__init__(message, *args)


class ProjectError(DavinciMCPError):
    """Exception raised for errors related to DaVinci Resolve projects."""
    
    def __init__(self, message: str = "Error with DaVinci Resolve project", *args: Any) -> None:
        super().__init__(message, *args)


class TimelineError(DavinciMCPError):
    """Exception raised for errors related to DaVinci Resolve timelines."""
    
    def __init__(self, message: str = "Error with DaVinci Resolve timeline", *args: Any) -> None:
        super().__init__(message, *args)


class MediaError(DavinciMCPError):
    """Exception raised for errors related to media operations."""
    
    def __init__(self, message: str = "Error with media operation", *args: Any) -> None:
        super().__init__(message, *args)


class ConfigError(DavinciMCPError):
    """Exception raised for configuration errors."""
    
    def __init__(self, message: str = "Configuration error", *args: Any) -> None:
        super().__init__(message, *args)


class AIError(DavinciMCPError):
    """Exception raised for errors related to AI operations."""
    
    def __init__(self, message: str = "Error with AI operation", api_error: Optional[Exception] = None, *args: Any) -> None:
        self.api_error = api_error
        super().__init__(message, *args)


class CommandError(DavinciMCPError):
    """Exception raised for errors in command execution."""
    
    def __init__(self, 
                 message: str = "Error executing command", 
                 command_name: Optional[str] = None, 
                 command_args: Optional[dict] = None, 
                 *args: Any) -> None:
        self.command_name = command_name
        self.command_args = command_args or {}
        super().__init__(message, *args)
        
    def __str__(self) -> str:
        """Return the string representation of the error."""
        if self.command_name:
            return f"{self.message} (command: {self.command_name})"
        return self.message


class UIError(DavinciMCPError):
    """Exception raised for errors in the UI."""
    
    def __init__(self, message: str = "Error in UI", *args: Any) -> None:
        super().__init__(message, *args)


class ValidationError(DavinciMCPError):
    """Exception raised for validation errors."""
    
    def __init__(self, 
                 message: str = "Validation error", 
                 field: Optional[str] = None, 
                 value: Optional[Any] = None, 
                 *args: Any) -> None:
        self.field = field
        self.value = value
        msg = message
        if field:
            msg = f"{message} (field: {field}"
            if value is not None:
                msg += f", value: {value}"
            msg += ")"
        super().__init__(msg, *args) 
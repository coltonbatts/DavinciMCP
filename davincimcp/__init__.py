"""
DavinciMCP - Python interface for controlling DaVinci Resolve with Gemini AI integration

This package provides tools for programmatically controlling DaVinci Resolve,
with integration for Google's Gemini AI for intelligent video editing assistance.
"""

# Version information
__version__ = "0.1.0"

# Import main components for easy access
from davincimcp.core.resolve_controller import ResolveController
from davincimcp.core.gemini_handler import GeminiAPIHandler
from davincimcp.core.mcp_handler import MCPOperationsHandler
from davincimcp.commands.command_registry import CommandRegistry, CommandExecutor, Command
from davincimcp.media.analyzer import MediaAnalyzer, EditSuggestionEngine
from davincimcp.utils.config import Config

# UI components
try:
    from davincimcp.ui import MainWindow, run_app
    __has_ui__ = True
except ImportError:
    __has_ui__ = False

__all__ = [
    'ResolveController',
    'GeminiAPIHandler', 
    'MCPOperationsHandler',
    'CommandRegistry',
    'CommandExecutor',
    'Command',
    'MediaAnalyzer',
    'EditSuggestionEngine',
    'Config',
    '__version__',
    '__has_ui__'
]

# Add UI components to __all__ if available
if __has_ui__:
    __all__ += ['MainWindow', 'run_app'] 
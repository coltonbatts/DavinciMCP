"""
DavinciMCP - Python interface for controlling DaVinci Resolve with Gemini AI integration

This package provides tools for programmatically controlling DaVinci Resolve,
with integration for Google's Gemini AI for intelligent video editing assistance.
"""

# Use string literals for __all__ to avoid circular imports
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
    '__version__'
]

# Version information
__version__ = "0.1.0"

# Use a function to get the version instead of importing directly
def get_version():
    return __version__ 
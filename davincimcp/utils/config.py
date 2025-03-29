#!/usr/bin/env python3
"""
config.py - Configuration management for DaVinci Resolve Control

Handles loading of configuration from environment variables and config files.
Also provides platform-specific paths and settings.
"""

import os
import sys
import platform
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file if it exists
load_dotenv()

class Config:
    """Configuration manager for DaVinci Resolve Control"""
    
    def __init__(self):
        """Initialize configuration with platform-specific paths"""
        self.platform = platform.system()
        self.resolve_modules_path = self._get_resolve_modules_path()
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.config_values = self._load_config()
        
    def _get_resolve_modules_path(self) -> str:
        """
        Get the path to DaVinci Resolve modules based on the platform
        
        Returns:
            str: Path to the modules directory
        """
        # Use environment variable path if set
        env_path = os.getenv("RESOLVE_MODULES_PATH")
        if env_path and os.path.exists(env_path):
            return env_path
            
        if self.platform == "Darwin":  # macOS
            return "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules"
        elif self.platform == "Windows":
            program_data = os.getenv("PROGRAMDATA", "C:\\ProgramData")
            return os.path.join(program_data, 
                               "Blackmagic Design", "DaVinci Resolve", "Support", "Developer", "Scripting", "Modules")
        elif self.platform == "Linux":
            return "/opt/resolve/Developer/Scripting/Modules"
        else:
            logger.warning(f"Unknown platform {self.platform}, using default path")
            return "./modules"  # Fallback to local directory
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from config file or environment variables
        
        Returns:
            Dict[str, Any]: Configuration values
        """
        config = {
            "log_level": os.getenv("LOG_LEVEL", "INFO"),
            "gemini_temperature": float(os.getenv("GEMINI_TEMPERATURE", "0.7")),
            "gemini_max_tokens": int(os.getenv("GEMINI_MAX_TOKENS", "1024")),
            "feedback_enabled": os.getenv("FEEDBACK_ENABLED", "True").lower() in ("true", "1", "yes"),
            
            # MCP configuration
            "mcp_enabled": os.getenv("MCP_ENABLED", "True").lower() in ("true", "1", "yes"),
            "mcp_server_script": os.getenv("MCP_SERVER_SCRIPT", ""),
            "mcp_server_capabilities": self._parse_capabilities(os.getenv("MCP_SERVER_CAPABILITIES", "resources,tools")),
        }
        
        logger.debug(f"Loaded configuration: {config}")
        return config
    
    def _parse_capabilities(self, capabilities_str: str) -> List[str]:
        """
        Parse comma-separated capabilities string into a list
        
        Args:
            capabilities_str (str): Comma-separated list of capabilities
            
        Returns:
            List[str]: List of capabilities
        """
        if not capabilities_str:
            return []
        
        capabilities = [cap.strip() for cap in capabilities_str.split(",")]
        return [cap for cap in capabilities if cap]  # Filter out empty strings
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value
        
        Args:
            key (str): Configuration key
            default (Any, optional): Default value if key not found
            
        Returns:
            Any: Configuration value
        """
        return self.config_values.get(key, default)
    
    def append_resolve_modules_to_path(self) -> bool:
        """
        Append the Resolve modules path to sys.path
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not os.path.exists(self.resolve_modules_path):
                logger.error(f"Resolve modules path does not exist: {self.resolve_modules_path}")
                return False
                
            sys.path.append(self.resolve_modules_path)
            logger.info(f"Added Resolve modules path to sys.path: {self.resolve_modules_path}")
            return True
        except Exception as e:
            logger.error(f"Error adding Resolve modules path: {str(e)}")
            return False 
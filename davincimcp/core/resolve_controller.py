#!/usr/bin/env python3
"""
resolve_controller.py - DaVinci Resolve Controller Module

This module provides the ResolveController class for managing connections
and interactions with DaVinci Resolve through its Python API.
"""

import logging
from typing import Dict, Any, Optional

# Logger for this module
logger = logging.getLogger(__name__)

class ResolveController:
    """
    Class to manage connections and operations with DaVinci Resolve
    """
    def __init__(self):
        self.resolve = None
        self.project_manager = None
        self.current_project = None
        self.connected = False
        
        # These will be imported at runtime to avoid circular imports
        self._bmd = None

    def _import_bmd(self):
        """Import the DaVinciResolveScript module if not already imported"""
        if self._bmd is None:
            try:
                import DaVinciResolveScript as bmd
                self._bmd = bmd
                return True
            except ImportError as e:
                logger.error(f"Failed to import DaVinciResolveScript module: {e}")
                return False
        return True

    def connect(self) -> bool:
        """
        Establish connection to DaVinci Resolve
        
        Returns:
            bool: True if connection is successful, False otherwise
        """
        # Ensure the module is imported
        if not self._import_bmd():
            return False
            
        try:
            # Initialize the connection to Resolve
            self.resolve = self._bmd.scriptapp("Resolve")
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
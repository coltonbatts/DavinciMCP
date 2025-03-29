#!/usr/bin/env python3
"""
resolve_server.py - Example MCP Server for DaVinci Resolve

This script demonstrates a Model Context Protocol (MCP) server that provides
access to DaVinci Resolve project information and editing capabilities.
"""

import os
import sys
import json
import logging
from pathlib import Path

# Add parent directory to sys.path to import davincimcp modules
sys.path.append(str(Path(__file__).parent.parent.parent))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)
logger = logging.getLogger("resolve-mcp-server")

# Import MCP libraries
try:
    from mcp import Server, Resource, Tool, ToolParameter, JSONType, ResourceContent
    from mcp.server.stdio import StdioServerTransport
except ImportError:
    logger.error("MCP SDK not found. Install with: pip install mcp")
    sys.exit(1)

# Import DavinciMCP libraries
from davincimcp.utils.config import Config
from davincimcp.core.resolve_controller import ResolveController

class ResolveServer:
    """MCP server implementation for DaVinci Resolve"""
    
    def __init__(self):
        """Initialize the server"""
        # Initialize Resolve connection
        self.config = Config()
        self.controller = ResolveController()
        
        # Connect to Resolve
        self.resolve_connected = self.controller.connect()
        if not self.resolve_connected:
            logger.warning("Could not connect to DaVinci Resolve. Limited functionality available.")
        
        # Initialize MCP server
        self.server = Server(
            {
                "name": "davincimcp-resolve-server",
                "version": "0.1.0",
                "display_name": "DaVinci Resolve Server",
            },
            {
                "capabilities": {
                    "resources": {},
                    "tools": {},
                }
            }
        )
        
        # Register resources
        self._register_resources()
        
        # Register tools
        self._register_tools()
        
        logger.info("Resolve MCP server initialized")
    
    def _register_resources(self):
        """Register resources with the server"""
        
        # Register list_resources handler
        @self.server.list_resources
        async def list_resources() -> list[Resource]:
            """List available resources"""
            resources = []
            
            # Project information resource
            if self.resolve_connected:
                project_info = self.controller.get_project_info()
                if project_info:
                    resources.append(Resource(
                        uri="resolve://project-info",
                        name=f"Project: {project_info.get('name', 'Unknown')}",
                        description="Current DaVinci Resolve project information"
                    ))
                    
                    # Add timeline resources if available
                    timeline_count = project_info.get('timeline_count', 0)
                    if timeline_count > 0:
                        for i in range(timeline_count):
                            timeline = self.controller.get_timeline(i)
                            if timeline:
                                timeline_name = timeline.GetName()
                                resources.append(Resource(
                                    uri=f"resolve://timeline/{i}",
                                    name=f"Timeline: {timeline_name}",
                                    description=f"Timeline in DaVinci Resolve project"
                                ))
            
            return resources
        
        # Register get_resource handler
        @self.server.get_resource
        async def get_resource(uri: str) -> ResourceContent:
            """Get resource content"""
            
            if uri == "resolve://project-info" and self.resolve_connected:
                project_info = self.controller.get_project_info()
                if project_info:
                    return ResourceContent.text(json.dumps(project_info, indent=2))
                    
            elif uri.startswith("resolve://timeline/") and self.resolve_connected:
                try:
                    timeline_index = int(uri.split("/")[-1])
                    timeline = self.controller.get_timeline(timeline_index)
                    if timeline:
                        info = {
                            "name": timeline.GetName(),
                            "start_frame": timeline.GetStartFrame(),
                            "end_frame": timeline.GetEndFrame(),
                            "track_count": {
                                "video": timeline.GetTrackCount("video"),
                                "audio": timeline.GetTrackCount("audio"),
                                "subtitle": timeline.GetTrackCount("subtitle")
                            }
                        }
                        return ResourceContent.text(json.dumps(info, indent=2))
                except Exception as e:
                    logger.error(f"Error getting timeline info: {str(e)}")
                    
            # Resource not found or error
            return ResourceContent.text("Resource not available")
    
    def _register_tools(self):
        """Register tools with the server"""
        
        # Add cut tool
        @self.server.tool("resolve.cut", "Cut at current position",
              parameters=[])
        async def cut_at_position() -> JSONType:
            """Cut the clip at the current playhead position"""
            if not self.resolve_connected:
                return {"success": False, "error": "Not connected to DaVinci Resolve"}
                
            try:
                timeline = self.controller.get_current_timeline()
                if not timeline:
                    return {"success": False, "error": "No timeline active"}
                    
                # Execute cut
                success = timeline.Split()
                
                if success:
                    return {"success": True, "message": "Cut performed successfully"}
                else:
                    return {"success": False, "error": "Failed to perform cut"}
            except Exception as e:
                logger.error(f"Error executing cut: {str(e)}")
                return {"success": False, "error": str(e)}
        
        # Add transition tool
        @self.server.tool("resolve.add_transition", "Add transition",
              parameters=[
                  ToolParameter("type", str, "Type of transition (CrossDissolve, DipToColor, etc.)"),
                  ToolParameter("duration", float, "Duration in seconds"),
              ])
        async def add_transition(type: str, duration: float) -> JSONType:
            """Add a transition at the current position"""
            if not self.resolve_connected:
                return {"success": False, "error": "Not connected to DaVinci Resolve"}
                
            try:
                timeline = self.controller.get_current_timeline()
                if not timeline:
                    return {"success": False, "error": "No timeline active"}
                
                # Convert duration to frames based on timeline frame rate
                frame_rate = timeline.GetSetting("frameRate")
                if not frame_rate:
                    frame_rate = 24.0  # Default to 24 fps
                else:
                    frame_rate = float(frame_rate)
                
                frames = int(duration * frame_rate)
                
                # Add transition
                # Note: This is simplified - actual implementation would need to handle
                # various transition types and verify current item selection
                success = False
                if type.lower() == "crossdissolve":
                    success = timeline.AddTransition("CrossDissolve", frames)
                elif type.lower() == "diptocolor":
                    success = timeline.AddTransition("DipToColor", frames)
                else:
                    return {"success": False, "error": f"Unsupported transition type: {type}"}
                
                if success:
                    return {"success": True, "message": f"Added {type} transition with duration {duration}s ({frames} frames)"}
                else:
                    return {"success": False, "error": "Failed to add transition"}
                    
            except Exception as e:
                logger.error(f"Error adding transition: {str(e)}")
                return {"success": False, "error": str(e)}
    
    async def start(self):
        """Start the server with stdio transport"""
        transport = StdioServerTransport()
        await self.server.connect(transport)
        logger.info("Server started and connected")


async def main():
    """Main entry point"""
    server = ResolveServer()
    await server.start()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 
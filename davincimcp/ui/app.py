#!/usr/bin/env python3
"""
app.py - Main entry point for the DavinciMCP GUI application

This module provides the main entry point for running the DavinciMCP application
with a graphical user interface using PySide6.
"""

import sys
import logging
from typing import Optional, List
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QCoreApplication, Qt

from davincimcp.ui.main_window import MainWindow
from davincimcp.core.resolve_controller import ResolveController
from davincimcp.core.gemini_handler import GeminiAPIHandler
from davincimcp.utils.config import Config

# Configure logging
logger = logging.getLogger(__name__)

def run_app(args: Optional[List[str]] = None) -> int:
    """
    Main entry point for the GUI application
    
    Args:
        args (Optional[List[str]]): Command line arguments (uses sys.argv if None)
        
    Returns:
        int: Exit code (0 for success, non-zero for errors)
    """
    # Set application information
    QCoreApplication.setApplicationName("DavinciMCP")
    QCoreApplication.setOrganizationName("Colton Batts")
    QCoreApplication.setApplicationVersion("0.1.0")
    
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    # Create Qt application
    app = QApplication(sys.argv if args is None else args)
    
    # Initialize configuration
    config = Config()
    
    # Initialize the Resolve controller
    controller = ResolveController()
    
    # Attempt to connect to Resolve
    resolve_connected = controller.connect()
    if not resolve_connected:
        logger.warning("Could not connect to DaVinci Resolve. Some features will be limited.")
    
    # Initialize Gemini handler
    gemini_handler = None
    if config.gemini_api_key:
        gemini_handler = GeminiAPIHandler(config.gemini_api_key)
        if not gemini_handler.initialized:
            logger.warning("Failed to initialize Gemini API. AI features will be disabled.")
    else:
        logger.warning("No Gemini API key found. AI features will be disabled.")
    
    # Create and show main window
    main_window = MainWindow(controller, gemini_handler, config)
    main_window.show()
    
    # Run the application
    return app.exec() 
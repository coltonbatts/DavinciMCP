#!/usr/bin/env python3
"""
main_window.py - Main Window for DavinciMCP GUI

This module provides the MainWindow class, which serves as the primary
container for all UI components in the DavinciMCP application.
"""

import logging
from typing import Optional
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QDockWidget, QMenuBar, QStatusBar, QLabel,
    QMenu, QMessageBox, QToolBar, QSizePolicy
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QIcon, QColor, QPalette

from davincimcp.core.resolve_controller import ResolveController
from davincimcp.core.gemini_handler import GeminiAPIHandler
from davincimcp.utils.config import Config
from davincimcp.ui.timeline_view import TimelineView
from davincimcp.ui.command_panel import CommandPanel
from davincimcp.ui.media_browser import MediaBrowser

# Configure logging
logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    """
    Main window for the DavinciMCP application
    """
    def __init__(
        self, 
        controller: Optional[ResolveController] = None, 
        gemini_handler: Optional[GeminiAPIHandler] = None,
        config: Optional[Config] = None,
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)
        
        self.controller = controller
        self.gemini_handler = gemini_handler
        self.config = config or Config()
        
        # Set window properties
        self.setWindowTitle("DavinciMCP - AI-Assisted Video Editing")
        self.setMinimumSize(1200, 800)
        
        # Set dark theme
        self._set_dark_theme()
        
        # Create UI components
        self._create_menu_bar()
        self._create_toolbar()
        self._create_status_bar()
        self._create_central_widget()
        self._create_dock_widgets()
        
        # Show connection status
        self._update_status_bar()
    
    def _set_dark_theme(self):
        """Apply dark theme to the application"""
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(45, 45, 45))
        dark_palette.setColor(QPalette.WindowText, QColor(208, 208, 208))
        dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.AlternateBase, QColor(45, 45, 45))
        dark_palette.setColor(QPalette.Text, QColor(208, 208, 208))
        dark_palette.setColor(QPalette.Button, QColor(45, 45, 45))
        dark_palette.setColor(QPalette.ButtonText, QColor(208, 208, 208))
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, Qt.black)
        self.setPalette(dark_palette)
    
    def _create_menu_bar(self):
        """Create the main menu bar"""
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)
        
        # File menu
        file_menu = QMenu("&File", self)
        menu_bar.addMenu(file_menu)
        
        # File menu actions
        file_menu.addAction("&Connect to Resolve", self._connect_to_resolve)
        file_menu.addSeparator()
        file_menu.addAction("E&xit", self.close)
        
        # Edit menu
        edit_menu = QMenu("&Edit", self)
        menu_bar.addMenu(edit_menu)
        
        # Tools menu
        tools_menu = QMenu("&Tools", self)
        menu_bar.addMenu(tools_menu)
        
        # AI menu
        ai_menu = QMenu("&AI", self)
        menu_bar.addMenu(ai_menu)
        
        ai_menu.addAction("&Configure Gemini API", self._configure_gemini)
        ai_menu.addAction("&Test AI Connection", self._test_ai_connection)
        
        # Help menu
        help_menu = QMenu("&Help", self)
        menu_bar.addMenu(help_menu)
        
        help_menu.addAction("&About", self._show_about_dialog)
    
    def _create_toolbar(self):
        """Create the main toolbar"""
        main_toolbar = QToolBar("Main Toolbar", self)
        main_toolbar.setMovable(False)
        main_toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(main_toolbar)
        
        # Add toolbar actions
        connect_action = QAction("Connect", self)
        connect_action.triggered.connect(self._connect_to_resolve)
        main_toolbar.addAction(connect_action)
        
        analyze_action = QAction("Analyze Current", self)
        analyze_action.triggered.connect(self._analyze_current_clip)
        main_toolbar.addAction(analyze_action)
    
    def _create_status_bar(self):
        """Create the status bar"""
        status_bar = QStatusBar(self)
        self.setStatusBar(status_bar)
        
        # Add status labels
        self.resolve_status_label = QLabel("Resolve: Not Connected")
        status_bar.addPermanentWidget(self.resolve_status_label)
        
        self.ai_status_label = QLabel("AI: Not Connected")
        status_bar.addPermanentWidget(self.ai_status_label)
    
    def _create_central_widget(self):
        """Create the central widget with the timeline view"""
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create timeline view
        self.timeline_view = TimelineView(self.controller, self)
        layout.addWidget(self.timeline_view)
    
    def _create_dock_widgets(self):
        """Create the dock widgets"""
        # Command panel dock
        command_dock = QDockWidget("Command Panel", self)
        command_dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        self.command_panel = CommandPanel(
            self.controller, 
            self.gemini_handler,
            self
        )
        command_dock.setWidget(self.command_panel)
        self.addDockWidget(Qt.BottomDockWidgetArea, command_dock)
        
        # Media browser dock
        media_dock = QDockWidget("Media Browser", self)
        media_dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        self.media_browser = MediaBrowser(self.controller, self)
        media_dock.setWidget(self.media_browser)
        self.addDockWidget(Qt.LeftDockWidgetArea, media_dock)
    
    def _update_status_bar(self):
        """Update the status bar with current connection status"""
        if self.controller and self.controller.connected:
            self.resolve_status_label.setText("Resolve: Connected")
            project_info = self.controller.get_project_info()
            if project_info:
                project_name = project_info.get('name', 'Unknown')
                self.resolve_status_label.setText(f"Resolve: Connected - {project_name}")
        else:
            self.resolve_status_label.setText("Resolve: Not Connected")
        
        if self.gemini_handler and self.gemini_handler.initialized:
            self.ai_status_label.setText("AI: Connected")
        else:
            self.ai_status_label.setText("AI: Not Connected")
    
    # Action methods
    def _connect_to_resolve(self):
        """Attempt to connect to DaVinci Resolve"""
        if not self.controller:
            self.controller = ResolveController()
        
        connected = self.controller.connect()
        self._update_status_bar()
        
        if connected:
            QMessageBox.information(
                self, 
                "Connection Successful",
                "Successfully connected to DaVinci Resolve"
            )
        else:
            QMessageBox.warning(
                self, 
                "Connection Failed",
                "Failed to connect to DaVinci Resolve. Is it running?"
            )
    
    def _configure_gemini(self):
        """Configure Gemini API settings"""
        # TODO: Implement configuration dialog
        QMessageBox.information(
            self, 
            "Configure Gemini API",
            "Gemini API configuration dialog will be implemented here."
        )
    
    def _test_ai_connection(self):
        """Test the connection to Gemini AI"""
        if not self.gemini_handler:
            QMessageBox.warning(
                self, 
                "AI Not Configured",
                "Gemini AI is not configured. Please add your API key."
            )
            return
        
        if self.gemini_handler.initialized:
            test_result = self.gemini_handler.test_connection()
            if test_result:
                QMessageBox.information(
                    self, 
                    "AI Connection Successful",
                    "Successfully connected to Gemini AI."
                )
            else:
                QMessageBox.warning(
                    self, 
                    "AI Connection Failed",
                    "Failed to connect to Gemini AI. Please check your API key."
                )
        else:
            QMessageBox.warning(
                self, 
                "AI Not Initialized",
                "Gemini AI is not initialized. Please check your API key."
            )
    
    def _analyze_current_clip(self):
        """Analyze the current clip"""
        QMessageBox.information(
            self, 
            "Analyze Clip",
            "Clip analysis feature will be implemented here."
        )
    
    def _show_about_dialog(self):
        """Show the about dialog"""
        QMessageBox.about(
            self,
            "About DavinciMCP",
            "DavinciMCP v0.1.0\n\n"
            "A Python interface for controlling DaVinci Resolve with\n"
            "support for Media Control Protocol (MCP) and Gemini AI integration.\n\n"
            "© 2025 Colton Batts"
        ) 
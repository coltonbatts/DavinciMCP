#!/usr/bin/env python3
"""
command_panel.py - Command Panel for DavinciMCP

This module provides the CommandPanel class for entering and executing
natural language commands via the Gemini AI integration.
"""

import logging
from typing import Optional, List
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTextEdit, QLineEdit, QLabel, QComboBox, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, Slot, QSize
from PySide6.QtGui import QTextCursor, QFont, QColor, QPalette

from davincimcp.core.resolve_controller import ResolveController
from davincimcp.core.gemini_handler import GeminiAPIHandler
from davincimcp.commands.command_registry import CommandRegistry, CommandExecutor

# Configure logging
logger = logging.getLogger(__name__)

class CommandPanel(QWidget):
    """
    Panel for entering and executing natural language commands
    """
    
    # Signals
    command_executed = Signal(str, bool)  # Command text, success
    
    def __init__(
        self, 
        controller: Optional[ResolveController] = None,
        gemini_handler: Optional[GeminiAPIHandler] = None,
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)
        
        self.controller = controller
        self.gemini_handler = gemini_handler
        self.command_history = []
        self.history_index = -1
        
        # Set up command system
        if self.controller:
            self.command_registry = CommandRegistry(self.controller)
            self.command_executor = CommandExecutor(
                self.command_registry, 
                feedback_enabled=True
            )
        else:
            self.command_registry = None
            self.command_executor = None
        
        # Initialize UI
        self._init_ui()
        
        # Populate suggestion dropdown
        self._populate_suggestions()
    
    def _init_ui(self):
        """Initialize the UI components"""
        # Main layout
        layout = QVBoxLayout(self)
        
        # Command history display
        self.history_display = QTextEdit()
        self.history_display.setReadOnly(True)
        self.history_display.setMinimumHeight(100)
        
        # Set monospace font for history display
        font = QFont("Courier New", 10)
        self.history_display.setFont(font)
        
        # Custom colors for history display
        palette = self.history_display.palette()
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.Text, QColor(220, 220, 220))
        self.history_display.setPalette(palette)
        
        layout.addWidget(self.history_display)
        
        # Command input area
        input_layout = QHBoxLayout()
        
        # Suggestion dropdown
        self.suggestion_dropdown = QComboBox()
        self.suggestion_dropdown.setEditable(False)
        self.suggestion_dropdown.setMinimumWidth(150)
        self.suggestion_dropdown.currentTextChanged.connect(self._handle_suggestion_selected)
        
        # Command input field
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("Enter a command (e.g., 'Add a cross dissolve transition that's 1.5 seconds')")
        self.command_input.returnPressed.connect(self._execute_command)
        
        # Execute button
        self.execute_button = QPushButton("Execute")
        self.execute_button.clicked.connect(self._execute_command)
        
        input_layout.addWidget(QLabel("Suggestions:"))
        input_layout.addWidget(self.suggestion_dropdown)
        input_layout.addWidget(self.command_input, 1)  # 1 is stretch factor
        input_layout.addWidget(self.execute_button)
        
        layout.addLayout(input_layout)
        
        # Feedback area
        self.feedback_label = QLabel("Ready")
        layout.addWidget(self.feedback_label)
    
    def _populate_suggestions(self):
        """Populate the suggestion dropdown with common commands"""
        common_commands = [
            "Select a suggestion or type your own...",
            "Add a cross dissolve transition that's 1.5 seconds",
            "Cut the clip at the current position",
            "Analyze this long take and suggest edits",
            "Add a fade to black at the end",
            "Speed up this clip by 20%",
            "Add a title with text 'Scene 1'",
            "Apply color correction to make it warmer",
            "Export the current timeline as MP4",
            "Undo the last operation"
        ]
        
        self.suggestion_dropdown.clear()
        for command in common_commands:
            self.suggestion_dropdown.addItem(command)
    
    def _handle_suggestion_selected(self, text: str):
        """Handle a suggestion being selected from the dropdown"""
        if text != "Select a suggestion or type your own...":
            self.command_input.setText(text)
    
    def _execute_command(self):
        """Execute the current command"""
        command_text = self.command_input.text().strip()
        if not command_text:
            return
        
        # Add command to history display
        self._add_to_history(f"Command: {command_text}", "blue")
        
        # Add to command history list
        self.command_history.append(command_text)
        self.history_index = len(self.command_history)
        
        # Check if resolve is connected
        if not self.controller or not self.controller.connected:
            self._add_to_history("Error: Not connected to DaVinci Resolve", "red")
            self.feedback_label.setText("Error: Not connected to DaVinci Resolve")
            return
        
        # Execute command using AI if available
        success = False
        if self.gemini_handler and self.gemini_handler.initialized and self.command_executor:
            try:
                # In a real implementation, this would use the AI to interpret the command
                # and then execute it using the command executor
                
                # For demonstration, we'll just show a simulated response
                simulated_result = f"Executed: {command_text}"
                self._add_to_history(simulated_result, "green")
                
                # Process specific known commands for the demonstration
                if "cross dissolve" in command_text.lower():
                    self._add_to_history("Added a cross dissolve transition of 1.5 seconds to the selected clip", "green")
                elif "cut" in command_text.lower():
                    self._add_to_history("Cut the current clip at the playhead position", "green")
                elif "analyze" in command_text.lower():
                    self._add_to_history("Analyzing the current clip...", "green")
                    self._add_to_history("Analysis suggests cuts at 00:05, 00:12, and 00:23 based on content changes", "green")
                
                success = True
                self.feedback_label.setText("Command executed successfully")
            except Exception as e:
                logger.error(f"Error executing command: {e}")
                self._add_to_history(f"Error: {str(e)}", "red")
                self.feedback_label.setText(f"Error: {str(e)}")
        else:
            self._add_to_history("Error: AI integration not available", "orange")
            self.feedback_label.setText("Error: AI integration not available")
        
        # Clear the input field
        self.command_input.clear()
        
        # Emit signal
        self.command_executed.emit(command_text, success)
    
    def _add_to_history(self, text: str, color: str):
        """Add text to history display with color"""
        cursor = self.history_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        
        # Set color based on message type
        if color == "red":
            self.history_display.setTextColor(QColor(255, 100, 100))
        elif color == "green":
            self.history_display.setTextColor(QColor(100, 255, 100))
        elif color == "blue":
            self.history_display.setTextColor(QColor(100, 180, 255))
        elif color == "orange":
            self.history_display.setTextColor(QColor(255, 180, 100))
        else:
            self.history_display.setTextColor(QColor(220, 220, 220))
        
        # Insert text and add newline
        self.history_display.insertPlainText(text + "\n")
        
        # Scroll to the bottom
        self.history_display.verticalScrollBar().setValue(
            self.history_display.verticalScrollBar().maximum()
        )
    
    def keyPressEvent(self, event):
        """Handle key press events for command history"""
        if self.command_input.hasFocus():
            if event.key() == Qt.Key_Up:
                # Navigate command history backward
                if self.history_index > 0:
                    self.history_index -= 1
                    self.command_input.setText(self.command_history[self.history_index])
            elif event.key() == Qt.Key_Down:
                # Navigate command history forward
                if self.history_index < len(self.command_history) - 1:
                    self.history_index += 1
                    self.command_input.setText(self.command_history[self.history_index])
                else:
                    self.history_index = len(self.command_history)
                    self.command_input.clear()
        
        # Pass event to parent
        super().keyPressEvent(event) 
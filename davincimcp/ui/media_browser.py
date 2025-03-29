#!/usr/bin/env python3
"""
media_browser.py - Media Browser for DavinciMCP

This module provides the MediaBrowser class for browsing and selecting
media files in DaVinci Resolve projects.
"""

import logging
from typing import Optional, List, Dict, Any
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QListWidget, QListWidgetItem, QLabel, QComboBox, 
    QSplitter, QToolBar, QSizePolicy, QMenu
)
from PySide6.QtCore import Qt, Signal, QSize, QRect
from PySide6.QtGui import QIcon, QPixmap, QColor, QPainter, QBrush, QPen

from davincimcp.core.resolve_controller import ResolveController

# Configure logging
logger = logging.getLogger(__name__)

class MediaBrowser(QWidget):
    """
    Widget for browsing and selecting media in DaVinci Resolve
    """
    
    # Signals
    media_selected = Signal(dict)  # Media item data
    
    def __init__(
        self, 
        controller: Optional[ResolveController] = None,
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)
        
        self.controller = controller
        self.media_items = []  # List of media items from Resolve
        self.current_bin = "Master"
        
        # Initialize UI
        self._init_ui()
        
        # Refresh the media list
        self.refresh_media()
    
    def _init_ui(self):
        """Initialize the UI components"""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Toolbar
        toolbar = QToolBar()
        
        # Bin selection dropdown
        self.bin_dropdown = QComboBox()
        self.bin_dropdown.setMinimumWidth(150)
        self.bin_dropdown.currentTextChanged.connect(self._handle_bin_selected)
        
        # Refresh button
        self.refresh_btn = QPushButton("↻")
        self.refresh_btn.setToolTip("Refresh Media")
        self.refresh_btn.clicked.connect(self.refresh_media)
        
        toolbar.addWidget(QLabel("Bin:"))
        toolbar.addWidget(self.bin_dropdown)
        toolbar.addWidget(self.refresh_btn)
        
        layout.addWidget(toolbar)
        
        # Create splitter for bin view and preview
        splitter = QSplitter(Qt.Vertical)
        
        # Media list
        self.media_list = QListWidget()
        self.media_list.setIconSize(QSize(80, 45))  # 16:9 thumbnail ratio
        self.media_list.setWordWrap(True)
        self.media_list.setSpacing(2)
        self.media_list.itemDoubleClicked.connect(self._handle_media_double_clicked)
        self.media_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.media_list.customContextMenuRequested.connect(self._show_context_menu)
        
        # Preview area
        self.preview_widget = MediaPreviewWidget(self)
        
        splitter.addWidget(self.media_list)
        splitter.addWidget(self.preview_widget)
        splitter.setSizes([200, 100])  # Initial sizes
        
        layout.addWidget(splitter)
    
    def refresh_media(self):
        """Refresh the media list from Resolve"""
        if not self.controller or not self.controller.connected:
            logger.warning("Cannot refresh media: Resolve not connected")
            self.media_items = []
            self._populate_dummy_bins()
        else:
            try:
                # In a real implementation, this would fetch actual media data
                # For now, we'll use dummy data for demonstration
                self._populate_dummy_bins()
                self.media_items = self._get_dummy_media_items()
            except Exception as e:
                logger.error(f"Error refreshing media: {e}")
                self.media_items = []
        
        # Update the media list
        self._update_media_list()
    
    def _populate_dummy_bins(self):
        """Populate dummy bins for demonstration"""
        bins = ["Master", "Raw Footage", "Music", "Sound FX", "Graphics"]
        
        self.bin_dropdown.clear()
        for bin in bins:
            self.bin_dropdown.addItem(bin)
    
    def _get_dummy_media_items(self) -> List[Dict[str, Any]]:
        """
        Generate dummy media item data for demonstration purposes
        
        In a real implementation, this would be replaced with actual data from Resolve
        """
        bin_name = self.current_bin
        
        if bin_name == "Master":
            return [
                {
                    "id": "clip001",
                    "name": "Interview_Wide.mp4",
                    "duration": 120.5,
                    "resolution": "1920x1080",
                    "fps": 24,
                    "path": "/footage/interview/wide.mp4",
                    "thumbnail_color": QColor(100, 150, 200)
                },
                {
                    "id": "clip002",
                    "name": "Interview_Close.mp4",
                    "duration": 118.2,
                    "resolution": "1920x1080",
                    "fps": 24,
                    "path": "/footage/interview/close.mp4",
                    "thumbnail_color": QColor(150, 100, 100)
                },
                {
                    "id": "clip003",
                    "name": "B-Roll_Office.mp4",
                    "duration": 45.8,
                    "resolution": "3840x2160",
                    "fps": 30,
                    "path": "/footage/b-roll/office.mp4",
                    "thumbnail_color": QColor(100, 200, 150)
                }
            ]
        elif bin_name == "Raw Footage":
            return [
                {
                    "id": "clip004",
                    "name": "Location_Exterior_001.mp4",
                    "duration": 85.3,
                    "resolution": "3840x2160",
                    "fps": 24,
                    "path": "/footage/location/exterior_001.mp4",
                    "thumbnail_color": QColor(200, 180, 100)
                },
                {
                    "id": "clip005",
                    "name": "Location_Interior_002.mp4",
                    "duration": 62.7,
                    "resolution": "3840x2160",
                    "fps": 24,
                    "path": "/footage/location/interior_002.mp4",
                    "thumbnail_color": QColor(180, 120, 210)
                }
            ]
        elif bin_name == "Music":
            return [
                {
                    "id": "audio001",
                    "name": "Theme_Music_v1.wav",
                    "duration": 128.0,
                    "channels": "Stereo",
                    "sample_rate": "48kHz",
                    "path": "/audio/music/theme_v1.wav",
                    "thumbnail_color": QColor(80, 80, 200)
                },
                {
                    "id": "audio002",
                    "name": "Background_Ambient.wav",
                    "duration": 240.0,
                    "channels": "Stereo",
                    "sample_rate": "48kHz",
                    "path": "/audio/music/ambient.wav",
                    "thumbnail_color": QColor(80, 200, 80)
                }
            ]
        else:
            return []
    
    def _update_media_list(self):
        """Update the media list widget with current media items"""
        self.media_list.clear()
        
        for item in self.media_items:
            list_item = QListWidgetItem()
            list_item.setText(item["name"])
            list_item.setData(Qt.UserRole, item)
            
            # Create a thumbnail
            pixmap = self._create_thumbnail(item)
            list_item.setIcon(QIcon(pixmap))
            
            # Add to list
            self.media_list.addItem(list_item)
    
    def _create_thumbnail(self, item: Dict[str, Any]) -> QPixmap:
        """Create a thumbnail pixmap for a media item"""
        width, height = 160, 90  # 16:9 ratio
        pixmap = QPixmap(width, height)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Fill with item's color
        color = item.get("thumbnail_color", QColor(100, 100, 100))
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(Qt.black, 1))
        painter.drawRoundedRect(0, 0, width, height, 5, 5)
        
        # Draw item type indicator (video/audio)
        if "audio" in item["id"]:
            # Draw audio waveform
            painter.setPen(QPen(Qt.white, 2))
            middle = height / 2
            for i in range(0, width, 4):
                # Simple wave pattern
                amplitude = 15 * (1 + (i/width)) * (0.5 + 0.5 * ((i % 16) / 16))
                painter.drawLine(i, int(middle - amplitude), i, int(middle + amplitude))
        else:
            # Draw video frame markers
            painter.setPen(QPen(Qt.white, 1))
            painter.drawLine(0, 10, width, 10)
            painter.drawLine(0, height-10, width, height-10)
            
            # Draw diagonal lines for corners
            size = 15
            painter.drawLine(0, 0, size, size)
            painter.drawLine(width, 0, width-size, size)
            painter.drawLine(0, height, size, height-size)
            painter.drawLine(width, height, width-size, height-size)
        
        painter.end()
        return pixmap
    
    def _handle_bin_selected(self, bin_name: str):
        """Handle a bin being selected from the dropdown"""
        self.current_bin = bin_name
        self.refresh_media()
    
    def _handle_media_double_clicked(self, item: QListWidgetItem):
        """Handle a media item being double-clicked"""
        media_data = item.data(Qt.UserRole)
        if media_data:
            self.media_selected.emit(media_data)
            self.preview_widget.set_media(media_data)
    
    def _show_context_menu(self, position):
        """Show context menu for media item"""
        item = self.media_list.itemAt(position)
        if not item:
            return
        
        media_data = item.data(Qt.UserRole)
        
        menu = QMenu(self)
        
        # Add actions
        add_to_timeline = menu.addAction("Add to Timeline")
        preview = menu.addAction("Preview")
        analyze = menu.addAction("Analyze with AI")
        menu.addSeparator()
        properties = menu.addAction("Properties")
        
        # Show menu and handle actions
        action = menu.exec_(self.media_list.mapToGlobal(position))
        
        if action == add_to_timeline:
            # This would add the clip to the timeline in a real implementation
            logger.info(f"Adding {media_data['name']} to timeline")
        elif action == preview:
            self.preview_widget.set_media(media_data)
        elif action == analyze:
            # This would trigger AI analysis in a real implementation
            logger.info(f"Analyzing {media_data['name']} with AI")
        elif action == properties:
            # This would show properties in a real implementation
            logger.info(f"Showing properties for {media_data['name']}")
    
    def get_selected_media(self) -> Optional[Dict[str, Any]]:
        """Get the currently selected media item"""
        items = self.media_list.selectedItems()
        if items:
            return items[0].data(Qt.UserRole)
        return None


class MediaPreviewWidget(QWidget):
    """
    Widget for previewing media items
    """
    
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        
        self.current_media = None
        self.frame_position = 0.0  # Current position in seconds
        
        # Set size policy
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumHeight(150)
        
        # Initialize UI
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the UI components"""
        # Main layout
        layout = QVBoxLayout(self)
        
        # Preview display
        self.preview_area = QLabel()
        self.preview_area.setAlignment(Qt.AlignCenter)
        self.preview_area.setMinimumHeight(100)
        self.preview_area.setText("No media selected")
        self.preview_area.setStyleSheet("background-color: #1a1a1a; border: 1px solid #333;")
        
        # Media info
        self.info_label = QLabel()
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("color: #ccc; font-size: 10pt;")
        
        # Transport controls
        transport_layout = QHBoxLayout()
        
        self.play_btn = QPushButton("▶")
        self.play_btn.setToolTip("Play/Pause")
        self.play_btn.setFixedWidth(40)
        
        self.prev_frame_btn = QPushButton("◀")
        self.prev_frame_btn.setToolTip("Previous Frame")
        self.prev_frame_btn.setFixedWidth(40)
        
        self.next_frame_btn = QPushButton("▶")
        self.next_frame_btn.setToolTip("Next Frame")
        self.next_frame_btn.setFixedWidth(40)
        
        self.time_label = QLabel("00:00:00.000")
        
        transport_layout.addWidget(self.prev_frame_btn)
        transport_layout.addWidget(self.play_btn)
        transport_layout.addWidget(self.next_frame_btn)
        transport_layout.addStretch()
        transport_layout.addWidget(self.time_label)
        
        # Add widgets to layout
        layout.addWidget(self.preview_area)
        layout.addWidget(self.info_label)
        layout.addLayout(transport_layout)
    
    def set_media(self, media: Dict[str, Any]):
        """Set the current media item for preview"""
        self.current_media = media
        self.frame_position = 0.0
        
        # Update the preview and info
        self._update_preview()
        self._update_info()
    
    def _update_preview(self):
        """Update the preview display with current media and position"""
        if not self.current_media:
            self.preview_area.setText("No media selected")
            return
        
        # In a real implementation, this would fetch a frame at the current position
        # For demonstration, we'll use a colored rectangle based on the media
        width, height = 320, 180  # 16:9 ratio
        pixmap = QPixmap(width, height)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Fill with item's color
        color = self.current_media.get("thumbnail_color", QColor(100, 100, 100))
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(Qt.black, 2))
        painter.drawRect(0, 0, width, height)
        
        # Draw a position indicator
        if "duration" in self.current_media:
            duration = self.current_media["duration"]
            position_pct = min(1.0, max(0.0, self.frame_position / duration))
            
            # Draw a line representing the position
            line_x = int(width * position_pct)
            painter.setPen(QPen(Qt.white, 3))
            painter.drawLine(line_x, 0, line_x, height)
            
            # Draw time text
            painter.setPen(Qt.white)
            painter.drawText(10, 20, f"Frame at {self.frame_position:.2f}s")
        
        painter.end()
        
        # Set the pixmap to display
        self.preview_area.setPixmap(pixmap)
        self.preview_area.setAlignment(Qt.AlignCenter)
        
        # Update time label
        self._update_time_display()
    
    def _update_info(self):
        """Update the info label with media information"""
        if not self.current_media:
            self.info_label.setText("")
            return
        
        # Build info text based on media type
        if "audio" in self.current_media["id"]:
            info = (
                f"<b>{self.current_media['name']}</b><br>"
                f"Audio • {self.current_media.get('duration', 0):.1f}s • "
                f"{self.current_media.get('channels', 'Unknown')} • "
                f"{self.current_media.get('sample_rate', 'Unknown')}"
            )
        else:
            info = (
                f"<b>{self.current_media['name']}</b><br>"
                f"Video • {self.current_media.get('duration', 0):.1f}s • "
                f"{self.current_media.get('resolution', 'Unknown')} • "
                f"{self.current_media.get('fps', 0)} fps"
            )
        
        self.info_label.setText(info)
    
    def _update_time_display(self):
        """Update the time display label"""
        if not self.current_media:
            self.time_label.setText("00:00:00.000")
            return
        
        total_seconds = int(self.frame_position)
        milliseconds = int((self.frame_position - total_seconds) * 1000)
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}"
        self.time_label.setText(time_str)
        
        # Also update the duration ratio if available
        if "duration" in self.current_media:
            duration = self.current_media["duration"]
            self.time_label.setText(f"{time_str} / {int(duration//60):02d}:{int(duration%60):02d}.{int((duration%1)*1000):03d}") 
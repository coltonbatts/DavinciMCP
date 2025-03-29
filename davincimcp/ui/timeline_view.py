#!/usr/bin/env python3
"""
timeline_view.py - Timeline visualization for DavinciMCP

This module provides the TimelineView class for visualizing and interacting
with the DaVinci Resolve timeline.
"""

import logging
from typing import Optional, List, Dict, Any
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QScrollArea, QPushButton, QSizePolicy
)
from PySide6.QtCore import Qt, QRect, QSize, QPoint, Signal, Slot
from PySide6.QtGui import (
    QPainter, QColor, QPen, QBrush, QPainterPath,
    QLinearGradient, QFont, QPaintEvent
)

from davincimcp.core.resolve_controller import ResolveController

# Configure logging
logger = logging.getLogger(__name__)

class TimelineView(QWidget):
    """
    Widget for visualizing and interacting with the DaVinci Resolve timeline
    """
    
    # Signals
    clip_selected = Signal(dict)
    playhead_moved = Signal(float)
    
    def __init__(
        self, 
        controller: Optional[ResolveController] = None,
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)
        
        self.controller = controller
        self.clips = []  # List of clip data from Resolve
        self.current_time = 0.0  # Current playhead position in seconds
        self.timeline_length = 60.0  # Default timeline length in seconds
        self.pixels_per_second = 20  # Zoom level
        self.selected_clip_index = -1
        
        # Set widget properties
        self.setMinimumHeight(150)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Initialize UI
        self._init_ui()
        
        # Refresh the timeline
        self.refresh_timeline()
    
    def _init_ui(self):
        """Initialize the UI components"""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Top controls
        top_layout = QHBoxLayout()
        
        self.zoom_in_btn = QPushButton("+")
        self.zoom_in_btn.setToolTip("Zoom In")
        self.zoom_in_btn.clicked.connect(self._zoom_in)
        
        self.zoom_out_btn = QPushButton("-")
        self.zoom_out_btn.setToolTip("Zoom Out")
        self.zoom_out_btn.clicked.connect(self._zoom_out)
        
        self.refresh_btn = QPushButton("↻")
        self.refresh_btn.setToolTip("Refresh Timeline")
        self.refresh_btn.clicked.connect(self.refresh_timeline)
        
        top_layout.addWidget(QLabel("Timeline Controls:"))
        top_layout.addWidget(self.zoom_in_btn)
        top_layout.addWidget(self.zoom_out_btn)
        top_layout.addWidget(self.refresh_btn)
        top_layout.addStretch()
        
        # Add time display
        self.time_label = QLabel("00:00:00.000")
        top_layout.addWidget(self.time_label)
        
        layout.addLayout(top_layout)
        
        # Timeline view
        self.timeline_widget = TimelineCanvas(self)
        
        # Add timeline to scrollable area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.timeline_widget)
        
        layout.addWidget(scroll_area)
    
    def refresh_timeline(self):
        """Refresh the timeline data from Resolve"""
        if not self.controller or not self.controller.connected:
            logger.warning("Cannot refresh timeline: Resolve not connected")
            self.clips = []
            self.timeline_length = 60.0
        else:
            try:
                # In a real implementation, this would fetch actual timeline data
                # For now, we'll use dummy data for demonstration
                self.clips = self._get_dummy_clips()
                self.timeline_length = max([clip["end_time"] for clip in self.clips], default=60.0)
            except Exception as e:
                logger.error(f"Error refreshing timeline: {e}")
                self.clips = []
        
        # Update the timeline canvas
        self.timeline_widget.set_clips(self.clips)
        self.timeline_widget.set_timeline_length(self.timeline_length)
        self.timeline_widget.set_pixels_per_second(self.pixels_per_second)
        self.timeline_widget.update()
    
    def _get_dummy_clips(self) -> List[Dict[str, Any]]:
        """
        Generate dummy clip data for demonstration purposes
        
        In a real implementation, this would be replaced with actual data from Resolve
        """
        return [
            {
                "index": 0,
                "name": "Clip 1",
                "start_time": 0.0,
                "end_time": 5.0,
                "color": QColor(100, 150, 200),
                "track": 0
            },
            {
                "index": 1,
                "name": "Clip 2",
                "start_time": 5.0,
                "end_time": 8.5,
                "color": QColor(200, 100, 100),
                "track": 0
            },
            {
                "index": 2,
                "name": "Clip 3",
                "start_time": 8.5,
                "end_time": 15.0,
                "color": QColor(100, 200, 100),
                "track": 0
            },
            {
                "index": 3,
                "name": "Title",
                "start_time": 2.0,
                "end_time": 7.0,
                "color": QColor(200, 200, 100),
                "track": 1
            }
        ]
    
    def _zoom_in(self):
        """Increase the zoom level"""
        self.pixels_per_second = min(self.pixels_per_second * 1.5, 200)
        self.timeline_widget.set_pixels_per_second(self.pixels_per_second)
        self.timeline_widget.update()
    
    def _zoom_out(self):
        """Decrease the zoom level"""
        self.pixels_per_second = max(self.pixels_per_second / 1.5, 5)
        self.timeline_widget.set_pixels_per_second(self.pixels_per_second)
        self.timeline_widget.update()
    
    def set_current_time(self, time: float):
        """Set the current playhead position"""
        self.current_time = max(0.0, min(time, self.timeline_length))
        self.timeline_widget.set_current_time(self.current_time)
        self._update_time_display()
    
    def _update_time_display(self):
        """Update the time display label"""
        total_seconds = int(self.current_time)
        milliseconds = int((self.current_time - total_seconds) * 1000)
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}"
        self.time_label.setText(time_str)


class TimelineCanvas(QWidget):
    """
    Canvas widget for rendering the timeline visualization
    """
    
    # Signals
    clip_clicked = Signal(int)  # Clip index
    
    def __init__(self, parent: TimelineView):
        super().__init__(parent)
        
        self.parent_view = parent
        self.clips = []
        self.timeline_length = 60.0  # seconds
        self.pixels_per_second = 20
        self.current_time = 0.0
        self.track_height = 50
        self.num_tracks = 3  # Default number of tracks
        
        # Colors
        self.background_color = QColor(30, 30, 30)
        self.grid_color = QColor(60, 60, 60)
        self.playhead_color = QColor(255, 50, 50)
        
        # Set minimum size
        self.setMinimumSize(800, 150)
    
    def set_clips(self, clips):
        """Set the clips data"""
        self.clips = clips
        self.num_tracks = max([clip["track"] for clip in clips], default=0) + 1
    
    def set_timeline_length(self, length):
        """Set the timeline length in seconds"""
        self.timeline_length = max(length, 10.0)  # Minimum 10 seconds
    
    def set_pixels_per_second(self, pixels):
        """Set the pixels per second (zoom level)"""
        self.pixels_per_second = pixels
        self.update_size()
    
    def set_current_time(self, time):
        """Set the current playhead position"""
        self.current_time = time
        self.update()
    
    def update_size(self):
        """Update the widget size based on timeline length and zoom"""
        width = int(self.timeline_length * self.pixels_per_second) + 100
        height = self.track_height * self.num_tracks + 50
        self.setMinimumSize(width, height)
    
    def mousePressEvent(self, event):
        """Handle mouse press events for selecting clips and moving playhead"""
        if event.button() == Qt.LeftButton:
            # Check if a clip was clicked
            pos = event.position()
            for i, clip in enumerate(self.clips):
                clip_rect = self._get_clip_rect(clip)
                if clip_rect.contains(pos.x(), pos.y()):
                    self.clip_clicked.emit(i)
                    self.parent_view.selected_clip_index = i
                    self.update()
                    return
            
            # If no clip was clicked, move playhead
            self.current_time = max(0, min(event.position().x() / self.pixels_per_second, self.timeline_length))
            self.parent_view.set_current_time(self.current_time)
            self.parent_view.playhead_moved.emit(self.current_time)
            self.update()
    
    def _get_clip_rect(self, clip):
        """Get the rectangle for a clip"""
        x = clip["start_time"] * self.pixels_per_second
        y = clip["track"] * self.track_height + 10
        width = (clip["end_time"] - clip["start_time"]) * self.pixels_per_second
        height = self.track_height - 15
        
        return QRect(int(x), int(y), int(width), int(height))
    
    def paintEvent(self, event: QPaintEvent):
        """Paint the timeline"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Fill background
        painter.fillRect(event.rect(), self.background_color)
        
        # Draw time grid
        self._draw_time_grid(painter)
        
        # Draw tracks
        self._draw_tracks(painter)
        
        # Draw clips
        self._draw_clips(painter)
        
        # Draw playhead
        self._draw_playhead(painter)
    
    def _draw_time_grid(self, painter: QPainter):
        """Draw the time grid with markers"""
        painter.setPen(QPen(self.grid_color, 1))
        
        # Determine grid spacing based on zoom level
        if self.pixels_per_second > 100:
            # Very zoomed in - show 0.1 second intervals
            grid_interval = 0.1
            label_interval = 1.0
        elif self.pixels_per_second > 50:
            # Zoomed in - show 0.5 second intervals
            grid_interval = 0.5
            label_interval = 5.0
        elif self.pixels_per_second > 20:
            # Medium zoom - show 1 second intervals
            grid_interval = 1.0
            label_interval = 5.0
        elif self.pixels_per_second > 5:
            # Medium-out zoom - show 5 second intervals
            grid_interval = 5.0
            label_interval = 30.0
        else:
            # Zoomed out - show 30 second intervals
            grid_interval = 30.0
            label_interval = 60.0
        
        # Draw vertical grid lines
        height = self.track_height * self.num_tracks + 30
        
        # Small grid lines
        time = 0
        while time <= self.timeline_length:
            x = time * self.pixels_per_second
            painter.drawLine(int(x), 0, int(x), height)
            time += grid_interval
        
        # Draw time labels
        painter.setPen(Qt.white)
        painter.setFont(QFont("Arial", 8))
        
        time = 0
        while time <= self.timeline_length:
            x = time * self.pixels_per_second
            
            # Format time as MM:SS
            minutes = int(time) // 60
            seconds = int(time) % 60
            time_str = f"{minutes:02d}:{seconds:02d}"
            
            painter.drawText(int(x + 3), height - 5, time_str)
            time += label_interval
    
    def _draw_tracks(self, painter: QPainter):
        """Draw the track backgrounds"""
        track_width = self.width()
        
        for i in range(self.num_tracks):
            y = i * self.track_height + 10
            track_rect = QRect(0, int(y), track_width, self.track_height - 5)
            
            # Create gradient for track
            gradient = QLinearGradient(0, y, 0, y + self.track_height - 5)
            gradient.setColorAt(0, QColor(50, 50, 50))
            gradient.setColorAt(1, QColor(40, 40, 40))
            
            painter.fillRect(track_rect, gradient)
            
            # Draw track label
            painter.setPen(Qt.white)
            painter.drawText(5, int(y + 20), f"Track {i+1}")
    
    def _draw_clips(self, painter: QPainter):
        """Draw all clips on the timeline"""
        for i, clip in enumerate(self.clips):
            clip_rect = self._get_clip_rect(clip)
            
            # Create gradient for clip
            base_color = clip["color"]
            gradient = QLinearGradient(0, clip_rect.top(), 0, clip_rect.bottom())
            gradient.setColorAt(0, base_color.lighter(120))
            gradient.setColorAt(1, base_color)
            
            painter.setBrush(QBrush(gradient))
            
            # Set border based on selection state
            if i == self.parent_view.selected_clip_index:
                painter.setPen(QPen(Qt.white, 2))
            else:
                painter.setPen(QPen(Qt.black, 1))
            
            # Draw rounded rectangle for clip
            path = QPainterPath()
            path.addRoundedRect(clip_rect, 5, 5)
            painter.drawPath(path)
            
            # Draw clip name
            painter.setPen(Qt.white)
            painter.drawText(clip_rect.adjusted(5, 5, -5, -5), Qt.AlignLeft | Qt.AlignTop, clip["name"])
    
    def _draw_playhead(self, painter: QPainter):
        """Draw the playhead at the current time"""
        x = self.current_time * self.pixels_per_second
        height = self.track_height * self.num_tracks + 30
        
        # Draw playhead line
        painter.setPen(QPen(self.playhead_color, 2))
        painter.drawLine(int(x), 0, int(x), height)
        
        # Draw playhead triangle
        painter.setBrush(QBrush(self.playhead_color))
        painter.setPen(Qt.NoPen)
        
        playhead_triangle = QPainterPath()
        triangle_size = 8
        
        playhead_triangle.moveTo(int(x), 0)
        playhead_triangle.lineTo(int(x - triangle_size), int(-triangle_size))
        playhead_triangle.lineTo(int(x + triangle_size), int(-triangle_size))
        playhead_triangle.closeSubpath()
        
        painter.drawPath(playhead_triangle) 
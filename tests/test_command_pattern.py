#!/usr/bin/env python3
"""
Tests for the command pattern implementation.
"""

import pytest
from unittest.mock import MagicMock, patch
import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from davincimcp.commands.command_base import Command
from davincimcp.commands.command_registry import CommandRegistry, CommandExecutor
from davincimcp.commands.editing_commands import CutCommand, AddTransitionCommand, SetMarkerCommand

class MockCommand(Command):
    """Mock command implementation for testing"""
    
    def __init__(self, return_value=None, should_fail=False):
        self.executed = False
        self.last_params = None
        self.return_value = return_value or {"status": "success", "message": "Test command executed"}
        self.should_fail = should_fail
    
    def execute(self, params=None):
        """Mock execute method"""
        self.executed = True
        self.last_params = params or {}
        
        if self.should_fail:
            return {"status": "error", "message": "Test command failed"}
        
        return self.return_value
    
    def get_description(self):
        """Mock get_description method"""
        return "Test command description"
    
    def get_feedback(self, result):
        """Mock get_feedback method"""
        if result.get("status") == "success":
            return "Test command succeeded"
        else:
            return "Test command failed"


class TestCommandBase:
    """Tests for the Command base class implementations"""
    
    def test_mock_command(self):
        """Test the mock command"""
        cmd = MockCommand()
        result = cmd.execute()
        
        assert cmd.executed is True
        assert result["status"] == "success"
        assert cmd.get_description() == "Test command description"
        assert cmd.get_feedback(result) == "Test command succeeded"
    
    def test_cut_command_initialization(self):
        """Test CutCommand initialization"""
        mock_controller = MagicMock()
        cmd = CutCommand(mock_controller)
        
        assert cmd.resolve_controller == mock_controller
        assert cmd.get_description() == "Cut/split the clip at the current playhead position"
    
    def test_transition_command_initialization(self):
        """Test AddTransitionCommand initialization"""
        mock_controller = MagicMock()
        cmd = AddTransitionCommand(mock_controller)
        
        assert cmd.resolve_controller == mock_controller
        assert cmd.get_description() == "Add a transition between clips"
    
    def test_marker_command_initialization(self):
        """Test SetMarkerCommand initialization"""
        mock_controller = MagicMock()
        cmd = SetMarkerCommand(mock_controller)
        
        assert cmd.resolve_controller == mock_controller
        assert cmd.get_description() == "Set a marker at the current playhead position"


class TestCommandRegistry:
    """Tests for the CommandRegistry class"""
    
    @pytest.fixture
    def mock_controller(self):
        """Create a mock resolve controller"""
        controller = MagicMock()
        controller.get_current_timeline.return_value = MagicMock()
        return controller
    
    @pytest.fixture
    def registry(self, mock_controller):
        """Create a command registry with a mock controller"""
        return CommandRegistry(mock_controller)
    
    def test_registry_initialization(self, registry, mock_controller):
        """Test registry initialization"""
        assert registry.resolve_controller == mock_controller
        assert len(registry.commands) > 0
        assert len(registry.nlp_matchers) > 0
    
    def test_get_command(self, registry):
        """Test getting a command by ID"""
        cut_cmd = registry.get_command("cut")
        assert isinstance(cut_cmd, CutCommand)
        
        transition_cmd = registry.get_command("transition")
        assert isinstance(transition_cmd, AddTransitionCommand)
        
        marker_cmd = registry.get_command("marker")
        assert isinstance(marker_cmd, SetMarkerCommand)
        
        # Non-existent command
        non_existent = registry.get_command("non_existent")
        assert non_existent is None
    
    def test_match_nlp_intent_cut(self, registry):
        """Test matching NLP intent for cut command"""
        result = registry.match_nlp_intent("cut the clip at current position")
        assert result is not None
        assert result["command_id"] == "cut"
        
        result = registry.match_nlp_intent("split this clip")
        assert result is not None
        assert result["command_id"] == "cut"
    
    def test_match_nlp_intent_transition(self, registry):
        """Test matching NLP intent for transition command"""
        result = registry.match_nlp_intent("add a cross dissolve transition")
        assert result is not None
        assert result["command_id"] == "transition"
        assert result["params"].get("type") == "Cross Dissolve"
        
        result = registry.match_nlp_intent("add a 2.5s fade transition")
        assert result is not None
        assert result["command_id"] == "transition"
        assert result["params"].get("type") == "Fade"
        assert result["params"].get("duration") == 2.5
    
    def test_match_nlp_intent_marker(self, registry):
        """Test matching NLP intent for marker command"""
        result = registry.match_nlp_intent("add a marker named 'Scene 1'")
        assert result is not None
        assert result["command_id"] == "marker"
        assert result["params"].get("name") == "Scene 1"
        
        result = registry.match_nlp_intent("set a red marker")
        assert result is not None
        assert result["command_id"] == "marker"
        assert result["params"].get("color") == "Red"
    
    def test_no_match_nlp_intent(self, registry):
        """Test no match for NLP intent"""
        result = registry.match_nlp_intent("do something completely different")
        assert result is None


class TestCommandExecutor:
    """Tests for the CommandExecutor class"""
    
    @pytest.fixture
    def mock_registry(self):
        """Create a mock command registry"""
        registry = MagicMock()
        registry.get_command.return_value = MockCommand()
        registry.match_nlp_intent.return_value = {
            "command_id": "test",
            "params": {"test_param": "test_value"}
        }
        return registry
    
    @pytest.fixture
    def executor(self, mock_registry):
        """Create a command executor with a mock registry"""
        return CommandExecutor(mock_registry)
    
    def test_executor_initialization(self, executor, mock_registry):
        """Test executor initialization"""
        assert executor.registry == mock_registry
        assert executor.feedback_enabled is True
        assert len(executor.history) == 0
    
    def test_execute_from_text_success(self, executor, mock_registry):
        """Test successful execution from text"""
        result = executor.execute_from_text("test command")
        
        assert mock_registry.match_nlp_intent.called_with("test command")
        assert mock_registry.get_command.called_with("test")
        assert result["status"] == "success"
        assert "feedback" in result
        assert len(executor.history) == 1
    
    def test_execute_from_text_no_match(self, executor, mock_registry):
        """Test execution with no NLP match"""
        mock_registry.match_nlp_intent.return_value = None
        
        result = executor.execute_from_text("unknown command")
        
        assert result["status"] == "error"
        assert "Could not understand command" in result["message"]
        assert len(executor.history) == 1
    
    def test_execute_from_text_command_not_found(self, executor, mock_registry):
        """Test execution with command not found"""
        mock_registry.get_command.return_value = None
        
        result = executor.execute_from_text("test command")
        
        assert result["status"] == "error"
        assert "not found" in result["message"]
        assert len(executor.history) == 1
    
    def test_execute_from_text_command_fails(self, executor, mock_registry):
        """Test execution with command failure"""
        mock_registry.get_command.return_value = MockCommand(should_fail=True)
        
        result = executor.execute_from_text("test command")
        
        assert result["status"] == "error"
        assert "Test command failed" in result["message"]
        assert "feedback" in result
        assert len(executor.history) == 1
    
    def test_get_last_feedback_with_history(self, executor):
        """Test getting last feedback with history"""
        # Add a mock result to history
        executor.history.append({
            "command_id": "test",
            "params": {},
            "result": {"status": "success", "feedback": "Test feedback"},
            "original_text": "test command"
        })
        
        feedback = executor.get_last_feedback()
        assert feedback == "Test feedback"
    
    def test_get_last_feedback_no_history(self, executor):
        """Test getting last feedback with no history"""
        feedback = executor.get_last_feedback()
        assert feedback is None 
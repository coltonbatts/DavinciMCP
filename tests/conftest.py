"""
Pytest configuration file with shared fixtures.
"""

import os
import sys
import pytest
from unittest.mock import MagicMock, patch

# Add the root directory to the Python path to ensure imports work correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from davincimcp.core.resolve_controller import ResolveController
from davincimcp.core.gemini_handler import GeminiAPIHandler
from davincimcp.utils.config import Config


@pytest.fixture
def mock_config():
    """Fixture for a mock Config object."""
    config = MagicMock(spec=Config)
    config.gemini_api_key = "mock_api_key"
    config.resolve_modules_path = "/mock/path/to/modules"
    config.get.return_value = None
    return config


@pytest.fixture
def mock_bmd():
    """Fixture for a mock bmd module."""
    mock = MagicMock()
    mock.scriptapp.return_value = MagicMock()
    return mock


@pytest.fixture
def mock_resolve_controller(mock_bmd):
    """Fixture for a mock ResolveController."""
    with patch('davincimcp.core.resolve_controller.bmd', mock_bmd):
        controller = ResolveController()
        controller.connect = MagicMock(return_value=True)
        controller.connected = True
        controller.resolve = MagicMock()
        controller.project_manager = MagicMock()
        controller.current_project = MagicMock()
        
        # Setup common methods
        controller.get_project_info.return_value = {
            "name": "Test Project",
            "timeline_count": 1
        }
        
        timeline_mock = MagicMock()
        timeline_mock.GetName.return_value = "Test Timeline"
        controller.get_current_timeline.return_value = timeline_mock
        
        media_pool_mock = MagicMock()
        controller.get_media_pool.return_value = media_pool_mock
        
        yield controller


@pytest.fixture
def mock_gemini_handler():
    """Fixture for a mock GeminiAPIHandler."""
    handler = MagicMock(spec=GeminiAPIHandler)
    handler.initialized = True
    handler.generate_response.return_value = "This is a mock AI response"
    return handler


@pytest.fixture
def test_env_vars():
    """Fixture to set and clean up test environment variables."""
    # Save original env vars
    original_env = os.environ.copy()
    
    # Set test vars
    os.environ["GEMINI_API_KEY"] = "test_api_key"
    os.environ["LOG_LEVEL"] = "DEBUG"
    os.environ["GEMINI_TEMPERATURE"] = "0.5"
    os.environ["GEMINI_MAX_TOKENS"] = "512"
    os.environ["FEEDBACK_ENABLED"] = "true"
    
    yield
    
    # Restore original env vars
    os.environ.clear()
    os.environ.update(original_env) 
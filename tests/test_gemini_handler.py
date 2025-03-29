#!/usr/bin/env python3
"""
Tests for the Gemini API handler.
"""

import pytest
from unittest.mock import MagicMock, patch
import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from davincimcp.core.gemini_handler import GeminiAPIHandler

class MockGeminiResponse:
    """Mock for Gemini API response"""
    
    def __init__(self, text):
        self.text = text


@pytest.fixture
def mock_genai():
    """Create a mock for google.generativeai"""
    with patch('google.generativeai.configure') as mock_configure:
        with patch('google.generativeai.GenerativeModel') as mock_model_class:
            # Set up the mock model instance
            mock_model = MagicMock()
            mock_model.generate_content.return_value = MockGeminiResponse("Mock response")
            mock_model.start_chat.return_value = MagicMock()
            
            # Set the model instance as the return value of GenerativeModel
            mock_model_class.return_value = mock_model
            
            yield {
                'configure': mock_configure,
                'GenerativeModel': mock_model_class,
                'model_instance': mock_model
            }


class TestGeminiAPIHandler:
    """Tests for the GeminiAPIHandler class"""
    
    def test_initialization_without_key(self):
        """Test initialization without API key"""
        handler = GeminiAPIHandler()
        assert handler.initialized is False
        assert handler.api_key is None
    
    def test_initialization_with_key(self, mock_genai):
        """Test initialization with API key"""
        handler = GeminiAPIHandler("test_api_key")
        
        assert handler.initialized is True
        assert handler.api_key == "test_api_key"
        mock_genai['configure'].assert_called_once_with(api_key="test_api_key")
        mock_genai['GenerativeModel'].assert_called_once_with('gemini-pro')
    
    def test_initialize_method(self, mock_genai):
        """Test initialize method"""
        handler = GeminiAPIHandler()
        assert handler.initialized is False
        
        result = handler.initialize("test_api_key")
        
        assert result is True
        assert handler.initialized is True
        assert handler.api_key == "test_api_key"
        mock_genai['configure'].assert_called_once_with(api_key="test_api_key")
    
    def test_initialize_method_fails(self):
        """Test initialize method failing"""
        with patch('google.generativeai.configure', side_effect=Exception("API error")):
            handler = GeminiAPIHandler()
            result = handler.initialize("test_api_key")
            
            assert result is False
            assert handler.initialized is False
    
    def test_generate_response(self, mock_genai):
        """Test generate_response method"""
        handler = GeminiAPIHandler("test_api_key")
        response = handler.generate_response("Test prompt")
        
        assert response == "Mock response"
        mock_genai['model_instance'].generate_content.assert_called_once_with("Test prompt")
    
    def test_generate_response_not_initialized(self):
        """Test generate_response when not initialized"""
        handler = GeminiAPIHandler()
        response = handler.generate_response("Test prompt")
        
        assert "Error: API not initialized" in response
    
    def test_generate_response_api_error(self, mock_genai):
        """Test generate_response with API error"""
        mock_genai['model_instance'].generate_content.side_effect = Exception("API error")
        
        handler = GeminiAPIHandler("test_api_key")
        response = handler.generate_response("Test prompt")
        
        assert "Error:" in response
        assert "API error" in response
    
    def test_generate_with_config(self, mock_genai):
        """Test generate_with_config method"""
        handler = GeminiAPIHandler("test_api_key")
        response = handler.generate_with_config(
            "Test prompt",
            temperature=0.8,
            max_output_tokens=2048
        )
        
        assert response == "Mock response"
        
        # Check that it was called with the correct custom config
        mock_genai['model_instance'].generate_content.assert_called_once()
        args, kwargs = mock_genai['model_instance'].generate_content.call_args
        
        assert args[0] == "Test prompt"
        assert "generation_config" in kwargs
        assert kwargs["generation_config"]["temperature"] == 0.8
        assert kwargs["generation_config"]["max_output_tokens"] == 2048
    
    def test_chat_session(self, mock_genai):
        """Test chat_session method"""
        # Set up the mock chat behavior
        mock_chat = MagicMock()
        mock_chat.send_message.return_value = MockGeminiResponse("Mock chat response")
        mock_genai['model_instance'].start_chat.return_value = mock_chat
        
        handler = GeminiAPIHandler("test_api_key")
        
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "model", "content": "Hi there"},
            {"role": "user", "content": "How are you?"}
        ]
        
        response = handler.chat_session(messages)
        
        assert response == "Mock chat response"
        mock_genai['model_instance'].start_chat.assert_called_once_with(history=[])
        
        # Should have sent two user messages
        assert mock_chat.send_message.call_count == 2
        mock_chat.send_message.assert_any_call("Hello")
        mock_chat.send_message.assert_any_call("How are you?") 
#!/usr/bin/env python3
"""
Tests for the configuration module.
"""

import os
import platform
import pytest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from davincimcp.utils.config import Config

class TestConfig:
    """Tests for the Config class"""
    
    def test_config_initialization(self):
        """Test basic config initialization"""
        config = Config()
        assert isinstance(config.resolve_modules_path, str)
        assert isinstance(config.config_values, dict)
    
    def test_platform_specific_paths(self):
        """Test platform-specific path determination"""
        with patch('platform.system', return_value='Darwin'):
            config = Config()
            assert 'Library/Application Support' in config.resolve_modules_path
        
        with patch('platform.system', return_value='Windows'):
            config = Config()
            assert 'Blackmagic Design' in config.resolve_modules_path
            assert '\\' in config.resolve_modules_path or '/' in config.resolve_modules_path
        
        with patch('platform.system', return_value='Linux'):
            config = Config()
            assert '/opt/resolve' in config.resolve_modules_path
    
    def test_load_config_default_values(self):
        """Test loading configuration with default values"""
        with patch.dict(os.environ, {}, clear=True):
            config = Config()
            assert config.config_values['log_level'] == 'INFO'
            assert config.config_values['gemini_temperature'] == 0.7
            assert config.config_values['gemini_max_tokens'] == 1024
            assert config.config_values['feedback_enabled'] is True
    
    def test_load_config_custom_values(self):
        """Test loading configuration with custom environment values"""
        mock_env = {
            'LOG_LEVEL': 'DEBUG',
            'GEMINI_TEMPERATURE': '0.5',
            'GEMINI_MAX_TOKENS': '2048',
            'FEEDBACK_ENABLED': 'False'
        }
        
        with patch.dict(os.environ, mock_env, clear=True):
            config = Config()
            assert config.config_values['log_level'] == 'DEBUG'
            assert config.config_values['gemini_temperature'] == 0.5
            assert config.config_values['gemini_max_tokens'] == 2048
            assert config.config_values['feedback_enabled'] is False
    
    def test_get_config_value(self):
        """Test getting configuration values"""
        config = Config()
        
        # Test existing keys
        assert config.get('log_level') == config.config_values['log_level']
        
        # Test default value for non-existent key
        assert config.get('non_existent_key') is None
        assert config.get('non_existent_key', 'default') == 'default'
    
    def test_append_resolve_modules_to_path(self):
        """Test appending Resolve modules path to sys.path"""
        with patch('os.path.exists', return_value=True):
            config = Config()
            original_path_length = len(sys.path)
            result = config.append_resolve_modules_to_path()
            assert result is True
            assert len(sys.path) > original_path_length
            assert config.resolve_modules_path in sys.path
    
    def test_append_resolve_modules_path_not_exists(self):
        """Test appending non-existent Resolve modules path"""
        with patch('os.path.exists', return_value=False):
            config = Config()
            original_path_length = len(sys.path)
            result = config.append_resolve_modules_to_path()
            assert result is False
            assert len(sys.path) == original_path_length 
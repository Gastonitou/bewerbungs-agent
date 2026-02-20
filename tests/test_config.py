"""
Tests for configuration management
"""
import os
import pytest
import tempfile
from pathlib import Path

from src.bewerbungs_agent.config import Config


class TestConfig:
    """Test configuration management"""
    
    def test_default_config(self):
        """Test default configuration loading"""
        config = Config('nonexistent.yaml')
        
        assert config.get('gmail.email') is not None
        assert config.get('openai.model') == 'gpt-4'
        assert config.get('agent.features.classify_emails') is True
    
    def test_get_nested_config(self):
        """Test getting nested configuration values"""
        config = Config('nonexistent.yaml')
        
        gmail_config = config.get_gmail_config()
        assert 'email' in gmail_config
        assert 'folders' in gmail_config
        
        openai_config = config.get_openai_config()
        assert 'model' in openai_config
    
    def test_get_with_default(self):
        """Test getting config with default value"""
        config = Config('nonexistent.yaml')
        
        value = config.get('nonexistent.key', 'default_value')
        assert value == 'default_value'
    
    def test_yaml_config_loading(self):
        """Test loading from YAML file"""
        # Create temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
gmail:
  email: test@example.com
  folders:
    rejections: TestFolder
openai:
  model: gpt-3.5-turbo
  temperature: 0.5
""")
            temp_path = f.name
        
        try:
            config = Config(temp_path)
            
            assert config.get('gmail.email') == 'test@example.com'
            assert config.get('gmail.folders.rejections') == 'TestFolder'
            assert config.get('openai.model') == 'gpt-3.5-turbo'
            assert config.get('openai.temperature') == 0.5
        
        finally:
            os.unlink(temp_path)
    
    def test_environment_variable_config_path(self):
        """Test loading config from environment variable"""
        # Set environment variable
        os.environ['BEWERBUNGS_CONFIG'] = 'test_config.yaml'
        
        try:
            config = Config()
            # Should not raise exception even if file doesn't exist
            assert config is not None
        finally:
            if 'BEWERBUNGS_CONFIG' in os.environ:
                del os.environ['BEWERBUNGS_CONFIG']

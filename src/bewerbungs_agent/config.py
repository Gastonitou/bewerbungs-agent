"""
Configuration management for the Bewerbungs-Agent
"""
import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path


class Config:
    """Configuration manager for the agent"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration
        
        Args:
            config_path: Path to configuration file. Defaults to config.yaml
        """
        if config_path is None:
            config_path = os.environ.get('BEWERBUNGS_CONFIG', 'config.yaml')
        
        self.config_path = config_path
        self._config: Dict[str, Any] = {}
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f)
        else:
            # Use default configuration for testing
            self._config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for testing"""
        return {
            'gmail': {
                'email': os.environ.get('GMAIL_EMAIL', 'test@example.com'),
                'credentials_file': os.environ.get('GMAIL_CREDENTIALS', 'credentials.json'),
                'token_file': os.environ.get('GMAIL_TOKEN', 'token.json'),
                'folders': {
                    'rejections': 'Absagen',
                    'acceptances': 'Zusagen',
                    'processed': 'Verarbeitet'
                }
            },
            'openai': {
                'api_key': os.environ.get('OPENAI_API_KEY', ''),
                'model': os.environ.get('OPENAI_MODEL', 'gpt-4'),
                'temperature': float(os.environ.get('OPENAI_TEMPERATURE', '0.3'))
            },
            'agent': {
                'features': {
                    'classify_emails': True,
                    'analyze_attachments': True,
                    'move_to_folders': True,
                    'team_distribution': True
                },
                'team': [
                    {'name': 'Reviewer', 'role': 'Reviews application documents'},
                    {'name': 'Feedback Writer', 'role': 'Writes feedback for applicants'},
                    {'name': 'Scheduler', 'role': 'Schedules interviews'}
                ]
            },
            'logging': {
                'level': os.environ.get('LOG_LEVEL', 'INFO'),
                'file': os.environ.get('LOG_FILE', 'logs/agent.log'),
                'console': True
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key (supports nested keys with dot notation)
        
        Args:
            key: Configuration key (e.g., 'gmail.email')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_gmail_config(self) -> Dict[str, Any]:
        """Get Gmail configuration"""
        return self._config.get('gmail', {})
    
    def get_openai_config(self) -> Dict[str, Any]:
        """Get OpenAI configuration"""
        return self._config.get('openai', {})
    
    def get_agent_config(self) -> Dict[str, Any]:
        """Get agent configuration"""
        return self._config.get('agent', {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration"""
        return self._config.get('logging', {})

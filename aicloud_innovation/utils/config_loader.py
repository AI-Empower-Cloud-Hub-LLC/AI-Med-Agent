"""
Configuration Loader
====================

Load and manage configuration for the enterprise framework.
"""

import os
import json
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigLoader:
    """
    Load configuration from various sources.
    
    Supports environment variables, JSON files, and AWS integration.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        
        if config_path and Path(config_path).exists():
            self.load_from_file(config_path)
    
    def load_from_file(self, file_path: str):
        """
        Load configuration from JSON file.
        
        Args:
            file_path: Path to JSON configuration file
        """
        with open(file_path, 'r') as f:
            self.config = json.load(f)
    
    def load_from_env(self, prefix: str = "AICLOUD_"):
        """
        Load configuration from environment variables.
        
        Args:
            prefix: Prefix for environment variables
        """
        env_config = {}
        for key, value in os.environ.items():
            if key.startswith(prefix):
                config_key = key[len(prefix):].lower()
                env_config[config_key] = value
        
        self.config.update(env_config)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """
        Set configuration value.
        
        Args:
            key: Configuration key
            value: Configuration value
        """
        self.config[key] = value
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get all configuration.
        
        Returns:
            Complete configuration dictionary
        """
        return self.config.copy()
    
    def merge(self, other_config: Dict[str, Any]):
        """
        Merge another configuration into this one.
        
        Args:
            other_config: Configuration to merge
        """
        self.config.update(other_config)

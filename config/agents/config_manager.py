"""
Configuration Manager
Manages agent configurations from multiple sources
"""

import yaml
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class ConfigManager:
    """
    Manages configuration for the agent framework
    Supports YAML files, environment variables, and AWS AppConfig
    """
    
    config_file: Optional[str] = None
    config_data: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Load configuration after initialization"""
        if self.config_file and os.path.exists(self.config_file):
            self.load_from_file(self.config_file)
        else:
            # Load default configuration
            self.load_defaults()
    
    def load_from_file(self, filepath: str) -> None:
        """
        Load configuration from YAML file
        
        Args:
            filepath: Path to YAML configuration file
        """
        with open(filepath, 'r') as f:
            self.config_data = yaml.safe_load(f) or {}
    
    def load_defaults(self) -> None:
        """Load default configuration"""
        self.config_data = {
            'agents': {
                'defaults': {
                    'max_retries': 3,
                    'timeout_seconds': 30,
                    'enable_logging': True,
                    'log_level': 'INFO'
                }
            },
            'orchestrator': {
                'max_agents': 100,
                'message_queue_size': 1000
            },
            'memory': {
                'working_memory_ttl_hours': 1,
                'max_memories_per_agent': 1000
            }
        }
    
    def get_agent_config(self, agent_type: str) -> Dict[str, Any]:
        """
        Get configuration for a specific agent type
        
        Args:
            agent_type: Type of agent (e.g., 'diagnosis', 'triage')
            
        Returns:
            Agent configuration dictionary
        """
        agents_config = self.config_data.get('agents', {})
        defaults = agents_config.get('defaults', {})
        agent_config = agents_config.get(agent_type, {})
        
        # Merge defaults with agent-specific config
        config = {**defaults, **agent_config}
        
        # Override with environment variables
        env_prefix = f"AGENT_{agent_type.upper()}_"
        for key in config.keys():
            env_key = env_prefix + key.upper()
            if env_key in os.environ:
                config[key] = os.environ[env_key]
        
        return config
    
    def get_orchestrator_config(self) -> Dict[str, Any]:
        """Get orchestrator configuration"""
        return self.config_data.get('orchestrator', {})
    
    def get_memory_config(self) -> Dict[str, Any]:
        """Get memory configuration"""
        return self.config_data.get('memory', {})
    
    def get_monitoring_config(self) -> Dict[str, Any]:
        """Get monitoring configuration"""
        return self.config_data.get('monitoring', {})
    
    def get_aws_config(self) -> Dict[str, Any]:
        """Get AWS integration configuration"""
        return self.config_data.get('aws', {})
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value by key (supports dot notation)
        
        Args:
            key: Configuration key (e.g., 'agents.defaults.max_retries')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config_data
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value
        
        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        keys = key.split('.')
        config = self.config_data
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save_to_file(self, filepath: str) -> None:
        """
        Save configuration to YAML file
        
        Args:
            filepath: Path to save configuration
        """
        with open(filepath, 'w') as f:
            yaml.dump(self.config_data, f, default_flow_style=False)

"""
Agent Helper Utilities
Common utility functions for agents
"""

import uuid
from typing import Any, Dict
from datetime import datetime


class AgentHelper:
    """Helper utilities for agent operations"""
    
    @staticmethod
    def generate_agent_id() -> str:
        """Generate a unique agent ID"""
        return str(uuid.uuid4())
    
    @staticmethod
    def generate_message_id() -> str:
        """Generate a unique message ID"""
        return str(uuid.uuid4())
    
    @staticmethod
    def timestamp_now() -> str:
        """Get current timestamp in ISO format"""
        return datetime.utcnow().isoformat()
    
    @staticmethod
    def validate_config(config: Dict[str, Any], required_fields: list[str]) -> bool:
        """
        Validate that a config has required fields
        
        Args:
            config: Configuration dictionary
            required_fields: List of required field names
            
        Returns:
            True if all required fields are present
        """
        return all(field in config for field in required_fields)
    
    @staticmethod
    def safe_get(data: Dict[str, Any], key: str, default: Any = None) -> Any:
        """
        Safely get a value from dictionary
        
        Args:
            data: Dictionary to get value from
            key: Key to retrieve
            default: Default value if key not found
            
        Returns:
            Value or default
        """
        return data.get(key, default)
    
    @staticmethod
    def format_error(error: Exception) -> Dict[str, str]:
        """
        Format an exception as a dictionary
        
        Args:
            error: Exception to format
            
        Returns:
            Dictionary with error details
        """
        return {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'timestamp': datetime.utcnow().isoformat()
        }

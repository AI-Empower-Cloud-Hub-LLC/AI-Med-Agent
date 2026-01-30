"""
Message Validators
Validation utilities for agent messages
"""

from typing import Dict, Any, List, Optional
from agents.base.protocol import AgentMessage, MessageType


class MessageValidator:
    """Validates agent messages and payloads"""
    
    @staticmethod
    def validate_message(message: AgentMessage) -> tuple[bool, Optional[str]]:
        """
        Validate a message structure
        
        Args:
            message: Message to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not message.message_id:
            return False, "Missing message_id"
        
        if not message.sender_id:
            return False, "Missing sender_id"
        
        if not message.receiver_id:
            return False, "Missing receiver_id"
        
        if not isinstance(message.message_type, MessageType):
            return False, "Invalid message_type"
        
        if not isinstance(message.payload, dict):
            return False, "Payload must be a dictionary"
        
        return True, None
    
    @staticmethod
    def validate_payload(payload: Dict[str, Any], required_fields: List[str]) -> tuple[bool, Optional[str]]:
        """
        Validate that payload contains required fields
        
        Args:
            payload: Payload to validate
            required_fields: List of required field names
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        missing_fields = [field for field in required_fields if field not in payload]
        
        if missing_fields:
            return False, f"Missing required fields: {', '.join(missing_fields)}"
        
        return True, None
    
    @staticmethod
    def validate_vital_signs(vital_signs: Dict[str, float]) -> tuple[bool, Optional[str]]:
        """
        Validate vital signs data
        
        Args:
            vital_signs: Vital signs dictionary
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check that all values are numeric
        for key, value in vital_signs.items():
            if not isinstance(value, (int, float)):
                return False, f"Vital sign '{key}' must be numeric, got {type(value).__name__}"
            
            if value < 0:
                return False, f"Vital sign '{key}' cannot be negative"
        
        # Validate specific vital signs if present
        if 'heart_rate' in vital_signs:
            if vital_signs['heart_rate'] > 300:
                return False, "Heart rate exceeds maximum possible value"
        
        if 'oxygen_saturation' in vital_signs:
            if vital_signs['oxygen_saturation'] > 100:
                return False, "Oxygen saturation cannot exceed 100%"
        
        if 'temperature' in vital_signs:
            if vital_signs['temperature'] > 45 or vital_signs['temperature'] < 30:
                return False, "Temperature out of possible range"
        
        return True, None

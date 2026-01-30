"""
Agent Logger
Enhanced logging for agent activities
"""

import logging
from typing import Any, Dict
from datetime import datetime
import json


class AgentLogger:
    """
    Enhanced logger for agent activities with structured logging
    """
    
    def __init__(self, agent_id: str, log_level: str = "INFO"):
        """
        Initialize agent logger
        
        Args:
            agent_id: Agent ID
            log_level: Logging level
        """
        self.agent_id = agent_id
        self.logger = logging.getLogger(f"Agent:{agent_id[:8]}")
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Add handler if not already present
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def log_event(self, event_type: str, message: str, data: Dict[str, Any] = None) -> None:
        """
        Log a structured event
        
        Args:
            event_type: Type of event
            message: Log message
            data: Additional structured data
        """
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'agent_id': self.agent_id,
            'event_type': event_type,
            'message': message
        }
        
        if data:
            log_entry['data'] = data
        
        self.logger.info(json.dumps(log_entry))
    
    def log_error(self, error: Exception, context: Dict[str, Any] = None) -> None:
        """
        Log an error with context
        
        Args:
            error: Exception that occurred
            context: Additional context
        """
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'agent_id': self.agent_id,
            'event_type': 'error',
            'error_type': type(error).__name__,
            'error_message': str(error)
        }
        
        if context:
            log_entry['context'] = context
        
        self.logger.error(json.dumps(log_entry))
    
    def log_performance(self, operation: str, duration_ms: float, success: bool = True) -> None:
        """
        Log performance metrics
        
        Args:
            operation: Operation name
            duration_ms: Duration in milliseconds
            success: Whether operation succeeded
        """
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'agent_id': self.agent_id,
            'event_type': 'performance',
            'operation': operation,
            'duration_ms': duration_ms,
            'success': success
        }
        
        self.logger.info(json.dumps(log_entry))

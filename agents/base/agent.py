"""
Base Agent Class
Core agent implementation with lifecycle management, state handling, and monitoring
"""

from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, List
from datetime import datetime
import logging
import uuid

from agents.base.protocol import AgentProtocol, AgentMessage, MessageType


class AgentStatus(Enum):
    """Agent lifecycle status"""
    INITIALIZING = "initializing"
    IDLE = "idle"
    PROCESSING = "processing"
    ERROR = "error"
    STOPPED = "stopped"


@dataclass
class AgentConfig:
    """Configuration for an agent"""
    agent_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agent_name: str = "BaseAgent"
    agent_type: str = "base"
    max_retries: int = 3
    timeout_seconds: int = 30
    enable_logging: bool = True
    log_level: str = "INFO"
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseAgent(ABC):
    """
    Base class for all AI agents in the framework.
    Provides core functionality for lifecycle management, communication, and monitoring.
    """
    
    def __init__(self, config: AgentConfig, protocol: Optional[AgentProtocol] = None):
        """
        Initialize the agent
        
        Args:
            config: Agent configuration
            protocol: Communication protocol instance (shared across agents)
        """
        self.config = config
        self.agent_id = config.agent_id
        self.status = AgentStatus.INITIALIZING
        self.protocol = protocol or AgentProtocol()
        
        # Set up logging
        self.logger = logging.getLogger(f"{config.agent_name}:{self.agent_id[:8]}")
        if config.enable_logging:
            self.logger.setLevel(getattr(logging, config.log_level))
        
        # State management
        self.state: Dict[str, Any] = {}
        self.created_at = datetime.utcnow()
        self.last_activity = datetime.utcnow()
        self.processing_count = 0
        self.error_count = 0
        
        # Message history
        self.message_history: List[AgentMessage] = []
        
        self.logger.info(f"Agent {config.agent_name} initialized with ID {self.agent_id}")
    
    def start(self) -> None:
        """Start the agent"""
        self.logger.info(f"Starting agent {self.config.agent_name}")
        self._on_start()
        self.status = AgentStatus.IDLE
        self.last_activity = datetime.utcnow()
    
    def stop(self) -> None:
        """Stop the agent"""
        self.logger.info(f"Stopping agent {self.config.agent_name}")
        self._on_stop()
        self.status = AgentStatus.STOPPED
    
    def process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """
        Process an incoming message
        
        Args:
            message: Message to process
            
        Returns:
            Response message if applicable
        """
        self.status = AgentStatus.PROCESSING
        self.processing_count += 1
        self.last_activity = datetime.utcnow()
        self.message_history.append(message)
        
        try:
            self.logger.debug(f"Processing message {message.message_id} from {message.sender_id}")
            
            # Handle different message types
            if message.message_type == MessageType.REQUEST:
                response = self._handle_request(message)
            elif message.message_type == MessageType.RESPONSE:
                response = self._handle_response(message)
            elif message.message_type == MessageType.NOTIFICATION:
                response = self._handle_notification(message)
            else:
                response = None
            
            self.status = AgentStatus.IDLE
            return response
            
        except Exception as e:
            self.logger.error(f"Error processing message: {str(e)}")
            self.error_count += 1
            self.status = AgentStatus.ERROR
            return self._create_error_response(message, str(e))
    
    def send_message(self, receiver_id: str, payload: Dict[str, Any], 
                     message_type: MessageType = MessageType.REQUEST) -> bool:
        """
        Send a message to another agent
        
        Args:
            receiver_id: ID of the receiving agent
            payload: Message payload
            message_type: Type of message
            
        Returns:
            True if message was sent successfully
        """
        message = AgentMessage(
            sender_id=self.agent_id,
            receiver_id=receiver_id,
            message_type=message_type,
            payload=payload
        )
        
        self.message_history.append(message)
        return self.protocol.send_message(message)
    
    def receive_messages(self) -> List[AgentMessage]:
        """Receive all pending messages"""
        return self.protocol.receive_messages(self.agent_id)
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status and metrics"""
        return {
            'agent_id': self.agent_id,
            'agent_name': self.config.agent_name,
            'agent_type': self.config.agent_type,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'last_activity': self.last_activity.isoformat(),
            'processing_count': self.processing_count,
            'error_count': self.error_count,
            'message_count': len(self.message_history),
            'state': self.state
        }
    
    def update_state(self, key: str, value: Any) -> None:
        """Update agent state"""
        self.state[key] = value
        self.last_activity = datetime.utcnow()
    
    def get_state(self, key: str, default: Any = None) -> Any:
        """Get value from agent state"""
        return self.state.get(key, default)
    
    @abstractmethod
    def _handle_request(self, message: AgentMessage) -> Optional[AgentMessage]:
        """
        Handle a request message (must be implemented by subclasses)
        
        Args:
            message: Request message
            
        Returns:
            Response message if applicable
        """
        pass
    
    def _handle_response(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Handle a response message"""
        self.logger.debug(f"Received response: {message.message_id}")
        return None
    
    def _handle_notification(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Handle a notification message"""
        self.logger.debug(f"Received notification: {message.message_id}")
        return None
    
    def _on_start(self) -> None:
        """Called when agent starts (can be overridden)"""
        pass
    
    def _on_stop(self) -> None:
        """Called when agent stops (can be overridden)"""
        pass
    
    def _create_error_response(self, original_message: AgentMessage, error: str) -> AgentMessage:
        """Create an error response message"""
        return AgentMessage(
            sender_id=self.agent_id,
            receiver_id=original_message.sender_id,
            message_type=MessageType.ERROR,
            payload={'error': error},
            correlation_id=original_message.message_id
        )

"""
Agent Communication Protocol
Defines message formats and communication standards for inter-agent communication
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from datetime import datetime
import uuid


class MessageType(Enum):
    """Types of messages agents can exchange"""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    ERROR = "error"
    HEARTBEAT = "heartbeat"


@dataclass
class AgentMessage:
    """Standard message format for agent communication"""
    
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender_id: str = ""
    receiver_id: str = ""
    message_type: MessageType = MessageType.REQUEST
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    correlation_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        return {
            'message_id': self.message_id,
            'sender_id': self.sender_id,
            'receiver_id': self.receiver_id,
            'message_type': self.message_type.value,
            'payload': self.payload,
            'timestamp': self.timestamp.isoformat(),
            'correlation_id': self.correlation_id,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentMessage':
        """Create message from dictionary"""
        return cls(
            message_id=data.get('message_id', str(uuid.uuid4())),
            sender_id=data.get('sender_id', ''),
            receiver_id=data.get('receiver_id', ''),
            message_type=MessageType(data.get('message_type', 'request')),
            payload=data.get('payload', {}),
            timestamp=datetime.fromisoformat(data['timestamp']) if 'timestamp' in data else datetime.utcnow(),
            correlation_id=data.get('correlation_id'),
            metadata=data.get('metadata', {})
        )


class AgentProtocol:
    """
    Protocol handler for agent communication
    Manages message routing, validation, and delivery
    """
    
    def __init__(self):
        self.message_queue: Dict[str, list] = {}
    
    def send_message(self, message: AgentMessage) -> bool:
        """
        Send message to another agent
        
        Args:
            message: AgentMessage to send
            
        Returns:
            True if message was queued successfully
        """
        receiver_id = message.receiver_id
        if receiver_id not in self.message_queue:
            self.message_queue[receiver_id] = []
        
        self.message_queue[receiver_id].append(message)
        return True
    
    def receive_messages(self, agent_id: str) -> list[AgentMessage]:
        """
        Receive all pending messages for an agent
        
        Args:
            agent_id: ID of the agent receiving messages
            
        Returns:
            List of pending messages
        """
        if agent_id in self.message_queue:
            messages = self.message_queue[agent_id].copy()
            self.message_queue[agent_id] = []
            return messages
        return []
    
    def create_request(self, sender_id: str, receiver_id: str, payload: Dict[str, Any]) -> AgentMessage:
        """Create a request message"""
        return AgentMessage(
            sender_id=sender_id,
            receiver_id=receiver_id,
            message_type=MessageType.REQUEST,
            payload=payload
        )
    
    def create_response(self, original_message: AgentMessage, payload: Dict[str, Any]) -> AgentMessage:
        """Create a response to a request"""
        return AgentMessage(
            sender_id=original_message.receiver_id,
            receiver_id=original_message.sender_id,
            message_type=MessageType.RESPONSE,
            payload=payload,
            correlation_id=original_message.message_id
        )

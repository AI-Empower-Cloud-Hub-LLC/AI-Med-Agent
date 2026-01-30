"""
Base Agent Architecture
=======================

Core abstract base class for all AI agents in the framework.
Provides standard interface and lifecycle management.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum
import uuid
from datetime import datetime
import logging

# Constants
MAX_MEMORY_SIZE = 100  # Maximum number of items to keep in agent memory


class AgentStatus(Enum):
    """Agent operational status"""
    INITIALIZING = "initializing"
    READY = "ready"
    PROCESSING = "processing"
    IDLE = "idle"
    ERROR = "error"
    SHUTDOWN = "shutdown"


@dataclass
class AgentConfig:
    """Configuration for an AI agent"""
    name: str
    agent_type: str
    description: str = ""
    capabilities: List[str] = field(default_factory=list)
    max_concurrent_tasks: int = 5
    timeout_seconds: int = 300
    retry_attempts: int = 3
    priority: int = 1  # 1=low, 5=high
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # AI Model configuration
    model_name: str = "gpt-4"
    model_temperature: float = 0.7
    max_tokens: int = 2000
    
    # Enterprise features
    enable_monitoring: bool = True
    enable_audit_log: bool = True
    enable_cache: bool = True


class BaseAgent(ABC):
    """
    Abstract base class for all AI agents.
    
    All agents must inherit from this class and implement the required methods.
    Provides enterprise-level features like monitoring, logging, and state management.
    """
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.agent_id = str(uuid.uuid4())
        self.status = AgentStatus.INITIALIZING
        self.created_at = datetime.now()
        self.last_active = datetime.now()
        
        # State management
        self.state: Dict[str, Any] = {}
        self.memory: List[Dict[str, Any]] = []
        
        # Statistics
        self.tasks_completed = 0
        self.tasks_failed = 0
        self.total_processing_time = 0.0
        
        # Setup logging
        self.logger = logging.getLogger(f"agent.{self.config.name}")
        self.logger.setLevel(logging.INFO)
        
        self._initialize()
    
    def _initialize(self):
        """Internal initialization logic"""
        self.logger.info(f"Initializing agent: {self.config.name} (ID: {self.agent_id})")
        self.status = AgentStatus.READY
    
    @abstractmethod
    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a task and return results.
        
        Args:
            task: Task definition with required parameters
            
        Returns:
            Processing results with status and output
        """
        pass
    
    @abstractmethod
    def validate_task(self, task: Dict[str, Any]) -> bool:
        """
        Validate if this agent can handle the given task.
        
        Args:
            task: Task to validate
            
        Returns:
            True if agent can handle the task, False otherwise
        """
        pass
    
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task with full lifecycle management.
        
        Args:
            task: Task to execute
            
        Returns:
            Execution result
        """
        start_time = datetime.now()
        self.status = AgentStatus.PROCESSING
        self.last_active = start_time
        
        try:
            # Validate task
            if not self.validate_task(task):
                raise ValueError(f"Task validation failed for agent {self.config.name}")
            
            # Log task execution
            self.logger.info(f"Executing task: {task.get('task_id', 'unknown')}")
            
            # Process the task
            result = self.process(task)
            
            # Update statistics
            self.tasks_completed += 1
            processing_time = (datetime.now() - start_time).total_seconds()
            self.total_processing_time += processing_time
            
            # Update memory
            if self.config.enable_cache:
                self._update_memory(task, result)
            
            self.status = AgentStatus.IDLE
            
            return {
                "status": "success",
                "agent_id": self.agent_id,
                "agent_name": self.config.name,
                "task_id": task.get("task_id"),
                "result": result,
                "processing_time": processing_time,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.tasks_failed += 1
            self.status = AgentStatus.ERROR
            self.logger.error(f"Task execution failed: {str(e)}")
            
            return {
                "status": "error",
                "agent_id": self.agent_id,
                "agent_name": self.config.name,
                "task_id": task.get("task_id"),
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _update_memory(self, task: Dict[str, Any], result: Dict[str, Any]):
        """Update agent memory with task and result"""
        self.memory.append({
            "task": task,
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep memory size manageable
        if len(self.memory) > MAX_MEMORY_SIZE:
            self.memory = self.memory[-MAX_MEMORY_SIZE:]
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status and statistics"""
        return {
            "agent_id": self.agent_id,
            "name": self.config.name,
            "type": self.config.agent_type,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "last_active": self.last_active.isoformat(),
            "tasks_completed": self.tasks_completed,
            "tasks_failed": self.tasks_failed,
            "avg_processing_time": (
                self.total_processing_time / self.tasks_completed 
                if self.tasks_completed > 0 else 0
            ),
            "capabilities": self.config.capabilities,
            "memory_size": len(self.memory)
        }
    
    def reset(self):
        """Reset agent state and statistics"""
        self.state = {}
        self.memory = []
        self.tasks_completed = 0
        self.tasks_failed = 0
        self.total_processing_time = 0.0
        self.status = AgentStatus.READY
        self.logger.info(f"Agent {self.config.name} has been reset")
    
    def shutdown(self):
        """Gracefully shutdown the agent"""
        self.logger.info(f"Shutting down agent: {self.config.name}")
        self.status = AgentStatus.SHUTDOWN
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self.config.name}', id='{self.agent_id[:8]}...', status='{self.status.value}')>"

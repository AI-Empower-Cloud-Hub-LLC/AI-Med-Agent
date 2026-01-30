"""Agent state management for autonomous operations"""

import logging
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class AgentStatus(Enum):
    """Agent execution status"""
    IDLE = "idle"
    RUNNING = "running"
    EVALUATING = "evaluating"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class DecisionOutcome(Enum):
    """Possible outcomes of agent decisions"""
    PROCEED = "proceed"
    REQUIRE_APPROVAL = "require_approval"
    SKIP = "skip"
    RETRY = "retry"
    ABORT = "abort"


@dataclass
class AgentAction:
    """Represents a single action to be executed"""
    action_type: str
    description: str
    parameters: Dict[str, Any]
    requires_approval: bool = False
    priority: int = 0
    retry_count: int = 0
    max_retries: int = 3
    status: str = "pending"
    result: Optional[Any] = None
    error: Optional[str] = None
    created_at: str = None
    completed_at: Optional[str] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()


class StateManager:
    """Manage agent state across autonomous operations"""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.status = AgentStatus.IDLE
        self.current_action: Optional[AgentAction] = None
        self.action_history: List[AgentAction] = []
        self.decision_log: List[Dict[str, Any]] = []
        self.errors: List[str] = []
        self.metrics = {
            'actions_executed': 0,
            'actions_failed': 0,
            'decisions_made': 0,
            'approvals_required': 0,
        }
        logger.info(f"StateManager initialized for agent {agent_id}")

    def set_status(self, status: AgentStatus) -> None:
        """Update agent status"""
        self.status = status
        logger.info(f"Agent {self.agent_id} status changed to {status.value}")

    def create_action(
        self,
        action_type: str,
        description: str,
        parameters: Dict[str, Any],
        requires_approval: bool = False,
        priority: int = 0
    ) -> AgentAction:
        """Create a new action"""
        action = AgentAction(
            action_type=action_type,
            description=description,
            parameters=parameters,
            requires_approval=requires_approval,
            priority=priority
        )
        logger.debug(f"Created action: {action_type} - {description}")
        return action

    def queue_action(self, action: AgentAction) -> None:
        """Queue an action for execution"""
        self.current_action = action
        logger.info(f"Queued action: {action.action_type}")

    def complete_action(self, result: Any = None) -> None:
        """Mark current action as completed"""
        if self.current_action:
            self.current_action.status = "completed"
            self.current_action.result = result
            self.current_action.completed_at = datetime.now().isoformat()
            self.action_history.append(self.current_action)
            self.metrics['actions_executed'] += 1
            logger.info(f"Completed action: {self.current_action.action_type}")

    def fail_action(self, error: str) -> None:
        """Mark current action as failed"""
        if self.current_action:
            self.current_action.status = "failed"
            self.current_action.error = error
            self.current_action.completed_at = datetime.now().isoformat()
            self.action_history.append(self.current_action)
            self.metrics['actions_failed'] += 1
            self.errors.append(error)
            logger.error(f"Action failed: {self.current_action.action_type} - {error}")

    def log_decision(
        self,
        decision_type: str,
        outcome: DecisionOutcome,
        reasoning: str,
        data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log a decision made by the agent"""
        decision = {
            'timestamp': datetime.now().isoformat(),
            'type': decision_type,
            'outcome': outcome.value,
            'reasoning': reasoning,
            'data': data or {}
        }
        self.decision_log.append(decision)
        self.metrics['decisions_made'] += 1
        
        if outcome == DecisionOutcome.REQUIRE_APPROVAL:
            self.metrics['approvals_required'] += 1
        
        logger.info(f"Decision logged: {decision_type} -> {outcome.value}")

    def get_state_summary(self) -> Dict[str, Any]:
        """Get current state summary"""
        return {
            'agent_id': self.agent_id,
            'status': self.status.value,
            'current_action': asdict(self.current_action) if self.current_action else None,
            'total_actions': len(self.action_history),
            'total_decisions': len(self.decision_log),
            'metrics': self.metrics,
            'errors': self.errors[-10:],  # Last 10 errors
        }

    def export_history(self) -> Dict[str, Any]:
        """Export complete operation history"""
        return {
            'agent_id': self.agent_id,
            'actions': [asdict(action) for action in self.action_history],
            'decisions': self.decision_log,
            'metrics': self.metrics,
            'errors': self.errors,
        }

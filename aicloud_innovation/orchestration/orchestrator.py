"""
Agent Orchestrator
==================

Coordinates multiple agents to work together on complex tasks.
Manages task distribution, workflow execution, and result aggregation.
"""

from typing import Dict, List, Any, Optional
from enum import Enum
import logging
from datetime import datetime
import uuid

from ..agents.base_agent import BaseAgent, AgentStatus
from ..agents.agent_registry import AgentRegistry


class WorkflowStatus(Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentOrchestrator:
    """
    Orchestrates multiple agents to execute complex workflows.
    
    Manages task routing, agent coordination, and result aggregation.
    """
    
    def __init__(self, registry: AgentRegistry):
        self.registry = registry
        self.workflows: Dict[str, Dict] = {}
        self.logger = logging.getLogger("AgentOrchestrator")
    
    def execute_workflow(self, workflow_definition: Dict[str, Any]) -> str:
        """
        Execute a multi-agent workflow.
        
        Args:
            workflow_definition: Workflow configuration with tasks and dependencies
            
        Returns:
            Workflow ID for tracking
        """
        workflow_id = str(uuid.uuid4())
        
        workflow = {
            "id": workflow_id,
            "definition": workflow_definition,
            "status": WorkflowStatus.PENDING,
            "created_at": datetime.now(),
            "started_at": None,
            "completed_at": None,
            "tasks": [],
            "results": {}
        }
        
        self.workflows[workflow_id] = workflow
        self.logger.info(f"Created workflow: {workflow_id}")
        
        # Start workflow execution
        self._execute_workflow_async(workflow_id)
        
        return workflow_id
    
    def _execute_workflow_async(self, workflow_id: str):
        """Execute workflow asynchronously"""
        workflow = self.workflows[workflow_id]
        workflow["status"] = WorkflowStatus.RUNNING
        workflow["started_at"] = datetime.now()
        
        try:
            tasks = workflow["definition"].get("tasks", [])
            
            for task in tasks:
                # Route task to appropriate agent
                result = self._route_task(task)
                workflow["results"][task.get("task_id")] = result
            
            workflow["status"] = WorkflowStatus.COMPLETED
            workflow["completed_at"] = datetime.now()
            self.logger.info(f"Workflow {workflow_id} completed successfully")
            
        except Exception as e:
            workflow["status"] = WorkflowStatus.FAILED
            workflow["error"] = str(e)
            workflow["completed_at"] = datetime.now()
            self.logger.error(f"Workflow {workflow_id} failed: {str(e)}")
    
    def _route_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route a task to the most suitable agent.
        
        Args:
            task: Task definition
            
        Returns:
            Task execution result
        """
        required_capability = task.get("required_capability")
        agent_type = task.get("agent_type")
        
        # Find suitable agents
        if required_capability:
            candidates = self.registry.get_agents_by_capability(required_capability)
        elif agent_type:
            candidates = self.registry.get_agents_by_type(agent_type)
        else:
            candidates = self.registry.get_available_agents()
        
        if not candidates:
            raise ValueError(f"No suitable agent found for task: {task.get('task_id')}")
        
        # Select best agent (simple: first available)
        agent = candidates[0]
        
        # Execute task
        self.logger.info(f"Routing task {task.get('task_id')} to agent {agent.config.name}")
        return agent.execute(task)
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict]:
        """
        Get workflow status and results.
        
        Args:
            workflow_id: Workflow identifier
            
        Returns:
            Workflow status dictionary or None if not found
        """
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return None
        
        return {
            "id": workflow["id"],
            "status": workflow["status"].value,
            "created_at": workflow["created_at"].isoformat(),
            "started_at": workflow["started_at"].isoformat() if workflow["started_at"] else None,
            "completed_at": workflow["completed_at"].isoformat() if workflow["completed_at"] else None,
            "tasks_count": len(workflow["definition"].get("tasks", [])),
            "results_count": len(workflow["results"]),
            "results": workflow["results"]
        }
    
    def cancel_workflow(self, workflow_id: str) -> bool:
        """
        Cancel a running workflow.
        
        Args:
            workflow_id: Workflow to cancel
            
        Returns:
            True if cancelled, False if not found or already completed
        """
        workflow = self.workflows.get(workflow_id)
        if not workflow or workflow["status"] not in [WorkflowStatus.PENDING, WorkflowStatus.RUNNING]:
            return False
        
        workflow["status"] = WorkflowStatus.CANCELLED
        workflow["completed_at"] = datetime.now()
        self.logger.info(f"Workflow {workflow_id} cancelled")
        return True


class WorkflowEngine:
    """
    Advanced workflow engine with dependency management and parallel execution.
    """
    
    def __init__(self, orchestrator: AgentOrchestrator):
        self.orchestrator = orchestrator
        self.logger = logging.getLogger("WorkflowEngine")
    
    def create_sequential_workflow(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create a sequential workflow where tasks execute one after another.
        
        Args:
            tasks: List of task definitions
            
        Returns:
            Workflow definition
        """
        return {
            "type": "sequential",
            "tasks": tasks,
            "execution_mode": "sequential"
        }
    
    def create_parallel_workflow(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create a parallel workflow where tasks can execute simultaneously.
        
        Args:
            tasks: List of task definitions
            
        Returns:
            Workflow definition
        """
        return {
            "type": "parallel",
            "tasks": tasks,
            "execution_mode": "parallel"
        }
    
    def create_conditional_workflow(
        self, 
        condition_task: Dict[str, Any],
        true_branch: List[Dict[str, Any]],
        false_branch: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Create a conditional workflow with branching logic.
        
        Args:
            condition_task: Task that determines which branch to execute
            true_branch: Tasks to execute if condition is true
            false_branch: Tasks to execute if condition is false
            
        Returns:
            Workflow definition
        """
        return {
            "type": "conditional",
            "condition": condition_task,
            "true_branch": true_branch,
            "false_branch": false_branch,
            "execution_mode": "conditional"
        }

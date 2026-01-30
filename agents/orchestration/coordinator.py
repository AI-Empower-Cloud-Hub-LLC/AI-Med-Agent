"""
Agent Coordinator
Coordinates multi-agent collaboration and workflows
"""

from typing import List, Dict, Any, Optional, Callable
import logging
from datetime import datetime
from enum import Enum

from agents.base.agent import BaseAgent
from agents.orchestration.orchestrator import AgentOrchestrator


class WorkflowStatus(Enum):
    """Status of a workflow execution"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentCoordinator:
    """
    Coordinates complex multi-agent workflows and collaboration
    """
    
    def __init__(self, orchestrator: AgentOrchestrator):
        """
        Initialize coordinator
        
        Args:
            orchestrator: Agent orchestrator instance
        """
        self.orchestrator = orchestrator
        self.logger = logging.getLogger("AgentCoordinator")
        self.logger.setLevel(logging.INFO)
        self.workflows: Dict[str, Dict[str, Any]] = {}
    
    def create_workflow(self, workflow_id: str, steps: List[Dict[str, Any]]) -> bool:
        """
        Create a multi-agent workflow
        
        Args:
            workflow_id: Unique workflow identifier
            steps: List of workflow steps, each containing agent_id and action
            
        Returns:
            True if workflow created successfully
        """
        if workflow_id in self.workflows:
            self.logger.warning(f"Workflow {workflow_id} already exists")
            return False
        
        self.workflows[workflow_id] = {
            'workflow_id': workflow_id,
            'steps': steps,
            'status': WorkflowStatus.PENDING.value,
            'current_step': 0,
            'created_at': datetime.utcnow(),
            'results': []
        }
        
        self.logger.info(f"Created workflow {workflow_id} with {len(steps)} steps")
        return True
    
    def execute_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Execute a workflow
        
        Args:
            workflow_id: Workflow to execute
            
        Returns:
            Workflow execution results
        """
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow = self.workflows[workflow_id]
        workflow['status'] = WorkflowStatus.RUNNING.value
        workflow['started_at'] = datetime.utcnow()
        
        self.logger.info(f"Executing workflow {workflow_id}")
        
        try:
            for step in workflow['steps']:
                agent_id = step.get('agent_id')
                action = step.get('action')
                params = step.get('params', {})
                
                agent = self.orchestrator.get_agent(agent_id)
                if not agent:
                    raise ValueError(f"Agent {agent_id} not found")
                
                # Execute step
                result = self._execute_step(agent, action, params)
                workflow['results'].append(result)
                workflow['current_step'] += 1
            
            workflow['status'] = WorkflowStatus.COMPLETED.value
            workflow['completed_at'] = datetime.utcnow()
            
        except Exception as e:
            self.logger.error(f"Workflow {workflow_id} failed: {str(e)}")
            workflow['status'] = WorkflowStatus.FAILED.value
            workflow['error'] = str(e)
        
        return workflow
    
    def _execute_step(self, agent: BaseAgent, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single workflow step
        
        Args:
            agent: Agent to execute action
            action: Action to perform
            params: Action parameters
            
        Returns:
            Step execution result
        """
        self.logger.debug(f"Executing {action} on agent {agent.agent_id}")
        
        # For now, store the action in agent state
        # In a real implementation, this would call specific agent methods
        agent.update_state(f'last_action', action)
        agent.update_state(f'last_params', params)
        
        return {
            'agent_id': agent.agent_id,
            'action': action,
            'timestamp': datetime.utcnow().isoformat(),
            'success': True
        }
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow status"""
        return self.workflows.get(workflow_id)
    
    def coordinate_agents(self, task: str, agent_ids: List[str]) -> Dict[str, Any]:
        """
        Coordinate multiple agents to complete a task
        
        Args:
            task: Task description
            agent_ids: List of agent IDs to coordinate
            
        Returns:
            Coordination results
        """
        self.logger.info(f"Coordinating {len(agent_ids)} agents for task: {task}")
        
        results = {
            'task': task,
            'agents': agent_ids,
            'started_at': datetime.utcnow().isoformat(),
            'agent_results': []
        }
        
        # Notify all agents about the coordination task
        for agent_id in agent_ids:
            agent = self.orchestrator.get_agent(agent_id)
            if agent:
                agent.update_state('coordination_task', task)
                results['agent_results'].append({
                    'agent_id': agent_id,
                    'status': 'coordinated'
                })
        
        return results

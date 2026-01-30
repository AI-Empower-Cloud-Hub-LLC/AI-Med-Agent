"""
Agent Registry
==============

Central registry for managing all agents in the enterprise system.
Provides discovery, lifecycle management, and coordination.
"""

from typing import Dict, List, Optional, Type
from ..agents.base_agent import BaseAgent, AgentConfig, AgentStatus
import logging


class AgentRegistry:
    """
    Central registry for all agents in the system.
    
    Manages agent lifecycle, discovery, and provides a unified interface
    for interacting with multiple agents.
    """
    
    def __init__(self):
        self._agents: Dict[str, BaseAgent] = {}
        self._agent_types: Dict[str, Type[BaseAgent]] = {}
        self.logger = logging.getLogger("AgentRegistry")
    
    def register_agent_type(self, agent_type: str, agent_class: Type[BaseAgent]):
        """
        Register a new agent type/class.
        
        Args:
            agent_type: Unique identifier for the agent type
            agent_class: Agent class (subclass of BaseAgent)
        """
        if not issubclass(agent_class, BaseAgent):
            raise ValueError(f"{agent_class} must be a subclass of BaseAgent")
        
        self._agent_types[agent_type] = agent_class
        self.logger.info(f"Registered agent type: {agent_type}")
    
    def create_agent(self, config: AgentConfig) -> BaseAgent:
        """
        Create and register a new agent instance.
        
        Args:
            config: Agent configuration
            
        Returns:
            Created agent instance
        """
        if config.agent_type not in self._agent_types:
            raise ValueError(f"Unknown agent type: {config.agent_type}")
        
        agent_class = self._agent_types[config.agent_type]
        agent = agent_class(config)
        
        self._agents[agent.agent_id] = agent
        self.logger.info(f"Created agent: {config.name} (ID: {agent.agent_id})")
        
        return agent
    
    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """
        Get agent by ID.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            Agent instance or None if not found
        """
        return self._agents.get(agent_id)
    
    def get_agents_by_type(self, agent_type: str) -> List[BaseAgent]:
        """
        Get all agents of a specific type.
        
        Args:
            agent_type: Agent type to filter by
            
        Returns:
            List of matching agents
        """
        return [
            agent for agent in self._agents.values()
            if agent.config.agent_type == agent_type
        ]
    
    def get_agents_by_capability(self, capability: str) -> List[BaseAgent]:
        """
        Find agents with a specific capability.
        
        Args:
            capability: Capability to search for
            
        Returns:
            List of agents with the capability
        """
        return [
            agent for agent in self._agents.values()
            if capability in agent.config.capabilities
        ]
    
    def get_available_agents(self) -> List[BaseAgent]:
        """
        Get all agents that are currently available (READY or IDLE).
        
        Returns:
            List of available agents
        """
        return [
            agent for agent in self._agents.values()
            if agent.status in [AgentStatus.READY, AgentStatus.IDLE]
        ]
    
    def remove_agent(self, agent_id: str) -> bool:
        """
        Remove and shutdown an agent.
        
        Args:
            agent_id: Agent to remove
            
        Returns:
            True if removed, False if not found
        """
        agent = self._agents.get(agent_id)
        if agent:
            agent.shutdown()
            del self._agents[agent_id]
            self.logger.info(f"Removed agent: {agent_id}")
            return True
        return False
    
    def list_agents(self) -> List[Dict]:
        """
        List all registered agents with their status.
        
        Returns:
            List of agent status dictionaries
        """
        return [agent.get_status() for agent in self._agents.values()]
    
    def get_statistics(self) -> Dict:
        """
        Get overall registry statistics.
        
        Returns:
            Statistics dictionary
        """
        total_agents = len(self._agents)
        agents_by_status = {}
        total_tasks_completed = 0
        total_tasks_failed = 0
        
        for agent in self._agents.values():
            status = agent.status.value
            agents_by_status[status] = agents_by_status.get(status, 0) + 1
            total_tasks_completed += agent.tasks_completed
            total_tasks_failed += agent.tasks_failed
        
        return {
            "total_agents": total_agents,
            "agents_by_status": agents_by_status,
            "registered_types": list(self._agent_types.keys()),
            "total_tasks_completed": total_tasks_completed,
            "total_tasks_failed": total_tasks_failed,
            "success_rate": (
                total_tasks_completed / (total_tasks_completed + total_tasks_failed)
                if (total_tasks_completed + total_tasks_failed) > 0 else 0
            )
        }
    
    def shutdown_all(self):
        """Shutdown all registered agents"""
        self.logger.info("Shutting down all agents")
        for agent in self._agents.values():
            agent.shutdown()
        self._agents.clear()

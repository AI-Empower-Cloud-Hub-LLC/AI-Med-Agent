"""
Agent Orchestrator
Manages multiple agents and coordinates their activities
"""

from typing import Dict, List, Optional, Any
import logging
from datetime import datetime

from agents.base.agent import BaseAgent, AgentStatus
from agents.base.protocol import AgentProtocol, AgentMessage, MessageType


class AgentOrchestrator:
    """
    Orchestrates multiple agents, managing their lifecycle and communication
    """
    
    def __init__(self, protocol: Optional[AgentProtocol] = None):
        """
        Initialize orchestrator
        
        Args:
            protocol: Shared communication protocol
        """
        self.protocol = protocol or AgentProtocol()
        self.agents: Dict[str, BaseAgent] = {}
        self.logger = logging.getLogger("AgentOrchestrator")
        self.logger.setLevel(logging.INFO)
        self.created_at = datetime.utcnow()
    
    def register_agent(self, agent: BaseAgent) -> bool:
        """
        Register an agent with the orchestrator
        
        Args:
            agent: Agent to register
            
        Returns:
            True if registered successfully
        """
        if agent.agent_id in self.agents:
            self.logger.warning(f"Agent {agent.agent_id} already registered")
            return False
        
        # Set the shared protocol
        agent.protocol = self.protocol
        self.agents[agent.agent_id] = agent
        self.logger.info(f"Registered agent {agent.config.agent_name} ({agent.agent_id})")
        return True
    
    def unregister_agent(self, agent_id: str) -> bool:
        """
        Unregister an agent
        
        Args:
            agent_id: ID of agent to unregister
            
        Returns:
            True if unregistered successfully
        """
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            agent.stop()
            del self.agents[agent_id]
            self.logger.info(f"Unregistered agent {agent_id}")
            return True
        return False
    
    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Get an agent by ID"""
        return self.agents.get(agent_id)
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """List all registered agents"""
        return [
            {
                'agent_id': agent.agent_id,
                'agent_name': agent.config.agent_name,
                'agent_type': agent.config.agent_type,
                'status': agent.status.value
            }
            for agent in self.agents.values()
        ]
    
    def start_all(self) -> None:
        """Start all registered agents"""
        self.logger.info("Starting all agents")
        for agent in self.agents.values():
            try:
                agent.start()
            except Exception as e:
                self.logger.error(f"Failed to start agent {agent.agent_id}: {str(e)}")
    
    def stop_all(self) -> None:
        """Stop all registered agents"""
        self.logger.info("Stopping all agents")
        for agent in self.agents.values():
            try:
                agent.stop()
            except Exception as e:
                self.logger.error(f"Failed to stop agent {agent.agent_id}: {str(e)}")
    
    def process_messages(self) -> int:
        """
        Process all pending messages for all agents
        
        Returns:
            Number of messages processed
        """
        processed = 0
        
        for agent in self.agents.values():
            if agent.status == AgentStatus.STOPPED:
                continue
            
            messages = agent.receive_messages()
            for message in messages:
                try:
                    response = agent.process_message(message)
                    if response:
                        self.protocol.send_message(response)
                    processed += 1
                except Exception as e:
                    self.logger.error(f"Error processing message for {agent.agent_id}: {str(e)}")
        
        return processed
    
    def send_broadcast(self, sender_id: str, payload: Dict[str, Any]) -> int:
        """
        Send a message to all agents
        
        Args:
            sender_id: ID of sender
            payload: Message payload
            
        Returns:
            Number of agents the message was sent to
        """
        count = 0
        for agent_id in self.agents.keys():
            if agent_id != sender_id:
                message = AgentMessage(
                    sender_id=sender_id,
                    receiver_id=agent_id,
                    message_type=MessageType.NOTIFICATION,
                    payload=payload
                )
                if self.protocol.send_message(message):
                    count += 1
        
        return count
    
    def get_status(self) -> Dict[str, Any]:
        """Get orchestrator status"""
        return {
            'created_at': self.created_at.isoformat(),
            'total_agents': len(self.agents),
            'agents_by_status': self._count_by_status(),
            'pending_messages': sum(len(self.protocol.message_queue.get(aid, [])) 
                                   for aid in self.agents.keys())
        }
    
    def _count_by_status(self) -> Dict[str, int]:
        """Count agents by status"""
        counts = {}
        for agent in self.agents.values():
            status = agent.status.value
            counts[status] = counts.get(status, 0) + 1
        return counts
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on all agents
        
        Returns:
            Health status for each agent
        """
        health = {}
        for agent_id, agent in self.agents.items():
            health[agent_id] = {
                'status': agent.status.value,
                'error_count': agent.error_count,
                'last_activity': agent.last_activity.isoformat(),
                'healthy': agent.status != AgentStatus.ERROR and agent.error_count < 10
            }
        return health

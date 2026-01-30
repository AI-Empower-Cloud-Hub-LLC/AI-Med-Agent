"""
Agent Development Template
Template for creating new custom agents
"""

from typing import Optional, Dict, Any
from agents.base.agent import BaseAgent, AgentConfig
from agents.base.protocol import AgentMessage, MessageType
from agents.memory.manager import MemoryManager, MemoryType


class CustomAgent(BaseAgent):
    """
    Custom Agent Template
    
    Replace this docstring with your agent's description.
    Explain what this agent does and its capabilities.
    """
    
    def __init__(self, config: AgentConfig, memory_manager: Optional[MemoryManager] = None):
        """
        Initialize custom agent
        
        Args:
            config: Agent configuration
            memory_manager: Optional memory manager instance
        """
        super().__init__(config)
        self.memory_manager = memory_manager or MemoryManager()
        
        # Add your custom initialization here
        # Example: self.knowledge_base = {}
        # Example: self.processing_rules = []
    
    def _on_start(self) -> None:
        """Called when agent starts - add initialization logic"""
        self.logger.info(f"{self.config.agent_name} starting up")
        
        # Initialize your agent's state
        self.update_state('initialized', True)
        self.update_state('request_count', 0)
        
        # Add any startup tasks here
    
    def _on_stop(self) -> None:
        """Called when agent stops - add cleanup logic"""
        self.logger.info(f"{self.config.agent_name} shutting down")
        
        # Add any cleanup tasks here
    
    def _handle_request(self, message: AgentMessage) -> Optional[AgentMessage]:
        """
        Handle incoming requests
        
        Expected payload structure:
        {
            'action': str,  # The action to perform
            'data': Dict,   # Action-specific data
            # Add your expected fields
        }
        
        Args:
            message: Incoming request message
            
        Returns:
            Response message or None
        """
        payload = message.payload
        action = payload.get('action')
        
        # Validate required fields
        if not action:
            return self._create_error_response(message, "Missing 'action' in payload")
        
        # Route to appropriate handler based on action
        if action == 'process':
            result = self._handle_process_action(payload)
        elif action == 'query':
            result = self._handle_query_action(payload)
        else:
            return self._create_error_response(message, f"Unknown action: {action}")
        
        # Store in memory if significant
        self._store_interaction(message, result)
        
        # Update metrics
        count = self.get_state('request_count', 0)
        self.update_state('request_count', count + 1)
        
        # Create response
        return self.protocol.create_response(message, result)
    
    def _handle_process_action(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle 'process' action
        
        Args:
            payload: Request payload
            
        Returns:
            Processing result
        """
        data = payload.get('data', {})
        
        # Add your processing logic here
        result = {
            'status': 'success',
            'processed': True,
            'data': data
        }
        
        return result
    
    def _handle_query_action(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle 'query' action
        
        Args:
            payload: Request payload
            
        Returns:
            Query result
        """
        query = payload.get('query', '')
        
        # Add your query logic here
        result = {
            'status': 'success',
            'query': query,
            'results': []
        }
        
        return result
    
    def _store_interaction(self, message: AgentMessage, result: Dict[str, Any]) -> None:
        """
        Store interaction in memory
        
        Args:
            message: Original message
            result: Processing result
        """
        self.memory_manager.remember(
            agent_id=self.agent_id,
            memory_type=MemoryType.EPISODIC,
            content={
                'message_id': message.message_id,
                'action': message.payload.get('action'),
                'result': result,
                'sender': message.sender_id
            },
            importance=0.5  # Adjust based on your needs
        )
    
    # Add your custom methods here
    def custom_method(self, param: str) -> Any:
        """
        Example custom method
        
        Args:
            param: Example parameter
            
        Returns:
            Processing result
        """
        self.logger.info(f"Custom method called with: {param}")
        return {'processed': param}


# Example usage
if __name__ == "__main__":
    # Create agent configuration
    config = AgentConfig(
        agent_name="MyCustomAgent",
        agent_type="custom",
        log_level="INFO"
    )
    
    # Create and start agent
    agent = CustomAgent(config)
    agent.start()
    
    # Send a test message
    test_message = agent.protocol.create_request(
        "test-sender",
        agent.agent_id,
        {
            'action': 'process',
            'data': {'test': 'data'}
        }
    )
    
    # Process message
    response = agent.process_message(test_message)
    print(f"Response: {response.payload}")
    
    # Get agent status
    status = agent.get_status()
    print(f"Agent Status: {status}")
    
    # Stop agent
    agent.stop()

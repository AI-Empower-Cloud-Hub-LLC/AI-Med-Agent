"""
Tests for Agent Orchestration
"""

import unittest
from agents.base.agent import BaseAgent, AgentConfig, AgentStatus
from agents.base.protocol import AgentProtocol, AgentMessage, MessageType
from agents.orchestration.orchestrator import AgentOrchestrator
from agents.orchestration.coordinator import AgentCoordinator


class SimpleTestAgent(BaseAgent):
    """Simple test agent for orchestration tests"""
    
    def _handle_request(self, message: AgentMessage):
        return self.protocol.create_response(message, {'status': 'ok'})


class TestAgentOrchestrator(unittest.TestCase):
    """Test cases for AgentOrchestrator"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.orchestrator = AgentOrchestrator()
        
        self.agent1 = SimpleTestAgent(
            AgentConfig(agent_name="Agent1", agent_type="test"),
            self.orchestrator.protocol
        )
        self.agent2 = SimpleTestAgent(
            AgentConfig(agent_name="Agent2", agent_type="test"),
            self.orchestrator.protocol
        )
    
    def test_register_agent(self):
        """Test agent registration"""
        success = self.orchestrator.register_agent(self.agent1)
        self.assertTrue(success)
        
        # Duplicate registration should fail
        success = self.orchestrator.register_agent(self.agent1)
        self.assertFalse(success)
    
    def test_unregister_agent(self):
        """Test agent unregistration"""
        self.orchestrator.register_agent(self.agent1)
        success = self.orchestrator.unregister_agent(self.agent1.agent_id)
        self.assertTrue(success)
        
        # Unregistering non-existent agent should fail
        success = self.orchestrator.unregister_agent("nonexistent")
        self.assertFalse(success)
    
    def test_get_agent(self):
        """Test getting agent by ID"""
        self.orchestrator.register_agent(self.agent1)
        
        agent = self.orchestrator.get_agent(self.agent1.agent_id)
        self.assertIsNotNone(agent)
        self.assertEqual(agent.agent_id, self.agent1.agent_id)
        
        agent = self.orchestrator.get_agent("nonexistent")
        self.assertIsNone(agent)
    
    def test_list_agents(self):
        """Test listing agents"""
        self.orchestrator.register_agent(self.agent1)
        self.orchestrator.register_agent(self.agent2)
        
        agents = self.orchestrator.list_agents()
        self.assertEqual(len(agents), 2)
    
    def test_start_stop_all(self):
        """Test starting and stopping all agents"""
        self.orchestrator.register_agent(self.agent1)
        self.orchestrator.register_agent(self.agent2)
        
        self.orchestrator.start_all()
        self.assertEqual(self.agent1.status, AgentStatus.IDLE)
        self.assertEqual(self.agent2.status, AgentStatus.IDLE)
        
        self.orchestrator.stop_all()
        self.assertEqual(self.agent1.status, AgentStatus.STOPPED)
        self.assertEqual(self.agent2.status, AgentStatus.STOPPED)
    
    def test_process_messages(self):
        """Test message processing across agents"""
        self.orchestrator.register_agent(self.agent1)
        self.orchestrator.register_agent(self.agent2)
        self.orchestrator.start_all()
        
        # Send message from agent1 to agent2
        self.agent1.send_message(
            self.agent2.agent_id,
            {'test': 'data'}
        )
        
        # Process messages
        count = self.orchestrator.process_messages()
        self.assertGreater(count, 0)
    
    def test_health_check(self):
        """Test health check"""
        self.orchestrator.register_agent(self.agent1)
        self.orchestrator.start_all()
        
        health = self.orchestrator.health_check()
        self.assertIn(self.agent1.agent_id, health)
        self.assertTrue(health[self.agent1.agent_id]['healthy'])


class TestAgentCoordinator(unittest.TestCase):
    """Test cases for AgentCoordinator"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.orchestrator = AgentOrchestrator()
        self.coordinator = AgentCoordinator(self.orchestrator)
        
        self.agent1 = SimpleTestAgent(
            AgentConfig(agent_name="Agent1", agent_type="test"),
            self.orchestrator.protocol
        )
        self.orchestrator.register_agent(self.agent1)
        self.orchestrator.start_all()
    
    def test_create_workflow(self):
        """Test workflow creation"""
        steps = [
            {'agent_id': self.agent1.agent_id, 'action': 'test', 'params': {}}
        ]
        
        success = self.coordinator.create_workflow('test-workflow', steps)
        self.assertTrue(success)
        
        # Duplicate workflow should fail
        success = self.coordinator.create_workflow('test-workflow', steps)
        self.assertFalse(success)
    
    def test_execute_workflow(self):
        """Test workflow execution"""
        steps = [
            {'agent_id': self.agent1.agent_id, 'action': 'test1', 'params': {}},
            {'agent_id': self.agent1.agent_id, 'action': 'test2', 'params': {}}
        ]
        
        self.coordinator.create_workflow('test-workflow', steps)
        result = self.coordinator.execute_workflow('test-workflow')
        
        self.assertEqual(result['status'], 'completed')
        self.assertEqual(result['current_step'], len(steps))
    
    def test_coordinate_agents(self):
        """Test agent coordination"""
        result = self.coordinator.coordinate_agents(
            'test-task',
            [self.agent1.agent_id]
        )
        
        self.assertEqual(result['task'], 'test-task')
        self.assertEqual(len(result['agent_results']), 1)


if __name__ == '__main__':
    unittest.main()

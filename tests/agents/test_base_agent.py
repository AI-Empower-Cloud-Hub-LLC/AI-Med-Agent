"""
Tests for Base Agent Functionality
"""

import unittest
from agents.base.agent import BaseAgent, AgentConfig, AgentStatus
from agents.base.protocol import AgentProtocol, AgentMessage, MessageType


class TestAgent(BaseAgent):
    """Test implementation of BaseAgent"""
    
    def _handle_request(self, message: AgentMessage):
        """Simple echo handler"""
        return self.protocol.create_response(
            message,
            {'echo': message.payload, 'processed': True}
        )


class TestBaseAgent(unittest.TestCase):
    """Test cases for BaseAgent"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = AgentConfig(
            agent_name="TestAgent",
            agent_type="test"
        )
        self.protocol = AgentProtocol()
        self.agent = TestAgent(self.config, self.protocol)
    
    def test_agent_initialization(self):
        """Test agent initialization"""
        self.assertEqual(self.agent.config.agent_name, "TestAgent")
        self.assertEqual(self.agent.status, AgentStatus.INITIALIZING)
        self.assertIsNotNone(self.agent.agent_id)
    
    def test_agent_start_stop(self):
        """Test agent lifecycle"""
        self.agent.start()
        self.assertEqual(self.agent.status, AgentStatus.IDLE)
        
        self.agent.stop()
        self.assertEqual(self.agent.status, AgentStatus.STOPPED)
    
    def test_message_processing(self):
        """Test message processing"""
        self.agent.start()
        
        message = AgentMessage(
            sender_id="test-sender",
            receiver_id=self.agent.agent_id,
            message_type=MessageType.REQUEST,
            payload={'test': 'data'}
        )
        
        response = self.agent.process_message(message)
        
        self.assertIsNotNone(response)
        self.assertEqual(response.message_type, MessageType.RESPONSE)
        self.assertEqual(response.payload['echo']['test'], 'data')
        self.assertTrue(response.payload['processed'])
    
    def test_state_management(self):
        """Test agent state management"""
        self.agent.update_state('key1', 'value1')
        self.assertEqual(self.agent.get_state('key1'), 'value1')
        
        self.agent.update_state('key2', 42)
        self.assertEqual(self.agent.get_state('key2'), 42)
        
        self.assertIsNone(self.agent.get_state('nonexistent'))
        self.assertEqual(self.agent.get_state('nonexistent', 'default'), 'default')
    
    def test_get_status(self):
        """Test status reporting"""
        self.agent.start()
        status = self.agent.get_status()
        
        self.assertEqual(status['agent_name'], 'TestAgent')
        self.assertEqual(status['agent_type'], 'test')
        self.assertEqual(status['status'], AgentStatus.IDLE.value)
        self.assertIn('created_at', status)
        self.assertIn('processing_count', status)


class TestAgentProtocol(unittest.TestCase):
    """Test cases for AgentProtocol"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.protocol = AgentProtocol()
    
    def test_send_receive_message(self):
        """Test message sending and receiving"""
        message = AgentMessage(
            sender_id="agent-1",
            receiver_id="agent-2",
            message_type=MessageType.REQUEST,
            payload={'data': 'test'}
        )
        
        success = self.protocol.send_message(message)
        self.assertTrue(success)
        
        messages = self.protocol.receive_messages("agent-2")
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].payload['data'], 'test')
        
        # Messages should be cleared after retrieval
        messages = self.protocol.receive_messages("agent-2")
        self.assertEqual(len(messages), 0)
    
    def test_create_request(self):
        """Test request message creation"""
        message = self.protocol.create_request(
            "sender-1",
            "receiver-1",
            {'action': 'test'}
        )
        
        self.assertEqual(message.sender_id, "sender-1")
        self.assertEqual(message.receiver_id, "receiver-1")
        self.assertEqual(message.message_type, MessageType.REQUEST)
        self.assertEqual(message.payload['action'], 'test')
    
    def test_create_response(self):
        """Test response message creation"""
        original = AgentMessage(
            sender_id="agent-1",
            receiver_id="agent-2",
            message_type=MessageType.REQUEST,
            payload={}
        )
        
        response = self.protocol.create_response(
            original,
            {'result': 'success'}
        )
        
        self.assertEqual(response.sender_id, "agent-2")
        self.assertEqual(response.receiver_id, "agent-1")
        self.assertEqual(response.message_type, MessageType.RESPONSE)
        self.assertEqual(response.correlation_id, original.message_id)


if __name__ == '__main__':
    unittest.main()

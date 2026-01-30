"""
Tests for Medical Agents
"""

import unittest
from agents.base.agent import AgentConfig
from agents.base.protocol import AgentProtocol, MessageType
from agents.medical.diagnosis_agent import DiagnosisAgent
from agents.medical.triage_agent import TriageAgent, TriagePriority
from agents.medical.monitoring_agent import PatientMonitoringAgent
from agents.memory.manager import MemoryManager


class TestDiagnosisAgent(unittest.TestCase):
    """Test cases for DiagnosisAgent"""
    
    def setUp(self):
        """Set up test fixtures"""
        config = AgentConfig(
            agent_name="TestDiagnosis",
            agent_type="diagnosis"
        )
        self.agent = DiagnosisAgent(config)
        self.agent.start()
    
    def test_diagnosis_request(self):
        """Test diagnosis request handling"""
        message = self.agent.protocol.create_request(
            "test-sender",
            self.agent.agent_id,
            {
                'patient_id': 'P-TEST-001',
                'symptoms': ['fever', 'cough'],
                'medical_history': {}
            }
        )
        
        response = self.agent.process_message(message)
        
        self.assertIsNotNone(response)
        self.assertEqual(response.message_type, MessageType.RESPONSE)
        self.assertIn('diagnosis', response.payload)
        self.assertIn('possible_conditions', response.payload['diagnosis'])
    
    def test_missing_patient_id(self):
        """Test error handling for missing patient_id"""
        message = self.agent.protocol.create_request(
            "test-sender",
            self.agent.agent_id,
            {'symptoms': ['fever']}
        )
        
        response = self.agent.process_message(message)
        
        self.assertEqual(response.message_type, MessageType.ERROR)
        self.assertIn('error', response.payload)


class TestTriageAgent(unittest.TestCase):
    """Test cases for TriageAgent"""
    
    def setUp(self):
        """Set up test fixtures"""
        config = AgentConfig(
            agent_name="TestTriage",
            agent_type="triage"
        )
        self.agent = TriageAgent(config)
        self.agent.start()
    
    def test_emergency_triage(self):
        """Test emergency triage assessment"""
        message = self.agent.protocol.create_request(
            "test-sender",
            self.agent.agent_id,
            {
                'patient_id': 'P-TEST-002',
                'symptoms': ['chest pain', 'difficulty breathing'],
                'vital_signs': {
                    'heart_rate': 120,
                    'systolic_bp': 190,
                    'oxygen_saturation': 88
                },
                'chief_complaint': 'Chest pain'
            }
        )
        
        response = self.agent.process_message(message)
        
        self.assertIsNotNone(response)
        self.assertEqual(response.message_type, MessageType.RESPONSE)
        
        triage_result = response.payload['triage_result']
        # Should be emergency or urgent due to critical symptoms
        self.assertIn(triage_result['priority'], 
                     [TriagePriority.EMERGENCY.value, TriagePriority.URGENT.value])
    
    def test_non_urgent_triage(self):
        """Test non-urgent triage assessment"""
        message = self.agent.protocol.create_request(
            "test-sender",
            self.agent.agent_id,
            {
                'patient_id': 'P-TEST-003',
                'symptoms': ['headache'],
                'vital_signs': {
                    'heart_rate': 75,
                    'systolic_bp': 120,
                    'oxygen_saturation': 98
                },
                'chief_complaint': 'Mild headache'
            }
        )
        
        response = self.agent.process_message(message)
        triage_result = response.payload['triage_result']
        
        # Should be non-urgent
        self.assertIn(triage_result['priority'],
                     [TriagePriority.NON_URGENT.value, TriagePriority.SEMI_URGENT.value])


class TestPatientMonitoringAgent(unittest.TestCase):
    """Test cases for PatientMonitoringAgent"""
    
    def setUp(self):
        """Set up test fixtures"""
        config = AgentConfig(
            agent_name="TestMonitoring",
            agent_type="monitoring"
        )
        self.agent = PatientMonitoringAgent(config)
        self.agent.start()
    
    def test_record_normal_vitals(self):
        """Test recording normal vital signs"""
        message = self.agent.protocol.create_request(
            "test-sender",
            self.agent.agent_id,
            {
                'patient_id': 'P-TEST-004',
                'action': 'record',
                'vital_signs': {
                    'heart_rate': 75,
                    'oxygen_saturation': 98,
                    'temperature': 36.8
                }
            }
        )
        
        response = self.agent.process_message(message)
        
        self.assertIsNotNone(response)
        self.assertEqual(response.payload['result']['recorded'], True)
        self.assertEqual(len(response.payload['result']['alerts']), 0)
    
    def test_record_abnormal_vitals(self):
        """Test recording abnormal vital signs"""
        message = self.agent.protocol.create_request(
            "test-sender",
            self.agent.agent_id,
            {
                'patient_id': 'P-TEST-005',
                'action': 'record',
                'vital_signs': {
                    'heart_rate': 150,  # Abnormally high
                    'oxygen_saturation': 88,  # Low
                    'temperature': 39.0  # High fever
                }
            }
        )
        
        response = self.agent.process_message(message)
        
        self.assertIsNotNone(response)
        self.assertEqual(response.payload['result']['recorded'], True)
        self.assertGreater(len(response.payload['result']['alerts']), 0)
    
    def test_analyze_patient(self):
        """Test patient analysis"""
        # First record some vitals
        self.agent.send_message(
            self.agent.agent_id,
            {
                'patient_id': 'P-TEST-006',
                'action': 'record',
                'vital_signs': {'heart_rate': 75, 'oxygen_saturation': 98}
            }
        )
        self.agent.process_message(self.agent.receive_messages()[0])
        
        # Then analyze
        message = self.agent.protocol.create_request(
            "test-sender",
            self.agent.agent_id,
            {
                'patient_id': 'P-TEST-006',
                'action': 'analyze'
            }
        )
        
        response = self.agent.process_message(message)
        
        self.assertIsNotNone(response)
        self.assertIn('current_status', response.payload['result'])
        self.assertIn('trends', response.payload['result'])


if __name__ == '__main__':
    unittest.main()

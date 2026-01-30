"""
Integration Tests for AICloud-Innovation Framework
===================================================

Tests the complete enterprise framework functionality.
"""

import sys
sys.path.insert(0, '/home/runner/work/AI-Med-Agent/AI-Med-Agent')

import unittest
from aicloud_innovation import (
    AgentRegistry,
    AgentConfig,
    AgentOrchestrator,
    AgentObserver,
)
from aicloud_innovation.agents import (
    MedicalDiagnosisAgent,
    TreatmentPlanAgent,
    PatientMonitoringAgent,
    ClinicalResearchAgent,
)
from aicloud_innovation.orchestration import WorkflowEngine


class TestAgentRegistry(unittest.TestCase):
    """Test Agent Registry functionality"""
    
    def setUp(self):
        self.registry = AgentRegistry()
        self.registry.register_agent_type("medical_diagnosis", MedicalDiagnosisAgent)
    
    def test_register_agent_type(self):
        """Test registering a new agent type"""
        self.assertIn("medical_diagnosis", self.registry._agent_types)
    
    def test_create_agent(self):
        """Test creating an agent instance"""
        config = AgentConfig(
            name="Test Agent",
            agent_type="medical_diagnosis",
            capabilities=["test"]
        )
        agent = self.registry.create_agent(config)
        self.assertIsNotNone(agent)
        self.assertEqual(agent.config.name, "Test Agent")
    
    def test_get_agent(self):
        """Test retrieving an agent by ID"""
        config = AgentConfig(name="Test", agent_type="medical_diagnosis")
        agent = self.registry.create_agent(config)
        retrieved = self.registry.get_agent(agent.agent_id)
        self.assertEqual(agent, retrieved)
    
    def test_list_agents(self):
        """Test listing all agents"""
        config1 = AgentConfig(name="Agent1", agent_type="medical_diagnosis")
        config2 = AgentConfig(name="Agent2", agent_type="medical_diagnosis")
        self.registry.create_agent(config1)
        self.registry.create_agent(config2)
        agents = self.registry.list_agents()
        self.assertEqual(len(agents), 2)


class TestAgents(unittest.TestCase):
    """Test specialized agent functionality"""
    
    def test_medical_diagnosis_agent(self):
        """Test Medical Diagnosis Agent"""
        config = AgentConfig(
            name="Diagnosis Agent",
            agent_type="medical_diagnosis"
        )
        agent = MedicalDiagnosisAgent(config)
        
        task = {
            "task_id": "TEST-001",
            "patient_id": "PT-001",
            "symptoms": ["fever", "cough"]
        }
        
        result = agent.execute(task)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["agent_name"], "Diagnosis Agent")
    
    def test_treatment_plan_agent(self):
        """Test Treatment Planning Agent"""
        config = AgentConfig(
            name="Treatment Agent",
            agent_type="treatment_planning"
        )
        agent = TreatmentPlanAgent(config)
        
        task = {
            "task_id": "TEST-002",
            "patient_id": "PT-001",
            "diagnosis": "Test Condition"
        }
        
        result = agent.execute(task)
        self.assertEqual(result["status"], "success")
    
    def test_monitoring_agent(self):
        """Test Patient Monitoring Agent"""
        config = AgentConfig(
            name="Monitor Agent",
            agent_type="patient_monitoring"
        )
        agent = PatientMonitoringAgent(config)
        
        task = {
            "task_id": "TEST-003",
            "patient_id": "PT-001",
            "vital_signs": {"heart_rate": 75}
        }
        
        result = agent.execute(task)
        self.assertEqual(result["status"], "success")
    
    def test_research_agent(self):
        """Test Clinical Research Agent"""
        config = AgentConfig(
            name="Research Agent",
            agent_type="clinical_research"
        )
        agent = ClinicalResearchAgent(config)
        
        task = {
            "task_id": "TEST-004",
            "research_query": "Test query"
        }
        
        result = agent.execute(task)
        self.assertEqual(result["status"], "success")


class TestOrchestrator(unittest.TestCase):
    """Test Agent Orchestrator functionality"""
    
    def setUp(self):
        self.registry = AgentRegistry()
        self.registry.register_agent_type("medical_diagnosis", MedicalDiagnosisAgent)
        self.registry.register_agent_type("treatment_planning", TreatmentPlanAgent)
        
        # Create test agents
        config1 = AgentConfig(name="Agent1", agent_type="medical_diagnosis")
        config2 = AgentConfig(name="Agent2", agent_type="treatment_planning")
        self.registry.create_agent(config1)
        self.registry.create_agent(config2)
        
        self.orchestrator = AgentOrchestrator(self.registry)
    
    def test_execute_workflow(self):
        """Test workflow execution"""
        workflow = {
            "tasks": [
                {
                    "task_id": "WF-001",
                    "agent_type": "medical_diagnosis",
                    "patient_id": "PT-001",
                    "symptoms": ["fever"]
                }
            ]
        }
        
        workflow_id = self.orchestrator.execute_workflow(workflow)
        self.assertIsNotNone(workflow_id)
        
        status = self.orchestrator.get_workflow_status(workflow_id)
        self.assertIsNotNone(status)
        self.assertEqual(status["status"], "completed")


class TestObserver(unittest.TestCase):
    """Test Agent Observer functionality"""
    
    def setUp(self):
        self.observer = AgentObserver()
        config = AgentConfig(
            name="Test Agent",
            agent_type="medical_diagnosis"
        )
        self.agent = MedicalDiagnosisAgent(config)
    
    def test_monitor_agent(self):
        """Test monitoring an agent"""
        self.observer.monitor_agent(self.agent)
        health = self.observer.get_agent_health(self.agent.agent_id)
        self.assertIsNotNone(health)
        self.assertIn("status", health)
    
    def test_generate_report(self):
        """Test generating monitoring report"""
        self.observer.monitor_agent(self.agent)
        report = self.observer.generate_monitoring_report()
        self.assertIn("total_agents_monitored", report)
        self.assertIn("health_summary", report)


class TestWorkflowEngine(unittest.TestCase):
    """Test Workflow Engine functionality"""
    
    def setUp(self):
        registry = AgentRegistry()
        orchestrator = AgentOrchestrator(registry)
        self.engine = WorkflowEngine(orchestrator)
    
    def test_create_sequential_workflow(self):
        """Test creating sequential workflow"""
        tasks = [
            {"task_id": "T1", "agent_type": "test"},
            {"task_id": "T2", "agent_type": "test"}
        ]
        workflow = self.engine.create_sequential_workflow(tasks)
        self.assertEqual(workflow["type"], "sequential")
        self.assertEqual(len(workflow["tasks"]), 2)
    
    def test_create_parallel_workflow(self):
        """Test creating parallel workflow"""
        tasks = [
            {"task_id": "T1", "agent_type": "test"},
            {"task_id": "T2", "agent_type": "test"}
        ]
        workflow = self.engine.create_parallel_workflow(tasks)
        self.assertEqual(workflow["type"], "parallel")
    
    def test_create_conditional_workflow(self):
        """Test creating conditional workflow"""
        condition = {"task_id": "COND", "agent_type": "test"}
        true_branch = [{"task_id": "T1"}]
        false_branch = [{"task_id": "T2"}]
        
        workflow = self.engine.create_conditional_workflow(
            condition, true_branch, false_branch
        )
        self.assertEqual(workflow["type"], "conditional")


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestAgentRegistry))
    suite.addTests(loader.loadTestsFromTestCase(TestAgents))
    suite.addTests(loader.loadTestsFromTestCase(TestOrchestrator))
    suite.addTests(loader.loadTestsFromTestCase(TestObserver))
    suite.addTests(loader.loadTestsFromTestCase(TestWorkflowEngine))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    exit_code = run_tests()
    exit(exit_code)

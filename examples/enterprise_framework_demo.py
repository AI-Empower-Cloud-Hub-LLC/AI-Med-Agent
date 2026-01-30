"""
AICloud-Innovation Framework - Example Usage
============================================

This example demonstrates how to use the enterprise-level AI agent framework
to develop powerful AI agentic agents.
"""

import sys
sys.path.insert(0, '/home/runner/work/AI-Med-Agent/AI-Med-Agent')

from aicloud_innovation import (
    BaseAgent,
    AgentConfig,
    AgentRegistry,
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
from aicloud_innovation.utils import setup_logging


def main():
    """
    Demonstrate the AICloud-Innovation framework capabilities.
    """
    # Setup logging
    setup_logging(level="INFO")
    
    print("=" * 70)
    print("AICloud-Innovation Enterprise Framework")
    print("Developing Powerful AI Agentic Agents")
    print("=" * 70)
    print()
    
    # Step 1: Create Agent Registry
    print("Step 1: Initializing Agent Registry")
    print("-" * 70)
    registry = AgentRegistry()
    
    # Register agent types
    registry.register_agent_type("medical_diagnosis", MedicalDiagnosisAgent)
    registry.register_agent_type("treatment_planning", TreatmentPlanAgent)
    registry.register_agent_type("patient_monitoring", PatientMonitoringAgent)
    registry.register_agent_type("clinical_research", ClinicalResearchAgent)
    
    print(f"✓ Registered {len(registry._agent_types)} agent types")
    print()
    
    # Step 2: Create Specialized Agents
    print("Step 2: Creating Specialized AI Agents")
    print("-" * 70)
    
    # Medical Diagnosis Agent
    diagnosis_config = AgentConfig(
        name="Primary Diagnosis Agent",
        agent_type="medical_diagnosis",
        description="AI agent for medical diagnosis and symptom analysis",
        capabilities=["symptom_analysis", "differential_diagnosis"],
        priority=5
    )
    diagnosis_agent = registry.create_agent(diagnosis_config)
    print(f"✓ Created: {diagnosis_agent.config.name}")
    
    # Treatment Planning Agent
    treatment_config = AgentConfig(
        name="Treatment Planning Agent",
        agent_type="treatment_planning",
        description="AI agent for creating personalized treatment plans",
        capabilities=["treatment_recommendation", "medication_management"],
        priority=4
    )
    treatment_agent = registry.create_agent(treatment_config)
    print(f"✓ Created: {treatment_agent.config.name}")
    
    # Patient Monitoring Agent
    monitoring_config = AgentConfig(
        name="24/7 Patient Monitor",
        agent_type="patient_monitoring",
        description="Continuous patient monitoring and alert system",
        capabilities=["vital_monitoring", "anomaly_detection"],
        priority=5
    )
    monitoring_agent = registry.create_agent(monitoring_config)
    print(f"✓ Created: {monitoring_agent.config.name}")
    
    # Clinical Research Agent
    research_config = AgentConfig(
        name="Clinical Research Assistant",
        agent_type="clinical_research",
        description="Evidence-based clinical research and analysis",
        capabilities=["literature_review", "evidence_synthesis"],
        priority=3
    )
    research_agent = registry.create_agent(research_config)
    print(f"✓ Created: {research_agent.config.name}")
    print()
    
    # Step 3: Execute Individual Agent Tasks
    print("Step 3: Executing Individual Agent Tasks")
    print("-" * 70)
    
    # Diagnosis task
    diagnosis_task = {
        "task_id": "DIAG-001",
        "patient_id": "PT-12345",
        "symptoms": ["fever", "cough", "fatigue"],
        "medical_history": {"chronic_conditions": []}
    }
    
    diagnosis_result = diagnosis_agent.execute(diagnosis_task)
    print(f"✓ Diagnosis Task: {diagnosis_result['status']}")
    print(f"  Processing Time: {diagnosis_result.get('processing_time', 0):.3f}s")
    
    # Treatment planning task
    treatment_task = {
        "task_id": "TREAT-001",
        "patient_id": "PT-12345",
        "diagnosis": "Influenza Type A"
    }
    
    treatment_result = treatment_agent.execute(treatment_task)
    print(f"✓ Treatment Task: {treatment_result['status']}")
    print(f"  Processing Time: {treatment_result.get('processing_time', 0):.3f}s")
    
    # Monitoring task
    monitoring_task = {
        "task_id": "MON-001",
        "patient_id": "PT-12345",
        "vital_signs": {
            "temperature": 38.5,
            "heart_rate": 95,
            "blood_pressure": "120/80"
        }
    }
    
    monitoring_result = monitoring_agent.execute(monitoring_task)
    print(f"✓ Monitoring Task: {monitoring_result['status']}")
    print(f"  Processing Time: {monitoring_result.get('processing_time', 0):.3f}s")
    print()
    
    # Step 4: Agent Orchestration
    print("Step 4: Multi-Agent Orchestration")
    print("-" * 70)
    
    orchestrator = AgentOrchestrator(registry)
    workflow_engine = WorkflowEngine(orchestrator)
    
    # Create a sequential workflow for patient care
    patient_care_workflow = workflow_engine.create_sequential_workflow([
        {
            "task_id": "WF-DIAG",
            "agent_type": "medical_diagnosis",
            "patient_id": "PT-67890",
            "symptoms": ["chest pain", "shortness of breath"]
        },
        {
            "task_id": "WF-TREAT",
            "agent_type": "treatment_planning",
            "patient_id": "PT-67890",
            "diagnosis": "Suspected cardiac event"
        },
        {
            "task_id": "WF-MON",
            "agent_type": "patient_monitoring",
            "patient_id": "PT-67890",
            "vital_signs": {"heart_rate": 110, "blood_pressure": "140/95"}
        }
    ])
    
    workflow_id = orchestrator.execute_workflow(patient_care_workflow)
    print(f"✓ Workflow Created: {workflow_id}")
    print(f"  Tasks: 3 (Diagnosis → Treatment → Monitoring)")
    
    # Get workflow status
    workflow_status = orchestrator.get_workflow_status(workflow_id)
    print(f"  Status: {workflow_status['status']}")
    print()
    
    # Step 5: Agent Monitoring & Observability
    print("Step 5: Agent Monitoring & Health Checks")
    print("-" * 70)
    
    observer = AgentObserver()
    
    # Monitor all agents
    for agent in registry.list_agents():
        agent_obj = registry.get_agent(agent["agent_id"])
        observer.monitor_agent(agent_obj)
    
    # Generate monitoring report
    monitoring_report = observer.generate_monitoring_report()
    print(f"✓ Monitoring Report Generated")
    print(f"  Total Agents: {monitoring_report['total_agents_monitored']}")
    print(f"  Healthy: {monitoring_report['health_summary']['healthy']}")
    print(f"  Degraded: {monitoring_report['health_summary']['degraded']}")
    print(f"  Total Alerts: {monitoring_report['alerts']['total']}")
    print()
    
    # Step 6: Registry Statistics
    print("Step 6: Registry Statistics")
    print("-" * 70)
    
    stats = registry.get_statistics()
    print(f"Total Agents: {stats['total_agents']}")
    print(f"Tasks Completed: {stats['total_tasks_completed']}")
    print(f"Tasks Failed: {stats['total_tasks_failed']}")
    print(f"Success Rate: {stats['success_rate']:.1%}")
    print()
    
    # Step 7: List All Agents
    print("Step 7: Active Agents Summary")
    print("-" * 70)
    
    agents = registry.list_agents()
    for agent_info in agents:
        print(f"• {agent_info['name']}")
        print(f"  Type: {agent_info['type']}")
        print(f"  Status: {agent_info['status']}")
        print(f"  Tasks: {agent_info['tasks_completed']} completed, {agent_info['tasks_failed']} failed")
        print(f"  Capabilities: {', '.join(agent_info['capabilities'][:3])}")
        print()
    
    print("=" * 70)
    print("Framework demonstration complete!")
    print("=" * 70)
    print()
    print("Next Steps:")
    print("1. Integrate actual AI models (OpenAI, Anthropic, AWS Bedrock)")
    print("2. Connect to medical databases and EHR systems")
    print("3. Deploy agents to production AWS infrastructure")
    print("4. Set up real-time monitoring and alerting")
    print("5. Implement advanced workflow orchestration")
    print()


if __name__ == "__main__":
    main()

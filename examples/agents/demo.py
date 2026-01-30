"""
AI-Med-Agent Framework Demo
Demonstrates the complete enterprise AI agent framework with medical agents
"""

import sys
import os
import logging
from datetime import datetime

# Add parent directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Import framework components
from agents.base.agent import AgentConfig
from agents.base.protocol import AgentProtocol
from agents.medical.diagnosis_agent import DiagnosisAgent
from agents.medical.triage_agent import TriageAgent
from agents.medical.monitoring_agent import PatientMonitoringAgent
from agents.orchestration.orchestrator import AgentOrchestrator
from agents.orchestration.coordinator import AgentCoordinator
from agents.memory.manager import MemoryManager
from agents.monitoring.metrics import MetricsCollector


def print_section(title: str):
    """Print a section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def demo_medical_agents():
    """Demonstrate medical agents working together"""
    
    print_section("AI-Med-Agent Framework Demo")
    
    # Initialize shared components
    print("🔧 Initializing framework components...")
    protocol = AgentProtocol()
    memory_manager = MemoryManager()
    metrics = MetricsCollector()
    orchestrator = AgentOrchestrator(protocol=protocol)
    coordinator = AgentCoordinator(orchestrator=orchestrator)
    
    # Create medical agents
    print("👥 Creating specialized medical agents...")
    
    # Diagnosis Agent
    diagnosis_config = AgentConfig(
        agent_name="Dr. Diagnosis",
        agent_type="diagnosis",
        log_level="INFO"
    )
    diagnosis_agent = DiagnosisAgent(diagnosis_config, memory_manager)
    
    # Triage Agent
    triage_config = AgentConfig(
        agent_name="Nurse Triage",
        agent_type="triage",
        log_level="INFO"
    )
    triage_agent = TriageAgent(triage_config, memory_manager)
    
    # Monitoring Agent
    monitoring_config = AgentConfig(
        agent_name="Monitor Pro",
        agent_type="monitoring",
        log_level="INFO"
    )
    monitoring_agent = PatientMonitoringAgent(monitoring_config, memory_manager)
    
    # Register agents with orchestrator
    print("📋 Registering agents with orchestrator...")
    orchestrator.register_agent(diagnosis_agent)
    orchestrator.register_agent(triage_agent)
    orchestrator.register_agent(monitoring_agent)
    
    # Start all agents
    print("▶️  Starting all agents...\n")
    orchestrator.start_all()
    
    # Demo 1: Patient Triage
    print_section("Demo 1: Patient Triage Assessment")
    
    patient_data = {
        'patient_id': 'P-001',
        'symptoms': ['chest pain', 'difficulty breathing'],
        'vital_signs': {
            'heart_rate': 110,
            'systolic_bp': 160,
            'oxygen_saturation': 92,
            'temperature': 37.2
        },
        'chief_complaint': 'Chest discomfort and shortness of breath'
    }
    
    print(f"Patient: {patient_data['patient_id']}")
    print(f"Symptoms: {', '.join(patient_data['symptoms'])}")
    print(f"Vital Signs: HR={patient_data['vital_signs']['heart_rate']}, "
          f"BP={patient_data['vital_signs']['systolic_bp']}, "
          f"O2={patient_data['vital_signs']['oxygen_saturation']}%")
    
    # Send triage request
    triage_agent.send_message(
        receiver_id=triage_agent.agent_id,
        payload=patient_data
    )
    
    # Process messages
    messages_processed = orchestrator.process_messages()
    
    # Get triage result from agent state
    print(f"\n✅ Triage completed!")
    print(f"   Status: {triage_agent.status.value}")
    print(f"   Patients triaged: {triage_agent.get_state('patients_triaged', 0)}")
    
    # Demo 2: Diagnosis Consultation
    print_section("Demo 2: Medical Diagnosis Consultation")
    
    diagnosis_data = {
        'patient_id': 'P-002',
        'symptoms': ['fever', 'cough', 'fatigue', 'headache'],
        'medical_history': {
            'age': 45,
            'conditions': ['hypertension']
        }
    }
    
    print(f"Patient: {diagnosis_data['patient_id']}")
    print(f"Symptoms: {', '.join(diagnosis_data['symptoms'])}")
    
    # Send diagnosis request
    diagnosis_agent.send_message(
        receiver_id=diagnosis_agent.agent_id,
        payload=diagnosis_data
    )
    
    # Process messages
    messages_processed = orchestrator.process_messages()
    
    print(f"\n✅ Diagnosis analysis completed!")
    print(f"   Status: {diagnosis_agent.status.value}")
    print(f"   Consultations: {diagnosis_agent.get_state('consultations_count', 0)}")
    
    # Demo 3: Patient Monitoring
    print_section("Demo 3: Continuous Patient Monitoring")
    
    print("📊 Recording vital signs for patient P-003...")
    
    # Simulate multiple vital sign readings
    vital_readings = [
        {'heart_rate': 75, 'oxygen_saturation': 98, 'temperature': 36.8},
        {'heart_rate': 78, 'oxygen_saturation': 97, 'temperature': 36.9},
        {'heart_rate': 82, 'oxygen_saturation': 96, 'temperature': 37.0},
        {'heart_rate': 145, 'oxygen_saturation': 89, 'temperature': 38.5},  # Abnormal
    ]
    
    for i, vitals in enumerate(vital_readings, 1):
        monitoring_data = {
            'patient_id': 'P-003',
            'vital_signs': vitals,
            'timestamp': datetime.utcnow().isoformat(),
            'action': 'record'
        }
        
        monitoring_agent.send_message(
            receiver_id=monitoring_agent.agent_id,
            payload=monitoring_data
        )
        
        orchestrator.process_messages()
        print(f"   Reading {i}: HR={vitals['heart_rate']}, "
              f"O2={vitals['oxygen_saturation']}%, Temp={vitals['temperature']}°C")
    
    # Analyze patient
    analysis_request = {
        'patient_id': 'P-003',
        'action': 'analyze'
    }
    
    monitoring_agent.send_message(
        receiver_id=monitoring_agent.agent_id,
        payload=analysis_request
    )
    
    orchestrator.process_messages()
    
    print(f"\n✅ Monitoring analysis completed!")
    print(f"   Alerts generated: {monitoring_agent.get_state('alerts_generated', 0)}")
    
    # Demo 4: Multi-Agent Collaboration
    print_section("Demo 4: Multi-Agent Collaboration Workflow")
    
    print("🤝 Coordinating multiple agents for comprehensive patient care...")
    
    # Create a workflow
    workflow_steps = [
        {
            'agent_id': triage_agent.agent_id,
            'action': 'assess_priority',
            'params': {'patient_id': 'P-004'}
        },
        {
            'agent_id': diagnosis_agent.agent_id,
            'action': 'analyze_symptoms',
            'params': {'patient_id': 'P-004'}
        },
        {
            'agent_id': monitoring_agent.agent_id,
            'action': 'start_monitoring',
            'params': {'patient_id': 'P-004'}
        }
    ]
    
    coordinator.create_workflow('patient-care-workflow', workflow_steps)
    workflow_result = coordinator.execute_workflow('patient-care-workflow')
    
    print(f"   Workflow Status: {workflow_result['status']}")
    print(f"   Steps Completed: {workflow_result['current_step']}/{len(workflow_steps)}")
    
    # Framework Status
    print_section("Framework Status Summary")
    
    print("📊 Orchestrator Status:")
    orch_status = orchestrator.get_status()
    print(f"   Total Agents: {orch_status['total_agents']}")
    print(f"   Agents by Status: {orch_status['agents_by_status']}")
    
    print("\n🏥 Agent Details:")
    for agent in [diagnosis_agent, triage_agent, monitoring_agent]:
        status = agent.get_status()
        print(f"\n   {status['agent_name']} ({status['agent_type']}):")
        print(f"      Status: {status['status']}")
        print(f"      Messages Processed: {status['message_count']}")
        print(f"      Processing Count: {status['processing_count']}")
        print(f"      Error Count: {status['error_count']}")
    
    print("\n🧠 Memory Summary:")
    for agent in [diagnosis_agent, triage_agent, monitoring_agent]:
        summary = memory_manager.get_memory_summary(agent.agent_id)
        print(f"\n   {agent.config.agent_name}:")
        print(f"      Total Memories: {summary['total_memories']}")
        if summary['total_memories'] > 0:
            print(f"      By Type: {summary['by_type']}")
            print(f"      Average Importance: {summary['average_importance']:.2f}")
    
    # Health Check
    print("\n🏥 Health Check:")
    health = orchestrator.health_check()
    for agent_id, health_status in health.items():
        agent = orchestrator.get_agent(agent_id)
        print(f"   {agent.config.agent_name}: {'✅ Healthy' if health_status['healthy'] else '❌ Unhealthy'}")
    
    # Cleanup
    print_section("Shutting Down")
    print("⏹️  Stopping all agents...")
    orchestrator.stop_all()
    
    print("\n✅ Demo completed successfully!")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    try:
        demo_medical_agents()
    except Exception as e:
        print(f"\n❌ Error during demo: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

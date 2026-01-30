# AI-Med-Agent Framework Guide

## Table of Contents

1. [Getting Started](#getting-started)
2. [Core Concepts](#core-concepts)
3. [Creating Agents](#creating-agents)
4. [Agent Communication](#agent-communication)
5. [Memory Management](#memory-management)
6. [Orchestration](#orchestration)
7. [Monitoring](#monitoring)
8. [Configuration](#configuration)
9. [Testing](#testing)
10. [Deployment](#deployment)

## Getting Started

### Installation

```bash
# Clone the repository
git clone https://github.com/AI-Empower-Cloud-Hub-LLC/AI-Med-Agent.git
cd AI-Med-Agent

# Install dependencies
pip install -r requirements.txt

# Run the demo
python examples/agents/demo.py
```

### Quick Example

```python
from agents.base.agent import AgentConfig
from agents.medical.diagnosis_agent import DiagnosisAgent
from agents.orchestration.orchestrator import AgentOrchestrator

# Create orchestrator
orchestrator = AgentOrchestrator()

# Create and register agent
config = AgentConfig(agent_name="Dr. AI", agent_type="diagnosis")
agent = DiagnosisAgent(config)
orchestrator.register_agent(agent)

# Start agent
orchestrator.start_all()

# Send request
agent.send_message(
    receiver_id=agent.agent_id,
    payload={
        'patient_id': 'P-001',
        'symptoms': ['fever', 'cough']
    }
)

# Process messages
orchestrator.process_messages()
```

## Core Concepts

### Agents

Agents are autonomous entities that:
- Process messages independently
- Maintain their own state
- Communicate via standardized protocols
- Can collaborate with other agents

### Messages

Messages are the primary communication mechanism:

```python
from agents.base.protocol import AgentMessage, MessageType

message = AgentMessage(
    sender_id="agent-1",
    receiver_id="agent-2",
    message_type=MessageType.REQUEST,
    payload={'action': 'diagnose', 'data': {...}}
)
```

### Lifecycle

Agent lifecycle states:
1. **INITIALIZING**: Being set up
2. **IDLE**: Ready and waiting
3. **PROCESSING**: Handling a message
4. **ERROR**: Error state
5. **STOPPED**: Shut down

## Creating Agents

### Basic Agent

```python
from agents.base.agent import BaseAgent, AgentConfig
from agents.base.protocol import AgentMessage

class MyCustomAgent(BaseAgent):
    """Custom agent implementation"""
    
    def _on_start(self):
        """Called when agent starts"""
        self.logger.info("Custom agent starting")
        self.update_state('initialized', True)
    
    def _handle_request(self, message: AgentMessage):
        """Handle incoming requests"""
        action = message.payload.get('action')
        
        if action == 'process':
            result = self._do_processing(message.payload)
            return self.protocol.create_response(
                message,
                {'result': result}
            )
        
        return self._create_error_response(
            message,
            f"Unknown action: {action}"
        )
    
    def _do_processing(self, data):
        """Custom processing logic"""
        return {"status": "processed"}

# Usage
config = AgentConfig(
    agent_name="MyAgent",
    agent_type="custom"
)
agent = MyCustomAgent(config)
agent.start()
```

### Medical Agent Example

```python
from agents.medical.diagnosis_agent import DiagnosisAgent
from agents.memory.manager import MemoryManager

# Create with memory
memory = MemoryManager()
config = AgentConfig(
    agent_name="Diagnostician",
    agent_type="diagnosis"
)
agent = DiagnosisAgent(config, memory)
agent.start()

# Send diagnosis request
agent.send_message(
    receiver_id=agent.agent_id,
    payload={
        'patient_id': 'P-123',
        'symptoms': ['fever', 'cough', 'fatigue'],
        'medical_history': {'age': 45}
    }
)

# Process and get result
messages = agent.receive_messages()
for msg in messages:
    response = agent.process_message(msg)
    print(response.payload)
```

## Agent Communication

### Direct Messaging

```python
# Agent A sends to Agent B
agent_a.send_message(
    receiver_id=agent_b.agent_id,
    payload={'data': 'hello'},
    message_type=MessageType.REQUEST
)

# Agent B receives and processes
messages = agent_b.receive_messages()
for msg in messages:
    response = agent_b.process_message(msg)
    if response:
        protocol.send_message(response)
```

### Broadcasting

```python
# Send to all agents
orchestrator.send_broadcast(
    sender_id=agent.agent_id,
    payload={'alert': 'system notification'}
)
```

### Request-Response Pattern

```python
# Send request
request = protocol.create_request(
    sender_id="agent-1",
    receiver_id="agent-2",
    payload={'query': 'data'}
)
protocol.send_message(request)

# Agent 2 processes and responds
response = protocol.create_response(
    original_message=request,
    payload={'result': 'data response'}
)
protocol.send_message(response)
```

## Memory Management

### Storing Memories

```python
from agents.memory.manager import MemoryManager, MemoryType

memory = MemoryManager()

# Store episodic memory (event)
memory.remember(
    agent_id="agent-1",
    memory_type=MemoryType.EPISODIC,
    content={
        'event': 'patient_consultation',
        'patient_id': 'P-123',
        'diagnosis': 'influenza'
    },
    importance=0.8
)

# Store semantic memory (knowledge)
memory.remember(
    agent_id="agent-1",
    memory_type=MemoryType.SEMANTIC,
    content={
        'fact': 'Fever is a symptom of influenza',
        'confidence': 0.95
    },
    importance=0.7
)
```

### Retrieving Memories

```python
# Get recent memories
recent = memory.recall_recent(
    agent_id="agent-1",
    memory_type=MemoryType.EPISODIC,
    limit=10
)

# Get important memories
important = memory.recall_important(
    agent_id="agent-1",
    min_importance=0.8,
    limit=5
)

# Get memory summary
summary = memory.get_memory_summary("agent-1")
print(f"Total memories: {summary['total_memories']}")
print(f"By type: {summary['by_type']}")
```

## Orchestration

### Basic Orchestration

```python
from agents.orchestration.orchestrator import AgentOrchestrator

orchestrator = AgentOrchestrator()

# Register multiple agents
orchestrator.register_agent(diagnosis_agent)
orchestrator.register_agent(triage_agent)
orchestrator.register_agent(monitoring_agent)

# Start all
orchestrator.start_all()

# Process all pending messages
count = orchestrator.process_messages()
print(f"Processed {count} messages")

# Health check
health = orchestrator.health_check()
for agent_id, status in health.items():
    print(f"{agent_id}: {'Healthy' if status['healthy'] else 'Unhealthy'}")
```

### Workflow Coordination

```python
from agents.orchestration.coordinator import AgentCoordinator

coordinator = AgentCoordinator(orchestrator)

# Define workflow
workflow_steps = [
    {
        'agent_id': triage_agent.agent_id,
        'action': 'assess_priority',
        'params': {'patient_id': 'P-001'}
    },
    {
        'agent_id': diagnosis_agent.agent_id,
        'action': 'diagnose',
        'params': {'patient_id': 'P-001'}
    },
    {
        'agent_id': monitoring_agent.agent_id,
        'action': 'start_monitoring',
        'params': {'patient_id': 'P-001'}
    }
]

# Execute workflow
coordinator.create_workflow('patient-intake', workflow_steps)
result = coordinator.execute_workflow('patient-intake')

print(f"Workflow status: {result['status']}")
print(f"Steps completed: {result['current_step']}")
```

## Monitoring

### Metrics Collection

```python
from agents.monitoring.metrics import MetricsCollector

metrics = MetricsCollector()

# Record metrics
metrics.record_metric(
    agent_id="agent-1",
    metric_name="processing_time",
    value=125.5,
    metadata={'unit': 'ms'}
)

# Get aggregated metrics
agg = metrics.get_aggregate_metrics("agent-1")
print(f"Avg processing time: {agg['processing_time']['avg']} ms")

# Export metrics
metrics.export_metrics('/tmp/metrics.json')
```

### Structured Logging

```python
from agents.monitoring.logger import AgentLogger

logger = AgentLogger("agent-1", log_level="INFO")

# Log events
logger.log_event(
    event_type="patient_processed",
    message="Patient diagnosis completed",
    data={'patient_id': 'P-001', 'duration': 125}
)

# Log errors
try:
    # ... some operation
    pass
except Exception as e:
    logger.log_error(e, context={'operation': 'diagnosis'})

# Log performance
logger.log_performance(
    operation="symptom_analysis",
    duration_ms=45.2,
    success=True
)
```

## Configuration

### YAML Configuration

```yaml
# config/agents/agent_config.yaml
agents:
  defaults:
    max_retries: 3
    timeout_seconds: 30
    enable_logging: true
    log_level: INFO
  
  diagnosis:
    agent_type: diagnosis
    agent_name: DiagnosisAgent
    max_retries: 5
    timeout_seconds: 60
```

### Using ConfigManager

```python
from config.agents.config_manager import ConfigManager

# Load configuration
config_mgr = ConfigManager(
    config_file='config/agents/agent_config.yaml'
)

# Get agent config
agent_config = config_mgr.get_agent_config('diagnosis')
print(agent_config)

# Get specific values
timeout = config_mgr.get('agents.diagnosis.timeout_seconds')

# Override with environment variable
# AGENT_DIAGNOSIS_TIMEOUT_SECONDS=90 python app.py
```

## Testing

### Unit Tests

```python
import unittest
from agents.base.agent import BaseAgent, AgentConfig

class TestMyAgent(unittest.TestCase):
    def setUp(self):
        config = AgentConfig(
            agent_name="TestAgent",
            agent_type="test"
        )
        self.agent = MyCustomAgent(config)
    
    def test_agent_start(self):
        self.agent.start()
        self.assertEqual(self.agent.status, AgentStatus.IDLE)
    
    def test_message_processing(self):
        self.agent.start()
        message = self.agent.protocol.create_request(
            "sender",
            self.agent.agent_id,
            {'action': 'test'}
        )
        response = self.agent.process_message(message)
        self.assertIsNotNone(response)
```

### Running Tests

```bash
# Run all tests
python -m unittest discover tests/

# Run specific test file
python -m unittest tests/agents/test_base_agent.py

# Run with coverage
pip install coverage
coverage run -m unittest discover tests/
coverage report
```

## Deployment

### Production Deployment

```python
# production_app.py
import logging
from agents.orchestration.orchestrator import AgentOrchestrator
from agents.medical import DiagnosisAgent, TriageAgent, PatientMonitoringAgent
from config.agents.config_manager import ConfigManager

# Set up logging
logging.basicConfig(level=logging.INFO)

# Load production config
config_mgr = ConfigManager(
    config_file='/etc/ai-med-agent/config.yaml'
)

# Initialize orchestrator
orchestrator = AgentOrchestrator()

# Create and register agents
agents = [
    DiagnosisAgent(config_mgr.get_agent_config('diagnosis')),
    TriageAgent(config_mgr.get_agent_config('triage')),
    PatientMonitoringAgent(config_mgr.get_agent_config('monitoring'))
]

for agent in agents:
    orchestrator.register_agent(agent)

# Start system
orchestrator.start_all()

# Main processing loop
while True:
    orchestrator.process_messages()
    # Add sleep or event-driven trigger
```

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "production_app.py"]
```

### AWS Deployment

- Deploy on **ECS/Fargate** for container orchestration
- Use **Lambda** for serverless agent execution
- **SQS** for message queuing between agents
- **DynamoDB** for distributed state/memory
- **CloudWatch** for monitoring and logging

## Best Practices

1. **Always use try-except** in agent message handlers
2. **Validate inputs** using `MessageValidator`
3. **Set appropriate timeouts** for operations
4. **Use structured logging** for observability
5. **Implement health checks** for production
6. **Store sensitive data** in AWS Secrets Manager
7. **Test agents individually** before orchestration
8. **Monitor memory usage** for long-running agents
9. **Use configuration files** for environment-specific settings
10. **Document custom agents** with clear examples

## Additional Resources

- [Architecture Documentation](ARCHITECTURE.md)
- [API Reference](API_REFERENCE.md)
- [Example Demos](../../examples/agents/)
- [Test Suite](../../tests/agents/)

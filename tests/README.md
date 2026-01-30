# Running Tests

## Quick Start

Run all tests with:

```bash
cd /home/runner/work/AI-Med-Agent/AI-Med-Agent
export PYTHONPATH=$PYTHONPATH:$(pwd)
python -m unittest tests/agents/test_base_agent.py tests/agents/test_medical_agents.py tests/agents/test_orchestration.py -v
```

Or run individual test files:

```bash
# Test base agent
python -m unittest tests/agents/test_base_agent.py -v

# Test medical agents
python -m unittest tests/agents/test_medical_agents.py -v

# Test orchestration
python -m unittest tests/agents/test_orchestration.py -v
```

## Test Coverage

- `test_base_agent.py`: Tests for BaseAgent, AgentConfig, AgentProtocol
- `test_medical_agents.py`: Tests for DiagnosisAgent, TriageAgent, PatientMonitoringAgent
- `test_orchestration.py`: Tests for AgentOrchestrator and AgentCoordinator

## Running with Coverage

```bash
pip install coverage
export PYTHONPATH=$PYTHONPATH:$(pwd)
coverage run -m unittest tests/agents/test_base_agent.py tests/agents/test_medical_agents.py tests/agents/test_orchestration.py
coverage report
coverage html
```

## CI/CD

Tests are automatically run via GitHub Actions on push to main/develop branches.
See `.github/workflows/agent-framework.yml` for details.

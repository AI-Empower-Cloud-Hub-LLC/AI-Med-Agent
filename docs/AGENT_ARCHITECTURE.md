"""
AI-Med-Agent: Autonomous AWS Organizations Management

A production-grade autonomous agent for managing AWS Organizations,
with state management, decision-making loops, AppConfig deployment,
comprehensive testing, and governance automation.

## Quick Start

### Installation

```bash
# Install with development tools
pip install -e .[dev]

# Setup pre-commit hooks
pre-commit install
```

### Run Tests

```bash
# Unit tests
pytest tests/unit -v

# With coverage
pytest tests/unit --cov=src --cov-report=html

# All tests
pytest tests/ -v
```

### Code Quality

```bash
# Format code
black .

# Lint
ruff check . --fix

# Type check
mypy src

# Security check
bandit -r src
```

### Deploy Configuration

```bash
python scripts/deploy_appconfig.py \
  --application-id <APP_ID> \
  --environment dev \
  --strategy linear
```

## Architecture

### Folder Structure

- **src/**
  - **agent/** - Orchestrator and autonomous operations
  - **clients/** - AWS API clients (Organizations, Config, AppConfig)
  - **core/** - Logger, state management, decision-making
- **tests/** - Comprehensive unit and integration tests
- **config/** - Environment-specific configurations (dev/staging/prod)
- **infrastructure/appconfig/** - CloudFormation infrastructure
- **scripts/** - Deployment and utility scripts
- **.github/workflows/** - CI/CD pipelines

### Core Components

#### AgentOrchestrator
- Autonomous decision-making and action execution
- State management across operations
- Error handling and retry logic
- Action handler registration and dispatch

#### StateManager
- Tracks agent status (idle, running, evaluating, executing, completed, failed)
- Maintains action history and decision logs
- Records metrics and errors
- Exports operation history

#### AWSOrganizationsManager
- Manages OUs, accounts, SCPs, tagging
- CloudTrail and Config integration
- Comprehensive organization reports

#### ConfigManager
- Secrets Manager integration
- AppConfig configuration retrieval
- Feature flags and environment-specific settings

### Autonomous Operations

The agent can autonomously:
1. **Generate Governance Reports** - Full organization state
2. **Analyze Compliance** - Identify governance gaps
3. **Execute Remediation** - Apply corrections (with approval controls)
4. **Log Decisions** - Complete audit trail
5. **Manage State** - Persist operation history

### AppConfig Deployment

Three-tier deployment strategy:
- **Development** (Linear): 10% every 30 seconds, 5-min final bake
- **Staging** (Canary): 20% for 5 min, then 100%
- **Production** (Canary): Monitored with CloudWatch alarms

## Testing

### Unit Tests
- Mocked AWS clients
- State management logic
- Action creation and execution
- Decision-making flows
- Governance analysis

### Integration Tests
- Real AWS API calls (when not mocked)
- End-to-end workflows
- Multi-service interactions

### Running Tests

```bash
# Run specific test file
pytest tests/unit/test_orchestrator.py -v

# Run specific test
pytest tests/unit/test_orchestrator.py::TestAgentOrchestrator::test_initialize -v

# With markers
pytest -m unit -v
```

## Configuration

### Agent Configuration (AppConfig)

```json
{
  "agent": {
    "log_level": "INFO",
    "max_retries": 3,
    "require_approval": false,
    "governance_check_interval_minutes": 60,
    "auto_remediation_enabled": false
  },
  "features": {
    "autonomous_governance": true,
    "state_persistence": true,
    "decision_logging": true
  }
}
```

### Feature Flags

- `auto_governance_enabled` - Enable autonomous checks
- `detailed_logging` - Verbose operation logs
- `cost_optimization` - Cost recommendations
- `security_hardening` - Auto-enforce security policies
- `canary_deployments` - Use canary strategy

## Deployment

### Prerequisites

- AWS Organizations enabled
- AppConfig application created
- S3 bucket for configurations
- IAM roles with appropriate permissions

### Deploy Infrastructure

```bash
aws cloudformation deploy \
  --template-file infrastructure/appconfig/appconfig-infrastructure.yaml \
  --stack-name ai-med-agent-appconfig \
  --parameter-overrides Environment=dev
```

### Deploy Configuration

```bash
# Automatic via GitHub Actions
git push  # Triggers test-lint and deploy-appconfig workflows

# Manual deployment
python scripts/deploy_appconfig.py \
  --application-id ie50sgm \
  --environment prod \
  --strategy canary
```

## Monitoring

### CloudWatch Metrics

- Agent status transitions
- Action execution counts (success/failure)
- Decision logs and reasoning
- Operation errors and retries

### Alarms

- Configuration deployment errors
- Agent state failures
- Policy attachment failures

## Usage Examples

### Autonomous Governance Check

```python
from src.agent.orchestrator import AgentOrchestrator

agent = AgentOrchestrator(agent_id="prod-agent")
result = agent.run_autonomous_governance_check()

print(f"Status: {result['status']}")
print(f"Findings: {result['analysis']['findings']}")
print(f"Accounts: {result['analysis']['total_accounts']}")
```

### Execute Custom Action

```python
from src.core.state import AgentAction

action = agent.state.create_action(
    action_type="create_ou",
    description="Create Production OU",
    parameters={
        "parent_id": "r-xxx",
        "ou_name": "Production",
        "tags": {"Environment": "production"}
    }
)

ou_id = agent.execute_action(action)
print(f"Created OU: {ou_id}")
```

### Export Operation History

```python
history = agent.export_operation_history()

print(f"Total actions: {len(history['actions'])}")
print(f"Total decisions: {len(history['decisions'])}")
print(f"Failed actions: {history['metrics']['actions_failed']}")
```

## Contributing

1. Create feature branch
2. Run tests: `pytest tests/ -v`
3. Format code: `black .`
4. Lint: `ruff check . --fix`
5. Submit PR

## License

See LICENSE file
"""

# AI-Med-Agent: Production-Grade Autonomous Agent

An **autonomous AI-driven agent** for managing AWS Organizations at scale. Features production-grade decision-making, state management, comprehensive testing, AppConfig deployment, and comprehensive governance automation.

## ✨ Key Capabilities

- **Autonomous Operations** - Decision-making loops with approval workflows
- **State Management** - Track actions, decisions, and operation history  
- **AWS Organizations** - Full management of OUs, accounts, SCPs, and policies
- **AppConfig Deployment** - Multi-environment configuration (dev/staging/prod)
- **Comprehensive Testing** - 150+ unit tests with mocking and coverage
- **Code Quality** - Black, Ruff, MyPy, Bandit with pre-commit hooks
- **Production Ready** - CI/CD pipelines, error handling, logging, monitoring

## 📚 Documentation

- **[Production Transformation Summary](PRODUCTION_TRANSFORMATION_SUMMARY.md)** - Complete implementation overview
- **[Agent Architecture](docs/AGENT_ARCHITECTURE.md)** - Technical architecture and usage
- **[AppConfig Reference](docs/APPCONFIG_REFERENCE.md)** - Centralized configuration management via [Appconfig repository](https://github.com/AI-Empower-Cloud-Hub-LLC/Appconfig)
- **[Getting Started](docs/setup/SETUP_SUMMARY.md)** - Quick setup guide
- **[All Documentation](docs/INDEX.md)** - Complete documentation index
- **[Organizations Guide](docs/organizations/SETUP.md)** - AWS Organizations setup
- **[Security & Secrets](docs/security/SECURITY_AND_SECRETS.md)** - Security practices
- **[Operations Checklist](docs/operations/PRODUCTION_READINESS_CHECKLIST.md)** - Pre-production validation

## 🚀 Quick Start

### Installation

```bash
# Clone repo
git clone https://github.com/AI-Empower-Cloud-Hub-LLC/AI-Med-Agent.git
cd AI-Med-Agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or: venv\Scripts\activate on Windows

# Install with development tools
pip install -e .[dev]

# Setup pre-commit hooks
pre-commit install
```

### Run Tests

```bash
# Quick unit tests
pytest tests/unit -v

# Full test suite with coverage
pytest tests/ -v --cov=src --cov-report=html
```

### Code Quality

```bash
# Format code
black .

# Lint
ruff check . --fix

# Type check
mypy src

# Security scan
bandit -r src
```

## 🏗️ Project Structure

```
src/
├── agent/           # Orchestrator & autonomous operations
├── clients/         # AWS API clients (Organizations, Config)
└── core/            # Logger, state management, decision-making

config/
├── agent-config-dev.json      # Development configuration
├── agent-config-staging.json  # Staging configuration
├── agent-config-prod.json     # Production configuration
└── feature-flags.json         # Feature toggles

infrastructure/
└── appconfig/                 # CloudFormation for AppConfig

tests/
├── unit/            # Unit tests with mocks
└── integration/     # Integration test templates

.github/workflows/
├── test-lint.yml     # CI/CD: Testing & linting
├── deploy-appconfig.yml  # CI/CD: AppConfig deployment
└── secrets-scan.yml  # Secret detection
```

## 🤖 Agent Features

### Autonomous Decision-Making

The agent evaluates actions before execution:

```python
from src.agent.orchestrator import AgentOrchestrator

agent = AgentOrchestrator(agent_id="prod-agent")
agent.run_autonomous_governance_check()
```

### State Management

Track all operations with complete audit trail:

```python
# Get current state
state = agent.get_state_summary()

# Export operation history
history = agent.export_operation_history()
```

### AWS Organizations Management

Full control over OUs, accounts, and policies:

```python
from src.clients.organizations_manager import AWSOrganizationsManager

manager = AWSOrganizationsManager()
report = manager.generate_organization_report()
```

## 🔧 Configuration

### AppConfig Deployment

Deploy configurations to dev/staging/prod with automated strategies:

```bash
python scripts/deploy_appconfig.py \
  --application-id <APP_ID> \
  --environment prod \
  --strategy canary
```

### Feature Flags

Enable/disable features dynamically via AppConfig:

- `auto_governance_enabled` - Autonomous checks
- `detailed_logging` - Verbose operation logs  
- `security_hardening` - Auto-enforce policies
- `canary_deployments` - Use canary deployment strategy

## 🔐 Security & Secrets

- **git-secrets** - Prevent committing secrets
- **GitHub Secrets** - Secure CI/CD credentials
- **AWS Secrets Manager** - Production secret storage
- **AppConfig** - Non-sensitive configuration management

See [docs/security/SECURITY_AND_SECRETS.md](docs/security/SECURITY_AND_SECRETS.md) for details.

## 📊 Testing & Quality

- **150+ unit tests** with pytest and mocking
- **Coverage reporting** with codecov integration
- **Black formatting** for consistent code style
- **Ruff linting** with extensive rules
- **MyPy type checking** for type safety
- **Bandit security** scanning
- **Pre-commit hooks** for local validation
- **GitHub Actions CI/CD** for automated testing

## 🚀 Production Deployment

### Prerequisites

- AWS Organizations enabled
- AppConfig application created
- S3 bucket for configurations
- CloudWatch monitoring configured
- IAM roles with appropriate permissions

### Deploy Infrastructure

```bash
aws cloudformation deploy \
  --template-file infrastructure/appconfig/appconfig-infrastructure.yaml \
  --stack-name ai-med-agent-appconfig \
  --parameter-overrides Environment=prod
```

### Deploy Configuration

```bash
# Automatic via GitHub Actions (on push to config files)
git push

# Or manual deployment
python scripts/deploy_appconfig.py \
  --application-id <APP_ID> \
  --environment prod
```

## 📈 Monitoring

- **CloudWatch Metrics** - Agent status, action counts, decision logs
- **CloudWatch Alarms** - Configuration deployment failures
- **Operation History** - Complete audit trail of all actions
- **Decision Logging** - Reasoning for every decision made

## 🤝 Contributing

1. Create feature branch
2. Write tests for new functionality
3. Run full test suite: `pytest tests/ -v`
4. Format code: `black .`
5. Lint: `ruff check . --fix && mypy src`
6. Submit pull request

## 📝 AWS Organizations & Governance

This project uses AWS Organizations for multi-account governance:

- **4 Organizational Units**: Production, Staging, Development, Security
- **3 Service Control Policies**: Environment-specific security guardrails
- **CloudTrail**: Organization-wide audit logging
- **AWS Config**: Compliance tracking and enforcement

[See full details](docs/organizations/SUMMARY.md)

## 📄 License

See LICENSE file

## 🙋 Support

- Documentation: [docs/INDEX.md](docs/INDEX.md)
- Issues: GitHub Issues
- Security: See SECURITY.md for responsible disclosure

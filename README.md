# AI-Med-Agent

An AI Medical Agent is an intelligent healthcare assistant that uses artificial intelligence to help with medical tasks, patient care, and healthcare operations. It's built using AWS services to be secure, compliant, and scalable.

## 🚀 AICloud-Innovation Enterprise Framework

**NEW:** This repository now includes the **AICloud-Innovation Enterprise Framework** - a powerful infrastructure for developing sophisticated AI Agentic Agents at enterprise scale.

### Quick Start with the Framework

```bash
# Run the enterprise framework demo
python examples/enterprise_framework_demo.py
```

**Features:**
- 🤖 **Multi-Agent System**: Coordinate multiple specialized AI agents
- 🏥 **Healthcare Agents**: Diagnosis, Treatment Planning, Patient Monitoring, Clinical Research
- 📊 **Enterprise Monitoring**: Real-time health checks and performance metrics
- 🔄 **Workflow Orchestration**: Sequential, parallel, and conditional agent workflows
- ☁️ **Cloud-Native**: Built for AWS with Organizations integration

**[📖 Complete Framework Documentation →](AICLOUD_INNOVATION_FRAMEWORK.md)**

---

## AWS Organizations & Governance

This project uses AWS Organizations for multi-account governance with:

- **4 Organizational Units (OUs)**: Production, Staging, Development, Security
- **3 Service Control Policies (SCPs)**: Environment-specific security guardrails
- **CloudTrail**: Organization-wide audit logging
- **AWS Config**: Compliance tracking and enforcement

**See [ORGANIZATIONS_SETUP.md](ORGANIZATIONS_SETUP.md) for complete details.**

### Quick Reference
```
Organization ID: o-lz5ryybhfh
Master Account: 996099991638

OUs:
- Production (ou-b0ab-bj6zyii3)
- Staging (ou-b0ab-ky6kdwql)
- Development (ou-b0ab-7t9356e2)
- Security (ou-b0ab-qb48c366)

SCPs:
- ProductionEnvironmentPolicy (p-fnajp74q)
- StagingEnvironmentPolicy (p-5baz2zrv)
- DevelopmentEnvironmentPolicy (p-1vhhyht3)
```

**Python Management:**
```python
from aws_organizations import AWSOrganizationsManager

manager = AWSOrganizationsManager()
report = manager.generate_organization_report()
```

---

## Security & Secrets Management

This project uses multiple layers of secret management to protect sensitive data:

### 1. **git-secrets** (Local Prevention)
Prevents accidentally committing secrets to Git. Hooks are installed on clone/setup.

```bash
# Install locally (if not already installed)
git clone https://github.com/awslabs/git-secrets.git /tmp/git-secrets
cd /tmp/git-secrets && sudo make install

# Configure for this repo
git secrets --install -f
git secrets --register-aws

# Scan for existing secrets
git secrets --scan-history
```

**What it catches:**
- AWS Access Key IDs (AKIA*, ASIA*)
- AWS Secret Access Keys
- Private keys and certificates
- Database passwords
- API tokens (configurable patterns)

### 2. **GitHub Secrets** (CI/CD)
Secure secrets storage for GitHub Actions workflows.

**To add a GitHub Secret:**
1. Go to repo → Settings → Secrets and variables → Actions → New repository secret
2. Add secrets used in `.github/workflows/`:
   - `AWS_ROLE_TO_ASSUME` - IAM role ARN for OIDC (recommended over key/secret)
   - `DEPLOYMENT_TOKEN` - Deployment authorization
   - `SLACK_WEBHOOK_URL` - Slack notifications (optional)

**Usage in workflows:**
```yaml
env:
  DEPLOYMENT_TOKEN: ${{ secrets.DEPLOYMENT_TOKEN }}
run: echo "Token is automatically masked in logs"
```

### 3. **AWS Secrets Manager** (Production)
Store and retrieve secrets from AWS for applications.

```bash
# Store a secret
aws secretsmanager create-secret \
  --name ai-med-agent/db/password \
  --secret-string "your-password"

# Retrieve in app or workflow
DB_PASSWORD=$(aws secretsmanager get-secret-value \
  --secret-id ai-med-agent/db/password \
  --query SecretString \
  --output text)
```

### 4. **Environment Variables** (.env files)
Use `.env.example` as a template. Never commit actual `.env` files.

```bash
cp .env.example .env
# Edit .env with your local values
# .env is in .gitignore
```

**Files to keep secret:**
- `.env` (local development)
- `~/.aws/credentials`
- `~/.aws/config`

### 5. **AppConfig Feature Flags** (Dynamic Configs)
Non-sensitive configurations are managed via AWS AppConfig (created by CloudFormation stack `ai-med-agent-appconfig-dev`).

---

## Setup Instructions

### Prerequisites
- AWS CLI configured with credentials
- git-secrets installed and configured
- GitHub access for CI/CD (optional, for GitHub Actions)

### Installation
```bash
# Clone repo
git clone https://github.com/AI-Empower-360/AI-Med-Agent.git
cd AI-Med-Agent

# Install git-secrets hooks (if not auto-installed)
git secrets --install -f
git secrets --register-aws

# Set up local environment
cp .env.example .env
# Edit .env with your local values

# Install dependencies (Python example)
pip install -r requirements.txt

# Or (Node.js example)
npm install
```

### AWS Integration
```bash
# Configure AWS CLI
aws configure

# Verify credentials
aws sts get-caller-identity

# Retrieve AppConfig settings
aws appconfig get-latest-configuration \
  --application AI-Med-Agent-dev \
  --environment backend-dev \
  --configuration feature-flags \
  --configuration-token INITIAL
```

### Running Locally
```bash
# Start application
python app.py

# Or with Node.js
npm start
```

### CI/CD Pipeline
GitHub Actions workflows are triggered on:
- **Push to main/develop**: Secrets scan + optional deployment
- **Pull requests**: Secrets scan only (no deployment)

**Workflows:**
- `.github/workflows/secrets-scan.yml` - Runs git-secrets in CI
- `.github/workflows/deploy.yml` - Deploys to AWS with GitHub Secrets

---

## Troubleshooting

### git-secrets blocking my commit
```bash
# Review what was detected
git diff --cached

# If it's a false positive, allow it
git secrets --add --allowed '<pattern>'

# Bypass hooks (not recommended, use for testing only)
git commit --no-verify
```

### Missing AWS credentials in workflow
1. Ensure GitHub Secret `AWS_ROLE_TO_ASSUME` is set (OIDC approach is preferred)
2. Or set `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY` as GitHub Secrets (less secure)

### Secrets Manager access denied
```bash
# Check IAM permissions
aws iam get-user

# Verify secret exists and accessible
aws secretsmanager describe-secret --secret-id ai-med-agent/db/password
```

---

## References
- [git-secrets Documentation](https://github.com/awslabs/git-secrets)
- [GitHub Secrets & Variables](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [AWS Secrets Manager](https://docs.aws.amazon.com/secretsmanager/)
- [AWS AppConfig](https://docs.aws.amazon.com/appconfig/)

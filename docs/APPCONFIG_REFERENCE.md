# AppConfig Integration Reference

## Overview

The AI-Med-Agent now uses centralized AppConfig deployment managed through the [Appconfig repository](https://github.com/AI-Empower-Cloud-Hub-LLC/Appconfig).

## Migration Notice

⚠️ **The AppConfig infrastructure has been migrated to a centralized repository for consistency across all AI-Empower-Cloud-Hub projects.**

### What Changed

- **Old Location:** `infrastructure/appconfig/appconfig-infrastructure.yaml` (in this repo)
- **New Location:** [Appconfig/infrastructure/ai-med-agent.yaml](https://github.com/AI-Empower-Cloud-Hub-LLC/Appconfig/blob/main/infrastructure/ai-med-agent.yaml)

### Why This Change?

1. **Centralized Management:** All projects (AI-Med-Agent, AI-Film-Studio, etc.) use the same AppConfig deployment patterns
2. **Consistency:** Shared base template ensures identical infrastructure across projects
3. **Simplified Updates:** Configuration changes in one place propagate to all projects
4. **Better CI/CD:** Automated deployment workflows in dedicated repository

## Using AppConfig with AI-Med-Agent

### Configuration Files

AI-Med-Agent configurations are now maintained in the Appconfig repository:

- **Development:** [configs/ai-med-agent/dev.json](https://github.com/AI-Empower-Cloud-Hub-LLC/Appconfig/blob/main/configs/ai-med-agent/dev.json)
- **Staging:** [configs/ai-med-agent/staging.json](https://github.com/AI-Empower-Cloud-Hub-LLC/Appconfig/blob/main/configs/ai-med-agent/staging.json)
- **Production:** [configs/ai-med-agent/prod.json](https://github.com/AI-Empower-Cloud-Hub-LLC/Appconfig/blob/main/configs/ai-med-agent/prod.json)
- **Feature Flags:** [configs/ai-med-agent/feature-flags.json](https://github.com/AI-Empower-Cloud-Hub-LLC/Appconfig/blob/main/configs/ai-med-agent/feature-flags.json)

### Deployment

To deploy AI-Med-Agent AppConfig changes:

#### Option 1: GitHub Actions (Recommended)

1. Navigate to [Appconfig repository](https://github.com/AI-Empower-Cloud-Hub-LLC/Appconfig)
2. Go to **Actions** tab
3. Select **Deploy AI-Med-Agent AppConfig** workflow
4. Click **Run workflow**
5. Choose environment and deployment strategy
6. Monitor deployment progress

#### Option 2: Local Deployment

```bash
# Clone Appconfig repository
git clone https://github.com/AI-Empower-Cloud-Hub-LLC/Appconfig.git
cd Appconfig

# Install dependencies
pip install -r requirements.txt

# Deploy infrastructure (if not already deployed)
aws cloudformation deploy \
  --template-file infrastructure/ai-med-agent.yaml \
  --stack-name ai-med-agent-appconfig-dev \
  --parameter-overrides Environment=dev \
  --capabilities CAPABILITY_IAM

# Deploy configuration
python scripts/deploy.py \
  --application-id <app-id> \
  --environment dev \
  --config-file configs/ai-med-agent/dev.json \
  --strategy linear \
  --verbose
```

## Configuration Structure

### Application Settings

The AI-Med-Agent uses the following configuration structure:

```json
{
  "agent": {
    "log_level": "INFO",
    "max_retries": 3,
    "require_approval": true,
    "governance_check_interval_seconds": 300
  },
  "aws": {
    "organizations": {
      "enabled": true,
      "default_ou": "Workloads"
    }
  },
  "monitoring": {
    "enabled": true,
    "cloudwatch_namespace": "AIGovernanceAgent"
  }
}
```

### Feature Flags

Feature flags allow toggling capabilities without code changes:

```json
{
  "features": {
    "auto_remediation": {
      "enabled": false,
      "description": "Automatically remediate non-compliant resources"
    },
    "ml_recommendations": {
      "enabled": true,
      "rollout_percentage": 25,
      "description": "AI-powered compliance recommendations"
    }
  }
}
```

## Integration in Application

The AI-Med-Agent integrates with AppConfig through `src/clients/config_manager.py`:

```python
from src.clients.config_manager import ConfigManager

# Initialize config manager
config_manager = ConfigManager(
    application_id="ai-med-agent-app",
    environment="dev",
    profile_id="agent-config"
)

# Retrieve configuration
config = config_manager.get_configuration()

# Access settings
log_level = config['agent']['log_level']
max_retries = config['agent']['max_retries']

# Check feature flags
if config_manager.is_feature_enabled('auto_remediation'):
    # Execute auto-remediation logic
    pass
```

## Monitoring Deployments

### CloudWatch Alarms

AppConfig deployments are monitored with CloudWatch alarms:

- **DeploymentErrors:** Triggers if deployment error rate exceeds 5%
- **DeploymentDuration:** Triggers if deployment exceeds 5 minutes

View alarms in AWS Console:
```
CloudWatch → Alarms → Filter by "AppConfig-ai-med-agent"
```

### Deployment Status

Check deployment status:

```bash
# Get application ID
APP_ID=$(aws appconfig list-applications \
  --query "Items[?Name=='ai-med-agent'].Id" \
  --output text)

# List recent deployments
aws appconfig list-deployments \
  --application-id $APP_ID \
  --environment-id <env-id>
```

## Deployment Strategies

### Linear Deployment (Default for Dev)

- Deploys configuration gradually: 10% every 30 seconds
- Total rollout time: ~5 minutes
- Best for: Development, low-risk changes

### Canary Deployment (Recommended for Prod)

- Deploys to 20% initially, then 100% after bake time
- 30-second validation between phases
- Best for: Production, high-risk changes

## Rollback Procedures

If a deployment causes issues:

### Automatic Rollback

AppConfig automatically rolls back if:
- CloudWatch alarm triggers during deployment
- Error threshold exceeded (>5% error rate)
- Deployment validation fails

### Manual Rollback

1. **Stop current deployment:**
```bash
aws appconfig stop-deployment \
  --application-id $APP_ID \
  --environment-id $ENV_ID \
  --deployment-number $DEPLOYMENT_NUM
```

2. **Deploy previous version:**
```bash
cd Appconfig
python scripts/deploy.py \
  --application-id $APP_ID \
  --environment dev \
  --config-version <previous-version> \
  --strategy linear
```

## Making Configuration Changes

### Process

1. **Clone Appconfig repository:**
   ```bash
   git clone https://github.com/AI-Empower-Cloud-Hub-LLC/Appconfig.git
   cd Appconfig
   ```

2. **Edit configuration:**
   ```bash
   # Edit dev config
   vim configs/ai-med-agent/dev.json
   
   # Validate JSON
   python -m json.tool configs/ai-med-agent/dev.json
   ```

3. **Commit and push:**
   ```bash
   git add configs/ai-med-agent/dev.json
   git commit -m "feat(ai-med-agent): increase max_retries to 5"
   git push origin main
   ```

4. **Deployment triggers automatically** via GitHub Actions (for changes pushed to main)

   OR manually trigger workflow in GitHub Actions UI

### Testing Changes

Always test configuration changes in dev before promoting:

```
Dev → Test → Staging → Validate → Production
```

## Documentation

For detailed information:

- **Deployment Guide:** [Appconfig/docs/DEPLOYMENT_GUIDE.md](https://github.com/AI-Empower-Cloud-Hub-LLC/Appconfig/blob/main/docs/DEPLOYMENT_GUIDE.md)
- **Troubleshooting:** [Appconfig/docs/TROUBLESHOOTING.md](https://github.com/AI-Empower-Cloud-Hub-LLC/Appconfig/blob/main/docs/TROUBLESHOOTING.md)
- **Best Practices:** [Appconfig/docs/BEST_PRACTICES.md](https://github.com/AI-Empower-Cloud-Hub-LLC/Appconfig/blob/main/docs/BEST_PRACTICES.md)

## Support

For issues or questions:

1. Check [Troubleshooting Guide](https://github.com/AI-Empower-Cloud-Hub-LLC/Appconfig/blob/main/docs/TROUBLESHOOTING.md)
2. Review [GitHub Actions logs](https://github.com/AI-Empower-Cloud-Hub-LLC/Appconfig/actions)
3. Create issue in [Appconfig repository](https://github.com/AI-Empower-Cloud-Hub-LLC/Appconfig/issues)

## Migration Path

If you have local AppConfig infrastructure from this repository:

1. **Export current configurations:**
   ```bash
   aws appconfig get-configuration-profile \
     --application-id <app-id> \
     --configuration-profile-id <profile-id> > backup.json
   ```

2. **Deploy using centralized Appconfig repository** (see deployment section above)

3. **Verify new configuration** works correctly

4. **Decommission old infrastructure:**
   ```bash
   aws cloudformation delete-stack \
     --stack-name old-appconfig-stack
   ```

## Related Resources

- [Appconfig Repository](https://github.com/AI-Empower-Cloud-Hub-LLC/Appconfig) - Centralized AppConfig management
- [AI-Med-Agent Repository](https://github.com/AI-Empower-Cloud-Hub-LLC/AI-Med-Agent) - This repository
- [AWS AppConfig Documentation](https://docs.aws.amazon.com/appconfig/) - Official AWS docs

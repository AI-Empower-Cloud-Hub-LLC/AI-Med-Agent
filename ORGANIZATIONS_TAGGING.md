# AWS Organizations Tagging & Resource Strategy

## Tagging Strategy for AI-Med-Agent

### Standard Tags for All Resources

```json
{
  "Environment": "production|staging|development",
  "Project": "ai-med-agent",
  "Owner": "team@ai-empower-cloud.com",
  "CostCenter": "cc-001",
  "ManagedBy": "terraform|cloudformation|manual",
  "BackupRequired": "true|false",
  "DataClassification": "public|internal|confidential|restricted"
}
```

### Environment-Specific Tags

#### Production
```json
{
  "Environment": "production",
  "Criticality": "high",
  "Compliance": "hipaa|gdpr|sox",
  "DisasterRecovery": "true",
  "BackupFrequency": "hourly"
}
```

#### Staging
```json
{
  "Environment": "staging",
  "Criticality": "medium",
  "Compliance": "gdpr",
  "DisasterRecovery": "false",
  "BackupFrequency": "daily"
}
```

#### Development
```json
{
  "Environment": "development",
  "Criticality": "low",
  "Compliance": "none",
  "DisasterRecovery": "false",
  "BackupFrequency": "weekly"
}
```

### Cost Allocation Tags

```json
{
  "CostCenter": "cc-001",
  "Department": "engineering",
  "Service": "backend|frontend|ai-agents|database",
  "Application": "ai-med-agent",
  "Billable": "true|false"
}
```

### Operational Tags

```json
{
  "SchedulingPolicy": "always-on|business-hours|auto-scale",
  "MaintenanceWindow": "sunday-02:00-04:00",
  "Monitoring": "enabled",
  "Logging": "cloudtrail|cloudwatch|s3",
  "Encryption": "required",
  "AutoShutdown": "true|false"
}
```

## Account Naming Convention

```
Format: {OrgPrefix}-{Environment}-{Purpose}-{Number}

Examples:
- ai-prod-backend-001
- ai-staging-agents-001  
- ai-dev-shared-001
- ai-security-central-001
```

## OU Structure with Tagging

```
Root
├── Production/
│   ├── Tags: Environment=prod, Criticality=high
│   ├── Accounts:
│   │   └── ai-prod-backend-001
│   │       Tags: Environment=prod, Service=backend
│   └── SCPs: ProductionLockdown, MFARequired
│
├── Staging/
│   ├── Tags: Environment=staging, Criticality=medium
│   ├── Accounts:
│   │   ├── ai-staging-full-001
│   │   └── ai-staging-agents-001
│   └── SCPs: StagingLimitations
│
├── Development/
│   ├── Tags: Environment=dev, Criticality=low
│   ├── Accounts:
│   │   ├── ai-dev-main-001
│   │   └── ai-dev-experiments-001
│   └── SCPs: DevelopmentRestrictions
│
└── Security/
    ├── Tags: Environment=security, Criticality=critical
    ├── Accounts:
    │   └── ai-security-central-001
    └── SCPs: SecurityLockdown
```

## Implementation Example (Boto3)

```python
from aws_organizations import AWSOrganizationsManager

manager = AWSOrganizationsManager()

# Tag Production OU
manager.tag_resource(
    resource_id='ou-prod-id',
    tags={
        'Environment': 'production',
        'Criticality': 'high',
        'CostCenter': 'cc-001'
    }
)

# Tag Production Account
manager.tag_resource(
    resource_id='account-prod-backend-id',
    tags={
        'Environment': 'production',
        'Service': 'backend',
        'Owner': 'backend-team@ai-empower.com',
        'ManagedBy': 'terraform'
    }
)

# List tags
tags = manager.list_tags_for_resource('account-prod-backend-id')
print(tags)
```

## Cost Management

### Cost Tags
- **CostCenter**: Allows chargeback to departments
- **Project**: Groups all costs by project
- **Environment**: Separates environment costs

### Cost Anomaly Detection
```bash
aws ce create-anomaly-monitor \
  --anomaly-monitor '{
    "MonitorName": "ai-med-agent-costs",
    "MonitorType": "DIMENSIONAL",
    "MonitorDimension": "SERVICE"
  }' \
  --region us-east-1
```

### Budget Alerts
- Production: $10,000/month threshold
- Staging: $2,000/month threshold
- Development: $1,000/month threshold

## Compliance & Security Tags

### HIPAA Compliance
```json
{
  "HIPAA": "true",
  "Encryption": "required",
  "AuditLogging": "required",
  "DataResidency": "us-east-1"
}
```

### GDPR Compliance
```json
{
  "GDPR": "true",
  "DataProcessor": "AI-Empower-Cloud-Hub-LLC",
  "DataLocation": "us-east-1",
  "RetentionDays": "365"
}
```

## Automated Enforcement

### AWS Config Rules

```python
# Example: Enforce tagging on all resources
aws configrules put-config-rule \
  --config-rule '{
    "ConfigRuleName": "required-tags",
    "Source": {
      "Owner": "AWS",
      "SourceIdentifier": "REQUIRED_TAGS",
      "SourceDetails": [{
        "EventSource": "aws.config",
        "MessageType": "ConfigurationItemChangeNotification"
      }],
      "SourceVersion": "3.0"
    },
    "Scope": {
      "ComplianceResourceTypes": [
        "AWS::EC2::Instance",
        "AWS::RDS::DBInstance",
        "AWS::S3::Bucket"
      ]
    },
    "InputParameters": "{
      \"tag1Key\": \"Environment\",
      \"tag2Key\": \"Owner\",
      \"tag3Key\": \"CostCenter\"
    }"
  }'
```

## Resource Tagging Best Practices

1. **Consistency**: Use same tag keys across all accounts
2. **Automation**: Auto-tag resources on creation
3. **Compliance**: Enforce tags through SCPs/Config rules
4. **Monitoring**: Use CloudWatch to track tag compliance
5. **Documentation**: Maintain tag registry and definitions
6. **Governance**: Regular audits of tag usage

## Tag Compliance Report

```bash
#!/bin/bash

echo "=== Resource Tagging Compliance Report ==="
echo "Generated: $(date)"
echo ""

aws resourcegroupstaggingapi get-resources \
  --tag-filter 'Key=Environment,Values=production' \
  --resource-type-filter 'ec2' \
  --query 'ResourceTagMappingList[*].[ResourceARN,Tags]' \
  --output table

echo ""
echo "Resources missing Environment tag:"
aws resourcegroupstaggingapi get-resources \
  --tag-filter 'Key=!Environment' \
  --query 'ResourceTagMappingList[*].ResourceARN' \
  --output table
```

## See Also

- [AWS Organizations](aws-organizations-setup.yaml)
- [Python AWS Organizations Manager](aws_organizations.py)
- [AWS Config Compliance](README.md#AWS-Config)

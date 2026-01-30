# AWS Organizations Tagging Strategy

## Standard Tags (All Resources)
```json
{
  "Environment": "production|staging|development",
  "Project": "ai-med-agent",
  "Owner": "team@company.com",
  "CostCenter": "cc-001",
  "ManagedBy": "terraform|cloudformation|manual",
  "DataClassification": "public|internal|confidential|restricted"
}
```

## Environment-Specific Tags
### Production
```json
{
  "Environment": "production",
  "Criticality": "high",
  "Compliance": "hipaa|gdpr|sox",
  "DisasterRecovery": "true",
  "BackupFrequency": "hourly"
}
```

### Staging
```json
{
  "Environment": "staging",
  "Criticality": "medium",
  "Compliance": "gdpr",
  "DisasterRecovery": "false",
  "BackupFrequency": "daily"
}
```

### Development
```json
{
  "Environment": "development",
  "Criticality": "low",
  "Compliance": "none",
  "DisasterRecovery": "false",
  "BackupFrequency": "weekly"
}
```

## Cost Allocation Tags
```json
{
  "CostCenter": "cc-001",
  "Department": "engineering",
  "Service": "backend|frontend|ai-agents|database",
  "Application": "ai-med-agent",
  "Billable": "true|false"
}
```

## Enforcement (AWS Config)
Use AWS Config rules to enforce required tags on critical resource types.

## References
- [Organizations Setup Guide](./SETUP.md)

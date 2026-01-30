# AWS Organizations Integration - Complete Setup Guide

## Organization Overview

Your AWS Organization has been successfully set up with full governance features:

- **Organization ID**: o-lz5ryybhfh
- **Feature Set**: ALL (includes SCPs, CloudTrail, Config)
- **Master Account**: 996099991638
- **Region**: us-east-1

## Organizational Structure

```
Root (r-b0ab)
├── Production (ou-b0ab-bj6zyii3)
│   ├── Purpose: Production workloads
│   ├── SCP: ProductionEnvironmentPolicy (p-fnajp74q)
│   └── Criticality: High
│
├── Staging (ou-b0ab-ky6kdwql)
│   ├── Purpose: Pre-production testing
│   ├── SCP: StagingEnvironmentPolicy (p-5baz2zrv)
│   └── Criticality: Medium
│
├── Development (ou-b0ab-7t9356e2)
│   ├── Purpose: Development and testing
│   ├── SCP: DevelopmentEnvironmentPolicy (p-1vhhyht3)
│   └── Criticality: Low
│
└── Security (ou-b0ab-qb48c366)
    ├── Purpose: Security tooling and monitoring
    ├── Criticality: Critical
    └── Note: Receives all CloudTrail and Config logs
```

## Service Control Policies (SCPs)

### 1. ProductionEnvironmentPolicy (p-fnajp74q)
**Protection Level**: Maximum

- Denies root account usage (CreateAccessKey, CreateLoginProfile, MFA)
- Requires MFA for console access
- Prevents dangerous regional deletions (snapshots, DBs, buckets)

### 2. StagingEnvironmentPolicy (p-5baz2zrv)
**Protection Level**: Moderate

- Allows: EC2, RDS, S3, Lambda, DynamoDB, CloudFormation
- Denies: SageMaker, AppStream, WorkSpaces
- Purpose: Cost control + development freedom

### 3. DevelopmentEnvironmentPolicy (p-1vhhyht3)
**Protection Level**: Minimal

- Allows all services
- Denies organization changes
- Allows developers maximum flexibility

## How to Attach SCPs to Accounts/OUs

### Using Python
```python
from aws_organizations import AWSOrganizationsManager

manager = AWSOrganizationsManager()

# Attach SCP to Production OU
manager.attach_policy(
    policy_id='p-fnajp74q',  # ProductionEnvironmentPolicy
    target_id='ou-b0ab-bj6zyii3'  # Production OU
)
```

### Using AWS CLI
```bash
aws organizations attach-policy \
  --policy-id p-fnajp74q \
  --target-id ou-b0ab-bj6zyii3
```

## Creating AWS Accounts in OUs

### Create Account in Production
```bash
aws organizations create-account \
  --account-name prod-backend \
  --email prod-backend@ai-empower-cloud.com
```

### Move Account to OU
```bash
aws organizations move-account \
  --account-id 123456789012 \
  --source-parent-id r-b0ab \
  --destination-parent-id ou-b0ab-bj6zyii3
```

## Logging & Compliance

### CloudTrail Setup
- **Trail Name**: ai-med-organization-trail
- **S3 Bucket**: ai-med-cloudtrail-{account-id}
- **Features**:
  - Multi-region logging
  - Global service events
  - Log file validation
  - Encryption at rest

### AWS Config Setup
- **Recorder**: ai-med-config
- **S3 Bucket**: ai-med-config-{account-id}
- **Frequency**: 6-hour snapshots
- **Compliance Checks**:
  - Required tags enforcement
  - Encrypted volumes validation
  - IAM MFA requirements

## Management Tasks

### View Organization Structure
```bash
# Get OUs
aws organizations list-organizational-units-for-parent --parent-id r-b0ab

# Get accounts in OU
aws organizations list-accounts-for-parent --parent-id ou-b0ab-bj6zyii3
```

### View Policies
```bash
# List all SCPs
aws organizations list-policies --filter SERVICE_CONTROL_POLICY

# Get policy details
aws organizations describe-policy --policy-id p-fnajp74q
```

### View Policy Attachments
```bash
# List targets for policy
aws organizations list-targets-for-policy --policy-id p-fnajp74q
```

## Next Steps

1. **Create AWS Accounts**
   ```bash
   # Account creation is automated in Organizations
   aws organizations create-account \
     --account-name {name} \
     --email {email}
   ```

2. **Move Accounts to OUs**
   ```bash
   # Move account after creation
   aws organizations move-account \
     --account-id {account-id} \
     --source-parent-id {source} \
     --destination-parent-id {dest}
   ```

3. **Attach SCPs to OUs**
   ```bash
   # SCPs provide guardrails for accounts in each OU
   aws organizations attach-policy \
     --policy-id {policy-id} \
     --target-id {ou-id}
   ```

4. **Enable Cost Allocation Tags**
   ```bash
   # Organize billing by tags
   aws ce create-cost-category-definition \
     --name ai-med-cost-categories \
     --rules-version CostCategoryValues.v1
   ```

5. **Set Up AWS Config Aggregator** (optional)
   ```bash
   # Centralized compliance view across accounts
   aws configservice put-configuration-aggregator \
     --configuration-aggregator-name organization \
     --account-aggregation-sources AllAwsRegions=true
   ```

## Python Management Examples

See [aws_organizations.py](aws_organizations.py) for complete Python API:

```python
from aws_organizations import AWSOrganizationsManager

manager = AWSOrganizationsManager()

# Get full org report
report = manager.generate_organization_report()

# Create OU
ou_id = manager.create_ou(parent_id='r-b0ab', ou_name='Shared')

# Attach policy
manager.attach_policy(policy_id='p-xxx', target_id='ou-xxx')

# Tag resources
manager.tag_resource(
    resource_id='ou-xxx',
    tags={'Environment': 'production', 'Owner': 'team@company.com'}
)

# List accounts in OU
accounts = manager.list_accounts_for_ou('ou-xxx')
```

## Tagging Strategy

See [ORGANIZATIONS_TAGGING.md](ORGANIZATIONS_TAGGING.md) for comprehensive tagging guide including:
- Standard tags for all resources
- Environment-specific tags
- Cost allocation tags
- Compliance tags
- Tag compliance enforcement

## Security Best Practices

1. **Root Account Protection**
   - Enable MFA on root account
   - Use SCP to deny root API access
   - Store root credentials securely

2. **SCPs as Guardrails**
   - SCPs are `Deny` statements (blacklist approach)
   - Enable SCPs carefully - test in Dev first
   - Monitor SCP impacts with CloudTrail

3. **Least Privilege**
   - Use separate accounts for environments
   - Apply SCPs per environment
   - Rotate credentials regularly

4. **Audit & Compliance**
   - CloudTrail logs all API calls
   - Config tracks resource compliance
   - Regular audit reviews

## References

- **Configuration Files**:
  - [aws_organizations.py](aws_organizations.py) - Python SDK wrapper
  - [ORGANIZATIONS_TAGGING.md](ORGANIZATIONS_TAGGING.md) - Tagging strategy
  - [aws-organizations-setup.yaml](aws-organizations-setup.yaml) - CloudFormation template (partial, OUs/SCPs created manually)

- **AWS Documentation**:
  - [AWS Organizations User Guide](https://docs.aws.amazon.com/organizations/)
  - [Service Control Policies](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_scps.html)
  - [Organizational Units](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_ous.html)

- **CLI Reference**:
  - [AWS Organizations CLI](https://docs.aws.amazon.com/cli/latest/reference/organizations/)

## Troubleshooting

### OUs not appearing
```bash
# Verify OUs exist
aws organizations list-roots
aws organizations list-organizational-units-for-parent --parent-id r-b0ab
```

### SCP not blocking actions
```bash
# Check if SCP is attached
aws organizations list-targets-for-policy --policy-id p-xxx

# SCPs use Deny logic - must be explicitly attached
```

### Can't move accounts
```bash
# Account might be in wrong state
# Check account status first
aws organizations list-accounts
```

## Contact & Support

- **Organization Owner**: AI-Empower-Cloud-Hub-LLC
- **AWS Account**: 996099991638
- **Primary Region**: us-east-1
- **Support**: Follow AWS Organizations console or use aws-organizations.py

---
**Last Updated**: January 30, 2025
**Status**: ✅ Full AWS Organizations integration complete

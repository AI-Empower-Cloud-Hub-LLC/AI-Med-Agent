# AWS Organizations Setup Guide

This guide describes how to configure AWS Organizations for AI-Med-Agent in a production-ready way.

## Prerequisites
- AWS Organizations enabled with **ALL features**
- IAM access to manage Organizations
- AWS CLI configured

## 1) Create Organizational Units
Create OUs for each environment:
- Production
- Staging
- Development
- Security

## 2) Create Service Control Policies
Create SCPs for environment guardrails:
- Production: strict security + MFA enforcement
- Staging: allow common services, deny high-cost services
- Development: deny org changes only

## 3) Attach SCPs
Attach SCPs to the corresponding OUs.

## 4) Enable Logging & Compliance
- CloudTrail organization trail
- AWS Config recorder + delivery channel
- Centralized S3 buckets for logs

## 5) Tagging Enforcement
Enforce standard tags using AWS Config rules:
- Environment
- Owner
- CostCenter
- Project

## 6) Create Accounts
Create accounts per environment and move into the correct OU.

## CLI Examples
```bash
aws organizations list-roots
aws organizations create-account --account-name prod-backend --email prod-backend@company.com
aws organizations move-account --account-id <ACCOUNT_ID> --source-parent-id <ROOT_ID> --destination-parent-id <PROD_OU_ID>
aws organizations attach-policy --policy-id <SCP_ID> --target-id <OU_ID>
```

## Python SDK Example
```python
from aws_organizations import AWSOrganizationsManager

manager = AWSOrganizationsManager()
manager.attach_policy(policy_id='<SCP_ID>', target_id='<OU_ID>')
```

## References
- [Tagging Strategy](./TAGGING.md)
- [AWS Organizations](https://docs.aws.amazon.com/organizations/)

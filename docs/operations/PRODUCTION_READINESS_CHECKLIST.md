# Production Readiness Checklist

## Governance
- [ ] AWS Organizations enabled with ALL features
- [ ] SCPs attached to Production OU
- [ ] Separate production account created and moved to Production OU

## Security
- [ ] Root account MFA enabled
- [ ] OIDC role for CI/CD configured (preferred)
- [ ] Secrets stored in AWS Secrets Manager
- [ ] No plaintext secrets in repo

## Logging & Compliance
- [ ] CloudTrail organization trail enabled
- [ ] AWS Config recorder enabled
- [ ] Required tags enforced by AWS Config rules

## Cost Controls
- [ ] Budgets configured
- [ ] Cost anomaly detection enabled

## Operational Readiness
- [ ] Runbooks documented
- [ ] Alerting configured (SNS/Slack)
- [ ] On-call process defined

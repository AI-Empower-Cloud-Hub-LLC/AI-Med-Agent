# Security & Secrets Management

## Local Secret Prevention (git-secrets)
- Install git-secrets
- Register AWS patterns
- Scan history before pushing

```bash
git secrets --install -f
git secrets --register-aws
git secrets --scan-history
```

## GitHub Secrets (CI/CD)
Use GitHub Secrets for CI/CD workflows:
- `AWS_ROLE_TO_ASSUME`
- `DEPLOYMENT_TOKEN`
- `SLACK_WEBHOOK_URL` (optional)

## AWS Secrets Manager
Store production secrets in Secrets Manager and retrieve at runtime.

```bash
aws secretsmanager create-secret --name ai-med-agent/db/password --secret-string "<PASSWORD>"
```

## Environment Files
Use `.env.example` as a template. Do not commit real secrets.

## References
- [GitHub Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [AWS Secrets Manager](https://docs.aws.amazon.com/secretsmanager/)
- [git-secrets](https://github.com/awslabs/git-secrets)

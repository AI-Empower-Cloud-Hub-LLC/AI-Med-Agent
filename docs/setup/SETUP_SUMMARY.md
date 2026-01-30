# Setup Summary

## Prerequisites
- AWS CLI configured
- git-secrets installed
- GitHub access for CI/CD (optional)

## Quick Setup
```bash
cp .env.example .env
pip install -r requirements.txt
```

## AWS Access Check
```bash
aws sts get-caller-identity
```

## AppConfig (Optional)
If using AppConfig, retrieve configuration using the AWS CLI and apply to your app settings.

## CI/CD
Configure GitHub Secrets for OIDC or key-based access.

## References
- [Security & Secrets](../security/SECURITY_AND_SECRETS.md)
- [Organizations Setup](../organizations/SETUP.md)

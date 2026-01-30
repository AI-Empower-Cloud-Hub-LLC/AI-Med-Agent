# Deployment Guide

## Overview

This guide covers deploying the AI-Med-Agent framework to various environments including local, development, staging, and production.

## Prerequisites

- Python 3.9 or higher
- AWS CLI configured with appropriate credentials
- Docker (for containerized deployments)
- Access to AWS services: Secrets Manager, AppConfig, CloudWatch, ECR/ECS (for cloud deployment)

## Local Development Deployment

### 1. Setup Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Linux/Mac
# or
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your local settings
nano .env
```

### 3. Run Demo

```bash
# Test the framework
python examples/agents/demo.py
```

### 4. Run Tests

```bash
# Run all tests
export PYTHONPATH=$PYTHONPATH:$(pwd)
python -m unittest discover tests/ -v
```

## Docker Deployment

### 1. Build Docker Image

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY agents/ ./agents/
COPY config/ ./config/
COPY examples/ ./examples/

# Set environment variables
ENV PYTHONPATH=/app
ENV LOG_LEVEL=INFO

# Run application
CMD ["python", "examples/agents/demo.py"]
```

```bash
# Build image
docker build -t ai-med-agent:latest .

# Run container
docker run -it --rm \
  -e AWS_REGION=us-east-1 \
  -e LOG_LEVEL=INFO \
  ai-med-agent:latest
```

### 2. Docker Compose for Multi-Agent Setup

```yaml
# docker-compose.yml
version: '3.8'

services:
  orchestrator:
    build: .
    environment:
      - AWS_REGION=us-east-1
      - AGENT_TYPE=orchestrator
    volumes:
      - ./config:/app/config
      - ./logs:/app/logs

  diagnosis-agent:
    build: .
    environment:
      - AWS_REGION=us-east-1
      - AGENT_TYPE=diagnosis
    depends_on:
      - orchestrator

  triage-agent:
    build: .
    environment:
      - AWS_REGION=us-east-1
      - AGENT_TYPE=triage
    depends_on:
      - orchestrator

  monitoring-agent:
    build: .
    environment:
      - AWS_REGION=us-east-1
      - AGENT_TYPE=monitoring
    depends_on:
      - orchestrator
```

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## AWS Cloud Deployment

### Option 1: AWS Lambda (Serverless)

```bash
# Package for Lambda
pip install -r requirements.txt -t package/
cp -r agents package/
cp -r config package/

# Create deployment package
cd package
zip -r ../lambda-deployment.zip .
cd ..

# Deploy to Lambda
aws lambda create-function \
  --function-name ai-med-agent \
  --runtime python3.9 \
  --role arn:aws:iam::ACCOUNT_ID:role/lambda-execution-role \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://lambda-deployment.zip \
  --timeout 300 \
  --memory-size 512
```

### Option 2: AWS ECS (Container Service)

#### 1. Push to ECR

```bash
# Authenticate Docker to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Create ECR repository
aws ecr create-repository --repository-name ai-med-agent

# Build and tag image
docker build -t ai-med-agent:latest .
docker tag ai-med-agent:latest ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/ai-med-agent:latest

# Push to ECR
docker push ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/ai-med-agent:latest
```

#### 2. Create ECS Task Definition

```json
{
  "family": "ai-med-agent",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "containerDefinitions": [
    {
      "name": "ai-med-agent",
      "image": "ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/ai-med-agent:latest",
      "essential": true,
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/ai-med-agent",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "environment": [
        {"name": "AWS_REGION", "value": "us-east-1"},
        {"name": "LOG_LEVEL", "value": "INFO"}
      ]
    }
  ]
}
```

```bash
# Register task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json

# Create ECS service
aws ecs create-service \
  --cluster ai-med-agent-cluster \
  --service-name ai-med-agent-service \
  --task-definition ai-med-agent \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
```

### Option 3: AWS EC2

```bash
# Launch EC2 instance with user data script
aws ec2 run-instances \
  --image-id ami-xxxxxxxxx \
  --instance-type t3.medium \
  --key-name your-key \
  --security-group-ids sg-xxx \
  --subnet-id subnet-xxx \
  --iam-instance-profile Name=ai-med-agent-role \
  --user-data file://user-data.sh
```

User data script (`user-data.sh`):
```bash
#!/bin/bash
yum update -y
yum install -y python39 git

# Clone repository
cd /home/ec2-user
git clone https://github.com/AI-Empower-Cloud-Hub-LLC/AI-Med-Agent.git
cd AI-Med-Agent

# Install dependencies
pip3 install -r requirements.txt

# Run application
export PYTHONPATH=/home/ec2-user/AI-Med-Agent
nohup python3 examples/agents/demo.py > /var/log/ai-med-agent.log 2>&1 &
```

## Environment-Specific Configurations

### Development

```yaml
# config/agents/agent_config.dev.yaml
agents:
  defaults:
    log_level: DEBUG
    timeout_seconds: 60

aws:
  region: us-east-1
  environment: development
```

### Staging

```yaml
# config/agents/agent_config.staging.yaml
agents:
  defaults:
    log_level: INFO
    timeout_seconds: 45

aws:
  region: us-east-1
  environment: staging
```

### Production

```yaml
# config/agents/agent_config.prod.yaml
agents:
  defaults:
    log_level: WARNING
    timeout_seconds: 30
    max_retries: 5

monitoring:
  enable_metrics: true
  metrics_export_interval: 300

aws:
  region: us-east-1
  environment: production
```

## Secrets Management

### Store Secrets in AWS Secrets Manager

```bash
# Database credentials
aws secretsmanager create-secret \
  --name ai-med-agent/prod/database \
  --secret-string '{"host":"db.example.com","user":"admin","password":"xxxxx"}'

# API keys
aws secretsmanager create-secret \
  --name ai-med-agent/prod/api-keys \
  --secret-string '{"openai":"sk-xxxxx","aws":"xxxxx"}'
```

### Access Secrets in Code

```python
import boto3
import json

def get_secret(secret_name):
    client = boto3.client('secretsmanager', region_name='us-east-1')
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])

# Use in application
db_creds = get_secret('ai-med-agent/prod/database')
```

## Monitoring and Logging

### CloudWatch Logs

```bash
# Create log group
aws logs create-log-group --log-group-name /aws/ai-med-agent

# Create log stream
aws logs create-log-stream \
  --log-group-name /aws/ai-med-agent \
  --log-stream-name agent-stream
```

### CloudWatch Metrics

```python
import boto3

cloudwatch = boto3.client('cloudwatch')

# Put custom metric
cloudwatch.put_metric_data(
    Namespace='AIAgent',
    MetricData=[
        {
            'MetricName': 'ProcessingTime',
            'Value': 125.5,
            'Unit': 'Milliseconds'
        }
    ]
)
```

### CloudWatch Alarms

```bash
# Create alarm for high error rate
aws cloudwatch put-metric-alarm \
  --alarm-name ai-agent-high-errors \
  --alarm-description "Alert when error rate is high" \
  --metric-name ErrorCount \
  --namespace AIAgent \
  --statistic Sum \
  --period 300 \
  --evaluation-periods 1 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold
```

## Health Checks

### Application Health Endpoint

```python
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/health')
def health_check():
    health = orchestrator.health_check()
    all_healthy = all(agent['healthy'] for agent in health.values())
    
    return jsonify({
        'status': 'healthy' if all_healthy else 'unhealthy',
        'agents': health
    }), 200 if all_healthy else 503

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
```

### Load Balancer Health Check

```bash
# Configure ALB target group health check
aws elbv2 modify-target-group \
  --target-group-arn arn:aws:elasticloadbalancing:... \
  --health-check-path /health \
  --health-check-interval-seconds 30 \
  --health-check-timeout-seconds 5 \
  --healthy-threshold-count 2 \
  --unhealthy-threshold-count 2
```

## Auto Scaling

### ECS Auto Scaling

```bash
# Register scalable target
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --resource-id service/cluster-name/service-name \
  --scalable-dimension ecs:service:DesiredCount \
  --min-capacity 1 \
  --max-capacity 10

# Create scaling policy
aws application-autoscaling put-scaling-policy \
  --service-namespace ecs \
  --resource-id service/cluster-name/service-name \
  --scalable-dimension ecs:service:DesiredCount \
  --policy-name cpu-scaling-policy \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration file://scaling-policy.json
```

## Backup and Disaster Recovery

### Backup Memory Store

```python
from agents.memory.manager import MemoryManager

memory = MemoryManager()

# Export memories to S3
import boto3
s3 = boto3.client('s3')

memories = memory.store.memories
s3.put_object(
    Bucket='ai-med-agent-backups',
    Key=f'memories/{datetime.now().isoformat()}.json',
    Body=json.dumps(memories)
)
```

### Restore from Backup

```python
# Download from S3
response = s3.get_object(
    Bucket='ai-med-agent-backups',
    Key='memories/2024-01-30.json'
)

# Restore memories
memories_data = json.loads(response['Body'].read())
# Load into memory store
```

## Troubleshooting

### Common Issues

1. **Module Not Found**
   ```bash
   export PYTHONPATH=$PYTHONPATH:$(pwd)
   ```

2. **AWS Permissions**
   - Ensure IAM role has permissions for Secrets Manager, AppConfig, CloudWatch

3. **Memory Issues**
   - Increase container/instance memory
   - Implement memory cleanup strategies

4. **Network Issues**
   - Check security groups
   - Verify VPC configuration

### Logs Location

- **Local**: `./logs/`
- **Docker**: Container logs via `docker logs`
- **ECS**: CloudWatch Logs `/ecs/ai-med-agent`
- **EC2**: `/var/log/ai-med-agent.log`

## Support

For issues and questions:
- GitHub Issues: https://github.com/AI-Empower-Cloud-Hub-LLC/AI-Med-Agent/issues
- Documentation: [docs/agents/](../docs/agents/)

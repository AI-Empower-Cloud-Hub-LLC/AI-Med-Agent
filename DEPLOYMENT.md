# AICloud-Innovation Deployment Guide

## Overview

This guide covers deploying the AICloud-Innovation enterprise framework to production AWS infrastructure.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     AWS Organizations                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Production  │  │   Staging    │  │ Development  │          │
│  │      OU      │  │      OU      │  │      OU      │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Agent Runtime Environment                      │
│                                                                  │
│  ┌────────────────┐    ┌────────────────┐    ┌───────────────┐ │
│  │   ECS/Fargate  │    │  Lambda (Edge) │    │   EKS (Scale) │ │
│  │   Containers   │    │   Functions    │    │   Kubernetes  │ │
│  └────────────────┘    └────────────────┘    └───────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    Agent Registry                           │ │
│  │  - Medical Diagnosis Agents                                │ │
│  │  - Treatment Planning Agents                               │ │
│  │  - Patient Monitoring Agents                               │ │
│  │  - Clinical Research Agents                                │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Data & Storage Layer                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   DynamoDB   │  │      RDS     │  │   S3 Bucket  │          │
│  │  (Metadata)  │  │  (Workflows) │  │   (Logs)     │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Monitoring & Observability                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  CloudWatch  │  │   X-Ray      │  │   EventBridge│          │
│  │   Metrics    │  │   Tracing    │  │   Events     │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

## Deployment Options

### Option 1: AWS ECS with Fargate (Recommended)

**Best for:** Production workloads with predictable traffic patterns

```bash
# 1. Build Docker image
docker build -t aicloud-innovation:latest .

# 2. Push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
docker tag aicloud-innovation:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/aicloud-innovation:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/aicloud-innovation:latest

# 3. Deploy to ECS
aws ecs create-service \
  --cluster aicloud-innovation \
  --service-name agent-service \
  --task-definition agent-task:1 \
  --desired-count 3 \
  --launch-type FARGATE
```

**ECS Task Definition:**
```json
{
  "family": "agent-task",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "agent-container",
      "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/aicloud-innovation:latest",
      "essential": true,
      "environment": [
        {"name": "AICLOUD_ENV", "value": "production"}
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/aicloud-innovation",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

### Option 2: AWS Lambda (Serverless)

**Best for:** Event-driven, sporadic workloads

```bash
# 1. Package the framework
cd /home/runner/work/AI-Med-Agent/AI-Med-Agent
zip -r aicloud-innovation.zip aicloud_innovation/ requirements.txt

# 2. Create Lambda function
aws lambda create-function \
  --function-name aicloud-agent-processor \
  --runtime python3.12 \
  --handler lambda_handler.handler \
  --role arn:aws:iam::<account-id>:role/lambda-agent-role \
  --zip-file fileb://aicloud-innovation.zip \
  --timeout 900 \
  --memory-size 2048
```

**Lambda Handler Example:**
```python
import json
from aicloud_innovation import AgentRegistry, AgentConfig

registry = AgentRegistry()
# ... initialize agents

def handler(event, context):
    task = json.loads(event['body'])
    agent_id = event['pathParameters']['agent_id']
    
    agent = registry.get_agent(agent_id)
    result = agent.execute(task)
    
    return {
        'statusCode': 200,
        'body': json.dumps(result)
    }
```

### Option 3: AWS EKS (Kubernetes)

**Best for:** Large-scale deployments requiring advanced orchestration

```bash
# 1. Create EKS cluster
eksctl create cluster \
  --name aicloud-innovation \
  --region us-east-1 \
  --nodegroup-name agents \
  --node-type t3.large \
  --nodes 3

# 2. Deploy agents
kubectl apply -f k8s/agent-deployment.yaml

# 3. Expose service
kubectl apply -f k8s/agent-service.yaml
```

## Infrastructure as Code

### CloudFormation Template

```yaml
# cloudformation/aicloud-innovation-stack.yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: AICloud-Innovation Enterprise Framework

Resources:
  # VPC Configuration
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16
      EnableDnsHostnames: true
      Tags:
        - Key: Name
          Value: aicloud-innovation-vpc

  # ECS Cluster
  ECSCluster:
    Type: AWS::ECS::Cluster
    Properties:
      ClusterName: aicloud-innovation
      CapacityProviders:
        - FARGATE
        - FARGATE_SPOT

  # DynamoDB Table for Agent Metadata
  AgentMetadataTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: aicloud-agent-metadata
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: agent_id
          AttributeType: S
      KeySchema:
        - AttributeName: agent_id
          KeyType: HASH

  # RDS for Workflow Data
  WorkflowDatabase:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceIdentifier: aicloud-workflows
      Engine: postgres
      EngineVersion: '15.4'
      DBInstanceClass: db.t3.medium
      AllocatedStorage: 100
      MasterUsername: admin
      MasterUserPassword: !Ref DBPassword

  # S3 Bucket for Logs
  LogsBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub 'aicloud-innovation-logs-${AWS::AccountId}'
      VersioningConfiguration:
        Status: Enabled
      LifecycleConfiguration:
        Rules:
          - Status: Enabled
            ExpirationInDays: 90

  # CloudWatch Log Group
  LogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: /aws/aicloud-innovation
      RetentionInDays: 30

Parameters:
  DBPassword:
    Type: String
    NoEcho: true
    Description: Database password

Outputs:
  ClusterName:
    Value: !Ref ECSCluster
  LogGroupName:
    Value: !Ref LogGroup
```

## Monitoring & Alerting

### CloudWatch Dashboards

```python
# monitoring/cloudwatch_dashboard.py
import boto3
import json

cloudwatch = boto3.client('cloudwatch')

dashboard_body = {
    "widgets": [
        {
            "type": "metric",
            "properties": {
                "metrics": [
                    ["AICloud", "TasksCompleted"],
                    [".", "TasksFailed"],
                    [".", "ActiveAgents"]
                ],
                "period": 300,
                "stat": "Sum",
                "region": "us-east-1",
                "title": "Agent Metrics"
            }
        }
    ]
}

cloudwatch.put_dashboard(
    DashboardName='AICloudInnovation',
    DashboardBody=json.dumps(dashboard_body)
)
```

### SNS Alerts

```bash
# Create SNS topic for alerts
aws sns create-topic --name aicloud-agent-alerts

# Create alarm for failed tasks
aws cloudwatch put-metric-alarm \
  --alarm-name agent-failure-rate \
  --alarm-description "Alert when agent failure rate is high" \
  --metric-name TasksFailed \
  --namespace AICloud \
  --statistic Sum \
  --period 300 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2 \
  --alarm-actions arn:aws:sns:us-east-1:<account-id>:aicloud-agent-alerts
```

## Security Configuration

### IAM Roles

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue",
        "appconfig:GetLatestConfiguration",
        "dynamodb:PutItem",
        "dynamodb:GetItem",
        "s3:PutObject",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "*"
    }
  ]
}
```

## Scaling Configuration

### Auto Scaling

```bash
# Configure ECS auto scaling
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --scalable-dimension ecs:service:DesiredCount \
  --resource-id service/aicloud-innovation/agent-service \
  --min-capacity 2 \
  --max-capacity 10

# Create scaling policy
aws application-autoscaling put-scaling-policy \
  --service-namespace ecs \
  --scalable-dimension ecs:service:DesiredCount \
  --resource-id service/aicloud-innovation/agent-service \
  --policy-name cpu-scaling \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration \
    file://scaling-policy.json
```

## Cost Optimization

1. **Use Fargate Spot** for non-critical workloads (70% cost savings)
2. **Lambda for burst traffic** instead of always-on containers
3. **DynamoDB on-demand** for variable workloads
4. **S3 Intelligent Tiering** for log storage
5. **Reserved Instances** for predictable production workloads

## Deployment Checklist

- [ ] Configure AWS Organizations and OUs
- [ ] Set up VPC and networking
- [ ] Deploy infrastructure with CloudFormation
- [ ] Configure secrets in AWS Secrets Manager
- [ ] Set up AppConfig for feature flags
- [ ] Deploy agent containers/functions
- [ ] Configure CloudWatch monitoring
- [ ] Set up SNS alerts
- [ ] Test agent health checks
- [ ] Validate workflow execution
- [ ] Configure auto-scaling policies
- [ ] Set up CI/CD pipeline
- [ ] Perform load testing
- [ ] Document runbooks

## Troubleshooting

### Common Issues

1. **Agent not starting**: Check IAM permissions and secrets access
2. **High latency**: Review network configuration and resource allocation
3. **Failed workflows**: Check CloudWatch logs for task errors
4. **Memory issues**: Increase container/function memory allocation

### Debug Commands

```bash
# View ECS tasks
aws ecs list-tasks --cluster aicloud-innovation

# Get task logs
aws logs tail /ecs/aicloud-innovation --follow

# Check agent health
curl https://api.aicloud.example.com/health

# View workflow status
aws dynamodb get-item \
  --table-name workflows \
  --key '{"workflow_id": {"S": "abc-123"}}'
```

## Support & Maintenance

- **Backup Strategy**: Daily snapshots of RDS, S3 versioning enabled
- **Disaster Recovery**: Multi-region deployment with Route 53 failover
- **Updates**: Blue/Green deployment with ECS
- **Monitoring**: 24/7 CloudWatch alarms with PagerDuty integration

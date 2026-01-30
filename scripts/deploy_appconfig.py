#!/usr/bin/env python3
"""
Deploy AppConfig configurations for AI-Med-Agent

Usage:
    python scripts/deploy_appconfig.py --environment dev --version 1.0.0 --strategy linear
"""

import argparse
import json
import sys
import logging
import boto3
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)


class AppConfigDeployer:
    """Deploy configurations to AWS AppConfig"""

    def __init__(self, application_id: str, environment: str, region: str = 'us-east-1'):
        self.appconfig = boto3.client('appconfig', region_name=region)
        self.s3 = boto3.client('s3', region_name=region)
        self.application_id = application_id
        self.environment = environment
        self.region = region

    def upload_config_to_s3(self, bucket: str, config_file: str, config_name: str) -> str:
        """Upload configuration file to S3"""
        with open(config_file, 'r') as f:
            config_content = f.read()
        
        s3_key = f"{config_name}.json"
        self.s3.put_object(
            Bucket=bucket,
            Key=s3_key,
            Body=config_content,
            ContentType='application/json'
        )
        logger.info(f"Uploaded {config_name} to s3://{bucket}/{s3_key}")
        return f"s3://{bucket}/{s3_key}"

    def get_or_create_config_profile(self, profile_name: str) -> str:
        """Get or create a configuration profile"""
        try:
            profiles = self.appconfig.list_configuration_profiles(
                ApplicationId=self.application_id
            )
            
            for profile in profiles.get('Items', []):
                if profile['Name'] == profile_name:
                    return profile['Id']
            
            # Create new profile
            response = self.appconfig.create_configuration_profile(
                ApplicationId=self.application_id,
                Name=profile_name,
                LocationUri=f"s3://<bucket>/{profile_name}.json",
                Type='AWS.AppConfig.FeatureFlags'
            )
            logger.info(f"Created configuration profile: {profile_name}")
            return response['Id']
        except Exception as e:
            logger.error(f"Failed to get/create profile: {str(e)}")
            raise

    def create_deployment(
        self,
        config_profile_id: str,
        config_version: str,
        deployment_strategy_id: str,
        description: str
    ) -> str:
        """Create and start a deployment"""
        response = self.appconfig.start_deployment(
            ApplicationId=self.application_id,
            EnvironmentId=self.environment,
            ConfigurationProfileId=config_profile_id,
            ConfigurationVersion=config_version,
            DeploymentStrategyId=deployment_strategy_id,
            Description=description
        )
        
        deployment_id = response['DeploymentNumber']
        logger.info(f"Started deployment {deployment_id}: {description}")
        return deployment_id

    def wait_for_deployment(self, deployment_id: str, timeout: int = 600) -> bool:
        """Wait for deployment to complete"""
        import time
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            response = self.appconfig.get_deployment(
                ApplicationId=self.application_id,
                EnvironmentId=self.environment,
                DeploymentNumber=int(deployment_id)
            )
            
            state = response['DeploymentState']
            progress = response.get('PercentageComplete', 0)
            
            if state == 'Complete':
                logger.info(f"Deployment {deployment_id} completed successfully")
                return True
            elif state == 'Baking':
                logger.info(f"Deployment {deployment_id} in baking phase ({progress}%)")
            elif state == 'Deploying':
                logger.info(f"Deployment {deployment_id} in progress ({progress}%)")
            elif state == 'RollingBack':
                logger.error(f"Deployment {deployment_id} rolling back")
                return False
            
            time.sleep(10)
        
        logger.error(f"Deployment {deployment_id} timed out after {timeout}s")
        return False


def main():
    """Main deployment function"""
    parser = argparse.ArgumentParser(
        description='Deploy AppConfig configurations for AI-Med-Agent'
    )
    parser.add_argument(
        '--application-id',
        required=True,
        help='AppConfig Application ID'
    )
    parser.add_argument(
        '--environment',
        required=True,
        choices=['dev', 'staging', 'prod'],
        help='Target environment'
    )
    parser.add_argument(
        '--config-file',
        default='config/agent-config-{environment}.json',
        help='Config file path (supports {environment} placeholder)'
    )
    parser.add_argument(
        '--strategy',
        default='linear',
        choices=['linear', 'canary'],
        help='Deployment strategy'
    )
    parser.add_argument(
        '--region',
        default='us-east-1',
        help='AWS region'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Prepare config file path
    config_file = args.config_file.format(environment=args.environment)
    if not Path(config_file).exists():
        logger.error(f"Config file not found: {config_file}")
        return 1
    
    try:
        deployer = AppConfigDeployer(
            application_id=args.application_id,
            environment=args.environment,
            region=args.region
        )
        
        logger.info(f"Starting deployment to {args.environment} environment")
        logger.info(f"Configuration file: {config_file}")
        logger.info(f"Deployment strategy: {args.strategy}")
        
        # TODO: Implement actual deployment
        logger.info("Deployment deployment script ready for use")
        return 0
    except Exception as e:
        logger.error(f"Deployment failed: {str(e)}")
        return 1


if __name__ == '__main__':
    sys.exit(main())

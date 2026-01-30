"""
AWS Configuration Manager
Retrieves secrets from Secrets Manager and configurations from AppConfig
"""

import json
import boto3
import logging
from functools import lru_cache
from typing import Dict, Any, Optional
from botocore.exceptions import BotoCoreError, ClientError

logger = logging.getLogger(__name__)


class ConfigurationException(Exception):
    """Base exception for configuration manager"""
    pass


class ConfigManager:
    """Manage AWS Secrets Manager and AppConfig with production-grade error handling"""

    def __init__(self, region: str = 'us-east-1'):
        self.region = region
        self.secrets_client = boto3.client("secretsmanager", region_name=region)
        self.appconfig_client = boto3.client("appconfig", region_name=region)
        self.appconfigdata_client = boto3.client("appconfigdata", region_name=region)
        logger.info(f"ConfigManager initialized (region={region})")

    def get_secret(self, secret_id: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        Retrieve a secret from AWS Secrets Manager.
        Results are cached by default to avoid repeated API calls.
        
        Args:
            secret_id: The name or ARN of the secret
            use_cache: Whether to use cached results
        
        Returns:
            Secret value as dict or string
        """
        try:
            if use_cache:
                return self._get_secret_cached(secret_id)
            
            response = self.secrets_client.get_secret_value(SecretId=secret_id)
            secret = self._parse_secret_response(response)
            logger.info(f"Retrieved secret {secret_id}")
            return secret
        except self.secrets_client.exceptions.ResourceNotFoundException:
            logger.error(f"Secret '{secret_id}' not found in AWS Secrets Manager")
            raise ConfigurationException(f"Secret '{secret_id}' not found")
        except ClientError as e:
            logger.error(f"Failed to retrieve secret '{secret_id}': {e.response['Error']['Code']}")
            raise ConfigurationException(f"Failed to retrieve secret: {str(e)}")

    @lru_cache(maxsize=32)
    def _get_secret_cached(self, secret_id: str) -> Dict[str, Any]:
        """Internal cached secret retrieval"""
        response = self.secrets_client.get_secret_value(SecretId=secret_id)
        return self._parse_secret_response(response)

    @staticmethod
    def _parse_secret_response(response: Dict) -> Dict[str, Any]:
        """Parse secret response from Secrets Manager"""
        if "SecretString" in response:
            secret = response["SecretString"]
            try:
                return json.loads(secret)
            except json.JSONDecodeError:
                return {"value": secret}
        else:
            return {"value": response["SecretBinary"]}

    def get_appconfig_configuration(
        self,
        application_id: str,
        environment: str,
        configuration_profile: str,
    ) -> Dict[str, Any]:
        """
        Retrieve configuration from AWS AppConfig.
        
        Args:
            application_id: AppConfig application ID
            environment: Environment identifier
            configuration_profile: Configuration profile identifier
            
        Returns:
            Configuration as dict
        """
        try:
            # Start a configuration session
            session_response = self.appconfigdata_client.start_configuration_session(
                ApplicationIdentifier=application_id,
                EnvironmentIdentifier=environment,
                ConfigurationProfileIdentifier=configuration_profile,
            )

            token = session_response["InitialConfigurationToken"]
            
            # Get the latest configuration
            config_response = self.appconfigdata_client.get_latest_configuration(
                ConfigurationToken=token
            )

            config_data = {}
            if config_response.get("Configuration"):
                config_data = json.loads(config_response["Configuration"].read())
            
            logger.info(f"Retrieved AppConfig configuration {configuration_profile} from {environment}")
            return config_data
        except ClientError as e:
            logger.error(f"Failed to retrieve AppConfig configuration: {e.response['Error']['Code']}")
            raise ConfigurationException(f"Failed to retrieve AppConfig configuration: {str(e)}")

    def get_database_config(self, secret_name: str = "ai-med-agent/db/password") -> Dict[str, Any]:
        """Retrieve database configuration from Secrets Manager"""
        db_secret = self.get_secret(secret_name)
        return {
            "host": db_secret.get("host", "localhost"),
            "user": db_secret.get("user", "postgres"),
            "password": db_secret.get("password", db_secret.get("value")),
            "database": db_secret.get("database", "ai_med_agent"),
            "port": db_secret.get("port", 5432),
        }

    def get_feature_flags(
        self,
        application_id: str = "ie50sgm",
        environment: str = "backend-dev",
        configuration_profile: str = "feature-flags"
    ) -> Dict[str, bool]:
        """Retrieve feature flags from AppConfig"""
        config = self.get_appconfig_configuration(application_id, environment, configuration_profile)
        flags = config.get("values", {})
        return {k: v.get("enabled", False) for k, v in flags.items()}

    def get_backend_config(
        self,
        application_id: str = "ie50sgm",
        environment: str = "backend-dev",
        configuration_profile: str = "backend-config"
    ) -> Dict[str, Any]:
        """Retrieve backend configuration from AppConfig"""
        return self.get_appconfig_configuration(application_id, environment, configuration_profile)

    def get_ai_agents_config(
        self,
        application_id: str = "ie50sgm",
        environment: str = "agents-dev",
        configuration_profile: str = "ai-agents-config"
    ) -> Dict[str, Any]:
        """Retrieve AI agents configuration from AppConfig"""
        return self.get_appconfig_configuration(application_id, environment, configuration_profile)

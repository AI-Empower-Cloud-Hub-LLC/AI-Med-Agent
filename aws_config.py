"""
AWS Configuration Helper
Retrieves secrets from AWS Secrets Manager and configurations from AppConfig
"""

import json
import boto3
from functools import lru_cache
from typing import Dict, Any

# AWS clients
secrets_client = boto3.client("secretsmanager", region_name="us-east-1")
appconfig_client = boto3.client("appconfig", region_name="us-east-1")
appconfigdata_client = boto3.client("appconfigdata", region_name="us-east-1")


@lru_cache(maxsize=1)
def get_secret(secret_id: str) -> Dict[str, Any]:
    """
    Retrieve a secret from AWS Secrets Manager.
    Results are cached to avoid repeated API calls.
    
    Args:
        secret_id: The name or ARN of the secret
        
    Returns:
        Secret value as dict or string
    """
    try:
        response = secrets_client.get_secret_value(SecretId=secret_id)
        
        if "SecretString" in response:
            secret = response["SecretString"]
            # Try to parse as JSON, otherwise return as-is
            try:
                return json.loads(secret)
            except json.JSONDecodeError:
                return {"value": secret}
        else:
            return {"value": response["SecretBinary"]}
    except secrets_client.exceptions.ResourceNotFoundException:
        raise ValueError(f"Secret '{secret_id}' not found in AWS Secrets Manager")
    except Exception as e:
        raise RuntimeError(f"Failed to retrieve secret '{secret_id}': {str(e)}")


@lru_cache(maxsize=32)
def get_appconfig_configuration(
    application_id: str,
    environment: str,
    configuration_profile: str,
) -> Dict[str, Any]:
    """
    Retrieve configuration from AWS AppConfig.
    Results are cached.
    
    Args:
        application_id: AppConfig application ID
        environment: Environment name (e.g., 'backend-dev')
        configuration_profile: Configuration profile name (e.g., 'feature-flags')
        
    Returns:
        Configuration as dict
    """
    try:
        # Start a configuration session
        session_response = appconfigdata_client.start_configuration_session(
            ApplicationIdentifier=application_id,
            EnvironmentIdentifier=environment,
            ConfigurationProfileIdentifier=configuration_profile,
        )
        
        token = session_response["InitialConfigurationToken"]
        
        # Get the latest configuration
        config_response = appconfigdata_client.get_latest_configuration(
            ConfigurationToken=token
        )
        
        if config_response.get("Configuration"):
            config_data = config_response["Configuration"].read()
            return json.loads(config_data)
        else:
            return {}
    except Exception as e:
        raise RuntimeError(f"Failed to retrieve AppConfig configuration: {str(e)}")


def get_database_config() -> Dict[str, str]:
    """
    Retrieve database configuration from Secrets Manager.
    Assumes the secret is stored as JSON with keys: host, user, password, database
    """
    db_secret = get_secret("ai-med-agent/db/password")
    return {
        "host": db_secret.get("host", "localhost"),
        "user": db_secret.get("user", "postgres"),
        "password": db_secret.get("password", db_secret.get("value")),
        "database": db_secret.get("database", "ai_med_agent"),
        "port": db_secret.get("port", 5432),
    }


def get_feature_flags() -> Dict[str, bool]:
    """
    Retrieve feature flags from AppConfig.
    """
    config = get_appconfig_configuration(
        application_id="ie50sgm",
        environment="backend-dev",
        configuration_profile="feature-flags",
    )
    
    # Extract feature flags from config
    flags = config.get("values", {})
    return {k: v.get("enabled", False) for k, v in flags.items()}


def get_backend_config() -> Dict[str, Any]:
    """
    Retrieve backend configuration from AppConfig.
    """
    return get_appconfig_configuration(
        application_id="ie50sgm",
        environment="backend-dev",
        configuration_profile="backend-config",
    )


def get_ai_agents_config() -> Dict[str, Any]:
    """
    Retrieve AI agents configuration from AppConfig.
    """
    return get_appconfig_configuration(
        application_id="ie50sgm",
        environment="agents-dev",
        configuration_profile="ai-agents-config",
    )


if __name__ == "__main__":
    # Example usage
    print("=== AWS Configuration Helper ===\n")
    
    # Test Secrets Manager
    print("1. Database Configuration:")
    try:
        db_config = get_database_config()
        print(f"   Host: {db_config['host']}")
        print(f"   User: {db_config['user']}")
        print(f"   Database: {db_config['database']}")
        print("   ✓ Secrets Manager accessible\n")
    except Exception as e:
        print(f"   ✗ Error: {e}\n")
    
    # Test AppConfig - Feature Flags
    print("2. Feature Flags:")
    try:
        flags = get_feature_flags()
        for flag_name, enabled in flags.items():
            status = "✓ ENABLED" if enabled else "✗ DISABLED"
            print(f"   {flag_name}: {status}")
        print("   ✓ AppConfig accessible\n")
    except Exception as e:
        print(f"   ✗ Error: {e}\n")
    
    # Test AppConfig - Backend Configuration
    print("3. Backend Configuration:")
    try:
        backend_config = get_backend_config()
        print(f"   Database Pool Size: {backend_config.get('database', {}).get('connectionPoolSize')}")
        print(f"   Cache TTL: {backend_config.get('cache', {}).get('ttl')} seconds")
        print(f"   Log Level: {backend_config.get('logging', {}).get('level')}")
        print("   ✓ Backend config retrieved\n")
    except Exception as e:
        print(f"   ✗ Error: {e}\n")
    
    # Test AppConfig - AI Agents Configuration
    print("4. AI Agents Configuration:")
    try:
        agents_config = get_ai_agents_config()
        print(f"   Default Model: {agents_config.get('models', {}).get('defaultModel')}")
        print(f"   Max Tokens: {agents_config.get('models', {}).get('maxTokens')}")
        print(f"   Temperature: {agents_config.get('models', {}).get('temperature')}")
        print("   ✓ AI Agents config retrieved\n")
    except Exception as e:
        print(f"   ✗ Error: {e}\n")
    
    print("=== All Tests Complete ===")

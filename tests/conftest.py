"""Test configuration and fixtures"""

import pytest
import logging
from unittest.mock import MagicMock, patch
from src.agent.orchestrator import AgentOrchestrator
from src.core.state import StateManager, AgentStatus
from src.clients.organizations_manager import AWSOrganizationsManager
from src.clients.config_manager import ConfigManager


@pytest.fixture
def mock_org_manager():
    """Mock AWS Organizations Manager"""
    manager = MagicMock(spec=AWSOrganizationsManager)
    manager.get_organization_info.return_value = {
        'Id': '<ORG_ID>',
        'MasterAccountId': '<ACCOUNT_ID>',
        'FeatureSet': 'ALL',
        'AvailablePolicyTypes': ['SERVICE_CONTROL_POLICY']
    }
    manager.list_accounts.return_value = [
        {'Id': '<ACCOUNT_ID>', 'Name': 'Master', 'Status': 'ACTIVE'},
        {'Id': 'acc-123', 'Name': 'Production', 'Status': 'ACTIVE'},
    ]
    manager.list_ous.return_value = [
        {'Id': 'ou-prod', 'Name': 'Production'},
        {'Id': 'ou-dev', 'Name': 'Development'},
    ]
    return manager


@pytest.fixture
def mock_config_manager():
    """Mock Config Manager"""
    manager = MagicMock(spec=ConfigManager)
    manager.get_feature_flags.return_value = {'auto_governance': True}
    return manager


@pytest.fixture
def agent_orchestrator(mock_org_manager, mock_config_manager):
    """Create agent orchestrator with mocked dependencies"""
    return AgentOrchestrator(
        agent_id="test-agent",
        org_manager=mock_org_manager,
        config_manager=mock_config_manager,
        require_approval=False
    )


@pytest.fixture
def state_manager():
    """Create state manager for testing"""
    return StateManager("test-agent")


# Logging setup for tests
@pytest.fixture(autouse=True)
def setup_logging():
    """Configure logging for tests"""
    logging.basicConfig(level=logging.DEBUG)
    yield

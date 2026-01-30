"""Unit tests for agent orchestrator"""

import pytest
from unittest.mock import MagicMock
from src.agent.orchestrator import AgentOrchestrator
from src.core.state import AgentStatus, DecisionOutcome, AgentAction


class TestAgentOrchestrator:
    """Test cases for AgentOrchestrator"""

    def test_initialization(self, agent_orchestrator):
        """Test orchestrator initialization"""
        assert agent_orchestrator.agent_id == "test-agent"
        assert agent_orchestrator.state.status == AgentStatus.IDLE
        assert len(agent_orchestrator.action_handlers) > 0

    def test_action_handler_registration(self, agent_orchestrator):
        """Test custom action handler registration"""
        custom_handler = MagicMock()
        agent_orchestrator.register_action_handler("custom_action", custom_handler)
        assert "custom_action" in agent_orchestrator.action_handlers

    def test_evaluate_action_proceed(self, agent_orchestrator):
        """Test action evaluation returning PROCEED"""
        action = agent_orchestrator.state.create_action(
            action_type="create_ou",
            description="Create test OU",
            parameters={"parent_id": "root", "ou_name": "test"}
        )
        outcome = agent_orchestrator.evaluate_action(action)
        assert outcome == DecisionOutcome.PROCEED

    def test_evaluate_action_risky_operation(self, agent_orchestrator):
        """Test that risky operations require approval"""
        agent_orchestrator.require_approval = True
        action = agent_orchestrator.state.create_action(
            action_type="delete_ou",
            description="Delete OU",
            parameters={"ou_id": "ou-123"}
        )
        outcome = agent_orchestrator.evaluate_action(action)
        assert outcome == DecisionOutcome.REQUIRE_APPROVAL

    def test_execute_action_success(self, agent_orchestrator):
        """Test successful action execution"""
        agent_orchestrator.org_manager.create_ou.return_value = "ou-new-123"
        
        action = agent_orchestrator.state.create_action(
            action_type="create_ou",
            description="Create test OU",
            parameters={"parent_id": "root", "ou_name": "test"}
        )
        
        result = agent_orchestrator.execute_action(action, skip_approval_check=True)
        assert result == "ou-new-123"
        assert len(agent_orchestrator.state.action_history) == 1

    def test_execute_action_missing_handler(self, agent_orchestrator):
        """Test action execution with missing handler"""
        action = agent_orchestrator.state.create_action(
            action_type="unknown_action",
            description="Unknown action",
            parameters={}
        )
        
        with pytest.raises(ValueError, match="No handler for action type"):
            agent_orchestrator.execute_action(action, skip_approval_check=True)

    def test_execute_action_with_exception(self, agent_orchestrator):
        """Test action execution with exception"""
        agent_orchestrator.org_manager.create_ou.side_effect = Exception("API Error")
        
        action = agent_orchestrator.state.create_action(
            action_type="create_ou",
            description="Create test OU",
            parameters={"parent_id": "root", "ou_name": "test"}
        )
        
        with pytest.raises(Exception):
            agent_orchestrator.execute_action(action, skip_approval_check=True)
        
        assert agent_orchestrator.state.status == AgentStatus.FAILED

    def test_get_state_summary(self, agent_orchestrator):
        """Test state summary retrieval"""
        summary = agent_orchestrator.get_state_summary()
        assert summary['agent_id'] == "test-agent"
        assert summary['status'] == "idle"
        assert 'metrics' in summary

    def test_run_autonomous_governance_check(self, agent_orchestrator):
        """Test autonomous governance check"""
        agent_orchestrator.org_manager.generate_organization_report.return_value = {
            'accounts': [{'Id': 'acc-123', 'Name': 'Production'}],
            'ous': [{'Id': 'ou-prod', 'Name': 'Production'}],
            'policies': [],
            'cloudtrail': {'trail_count': 1},
            'config': {'rule_count': 5}
        }
        
        result = agent_orchestrator.run_autonomous_governance_check()
        assert result['status'] == 'completed'
        assert 'report' in result
        assert 'analysis' in result

    def test_analyze_governance_report_no_issues(self, agent_orchestrator):
        """Test governance report analysis with no issues"""
        report = {
            'accounts': [{'Id': 'acc-123', 'Name': 'Production'}],
            'ous': [{'Id': 'ou-prod', 'Name': 'Production'}],
            'policies': [],
            'cloudtrail': {'trail_count': 1},
            'config': {'rule_count': 5}
        }
        
        analysis = agent_orchestrator._analyze_governance_report(report)
        assert analysis['findings'] == []
        assert analysis['total_accounts'] == 1
        assert analysis['total_ous'] == 1

    def test_analyze_governance_report_with_issues(self, agent_orchestrator):
        """Test governance report analysis with issues"""
        report = {
            'accounts': [{'Name': 'Production'}],  # Missing Id
            'ous': [],
            'policies': [],
            'cloudtrail': {'error': 'CloudTrail not enabled'},
            'config': {'error': 'Config not enabled'}
        }
        
        analysis = agent_orchestrator._analyze_governance_report(report)
        assert len(analysis['findings']) >= 2


class TestActionCreation:
    """Test action creation and management"""

    def test_create_action(self, state_manager):
        """Test action creation"""
        action = state_manager.create_action(
            action_type="create_ou",
            description="Create OU",
            parameters={"parent_id": "root"},
            requires_approval=False,
            priority=1
        )
        assert action.action_type == "create_ou"
        assert action.priority == 1
        assert action.status == "pending"

    def test_queue_and_complete_action(self, state_manager):
        """Test queuing and completing actions"""
        action = state_manager.create_action(
            action_type="create_ou",
            description="Create OU",
            parameters={"parent_id": "root"}
        )
        
        state_manager.queue_action(action)
        state_manager.complete_action(result="ou-123")
        
        assert len(state_manager.action_history) == 1
        assert state_manager.action_history[0].status == "completed"
        assert state_manager.metrics['actions_executed'] == 1

    def test_action_failure(self, state_manager):
        """Test action failure handling"""
        action = state_manager.create_action(
            action_type="create_ou",
            description="Create OU",
            parameters={"parent_id": "root"}
        )
        
        state_manager.queue_action(action)
        state_manager.fail_action("API Error")
        
        assert len(state_manager.action_history) == 1
        assert state_manager.action_history[0].status == "failed"
        assert state_manager.metrics['actions_failed'] == 1
        assert len(state_manager.errors) == 1

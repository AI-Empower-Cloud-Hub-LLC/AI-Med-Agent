"""
Autonomous AI-Med-Agent Orchestrator
Orchestrates autonomous AWS Organizations management with state tracking and decision-making
"""

import logging
import time
from typing import Dict, Any, Optional, List, Callable
from src.clients.organizations_manager import AWSOrganizationsManager, OrganizationsException
from src.clients.config_manager import ConfigManager
from src.core.state import StateManager, AgentStatus, DecisionOutcome, AgentAction

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """
    Orchestrates autonomous AWS Organizations management
    Handles decision-making, action execution, state management, and error recovery
    """

    def __init__(
        self,
        agent_id: str = "ai-med-agent-primary",
        org_manager: Optional[AWSOrganizationsManager] = None,
        config_manager: Optional[ConfigManager] = None,
        require_approval: bool = False
    ):
        self.agent_id = agent_id
        self.org_manager = org_manager or AWSOrganizationsManager()
        self.config_manager = config_manager or ConfigManager()
        self.state = StateManager(agent_id)
        self.require_approval = require_approval
        self.action_handlers: Dict[str, Callable] = {}
        self._register_default_handlers()
        logger.info(f"AgentOrchestrator initialized: {agent_id} (require_approval={require_approval})")

    def _register_default_handlers(self) -> None:
        """Register default action handlers"""
        self.action_handlers = {
            'create_ou': self._handle_create_ou,
            'delete_ou': self._handle_delete_ou,
            'create_account': self._handle_create_account,
            'move_account': self._handle_move_account,
            'attach_policy': self._handle_attach_policy,
            'detach_policy': self._handle_detach_policy,
            'tag_resource': self._handle_tag_resource,
            'generate_report': self._handle_generate_report,
        }

    def register_action_handler(self, action_type: str, handler: Callable) -> None:
        """Register a custom action handler"""
        self.action_handlers[action_type] = handler
        logger.info(f"Registered handler for action type: {action_type}")

    # =========================================================================
    # Decision Making
    # =========================================================================

    def evaluate_action(self, action: AgentAction) -> DecisionOutcome:
        """
        Evaluate whether an action should proceed, require approval, or be skipped
        Returns decision outcome based on action properties and current state
        """
        # Check if action requires approval
        if action.requires_approval and self.require_approval:
            self.state.log_decision(
                'action_approval',
                DecisionOutcome.REQUIRE_APPROVAL,
                f"Action {action.action_type} requires approval",
                {'action': action.action_type, 'description': action.description}
            )
            return DecisionOutcome.REQUIRE_APPROVAL

        # Check for risky operations
        if self._is_risky_operation(action):
            self.state.log_decision(
                'risk_assessment',
                DecisionOutcome.REQUIRE_APPROVAL,
                f"Risky operation detected: {action.action_type}",
                {'risk_level': 'high', 'action': action.action_type}
            )
            return DecisionOutcome.REQUIRE_APPROVAL

        # Check agent state
        if self.state.status == AgentStatus.FAILED:
            self.state.log_decision(
                'state_check',
                DecisionOutcome.SKIP,
                "Agent in FAILED state, skipping action",
                {}
            )
            return DecisionOutcome.SKIP

        # All checks passed
        self.state.log_decision(
            'pre_execution',
            DecisionOutcome.PROCEED,
            f"Ready to execute {action.action_type}",
            {'action': action.action_type}
        )
        return DecisionOutcome.PROCEED

    def _is_risky_operation(self, action: AgentAction) -> bool:
        """Determine if an operation is risky"""
        risky_actions = ['delete_ou', 'detach_policy']
        return action.action_type in risky_actions

    # =========================================================================
    # Action Handlers
    # =========================================================================

    def execute_action(self, action: AgentAction, skip_approval_check: bool = False) -> Any:
        """
        Execute an action with full error handling and state management
        
        Args:
            action: Action to execute
            skip_approval_check: Skip approval requirement (for testing)
        
        Returns:
            Action result
        """
        self.state.set_status(AgentStatus.EVALUATING)
        self.state.queue_action(action)

        # Evaluate action
        if not skip_approval_check:
            decision = self.evaluate_action(action)
            if decision == DecisionOutcome.REQUIRE_APPROVAL:
                raise PermissionError(f"Action {action.action_type} requires approval")
            elif decision != DecisionOutcome.PROCEED:
                logger.info(f"Action {action.action_type} skipped due to {decision.value}")
                return None

        # Execute action
        self.state.set_status(AgentStatus.EXECUTING)
        handler = self.action_handlers.get(action.action_type)
        if not handler:
            raise ValueError(f"No handler for action type: {action.action_type}")

        try:
            result = handler(action)
            self.state.complete_action(result)
            self.state.set_status(AgentStatus.COMPLETED)
            return result
        except Exception as e:
            logger.error(f"Action failed: {action.action_type} - {str(e)}")
            self.state.fail_action(str(e))
            self.state.set_status(AgentStatus.FAILED)
            raise

    def _handle_create_ou(self, action: AgentAction) -> str:
        """Handle OU creation"""
        params = action.parameters
        parent_id = params.get('parent_id')
        ou_name = params.get('ou_name')
        tags = params.get('tags', {})
        
        if not parent_id or not ou_name:
            raise ValueError("parent_id and ou_name are required")
        
        try:
            ou_id = self.org_manager.create_ou(parent_id, ou_name, tags)
            logger.info(f"Successfully created OU: {ou_name} ({ou_id})")
            return ou_id
        except OrganizationsException as e:
            logger.error(f"Failed to create OU: {str(e)}")
            raise

    def _handle_delete_ou(self, action: AgentAction) -> bool:
        """Handle OU deletion"""
        params = action.parameters
        ou_id = params.get('ou_id')
        
        if not ou_id:
            raise ValueError("ou_id is required")
        
        try:
            result = self.org_manager.delete_ou(ou_id)
            logger.info(f"Successfully deleted OU: {ou_id}")
            return result
        except OrganizationsException as e:
            logger.error(f"Failed to delete OU: {str(e)}")
            raise

    def _handle_create_account(self, action: AgentAction) -> str:
        """Handle account creation"""
        params = action.parameters
        email = params.get('email')
        account_name = params.get('account_name')
        
        if not email or not account_name:
            raise ValueError("email and account_name are required")
        
        try:
            request_id = self.org_manager.create_account(email, account_name)
            logger.info(f"Account creation initiated: {account_name} ({email})")
            return request_id
        except OrganizationsException as e:
            logger.error(f"Failed to create account: {str(e)}")
            raise

    def _handle_move_account(self, action: AgentAction) -> bool:
        """Handle account movement between OUs"""
        params = action.parameters
        account_id = params.get('account_id')
        source_parent_id = params.get('source_parent_id')
        destination_parent_id = params.get('destination_parent_id')
        
        if not all([account_id, source_parent_id, destination_parent_id]):
            raise ValueError("account_id, source_parent_id, and destination_parent_id are required")
        
        try:
            result = self.org_manager.move_account(account_id, source_parent_id, destination_parent_id)
            logger.info(f"Account {account_id} moved to {destination_parent_id}")
            return result
        except OrganizationsException as e:
            logger.error(f"Failed to move account: {str(e)}")
            raise

    def _handle_attach_policy(self, action: AgentAction) -> bool:
        """Handle policy attachment"""
        params = action.parameters
        policy_id = params.get('policy_id')
        target_id = params.get('target_id')
        
        if not policy_id or not target_id:
            raise ValueError("policy_id and target_id are required")
        
        try:
            result = self.org_manager.attach_policy(policy_id, target_id)
            logger.info(f"Policy {policy_id} attached to {target_id}")
            return result
        except OrganizationsException as e:
            logger.error(f"Failed to attach policy: {str(e)}")
            raise

    def _handle_detach_policy(self, action: AgentAction) -> bool:
        """Handle policy detachment"""
        params = action.parameters
        policy_id = params.get('policy_id')
        target_id = params.get('target_id')
        
        if not policy_id or not target_id:
            raise ValueError("policy_id and target_id are required")
        
        try:
            result = self.org_manager.detach_policy(policy_id, target_id)
            logger.info(f"Policy {policy_id} detached from {target_id}")
            return result
        except OrganizationsException as e:
            logger.error(f"Failed to detach policy: {str(e)}")
            raise

    def _handle_tag_resource(self, action: AgentAction) -> bool:
        """Handle resource tagging"""
        params = action.parameters
        resource_id = params.get('resource_id')
        tags = params.get('tags', {})
        
        if not resource_id or not tags:
            raise ValueError("resource_id and tags are required")
        
        try:
            result = self.org_manager.tag_resource(resource_id, tags)
            logger.info(f"Resource {resource_id} tagged with {len(tags)} tags")
            return result
        except OrganizationsException as e:
            logger.error(f"Failed to tag resource: {str(e)}")
            raise

    def _handle_generate_report(self, action: AgentAction) -> Dict[str, Any]:
        """Handle organization report generation"""
        try:
            report = self.org_manager.generate_organization_report()
            logger.info("Organization report generated successfully")
            return report
        except OrganizationsException as e:
            logger.error(f"Failed to generate report: {str(e)}")
            raise

    # =========================================================================
    # Autonomous Operations
    # =========================================================================

    def run_autonomous_governance_check(self) -> Dict[str, Any]:
        """
        Run autonomous governance check:
        1. Generate organization report
        2. Analyze compliance
        3. Identify and execute remediation actions
        """
        logger.info("Starting autonomous governance check")
        self.state.set_status(AgentStatus.RUNNING)
        
        try:
            # Generate report
            report = self.org_manager.generate_organization_report()
            
            # Analyze and log
            analysis = self._analyze_governance_report(report)
            self.state.log_decision(
                'governance_analysis',
                DecisionOutcome.PROCEED,
                'Governance check completed',
                analysis
            )
            
            logger.info(f"Governance check completed: {len(analysis.get('findings', []))} findings")
            return {
                'status': 'completed',
                'report': report,
                'analysis': analysis,
                'state': self.state.get_state_summary()
            }
        except Exception as e:
            logger.error(f"Governance check failed: {str(e)}")
            self.state.set_status(AgentStatus.FAILED)
            raise

    def _analyze_governance_report(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze governance report for issues"""
        findings = []
        
        # Check for untagged resources
        for account in report.get('accounts', []):
            account_id = account.get('Id')
            if not account_id:
                findings.append({
                    'severity': 'medium',
                    'issue': 'Account missing ID',
                    'account': account
                })
        
        # Check CloudTrail status
        cloudtrail = report.get('cloudtrail', {})
        if 'error' in cloudtrail:
            findings.append({
                'severity': 'high',
                'issue': 'CloudTrail not configured',
                'error': cloudtrail['error']
            })
        
        # Check Config compliance
        config = report.get('config', {})
        if 'error' in config:
            findings.append({
                'severity': 'medium',
                'issue': 'AWS Config not enabled',
                'error': config['error']
            })
        
        return {
            'findings': findings,
            'total_accounts': len(report.get('accounts', [])),
            'total_ous': len(report.get('ous', [])),
            'total_policies': len(report.get('policies', [])),
        }

    def get_state_summary(self) -> Dict[str, Any]:
        """Get current agent state"""
        return self.state.get_state_summary()

    def export_operation_history(self) -> Dict[str, Any]:
        """Export complete operation history"""
        return self.state.export_history()

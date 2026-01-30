"""
AWS Organizations Management Client
Manage accounts, OUs, SCPs, and organizational features with production-grade error handling
"""

import boto3
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from botocore.exceptions import BotoCoreError, ClientError

logger = logging.getLogger(__name__)


class OrganizationsException(Exception):
    """Base exception for Organizations manager"""
    pass


class AWSOrganizationsManager:
    """Manage AWS Organizations with comprehensive error handling and retries"""

    def __init__(self, region: str = 'us-east-1', max_retries: int = 3):
        self.org_client = boto3.client('organizations', region_name=region)
        self.sts_client = boto3.client('sts', region_name=region)
        self.cloudtrail_client = boto3.client('cloudtrail', region_name=region)
        self.config_client = boto3.client('config', region_name=region)
        self.max_retries = max_retries
        logger.info(f"AWSOrganizationsManager initialized (region={region}, max_retries={max_retries})")

    def _retry_on_failure(self, func, *args, **kwargs):
        """Retry wrapper for transient failures"""
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except (BotoCoreError, ClientError) as e:
                if attempt == self.max_retries - 1:
                    raise
                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}. Retrying...")

    # =========================================================================
    # Organization Information
    # =========================================================================

    def get_organization_info(self) -> Dict[str, Any]:
        """Get organization details"""
        try:
            response = self.org_client.describe_organization()
            logger.info("Successfully retrieved organization info")
            return response['Organization']
        except ClientError as e:
            logger.error(f"Failed to get organization info: {e.response['Error']['Code']}")
            raise OrganizationsException(f"Failed to get organization info: {str(e)}")

    def get_root_id(self) -> str:
        """Get the root organizational unit ID"""
        try:
            roots = self.org_client.list_roots()
            root_id = roots['Roots'][0]['Id']
            logger.info(f"Retrieved root ID: {root_id}")
            return root_id
        except (KeyError, IndexError) as e:
            logger.error("No roots found in organization")
            raise OrganizationsException("No roots found in organization")
        except ClientError as e:
            logger.error(f"Failed to get root ID: {e.response['Error']['Code']}")
            raise OrganizationsException(f"Failed to get root ID: {str(e)}")

    # =========================================================================
    # Organizational Units (OUs)
    # =========================================================================

    def list_ous(self, parent_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List organizational units, optionally filtered by parent"""
        try:
            if parent_id is None:
                parent_id = self.get_root_id()
            
            ous = []
            paginator = self.org_client.get_paginator('list_organizational_units_for_parent')
            
            for page in paginator.paginate(ParentId=parent_id):
                ous.extend(page['OrganizationalUnits'])
            
            logger.info(f"Retrieved {len(ous)} OUs for parent {parent_id}")
            return ous
        except ClientError as e:
            logger.error(f"Failed to list OUs: {e.response['Error']['Code']}")
            raise OrganizationsException(f"Failed to list OUs: {str(e)}")

    def create_ou(self, parent_id: str, ou_name: str, tags: Optional[Dict[str, str]] = None) -> str:
        """Create a new organizational unit"""
        try:
            response = self.org_client.create_organizational_unit(
                ParentId=parent_id,
                Name=ou_name
            )
            ou_id = response['OrganizationalUnit']['Id']
            
            # Apply tags if provided
            if tags:
                self.tag_resource(ou_id, tags)
            
            logger.info(f"Created OU '{ou_name}' with ID {ou_id}")
            return ou_id
        except self.org_client.exceptions.ParentNotFoundException:
            logger.error(f"Parent OU {parent_id} not found")
            raise OrganizationsException(f"Parent OU {parent_id} not found")
        except ClientError as e:
            logger.error(f"Failed to create OU: {e.response['Error']['Code']}")
            raise OrganizationsException(f"Failed to create OU: {str(e)}")

    def delete_ou(self, ou_id: str) -> bool:
        """Delete an organizational unit"""
        try:
            self.org_client.delete_organizational_unit(OrganizationalUnitId=ou_id)
            logger.info(f"Deleted OU {ou_id}")
            return True
        except ClientError as e:
            logger.error(f"Failed to delete OU: {e.response['Error']['Code']}")
            raise OrganizationsException(f"Failed to delete OU: {str(e)}")

    # =========================================================================
    # Accounts Management
    # =========================================================================

    def list_accounts(self) -> List[Dict[str, Any]]:
        """List all accounts in organization"""
        try:
            accounts = []
            paginator = self.org_client.get_paginator('list_accounts')
            
            for page in paginator.paginate():
                accounts.extend(page['Accounts'])
            
            logger.info(f"Retrieved {len(accounts)} accounts")
            return accounts
        except ClientError as e:
            logger.error(f"Failed to list accounts: {e.response['Error']['Code']}")
            raise OrganizationsException(f"Failed to list accounts: {str(e)}")

    def create_account(self, email: str, account_name: str, tags: Optional[Dict[str, str]] = None) -> str:
        """Create a new AWS account"""
        try:
            response = self.org_client.create_account(
                Email=email,
                AccountName=account_name
            )
            request_id = response['CreateAccountStatus']['Id']
            logger.info(f"Initiated account creation for '{account_name}' ({email}), request_id={request_id}")
            return request_id
        except ClientError as e:
            logger.error(f"Failed to create account: {e.response['Error']['Code']}")
            raise OrganizationsException(f"Failed to create account: {str(e)}")

    def create_account_status(self, create_account_request_id: str) -> Dict[str, Any]:
        """Check the status of account creation"""
        try:
            response = self.org_client.describe_create_account_status(
                CreateAccountRequestId=create_account_request_id
            )
            status_info = response['CreateAccountStatus']
            logger.debug(f"Account creation status: {status_info['State']}")
            return status_info
        except ClientError as e:
            logger.error(f"Failed to get account creation status: {e.response['Error']['Code']}")
            raise OrganizationsException(f"Failed to get account creation status: {str(e)}")

    def move_account(self, account_id: str, source_parent_id: str, destination_parent_id: str) -> bool:
        """Move account between OUs"""
        try:
            self.org_client.move_account(
                AccountId=account_id,
                SourceParentId=source_parent_id,
                DestinationParentId=destination_parent_id
            )
            logger.info(f"Moved account {account_id} from {source_parent_id} to {destination_parent_id}")
            return True
        except ClientError as e:
            logger.error(f"Failed to move account: {e.response['Error']['Code']}")
            raise OrganizationsException(f"Failed to move account: {str(e)}")

    def list_accounts_for_ou(self, ou_id: str) -> List[Dict[str, Any]]:
        """List accounts in a specific OU"""
        try:
            accounts = []
            paginator = self.org_client.get_paginator('list_accounts_for_parent')
            
            for page in paginator.paginate(ParentId=ou_id):
                accounts.extend(page['Accounts'])
            
            logger.info(f"Retrieved {len(accounts)} accounts for OU {ou_id}")
            return accounts
        except ClientError as e:
            logger.error(f"Failed to list accounts for OU: {e.response['Error']['Code']}")
            raise OrganizationsException(f"Failed to list accounts for OU: {str(e)}")

    # =========================================================================
    # Service Control Policies (SCPs)
    # =========================================================================

    def list_policies(self, policy_type: str = 'SERVICE_CONTROL_POLICY') -> List[Dict[str, Any]]:
        """List all policies of a specific type"""
        try:
            policies = []
            paginator = self.org_client.get_paginator('list_policies')
            
            for page in paginator.paginate(Filter=policy_type):
                policies.extend(page['Policies'])
            
            logger.info(f"Retrieved {len(policies)} {policy_type} policies")
            return policies
        except ClientError as e:
            logger.error(f"Failed to list policies: {e.response['Error']['Code']}")
            raise OrganizationsException(f"Failed to list policies: {str(e)}")

    def get_policy(self, policy_id: str) -> Dict[str, Any]:
        """Get policy details"""
        try:
            response = self.org_client.describe_policy(PolicyId=policy_id)
            logger.debug(f"Retrieved policy {policy_id}")
            return response['Policy']
        except ClientError as e:
            logger.error(f"Failed to get policy: {e.response['Error']['Code']}")
            raise OrganizationsException(f"Failed to get policy: {str(e)}")

    def attach_policy(self, policy_id: str, target_id: str) -> bool:
        """Attach policy to target (OU or account)"""
        try:
            self.org_client.attach_policy(PolicyId=policy_id, TargetId=target_id)
            logger.info(f"Attached policy {policy_id} to {target_id}")
            return True
        except ClientError as e:
            logger.error(f"Failed to attach policy: {e.response['Error']['Code']}")
            raise OrganizationsException(f"Failed to attach policy: {str(e)}")

    def detach_policy(self, policy_id: str, target_id: str) -> bool:
        """Detach policy from target"""
        try:
            self.org_client.detach_policy(PolicyId=policy_id, TargetId=target_id)
            logger.info(f"Detached policy {policy_id} from {target_id}")
            return True
        except ClientError as e:
            logger.error(f"Failed to detach policy: {e.response['Error']['Code']}")
            raise OrganizationsException(f"Failed to detach policy: {str(e)}")

    def list_targets_for_policy(self, policy_id: str) -> List[Dict[str, Any]]:
        """List all targets (OUs/accounts) a policy is attached to"""
        try:
            targets = []
            paginator = self.org_client.get_paginator('list_targets_for_policy')
            
            for page in paginator.paginate(PolicyId=policy_id):
                targets.extend(page['Targets'])
            
            logger.info(f"Retrieved {len(targets)} targets for policy {policy_id}")
            return targets
        except ClientError as e:
            logger.error(f"Failed to list policy targets: {e.response['Error']['Code']}")
            raise OrganizationsException(f"Failed to list policy targets: {str(e)}")

    # =========================================================================
    # Tagging & Resource Organization
    # =========================================================================

    def tag_resource(self, resource_id: str, tags: Dict[str, str]) -> bool:
        """Add tags to organization resource"""
        try:
            tag_list = [{'Key': k, 'Value': v} for k, v in tags.items()]
            self.org_client.tag_resource(ResourceId=resource_id, Tags=tag_list)
            logger.info(f"Tagged resource {resource_id} with {len(tags)} tags")
            return True
        except ClientError as e:
            logger.error(f"Failed to tag resource: {e.response['Error']['Code']}")
            raise OrganizationsException(f"Failed to tag resource: {str(e)}")

    def list_tags_for_resource(self, resource_id: str) -> List[Dict[str, str]]:
        """List tags for a resource"""
        try:
            response = self.org_client.list_tags_for_resource(ResourceId=resource_id)
            logger.debug(f"Retrieved tags for {resource_id}")
            return response['Tags']
        except ClientError as e:
            logger.error(f"Failed to list tags: {e.response['Error']['Code']}")
            raise OrganizationsException(f"Failed to list tags: {str(e)}")

    def untag_resource(self, resource_id: str, tag_keys: List[str]) -> bool:
        """Remove tags from resource"""
        try:
            self.org_client.untag_resource(ResourceId=resource_id, TagKeys=tag_keys)
            logger.info(f"Untagged {len(tag_keys)} tags from {resource_id}")
            return True
        except ClientError as e:
            logger.error(f"Failed to untag resource: {e.response['Error']['Code']}")
            raise OrganizationsException(f"Failed to untag resource: {str(e)}")

    # =========================================================================
    # AWS CloudTrail Integration
    # =========================================================================

    def get_cloudtrail_status(self) -> Dict[str, Any]:
        """Get CloudTrail status for organization"""
        try:
            response = self.cloudtrail_client.describe_trails(includeShadowTrails=True)
            trails = response.get('trailList', [])
            logger.info(f"Retrieved {len(trails)} CloudTrail trails")
            return {'trails': trails, 'trail_count': len(trails)}
        except ClientError as e:
            logger.error(f"Failed to get CloudTrail status: {e.response['Error']['Code']}")
            return {'error': str(e), 'trail_count': 0}

    # =========================================================================
    # AWS Config Integration
    # =========================================================================

    def get_config_compliance(self) -> Dict[str, Any]:
        """Get AWS Config compliance status"""
        try:
            response = self.config_client.describe_compliance_by_config_rule()
            rules = response.get('ComplianceByConfigRules', [])
            logger.info(f"Retrieved compliance for {len(rules)} Config rules")
            return {'rules': rules, 'rule_count': len(rules)}
        except ClientError as e:
            logger.error(f"Failed to get Config compliance: {e.response['Error']['Code']}")
            return {'error': str(e), 'rule_count': 0}

    # =========================================================================
    # Reporting
    # =========================================================================

    def generate_organization_report(self) -> Dict[str, Any]:
        """Generate comprehensive organization report"""
        try:
            org_info = self.get_organization_info()
            accounts = self.list_accounts()
            ous = self.list_ous()
            policies = self.list_policies()
            cloudtrail_status = self.get_cloudtrail_status()
            config_compliance = self.get_config_compliance()

            report = {
                'timestamp': datetime.now().isoformat(),
                'organization': org_info,
                'accounts_count': len(accounts),
                'accounts': accounts,
                'ous_count': len(ous),
                'ous': ous,
                'policies_count': len(policies),
                'policies': [{'Id': p['Id'], 'Name': p['Name'], 'Type': p['Type']} for p in policies],
                'cloudtrail': cloudtrail_status,
                'config': config_compliance,
                'features_enabled': org_info.get('AvailablePolicyTypes', [])
            }
            
            logger.info(f"Generated organization report with {len(accounts)} accounts, {len(ous)} OUs")
            return report
        except Exception as e:
            logger.error(f"Failed to generate report: {str(e)}")
            raise OrganizationsException(f"Failed to generate report: {str(e)}")

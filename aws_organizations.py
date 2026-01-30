"""
AWS Organizations Management
Manage accounts, OUs, SCPs, and organizational features
"""

import boto3
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

class AWSOrganizationsManager:
    """Manage AWS Organizations and accounts"""
    
    def __init__(self, region: str = 'us-east-1'):
        self.org_client = boto3.client('organizations', region_name=region)
        self.sts_client = boto3.client('sts', region_name=region)
        self.cloudtrail_client = boto3.client('cloudtrail', region_name=region)
        self.config_client = boto3.client('config', region_name=region)
    
    # =========================================================================
    # Organization Information
    # =========================================================================
    
    def get_organization_info(self) -> Dict[str, Any]:
        """Get organization details"""
        try:
            response = self.org_client.describe_organization()
            return response['Organization']
        except Exception as e:
            raise Exception(f"Failed to get organization info: {str(e)}")
    
    def get_root_id(self) -> str:
        """Get the root organizational unit ID"""
        try:
            roots = self.org_client.list_roots()
            return roots['Roots'][0]['Id']
        except Exception as e:
            raise Exception(f"Failed to get root ID: {str(e)}")
    
    # =========================================================================
    # Organizational Units (OUs)
    # =========================================================================
    
    def list_ous(self) -> List[Dict[str, Any]]:
        """List all organizational units"""
        try:
            root_id = self.get_root_id()
            ous = []
            paginator = self.org_client.get_paginator('list_organizational_units_for_parent')
            
            for page in paginator.paginate(ParentId=root_id):
                ous.extend(page['OrganizationalUnits'])
            
            return ous
        except Exception as e:
            raise Exception(f"Failed to list OUs: {str(e)}")
    
    def create_ou(self, parent_id: str, ou_name: str) -> str:
        """Create a new organizational unit"""
        try:
            response = self.org_client.create_organizational_unit(
                ParentId=parent_id,
                Name=ou_name
            )
            return response['OrganizationalUnit']['Id']
        except self.org_client.exceptions.ParentNotFoundException:
            raise Exception(f"Parent OU {parent_id} not found")
        except Exception as e:
            raise Exception(f"Failed to create OU: {str(e)}")
    
    def delete_ou(self, ou_id: str) -> bool:
        """Delete an organizational unit"""
        try:
            self.org_client.delete_organizational_unit(OrganizationalUnitId=ou_id)
            return True
        except Exception as e:
            raise Exception(f"Failed to delete OU: {str(e)}")
    
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
            
            return accounts
        except Exception as e:
            raise Exception(f"Failed to list accounts: {str(e)}")
    
    def create_account(self, email: str, account_name: str) -> str:
        """Create a new AWS account"""
        try:
            response = self.org_client.create_account(
                Email=email,
                AccountName=account_name
            )
            return response['CreateAccountStatus']['Id']
        except Exception as e:
            raise Exception(f"Failed to create account: {str(e)}")
    
    def create_account_status(self, create_account_request_id: str) -> Dict[str, Any]:
        """Check the status of account creation"""
        try:
            response = self.org_client.describe_create_account_status(
                CreateAccountRequestId=create_account_request_id
            )
            return response['CreateAccountStatus']
        except Exception as e:
            raise Exception(f"Failed to get account creation status: {str(e)}")
    
    def move_account(self, account_id: str, source_parent_id: str, destination_parent_id: str) -> bool:
        """Move account between OUs"""
        try:
            self.org_client.move_account(
                AccountId=account_id,
                SourceParentId=source_parent_id,
                DestinationParentId=destination_parent_id
            )
            return True
        except Exception as e:
            raise Exception(f"Failed to move account: {str(e)}")
    
    def list_accounts_for_ou(self, ou_id: str) -> List[Dict[str, Any]]:
        """List accounts in a specific OU"""
        try:
            accounts = []
            paginator = self.org_client.get_paginator('list_accounts_for_parent')
            
            for page in paginator.paginate(ParentId=ou_id):
                accounts.extend(page['Accounts'])
            
            return accounts
        except Exception as e:
            raise Exception(f"Failed to list accounts for OU: {str(e)}")
    
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
            
            return policies
        except Exception as e:
            raise Exception(f"Failed to list policies: {str(e)}")
    
    def get_policy(self, policy_id: str) -> Dict[str, Any]:
        """Get policy details"""
        try:
            response = self.org_client.describe_policy(PolicyId=policy_id)
            return response['Policy']
        except Exception as e:
            raise Exception(f"Failed to get policy: {str(e)}")
    
    def attach_policy(self, policy_id: str, target_id: str) -> bool:
        """Attach policy to target (OU or account)"""
        try:
            self.org_client.attach_policy(
                PolicyId=policy_id,
                TargetId=target_id
            )
            return True
        except Exception as e:
            raise Exception(f"Failed to attach policy: {str(e)}")
    
    def detach_policy(self, policy_id: str, target_id: str) -> bool:
        """Detach policy from target"""
        try:
            self.org_client.detach_policy(
                PolicyId=policy_id,
                TargetId=target_id
            )
            return True
        except Exception as e:
            raise Exception(f"Failed to detach policy: {str(e)}")
    
    def list_targets_for_policy(self, policy_id: str) -> List[Dict[str, Any]]:
        """List all targets (OUs/accounts) a policy is attached to"""
        try:
            targets = []
            paginator = self.org_client.get_paginator('list_targets_for_policy')
            
            for page in paginator.paginate(PolicyId=policy_id):
                targets.extend(page['Targets'])
            
            return targets
        except Exception as e:
            raise Exception(f"Failed to list policy targets: {str(e)}")
    
    # =========================================================================
    # Tagging & Resource Organization
    # =========================================================================
    
    def tag_resource(self, resource_id: str, tags: Dict[str, str]) -> bool:
        """Add tags to organization resource"""
        try:
            tag_list = [{'Key': k, 'Value': v} for k, v in tags.items()]
            self.org_client.tag_resource(
                ResourceId=resource_id,
                Tags=tag_list
            )
            return True
        except Exception as e:
            raise Exception(f"Failed to tag resource: {str(e)}")
    
    def list_tags_for_resource(self, resource_id: str) -> List[Dict[str, str]]:
        """List tags for a resource"""
        try:
            response = self.org_client.list_tags_for_resource(ResourceId=resource_id)
            return response['Tags']
        except Exception as e:
            raise Exception(f"Failed to list tags: {str(e)}")
    
    def untag_resource(self, resource_id: str, tag_keys: List[str]) -> bool:
        """Remove tags from resource"""
        try:
            self.org_client.untag_resource(
                ResourceId=resource_id,
                TagKeys=tag_keys
            )
            return True
        except Exception as e:
            raise Exception(f"Failed to untag resource: {str(e)}")
    
    # =========================================================================
    # AWS CloudTrail Integration
    # =========================================================================
    
    def get_cloudtrail_status(self) -> Dict[str, Any]:
        """Get CloudTrail status for organization"""
        try:
            response = self.cloudtrail_client.describe_trails(
                includeShadowTrails=True
            )
            return response['trailList'] if response['trailList'] else {}
        except Exception as e:
            return {'error': str(e)}
    
    # =========================================================================
    # AWS Config Integration
    # =========================================================================
    
    def get_config_compliance(self) -> Dict[str, Any]:
        """Get AWS Config compliance status"""
        try:
            response = self.config_client.describe_compliance_by_config_rule()
            return response['ComplianceByConfigRules']
        except Exception as e:
            return {'error': str(e)}
    
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
                'features_enabled': org_info.get('AvailablePolicyTypes', [])
            }
            
            return report
        except Exception as e:
            raise Exception(f"Failed to generate report: {str(e)}")


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == '__main__':
    manager = AWSOrganizationsManager()
    
    print("=== AWS Organizations Report ===\n")
    
    # Get organization info
    org_info = manager.get_organization_info()
    print(f"Organization ID: {org_info['Id']}")
    print(f"Master Account: {org_info['MasterAccountId']}")
    print(f"Feature Set: {org_info['FeatureSet']}\n")
    
    # List all OUs
    print("=== Organizational Units ===")
    ous = manager.list_ous()
    for ou in ous:
        print(f"  - {ou['Name']} (ID: {ou['Id']})")
    print()
    
    # List all accounts
    print("=== AWS Accounts ===")
    accounts = manager.list_accounts()
    for account in accounts:
        status = account.get('Status', 'UNKNOWN')
        print(f"  - {account['Name']} ({account['Id']}) - Status: {status}")
    print()
    
    # List policies
    print("=== Service Control Policies ===")
    policies = manager.list_policies()
    for policy in policies:
        print(f"  - {policy['Name']} (ID: {policy['Id']})")
    print()
    
    # Generate full report
    print("=== Full Organization Report ===")
    report = manager.generate_organization_report()
    print(json.dumps(report, indent=2, default=str))

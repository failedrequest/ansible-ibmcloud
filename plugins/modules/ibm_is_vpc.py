#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, IBM Cloud Team
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r'''
---
module: ibm_is_vpc
short_description: Manage IBM Cloud VPC resources
version_added: "1.0.0"
description:
    - Create, update, or delete IBM Cloud Virtual Private Cloud (VPC) resources
    - This module uses the native IBM Cloud Python SDK (no Terraform dependency)
    - Supports idempotent operations
requirements:
    - ibm-vpc >= 0.33.0
    - ibm-cloud-sdk-core >= 3.20.0
options:
    name:
        description:
            - Name of the VPC
            - Required when creating a new VPC
        type: str
        required: true
    id:
        description:
            - ID of the VPC
            - Required when updating or deleting an existing VPC
        type: str
        required: false
    address_prefix_management:
        description:
            - Address prefix management mode
        type: str
        choices: ['auto', 'manual']
        default: 'auto'
    classic_access:
        description:
            - Enable classic infrastructure access
        type: bool
        default: false
    default_network_acl_name:
        description:
            - Name for the default network ACL
        type: str
        required: false
    default_routing_table_name:
        description:
            - Name for the default routing table
        type: str
        required: false
    default_security_group_name:
        description:
            - Name for the default security group
        type: str
        required: false
    dns:
        description:
            - DNS configuration for the VPC
        type: dict
        required: false
        suboptions:
            enable_hub:
                description: Enable DNS hub
                type: bool
            resolution_binding_count:
                description: Number of resolution bindings
                type: int
    tags:
        description:
            - List of tags to attach to the VPC
        type: list
        elements: str
        required: false
    ibmcloud_api_key:
        description:
            - IBM Cloud API key
            - Can also be set via IC_API_KEY or IBMCLOUD_API_KEY environment variable
        type: str
        required: false
        no_log: true
    region:
        description:
            - IBM Cloud region
        type: str
        default: 'us-south'
        choices: ['us-south', 'us-east', 'eu-gb', 'eu-de', 'jp-tok', 'au-syd', 'jp-osa', 'ca-tor', 'br-sao']
    resource_group:
        description:
            - Resource group ID
        type: str
        required: false
    state:
        description:
            - Desired state of the VPC
        type: str
        default: 'present'
        choices: ['present', 'absent']
author:
    - IBM Cloud Team
'''

EXAMPLES = r'''
- name: Create a VPC
  ibm_is_vpc:
    name: my-vpc
    region: us-south
    address_prefix_management: auto
    classic_access: false
    tags:
      - env:dev
      - project:demo
    state: present

- name: Update VPC tags
  ibm_is_vpc:
    id: r006-12345678-1234-1234-1234-123456789012
    name: my-vpc
    tags:
      - env:prod
      - project:demo
    state: present

- name: Delete a VPC
  ibm_is_vpc:
    id: r006-12345678-1234-1234-1234-123456789012
    state: absent
'''

RETURN = r'''
resource:
    description: VPC resource information
    returned: always
    type: dict
    contains:
        id:
            description: VPC ID
            type: str
            sample: "r006-12345678-1234-1234-1234-123456789012"
        name:
            description: VPC name
            type: str
            sample: "my-vpc"
        crn:
            description: Cloud Resource Name
            type: str
            sample: "crn:v1:bluemix:public:is:us-south:a/123456::vpc:r006-12345678"
        status:
            description: VPC status
            type: str
            sample: "available"
        created_at:
            description: Creation timestamp
            type: str
            sample: "2024-01-01T00:00:00.000Z"
        resource_group:
            description: Resource group information
            type: dict
        default_network_acl:
            description: Default network ACL information
            type: dict
        default_routing_table:
            description: Default routing table information
            type: dict
        default_security_group:
            description: Default security group information
            type: dict
changed:
    description: Whether the VPC was changed
    returned: always
    type: bool
msg:
    description: Status message
    returned: always
    type: str
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ibm.cloudcollection.plugins.module_utils.ibm_cloud_sdk import (
    IBMCloudSDKModule,
    get_common_argument_spec
)

try:
    from ibm_vpc import VpcV1
    from ibm_cloud_sdk_core import ApiException
    HAS_IBM_VPC = True
except ImportError:
    HAS_IBM_VPC = False


class IBMVPCModule(IBMCloudSDKModule):
    """IBM Cloud VPC module implementation."""
    
    def __init__(self, module):
        """Initialize the VPC module."""
        super().__init__(module)
        
        if not HAS_IBM_VPC:
            self.fail_json(msg="ibm-vpc Python SDK is required. Install with: pip install ibm-vpc")
        
        # Initialize VPC service
        self.vpc_service = VpcV1(
            authenticator=self.auth.get_authenticator()
        )
        self.vpc_service.set_service_url(f'https://{self.region}.iaas.cloud.ibm.com/v1')
        
        # Module-specific parameters
        self.vpc_id = self.params.get('id')
        self.vpc_name = self.params.get('name')
        self.address_prefix_management = self.params.get('address_prefix_management', 'auto')
        self.classic_access = self.params.get('classic_access', False)
        self.tags = self.params.get('tags', [])
    
    def get_vpc_by_id(self, vpc_id: str):
        """Get VPC by ID."""
        try:
            response = self.vpc_service.get_vpc(id=vpc_id)
            return response.get_result()
        except ApiException as e:
            if e.code == 404:
                return None
            self.handle_api_exception(e, f"retrieve VPC {vpc_id}")
    
    def get_vpc_by_name(self, name: str):
        """Get VPC by name."""
        try:
            response = self.vpc_service.list_vpcs()
            vpcs = response.get_result().get('vpcs', [])
            
            for vpc in vpcs:
                if vpc.get('name') == name:
                    return vpc
            return None
        except ApiException as e:
            self.handle_api_exception(e, f"list VPCs to find {name}")
    
    def create_vpc(self):
        """Create a new VPC."""
        self.check_mode_exit(changed=True, msg=f"Would create VPC: {self.vpc_name}")
        
        try:
            # Prepare VPC prototype
            vpc_prototype = {
                'name': self.vpc_name,
                'address_prefix_management': self.address_prefix_management,
                'classic_access': self.classic_access
            }
            
            # Add optional parameters
            if self.resource_group_id:
                vpc_prototype['resource_group'] = {'id': self.resource_group_id}
            
            if self.params.get('default_network_acl_name'):
                vpc_prototype['default_network_acl'] = {
                    'name': self.params['default_network_acl_name']
                }
            
            if self.params.get('default_routing_table_name'):
                vpc_prototype['default_routing_table'] = {
                    'name': self.params['default_routing_table_name']
                }
            
            if self.params.get('default_security_group_name'):
                vpc_prototype['default_security_group'] = {
                    'name': self.params['default_security_group_name']
                }
            
            if self.params.get('dns'):
                vpc_prototype['dns'] = self.params['dns']
            
            # Create VPC
            response = self.vpc_service.create_vpc(**vpc_prototype)
            vpc = response.get_result()
            
            # Add tags if specified
            if self.tags:
                self._add_tags(vpc['crn'], self.tags)
            
            self.result['changed'] = True
            self.result['resource'] = vpc
            self.result['msg'] = f"VPC {self.vpc_name} created successfully"
            
        except ApiException as e:
            self.handle_api_exception(e, f"create VPC {self.vpc_name}")
    
    def update_vpc(self, vpc):
        """Update an existing VPC."""
        changed = False
        updates = {}
        
        # Check for name change
        if self.vpc_name and vpc.get('name') != self.vpc_name:
            updates['name'] = self.vpc_name
            changed = True
        
        # Update VPC if changes detected
        if updates:
            self.check_mode_exit(changed=True, msg=f"Would update VPC: {vpc['id']}")
            
            try:
                response = self.vpc_service.update_vpc(
                    id=vpc['id'],
                    vpc_patch=updates
                )
                vpc = response.get_result()
                changed = True
            except ApiException as e:
                self.handle_api_exception(e, f"update VPC {vpc['id']}")
        
        # Handle tags
        if self.tags:
            # Note: Tag management would require additional IBM Cloud Global Tagging API
            # This is a placeholder for tag update logic
            pass
        
        self.result['changed'] = changed
        self.result['resource'] = vpc
        self.result['msg'] = f"VPC {vpc['name']} updated" if changed else f"VPC {vpc['name']} unchanged"
    
    def delete_vpc(self, vpc_id: str):
        """Delete a VPC."""
        self.check_mode_exit(changed=True, msg=f"Would delete VPC: {vpc_id}")
        
        try:
            self.vpc_service.delete_vpc(id=vpc_id)
            self.result['changed'] = True
            self.result['msg'] = f"VPC {vpc_id} deleted successfully"
        except ApiException as e:
            self.handle_api_exception(e, f"delete VPC {vpc_id}")
    
    def _add_tags(self, crn: str, tags: list):
        """Add tags to a resource (placeholder for Global Tagging API)."""
        # This would require the IBM Cloud Global Tagging API
        # For now, this is a placeholder
        pass
    
    def run(self):
        """Execute the module logic."""
        # Validate required parameters
        if self.state == 'present' and not self.vpc_name:
            self.fail_json(msg="'name' is required when state is 'present'")
        
        # Get existing VPC - support lookup by ID or name
        existing_vpc = None
        if self.vpc_id:
            existing_vpc = self.get_vpc_by_id(self.vpc_id)
        elif self.vpc_name:
            existing_vpc = self.get_vpc_by_name(self.vpc_name)
        
        # Handle state
        if self.state == 'present':
            if existing_vpc:
                self.update_vpc(existing_vpc)
            else:
                self.create_vpc()
        
        elif self.state == 'absent':
            if existing_vpc:
                self.delete_vpc(existing_vpc['id'])
            else:
                self.result['msg'] = f"VPC '{self.vpc_name or self.vpc_id}' not found"
        
        self.exit_json()


def main():
    """Main module execution."""
    argument_spec = get_common_argument_spec()
    argument_spec.update({
        'name': {'type': 'str', 'required': True},
        'id': {'type': 'str', 'required': False},
        'address_prefix_management': {
            'type': 'str',
            'choices': ['auto', 'manual'],
            'default': 'auto'
        },
        'classic_access': {'type': 'bool', 'default': False},
        'default_network_acl_name': {'type': 'str', 'required': False},
        'default_routing_table_name': {'type': 'str', 'required': False},
        'default_security_group_name': {'type': 'str', 'required': False},
        'dns': {'type': 'dict', 'required': False},
        'tags': {'type': 'list', 'elements': 'str', 'required': False}
    })
    
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True
    )
    
    vpc_module = IBMVPCModule(module)
    vpc_module.run()


if __name__ == '__main__':
    main()

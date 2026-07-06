#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, IBM Cloud Team
# BSD 2-Clause License (see LICENSE or https://opensource.org/licenses/BSD-2-Clause)

DOCUMENTATION = r'''
---
module: ibm_is_security_group_rule
short_description: Manage IBM Cloud Security Group Rule
version_added: "1.0.0"
description:
    - Create, update, or delete IBM Cloud Security Group Rule
    - This module uses the native IBM Cloud Python SDK (no Terraform dependency)
    - Supports idempotent operations
requirements:
    - ibm-vpc >= 0.33.0
    - ibm-cloud-sdk-core >= 3.20.0
options:
    name:
        description:
            - Name of the resource
        type: str
        required: true
    id:
        description:
            - ID of the resource
        type: str
        required: false
    port_min:
        description:
            - Port Min
        type: str
        required: false
    port_max:
        description:
            - Port Max
        type: str
        required: false
    remote:
        description:
            - Remote
        type: str
        required: false
    code:
        description:
            - Code
        type: str
        required: false
    type:
        description:
            - Type
        type: str
        required: false
author:
    - IBM Cloud Team
'''

EXAMPLES = r'''
- name: Create Security Group Rule
  ibm_is_security_group_rule:
    name: my-security_group_rule
    state: present

- name: Delete Security Group Rule
  ibm_is_security_group_rule:
    id: resource-id-123
    state: absent

'''

RETURN = r'''
resource:
    description: Security Group Rule information
    returned: always
    type: dict
changed:
    description: Whether the resource was changed
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


class IBMSecurityGroupRuleModule(IBMCloudSDKModule):
    """IBM Cloud Security Group Rule module implementation."""
    
    def __init__(self, module):
        """Initialize the module."""
        super().__init__(module)
        
        if not HAS_IBM_VPC:
            self.fail_json(msg="ibm-vpc Python SDK is required")
        
        self.vpc_service = VpcV1(authenticator=self.auth.get_authenticator())
        self.vpc_service.set_service_url(f'https://{self.region}.iaas.cloud.ibm.com/v1')
        
        self.resource_id = self.params.get('id')
        self.resource_name = self.params.get('name')
    
    def get_resource(self, resource_id: str):
        """Get resource by ID."""
        try:
            response = self.vpc_service.get_security_group_rule(id=resource_id)
            return response.get_result()
        except ApiException as e:
            if e.code == 404:
                return None
            self.handle_api_exception(e, f"retrieve security_group_rule {resource_id}")
    
    def list_resources(self):
        """List all resources."""
        try:
            response = self.vpc_service.list_security_group_rules()
            return response.get_result().get('rules', [])
        except ApiException as e:
            self.handle_api_exception(e, f"list security_group_rules")
    
    def create_resource(self):
        """Create a new resource."""
        self.check_mode_exit(changed=True, msg=f"Would create security_group_rule")
        
        try:
            from ibm_vpc.vpc_v1 import (
                SecurityGroupRulePrototypeSecurityGroupRuleProtocolTCPUDP,
                SecurityGroupRuleRemotePrototypeSecurityGroupRuleCIDRPrototype
            )
            
            security_group_id = self.params.get('security_group')
            direction = self.params.get('direction')
            protocol = self.params.get('protocol')
            port_min = self.params.get('port_min')
            port_max = self.params.get('port_max')
            remote_cidr = self.params.get('remote')
            
            # Create remote prototype for CIDR
            remote = SecurityGroupRuleRemotePrototypeSecurityGroupRuleCIDRPrototype(
                cidr_block=remote_cidr
            ) if remote_cidr else None
            
            # Create rule prototype
            prototype = SecurityGroupRulePrototypeSecurityGroupRuleProtocolTCPUDP(
                direction=direction,
                protocol=protocol,
                port_min=int(port_min) if port_min else None,
                port_max=int(port_max) if port_max else None,
                remote=remote
            )
            
            response = self.vpc_service.create_security_group_rule(
                security_group_id=security_group_id,
                security_group_rule_prototype=prototype
            )
            resource = response.get_result()
            
            self.result['changed'] = True
            self.result['resource'] = resource
            self.result['msg'] = f"security_group_rule created successfully"
            
        except ApiException as e:
            self.handle_api_exception(e, f"create security_group_rule")
    
    def update_resource(self, resource):
        """Update an existing resource."""
        changed = False
        updates = {}
        
        if self.resource_name and resource.get('name') != self.resource_name:
            updates['name'] = self.resource_name
            changed = True
        
        if updates:
            self.check_mode_exit(changed=True, msg=f"Would update security_group_rule: {resource['id']}")
            
            try:
                response = self.vpc_service.update_security_group_rule(
                    id=resource['id'],
                    security_group_rule_patch=updates
                )
                resource = response.get_result()
                changed = True
            except ApiException as e:
                self.handle_api_exception(e, f"update security_group_rule {resource['id']}")
        
        self.result['changed'] = changed
        self.result['resource'] = resource
        self.result['msg'] = f"security_group_rule {resource['name']} " + ("updated" if changed else "unchanged")
    
    def delete_resource(self, resource_id: str):
        """Delete a resource."""
        self.check_mode_exit(changed=True, msg=f"Would delete security_group_rule: {resource_id}")
        
        try:
            self.vpc_service.delete_security_group_rule(id=resource_id)
            self.result['changed'] = True
            self.result['msg'] = f"security_group_rule {resource_id} deleted successfully"
        except ApiException as e:
            self.handle_api_exception(e, f"delete security_group_rule {resource_id}")
    
    def run(self):
        """Execute the module logic."""
        existing_resource = None
        if self.resource_id:
            existing_resource = self.get_resource(self.resource_id)
        elif self.resource_name:
            resources = self.list_resources()
            for res in resources:
                if res.get('name') == self.resource_name:
                    existing_resource = res
                    break
        
        if self.state == 'present':
            if existing_resource:
                self.update_resource(existing_resource)
            else:
                self.create_resource()
        
        elif self.state == 'absent':
            if existing_resource:
                self.delete_resource(existing_resource['id'])
            else:
                self.result['msg'] = f"security_group_rule not found"
        
        self.exit_json()


def main():
    """Main module execution."""
    argument_spec = get_common_argument_spec()
    argument_spec.update({
        'name': {'type': 'str', 'required': False},
        'id': {'type': 'str', 'required': False},
        'security_group': {'type': 'str', 'required': False},
        'direction': {'type': 'str', 'required': False},
        'protocol': {'type': 'str', 'required': False},
        'port_min': {'type': 'str', 'required': False},
        'port_max': {'type': 'str', 'required': False},
        'remote': {'type': 'str', 'required': False},
        'code': {'type': 'str', 'required': False},
        'type': {'type': 'str', 'required': False}
    })
    
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True
    )
    
    resource_module = IBMSecurityGroupRuleModule(module)
    resource_module.run()


if __name__ == '__main__':
    main()

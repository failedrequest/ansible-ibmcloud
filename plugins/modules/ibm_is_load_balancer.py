#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, IBM Cloud Team
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r'''
---
module: ibm_is_load_balancer
short_description: Manage IBM Cloud Load Balancer
version_added: "1.0.0"
description:
    - Create, update, or delete IBM Cloud Load Balancer
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
    is_public:
        description:
            - Is Public
        type: str
        required: false
    listeners:
        description:
            - Listeners
        type: str
        required: false
    pools:
        description:
            - Pools
        type: str
        required: false
    resource_group:
        description:
            - Resource Group
        type: str
        required: false
author:
    - IBM Cloud Team
'''

EXAMPLES = r'''
- name: Create Load Balancer
  ibm_is_load_balancer:
    name: my-load_balancer
    state: present

- name: Delete Load Balancer
  ibm_is_load_balancer:
    id: resource-id-123
    state: absent

'''

RETURN = r'''
resource:
    description: Load Balancer information
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


class IBMLoadBalancerModule(IBMCloudSDKModule):
    """IBM Cloud Load Balancer module implementation."""
    
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
            response = self.vpc_service.get_load_balancer(id=resource_id)
            return response.get_result()
        except ApiException as e:
            if e.code == 404:
                return None
            self.handle_api_exception(e, f"retrieve load_balancer {resource_id}")
    
    def list_resources(self):
        """List all resources."""
        try:
            response = self.vpc_service.list_load_balancers()
            return response.get_result().get('load_balancers', [])
        except ApiException as e:
            self.handle_api_exception(e, f"list load_balancers")
    
    def create_resource(self):
        """Create a new resource."""
        self.check_mode_exit(changed=True, msg=f"Would create load_balancer: {self.resource_name}")
        
        try:
            prototype = {
            'name': self.resource_name,
            'subnets': self.params.get('subnets')
        }
            
            response = self.vpc_service.create_load_balancer(**prototype)
            resource = response.get_result()
            
            self.result['changed'] = True
            self.result['resource'] = resource
            self.result['msg'] = f"load_balancer {self.resource_name} created successfully"
            
        except ApiException as e:
            self.handle_api_exception(e, f"create load_balancer {self.resource_name}")
    
    def update_resource(self, resource):
        """Update an existing resource."""
        changed = False
        updates = {}
        
        if self.resource_name and resource.get('name') != self.resource_name:
            updates['name'] = self.resource_name
            changed = True
        
        if updates:
            self.check_mode_exit(changed=True, msg=f"Would update load_balancer: {resource['id']}")
            
            try:
                response = self.vpc_service.update_load_balancer(
                    id=resource['id'],
                    load_balancer_patch=updates
                )
                resource = response.get_result()
                changed = True
            except ApiException as e:
                self.handle_api_exception(e, f"update load_balancer {resource['id']}")
        
        self.result['changed'] = changed
        self.result['resource'] = resource
        self.result['msg'] = f"load_balancer {resource['name']} " + ("updated" if changed else "unchanged")
    
    def delete_resource(self, resource_id: str):
        """Delete a resource."""
        self.check_mode_exit(changed=True, msg=f"Would delete load_balancer: {resource_id}")
        
        try:
            self.vpc_service.delete_load_balancer(id=resource_id)
            self.result['changed'] = True
            self.result['msg'] = f"load_balancer {resource_id} deleted successfully"
        except ApiException as e:
            self.handle_api_exception(e, f"delete load_balancer {resource_id}")
    
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
                self.result['msg'] = f"load_balancer not found"
        
        self.exit_json()


def main():
    """Main module execution."""
    argument_spec = get_common_argument_spec()
    argument_spec.update({
        'name': {'type': 'str', 'required': True},
        'id': {'type': 'str', 'required': False},
        'is_public': {'type': 'str', 'required': False},
        'listeners': {'type': 'str', 'required': False},
        'pools': {'type': 'str', 'required': False},
        'resource_group': {'type': 'str', 'required': False}
    })
    
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True
    )
    
    resource_module = IBMLoadBalancerModule(module)
    resource_module.run()


if __name__ == '__main__':
    main()

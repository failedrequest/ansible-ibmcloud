#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, IBM Cloud Team
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r'''
---
module: ibm_is_vpn_gateway_connection
short_description: Manage IBM Cloud Vpn Gateway Connection
version_added: "1.0.0"
description:
    - Create, update, or delete IBM Cloud Vpn Gateway Connection
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
    local_cidrs:
        description:
            - Local Cidrs
        type: str
        required: false
    peer_cidrs:
        description:
            - Peer Cidrs
        type: str
        required: false
    admin_state_up:
        description:
            - Admin State Up
        type: str
        required: false
author:
    - IBM Cloud Team
'''

EXAMPLES = r'''
- name: Create Vpn Gateway Connection
  ibm_is_vpn_gateway_connection:
    name: my-vpn_gateway_connection
    state: present

- name: Delete Vpn Gateway Connection
  ibm_is_vpn_gateway_connection:
    id: resource-id-123
    state: absent

'''

RETURN = r'''
resource:
    description: Vpn Gateway Connection information
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


class IBMVpnGatewayConnectionModule(IBMCloudSDKModule):
    """IBM Cloud Vpn Gateway Connection module implementation."""
    
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
            response = self.vpc_service.get_vpn_gateway_connection(id=resource_id)
            return response.get_result()
        except ApiException as e:
            if e.code == 404:
                return None
            self.handle_api_exception(e, f"retrieve vpn_gateway_connection {resource_id}")
    
    def list_resources(self):
        """List all resources."""
        try:
            response = self.vpc_service.list_vpn_gateway_connections()
            return response.get_result().get('connections', [])
        except ApiException as e:
            self.handle_api_exception(e, f"list vpn_gateway_connections")
    
    def create_resource(self):
        """Create a new resource."""
        self.check_mode_exit(changed=True, msg=f"Would create vpn_gateway_connection: {self.resource_name}")
        
        try:
            prototype = {
            'name': self.resource_name,
            'name': self.params.get('name'),
            'peer_address': self.params.get('peer_address'),
            'preshared_key': self.params.get('preshared_key')
        }
            
            response = self.vpc_service.create_vpn_gateway_connection(**prototype)
            resource = response.get_result()
            
            self.result['changed'] = True
            self.result['resource'] = resource
            self.result['msg'] = f"vpn_gateway_connection {self.resource_name} created successfully"
            
        except ApiException as e:
            self.handle_api_exception(e, f"create vpn_gateway_connection {self.resource_name}")
    
    def update_resource(self, resource):
        """Update an existing resource."""
        changed = False
        updates = {}
        
        if self.resource_name and resource.get('name') != self.resource_name:
            updates['name'] = self.resource_name
            changed = True
        
        if updates:
            self.check_mode_exit(changed=True, msg=f"Would update vpn_gateway_connection: {resource['id']}")
            
            try:
                response = self.vpc_service.update_vpn_gateway_connection(
                    id=resource['id'],
                    vpn_gateway_connection_patch=updates
                )
                resource = response.get_result()
                changed = True
            except ApiException as e:
                self.handle_api_exception(e, f"update vpn_gateway_connection {resource['id']}")
        
        self.result['changed'] = changed
        self.result['resource'] = resource
        self.result['msg'] = f"vpn_gateway_connection {resource['name']} " + ("updated" if changed else "unchanged")
    
    def delete_resource(self, resource_id: str):
        """Delete a resource."""
        self.check_mode_exit(changed=True, msg=f"Would delete vpn_gateway_connection: {resource_id}")
        
        try:
            self.vpc_service.delete_vpn_gateway_connection(id=resource_id)
            self.result['changed'] = True
            self.result['msg'] = f"vpn_gateway_connection {resource_id} deleted successfully"
        except ApiException as e:
            self.handle_api_exception(e, f"delete vpn_gateway_connection {resource_id}")
    
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
                self.result['msg'] = f"vpn_gateway_connection not found"
        
        self.exit_json()


def main():
    """Main module execution."""
    argument_spec = get_common_argument_spec()
    argument_spec.update({
        'name': {'type': 'str', 'required': True},
        'id': {'type': 'str', 'required': False},
        'local_cidrs': {'type': 'str', 'required': False},
        'peer_cidrs': {'type': 'str', 'required': False},
        'admin_state_up': {'type': 'str', 'required': False}
    })
    
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True
    )
    
    resource_module = IBMVpnGatewayConnectionModule(module)
    resource_module.run()


if __name__ == '__main__':
    main()

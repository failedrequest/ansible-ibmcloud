#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, IBM Cloud Team
# BSD 2-Clause License (see LICENSE or https://opensource.org/licenses/BSD-2-Clause)

DOCUMENTATION = r'''
---
module: ibm_is_virtual_network_interface
short_description: Manage IBM Cloud Virtual Network Interface
version_added: "1.0.0"
description:
    - Create, update, or delete IBM Cloud Virtual Network Interface
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
    subnet:
        description:
            - Subnet
        type: str
        required: false
    security_groups:
        description:
            - Security Groups
        type: str
        required: false
    enable_infrastructure_nat:
        description:
            - Enable Infrastructure Nat
        type: str
        required: false
author:
    - IBM Cloud Team
'''

EXAMPLES = r'''
- name: Create Virtual Network Interface
  ibm_is_virtual_network_interface:
    name: my-virtual_network_interface
    state: present

- name: Delete Virtual Network Interface
  ibm_is_virtual_network_interface:
    id: resource-id-123
    state: absent

'''

RETURN = r'''
resource:
    description: Virtual Network Interface information
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


class IBMVirtualNetworkInterfaceModule(IBMCloudSDKModule):
    """IBM Cloud Virtual Network Interface module implementation."""
    
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
            response = self.vpc_service.get_virtual_network_interface(id=resource_id)
            return response.get_result()
        except ApiException as e:
            if e.code == 404:
                return None
            self.handle_api_exception(e, f"retrieve virtual_network_interface {resource_id}")
    
    def list_resources(self):
        """List all resources."""
        try:
            response = self.vpc_service.list_virtual_network_interfaces()
            return response.get_result().get('virtual_network_interfaces', [])
        except ApiException as e:
            self.handle_api_exception(e, f"list virtual_network_interfaces")
    
    def create_resource(self):
        """Create a new resource."""
        self.check_mode_exit(changed=True, msg=f"Would create virtual_network_interface: {self.resource_name}")
        
        try:
            # Build prototype using dictionaries (more flexible than SDK classes)
            prototype_kwargs = {
                'name': self.resource_name,
                'enable_infrastructure_nat': self.params.get('enable_infrastructure_nat', True)
            }
            
            # Add primary IP configuration with reserved IP
            reserved_ip_address = self.params.get('primary_ip_address')
            reserved_ip_name = self.params.get('primary_ip_name')
            
            if reserved_ip_address or reserved_ip_name:
                primary_ip = {}
                if reserved_ip_address:
                    primary_ip['address'] = reserved_ip_address
                if reserved_ip_name:
                    primary_ip['name'] = reserved_ip_name
                prototype_kwargs['primary_ip'] = primary_ip
            
            # Add subnet
            subnet_id = self.params.get('subnet')
            if subnet_id:
                prototype_kwargs['subnet'] = {'id': subnet_id}
            
            # Add security groups
            security_group_ids = self.params.get('security_groups')
            if security_group_ids:
                if isinstance(security_group_ids, str):
                    security_group_ids = [security_group_ids]
                prototype_kwargs['security_groups'] = [{'id': sg_id} for sg_id in security_group_ids]
            
            response = self.vpc_service.create_virtual_network_interface(**prototype_kwargs)
            resource = response.get_result()
            
            self.result['changed'] = True
            self.result['resource'] = resource
            self.result['msg'] = f"virtual_network_interface {self.resource_name} created successfully"
            
        except ApiException as e:
            self.handle_api_exception(e, f"create virtual_network_interface {self.resource_name}")
    
    def update_resource(self, resource):
        """Update an existing resource."""
        changed = False
        updates = {}
        
        if self.resource_name and resource.get('name') != self.resource_name:
            updates['name'] = self.resource_name
            changed = True
        
        if updates:
            self.check_mode_exit(changed=True, msg=f"Would update virtual_network_interface: {resource['id']}")
            
            try:
                response = self.vpc_service.update_virtual_network_interface(
                    id=resource['id'],
                    virtual_network_interface_patch=updates
                )
                resource = response.get_result()
                changed = True
            except ApiException as e:
                self.handle_api_exception(e, f"update virtual_network_interface {resource['id']}")
        
        self.result['changed'] = changed
        self.result['resource'] = resource
        self.result['msg'] = f"virtual_network_interface {resource['name']} " + ("updated" if changed else "unchanged")
    
    def delete_resource(self, resource_id: str):
        """Delete a resource."""
        self.check_mode_exit(changed=True, msg=f"Would delete virtual_network_interface: {resource_id}")
        
        try:
            # Use the correct SDK method name (plural)
            response = self.vpc_service.delete_virtual_network_interfaces(
                id=resource_id
            )
            self.result['changed'] = True
            self.result['msg'] = f"virtual_network_interface {resource_id} deleted successfully"
        except ApiException as e:
            self.handle_api_exception(e, f"delete virtual_network_interface {resource_id}")
    
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
                self.result['msg'] = f"virtual_network_interface not found"
        
        self.exit_json()


def main():
    """Main module execution."""
    argument_spec = get_common_argument_spec()
    argument_spec.update({
        'name': {'type': 'str', 'required': True},
        'id': {'type': 'str', 'required': False},
        'subnet': {'type': 'str', 'required': False},
        'security_groups': {'type': 'list', 'elements': 'str', 'required': False},
        'enable_infrastructure_nat': {'type': 'bool', 'required': False, 'default': True},
        'primary_ip_address': {'type': 'str', 'required': False},
        'primary_ip_name': {'type': 'str', 'required': False}
    })
    
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True
    )
    
    resource_module = IBMVirtualNetworkInterfaceModule(module)
    resource_module.run()


if __name__ == '__main__':
    main()

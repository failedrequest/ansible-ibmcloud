#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, IBM Cloud Team
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r'''
---
module: ibm_is_subnet
short_description: Manage IBM Cloud Subnet
version_added: "1.0.0"
description:
    - Create, update, or delete IBM Cloud Subnet
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
    network_acl:
        description:
            - Network Acl
        type: str
        required: false
    public_gateway:
        description:
            - Public Gateway
        type: str
        required: false
    routing_table:
        description:
            - Routing Table
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
- name: Create Subnet
  ibm_is_subnet:
    name: my-subnet
    state: present

- name: Delete Subnet
  ibm_is_subnet:
    id: resource-id-123
    state: absent

'''

RETURN = r'''
resource:
    description: Subnet information
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


class IBMSubnetModule(IBMCloudSDKModule):
    """IBM Cloud Subnet module implementation."""
    
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
            response = self.vpc_service.get_subnet(id=resource_id)
            return response.get_result()
        except ApiException as e:
            if e.code == 404:
                return None
            self.handle_api_exception(e, f"retrieve subnet {resource_id}")
    
    def list_resources(self):
        """List all resources."""
        try:
            response = self.vpc_service.list_subnets()
            return response.get_result().get('subnets', [])
        except ApiException as e:
            self.handle_api_exception(e, f"list subnets")
    
    def create_resource(self):
        """Create a new resource."""
        self.check_mode_exit(changed=True, msg=f"Would create subnet: {self.resource_name}")
        
        try:
            from ibm_vpc.vpc_v1 import SubnetPrototypeSubnetByCIDR, VPCIdentityById, ZoneIdentityByName
            
            vpc_identity = VPCIdentityById(id=self.params.get('vpc'))
            zone_identity = ZoneIdentityByName(name=self.params.get('zone'))
            
            prototype = SubnetPrototypeSubnetByCIDR(
                vpc=vpc_identity,
                ipv4_cidr_block=self.params.get('ipv4_cidr_block'),
                name=self.resource_name,
                zone=zone_identity
            )
            
            response = self.vpc_service.create_subnet(subnet_prototype=prototype)
            resource = response.get_result()
            
            self.result['changed'] = True
            self.result['resource'] = resource
            self.result['msg'] = f"subnet {self.resource_name} created successfully"
            
        except ApiException as e:
            self.handle_api_exception(e, f"create subnet {self.resource_name}")
    
    def update_resource(self, resource):
        """Update an existing resource."""
        changed = False
        updates = {}
        
        if self.resource_name and resource.get('name') != self.resource_name:
            updates['name'] = self.resource_name
            changed = True
        
        if updates:
            self.check_mode_exit(changed=True, msg=f"Would update subnet: {resource['id']}")
            
            try:
                response = self.vpc_service.update_subnet(
                    id=resource['id'],
                    subnet_patch=updates
                )
                resource = response.get_result()
                changed = True
            except ApiException as e:
                self.handle_api_exception(e, f"update subnet {resource['id']}")
        
        self.result['changed'] = changed
        self.result['resource'] = resource
        self.result['msg'] = f"subnet {resource['name']} " + ("updated" if changed else "unchanged")
    
    def delete_resource(self, resource_id: str):
        """Delete a resource."""
        self.check_mode_exit(changed=True, msg=f"Would delete subnet: {resource_id}")
        
        try:
            self.vpc_service.delete_subnet(id=resource_id)
            self.result['changed'] = True
            self.result['msg'] = f"subnet {resource_id} deleted successfully"
        except ApiException as e:
            self.handle_api_exception(e, f"delete subnet {resource_id}")
    
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
                self.result['msg'] = f"subnet not found"
        
        self.exit_json()


def main():
    """Main module execution."""
    argument_spec = get_common_argument_spec()
    argument_spec.update({
        'name': {'type': 'str', 'required': True},
        'id': {'type': 'str', 'required': False},
        'vpc': {'type': 'str', 'required': False},
        'zone': {'type': 'str', 'required': False},
        'ipv4_cidr_block': {'type': 'str', 'required': False},
        'network_acl': {'type': 'str', 'required': False},
        'public_gateway': {'type': 'str', 'required': False},
        'routing_table': {'type': 'str', 'required': False},
        'resource_group': {'type': 'str', 'required': False}
    })
    
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True
    )
    
    resource_module = IBMSubnetModule(module)
    resource_module.run()


if __name__ == '__main__':
    main()

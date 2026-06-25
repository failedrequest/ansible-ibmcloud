#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, IBM Cloud Team
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r'''
---
module: ibm_is_address_prefix
short_description: Manage IBM Cloud Address Prefix
version_added: "1.0.0"
description:
    - Create, update, or delete IBM Cloud Address Prefix
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
    name:
        description:
            - Name
        type: str
        required: false
    is_default:
        description:
            - Is Default
        type: str
        required: false
author:
    - IBM Cloud Team
'''

EXAMPLES = r'''
- name: Create Address Prefix
  ibm_is_address_prefix:
    name: my-address_prefix
    state: present

- name: Delete Address Prefix
  ibm_is_address_prefix:
    id: resource-id-123
    state: absent

'''

RETURN = r'''
resource:
    description: Address Prefix information
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


class IBMAddressPrefixModule(IBMCloudSDKModule):
    """IBM Cloud Address Prefix module implementation."""
    
    def __init__(self, module):
        """Initialize the module."""
        super().__init__(module)
        
        if not HAS_IBM_VPC:
            self.fail_json(msg="ibm-vpc Python SDK is required")
        
        self.vpc_service = VpcV1(authenticator=self.auth.get_authenticator())
        self.vpc_service.set_service_url(f'https://{self.region}.iaas.cloud.ibm.com/v1')
        
        self.resource_id = self.params.get('id')
        self.resource_name = self.params.get('name')
    
    def get_resource(self, vpc_id: str, resource_id: str):
        """Get resource by ID."""
        try:
            response = self.vpc_service.get_vpc_address_prefix(
                vpc_id=vpc_id,
                id=resource_id
            )
            return response.get_result()
        except ApiException as e:
            if e.code == 404:
                return None
            self.handle_api_exception(e, f"retrieve address_prefix {resource_id}")
    
    def list_resources(self, vpc_id: str):
        """List all resources for a VPC."""
        try:
            response = self.vpc_service.list_vpc_address_prefixes(vpc_id=vpc_id)
            return response.get_result().get('address_prefixes', [])
        except ApiException as e:
            self.handle_api_exception(e, f"list address_prefixes for VPC {vpc_id}")
    
    def create_resource(self):
        """Create a new resource."""
        self.check_mode_exit(changed=True, msg=f"Would create address_prefix: {self.resource_name}")
        
        try:
            from ibm_vpc.vpc_v1 import ZoneIdentityByName
            
            vpc_id = self.params.get('vpc')
            zone_name = self.params.get('zone')
            cidr = self.params.get('cidr')
            
            if not vpc_id:
                self.fail_json(msg="vpc parameter is required for creating address prefix")
            if not zone_name:
                self.fail_json(msg="zone parameter is required for creating address prefix")
            if not cidr:
                self.fail_json(msg="cidr parameter is required for creating address prefix")
            
            zone_identity = ZoneIdentityByName(name=zone_name)
            
            response = self.vpc_service.create_vpc_address_prefix(
                vpc_id=vpc_id,
                cidr=cidr,
                zone=zone_identity,
                name=self.resource_name,
                is_default=self.params.get('is_default')
            )
            resource = response.get_result()
            
            self.result['changed'] = True
            self.result['resource'] = resource
            self.result['msg'] = f"address_prefix {self.resource_name} created successfully"
            
        except ApiException as e:
            self.handle_api_exception(e, f"create address_prefix {self.resource_name}")
    
    def update_resource(self, vpc_id: str, resource):
        """Update an existing resource."""
        changed = False
        updates = {}
        
        if self.resource_name and resource.get('name') != self.resource_name:
            updates['name'] = self.resource_name
            changed = True
        
        is_default = self.params.get('is_default')
        if is_default is not None and resource.get('is_default') != is_default:
            updates['is_default'] = is_default
            changed = True
        
        if updates:
            self.check_mode_exit(changed=True, msg=f"Would update address_prefix: {resource['id']}")
            
            try:
                response = self.vpc_service.update_vpc_address_prefix(
                    vpc_id=vpc_id,
                    id=resource['id'],
                    address_prefix_patch=updates
                )
                resource = response.get_result()
                changed = True
            except ApiException as e:
                self.handle_api_exception(e, f"update address_prefix {resource['id']}")
        
        self.result['changed'] = changed
        self.result['resource'] = resource
        self.result['msg'] = f"address_prefix {resource['name']} " + ("updated" if changed else "unchanged")
    
    def delete_resource(self, vpc_id: str, resource_id: str):
        """Delete a resource."""
        self.check_mode_exit(changed=True, msg=f"Would delete address_prefix: {resource_id}")
        
        try:
            self.vpc_service.delete_vpc_address_prefix(
                vpc_id=vpc_id,
                id=resource_id
            )
            self.result['changed'] = True
            self.result['msg'] = f"address_prefix {resource_id} deleted successfully"
        except ApiException as e:
            self.handle_api_exception(e, f"delete address_prefix {resource_id}")
    
    def run(self):
        """Execute the module logic."""
        vpc_id = self.params.get('vpc')
        
        existing_resource = None
        if self.resource_id and vpc_id:
            existing_resource = self.get_resource(vpc_id, self.resource_id)
        elif self.resource_name and vpc_id:
            resources = self.list_resources(vpc_id)
            for res in resources:
                if res.get('name') == self.resource_name:
                    existing_resource = res
                    break
        
        if self.state == 'present':
            if existing_resource:
                self.update_resource(vpc_id, existing_resource)
            else:
                self.create_resource()
        
        elif self.state == 'absent':
            if existing_resource:
                self.delete_resource(vpc_id, existing_resource['id'])
            else:
                self.result['msg'] = f"address_prefix not found"
        
        self.exit_json()


def main():
    """Main module execution."""
    argument_spec = get_common_argument_spec()
    argument_spec.update({
        'name': {'type': 'str', 'required': True},
        'id': {'type': 'str', 'required': False},
        'vpc': {'type': 'str', 'required': False},
        'zone': {'type': 'str', 'required': False},
        'cidr': {'type': 'str', 'required': False},
        'is_default': {'type': 'bool', 'required': False}
    })
    
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True
    )
    
    resource_module = IBMAddressPrefixModule(module)
    resource_module.run()


if __name__ == '__main__':
    main()

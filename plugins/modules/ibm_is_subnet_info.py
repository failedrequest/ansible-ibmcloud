#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, IBM Cloud Team
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r'''
---
module: ibm_is_subnet_info
short_description: Retrieve information about IBM Cloud VPC subnet resources
version_added: "1.0.0"
description:
    - Retrieve information about IBM Cloud VPC subnet resources
    - This is a read-only info module that does not modify resources
    - Can retrieve a specific subnet by ID or name, or list all subnets
    - Optionally filter subnets by VPC
requirements:
    - ibm-vpc >= 0.33.0
    - ibm-cloud-sdk-core >= 3.20.0
options:
    name:
        description:
            - Name of the subnet to retrieve
            - Mutually exclusive with id
        type: str
        required: false
    id:
        description:
            - ID of the subnet to retrieve
            - Mutually exclusive with name
        type: str
        required: false
    vpc:
        description:
            - VPC ID or name to filter subnets
            - Only used when listing all subnets (no name or id specified)
        type: str
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
author:
    - IBM Cloud Team
'''

EXAMPLES = r'''
- name: Get information about a specific subnet by name
  ibm_is_subnet_info:
    name: my-subnet
    region: us-south
  register: subnet_info

- name: Get information about a specific subnet by ID
  ibm_is_subnet_info:
    id: 0717-12345678-1234-1234-1234-123456789012
    region: us-south
  register: subnet_info

- name: List all subnets in a region
  ibm_is_subnet_info:
    region: us-south
  register: all_subnets

- name: List all subnets in a specific VPC
  ibm_is_subnet_info:
    vpc: my-vpc
    region: us-south
  register: vpc_subnets

- name: Use subnet info in subsequent tasks
  ibm_is_virtual_network_interface:
    name: my-vni
    subnet: "{{ subnet_info.resource.id }}"
    state: present
'''

RETURN = r'''
resource:
    description: Subnet resource information (when querying by name or id)
    returned: when name or id is specified
    type: dict
    contains:
        id:
            description: Subnet ID
            type: str
            sample: "0717-12345678-1234-1234-1234-123456789012"
        name:
            description: Subnet name
            type: str
            sample: "my-subnet"
        crn:
            description: Cloud Resource Name
            type: str
            sample: "crn:v1:bluemix:public:is:us-south-1:a/123456::subnet:0717-12345678"
        status:
            description: Subnet status
            type: str
            sample: "available"
        created_at:
            description: Creation timestamp
            type: str
            sample: "2024-01-15T10:30:00.000Z"
        vpc:
            description: VPC information
            type: dict
            contains:
                id:
                    description: VPC ID
                    type: str
                name:
                    description: VPC name
                    type: str
        zone:
            description: Zone information
            type: dict
        ipv4_cidr_block:
            description: IPv4 CIDR block
            type: str
            sample: "10.240.0.0/24"
        available_ipv4_address_count:
            description: Number of available IPv4 addresses
            type: int
        total_ipv4_address_count:
            description: Total number of IPv4 addresses
            type: int
        network_acl:
            description: Network ACL information
            type: dict
        public_gateway:
            description: Public gateway information
            type: dict
        resource_group:
            description: Resource group information
            type: dict
resources:
    description: List of all subnet resources (when listing all)
    returned: when neither name nor id is specified
    type: list
    elements: dict
found:
    description: Whether the resource was found
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


class IBMSubnetInfoModule(IBMCloudSDKModule):
    """IBM Cloud Subnet info module implementation."""
    
    def __init__(self, module):
        """Initialize the module."""
        super().__init__(module)
        
        if not HAS_IBM_VPC:
            self.fail_json(msg="ibm-vpc Python SDK is required")
        
        self.vpc_service = VpcV1(authenticator=self.auth.get_authenticator())
        self.vpc_service.set_service_url(f'https://{self.region}.iaas.cloud.ibm.com/v1')
        
        self.resource_id = self.params.get('id')
        self.resource_name = self.params.get('name')
        self.vpc_filter = self.params.get('vpc')
    
    def get_resource_by_id(self, resource_id: str):
        """Get subnet by ID."""
        try:
            response = self.vpc_service.get_subnet(id=resource_id)
            return response.get_result()
        except ApiException as e:
            if e.code == 404:
                return None
            self.handle_api_exception(e, f"retrieve subnet {resource_id}")
    
    def get_vpc_id_by_name(self, vpc_name: str):
        """Get VPC ID by name."""
        try:
            response = self.vpc_service.list_vpcs()
            vpcs = response.get_result().get('vpcs', [])
            
            for vpc in vpcs:
                if vpc.get('name') == vpc_name:
                    return vpc.get('id')
            
            return None
        except ApiException as e:
            self.handle_api_exception(e, f"list VPCs to find {vpc_name}")
    
    def get_resource_by_name(self, resource_name: str):
        """Get subnet by name."""
        try:
            response = self.vpc_service.list_subnets()
            subnets = response.get_result().get('subnets', [])
            
            for subnet in subnets:
                if subnet.get('name') == resource_name:
                    return subnet
            
            return None
        except ApiException as e:
            self.handle_api_exception(e, f"list subnets to find {resource_name}")
    
    def list_all_resources(self, vpc_id: str = None):
        """List all subnets, optionally filtered by VPC."""
        try:
            response = self.vpc_service.list_subnets()
            subnets = response.get_result().get('subnets', [])
            
            # Filter by VPC if specified
            if vpc_id:
                subnets = [s for s in subnets if s.get('vpc', {}).get('id') == vpc_id]
            
            return subnets
        except ApiException as e:
            self.handle_api_exception(e, "list subnets")
    
    def run(self):
        """Execute the module logic."""
        # If both name and id are provided, fail
        if self.resource_id and self.resource_name:
            self.fail_json(msg="Parameters 'id' and 'name' are mutually exclusive")
        
        # Get specific subnet by ID
        if self.resource_id:
            resource = self.get_resource_by_id(self.resource_id)
            if resource:
                self.result['resource'] = resource
                self.result['found'] = True
                self.result['msg'] = f"Subnet {self.resource_id} found"
            else:
                self.result['found'] = False
                self.result['msg'] = f"Subnet {self.resource_id} not found"
        
        # Get specific subnet by name
        elif self.resource_name:
            resource = self.get_resource_by_name(self.resource_name)
            if resource:
                self.result['resource'] = resource
                self.result['found'] = True
                self.result['msg'] = f"Subnet '{self.resource_name}' found"
            else:
                self.result['found'] = False
                self.result['msg'] = f"Subnet '{self.resource_name}' not found"
        
        # List all subnets (optionally filtered by VPC)
        else:
            vpc_id = None
            
            # If VPC filter is specified, resolve it
            if self.vpc_filter:
                # Check if it's a VPC ID (starts with 'r006-' or similar)
                if self.vpc_filter.startswith('r0'):
                    vpc_id = self.vpc_filter
                else:
                    # Assume it's a VPC name, look it up
                    vpc_id = self.get_vpc_id_by_name(self.vpc_filter)
                    if not vpc_id:
                        self.fail_json(msg=f"VPC '{self.vpc_filter}' not found")
            
            resources = self.list_all_resources(vpc_id)
            self.result['resources'] = resources
            self.result['found'] = len(resources) > 0
            
            if vpc_id:
                self.result['msg'] = f"Found {len(resources)} subnet(s) in VPC {self.vpc_filter}"
            else:
                self.result['msg'] = f"Found {len(resources)} subnet(s)"
        
        self.exit_json()


def main():
    """Main module execution."""
    argument_spec = get_common_argument_spec()
    argument_spec.update({
        'name': {'type': 'str', 'required': False},
        'id': {'type': 'str', 'required': False},
        'vpc': {'type': 'str', 'required': False}
    })
    
    # Remove state parameter as this is an info module
    if 'state' in argument_spec:
        del argument_spec['state']
    
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        mutually_exclusive=[['name', 'id']]
    )
    
    info_module = IBMSubnetInfoModule(module)
    info_module.run()


if __name__ == '__main__':
    main()

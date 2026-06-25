#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, IBM Cloud Team
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r'''
---
module: ibm_is_virtual_network_interface_info
short_description: Retrieve information about IBM Cloud Virtual Network Interface resources
version_added: "1.0.0"
description:
    - Retrieve information about IBM Cloud Virtual Network Interface (VNI) resources
    - This is a read-only info module that does not modify resources
    - Can retrieve a specific VNI by ID or name, or list all VNIs
requirements:
    - ibm-vpc >= 0.33.0
    - ibm-cloud-sdk-core >= 3.20.0
options:
    name:
        description:
            - Name of the VNI to retrieve
            - Mutually exclusive with id
        type: str
        required: false
    id:
        description:
            - ID of the VNI to retrieve
            - Mutually exclusive with name
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
- name: Get information about a specific VNI by name
  ibm_is_virtual_network_interface_info:
    name: my-vni
    region: us-south
  register: vni_info

- name: Get information about a specific VNI by ID
  ibm_is_virtual_network_interface_info:
    id: r006-12345678-1234-1234-1234-123456789012
    region: us-south
  register: vni_info

- name: List all VNIs in a region
  ibm_is_virtual_network_interface_info:
    region: us-south
  register: all_vnis

- name: Use VNI info in subsequent tasks
  ibm_ks_cluster_vni:
    cluster: my-cluster
    vni_id: "{{ vni_info.resource.id }}"
    vni_subnet_id: "{{ vni_info.resource.subnet.id }}"
    state: present
'''

RETURN = r'''
resource:
    description: VNI resource information (when querying by name or id)
    returned: when name or id is specified
    type: dict
    contains:
        id:
            description: VNI ID
            type: str
            sample: "r006-12345678-1234-1234-1234-123456789012"
        name:
            description: VNI name
            type: str
            sample: "my-vni"
        crn:
            description: Cloud Resource Name
            type: str
        created_at:
            description: Creation timestamp
            type: str
            sample: "2024-01-15T10:30:00.000Z"
        subnet:
            description: Subnet information
            type: dict
            contains:
                id:
                    description: Subnet ID
                    type: str
                name:
                    description: Subnet name
                    type: str
        primary_ip:
            description: Primary IP information
            type: dict
            contains:
                address:
                    description: IP address
                    type: str
                    sample: "10.240.0.150"
                name:
                    description: Reserved IP name
                    type: str
        enable_infrastructure_nat:
            description: Infrastructure NAT enabled
            type: bool
        security_groups:
            description: Security groups
            type: list
        resource_group:
            description: Resource group information
            type: dict
resources:
    description: List of all VNI resources (when listing all)
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


class IBMVirtualNetworkInterfaceInfoModule(IBMCloudSDKModule):
    """IBM Cloud Virtual Network Interface info module implementation."""
    
    def __init__(self, module):
        """Initialize the module."""
        super().__init__(module)
        
        if not HAS_IBM_VPC:
            self.fail_json(msg="ibm-vpc Python SDK is required")
        
        self.vpc_service = VpcV1(authenticator=self.auth.get_authenticator())
        self.vpc_service.set_service_url(f'https://{self.region}.iaas.cloud.ibm.com/v1')
        
        self.resource_id = self.params.get('id')
        self.resource_name = self.params.get('name')
    
    def get_resource_by_id(self, resource_id: str):
        """Get VNI by ID."""
        try:
            response = self.vpc_service.get_virtual_network_interface(id=resource_id)
            return response.get_result()
        except ApiException as e:
            if e.code == 404:
                return None
            self.handle_api_exception(e, f"retrieve virtual network interface {resource_id}")
    
    def get_resource_by_name(self, resource_name: str):
        """Get VNI by name."""
        try:
            response = self.vpc_service.list_virtual_network_interfaces()
            vnis = response.get_result().get('virtual_network_interfaces', [])
            
            for vni in vnis:
                if vni.get('name') == resource_name:
                    return vni
            
            return None
        except ApiException as e:
            self.handle_api_exception(e, f"list virtual network interfaces to find {resource_name}")
    
    def list_all_resources(self):
        """List all VNIs."""
        try:
            response = self.vpc_service.list_virtual_network_interfaces()
            return response.get_result().get('virtual_network_interfaces', [])
        except ApiException as e:
            self.handle_api_exception(e, "list virtual network interfaces")
    
    def run(self):
        """Execute the module logic."""
        # If both name and id are provided, fail
        if self.resource_id and self.resource_name:
            self.fail_json(msg="Parameters 'id' and 'name' are mutually exclusive")
        
        # Get specific VNI by ID
        if self.resource_id:
            resource = self.get_resource_by_id(self.resource_id)
            if resource:
                self.result['resource'] = resource
                self.result['found'] = True
                self.result['msg'] = f"Virtual network interface {self.resource_id} found"
            else:
                self.result['found'] = False
                self.result['msg'] = f"Virtual network interface {self.resource_id} not found"
        
        # Get specific VNI by name
        elif self.resource_name:
            resource = self.get_resource_by_name(self.resource_name)
            if resource:
                self.result['resource'] = resource
                self.result['found'] = True
                self.result['msg'] = f"Virtual network interface '{self.resource_name}' found"
            else:
                self.result['found'] = False
                self.result['msg'] = f"Virtual network interface '{self.resource_name}' not found"
        
        # List all VNIs
        else:
            resources = self.list_all_resources()
            self.result['resources'] = resources
            self.result['found'] = len(resources) > 0
            self.result['msg'] = f"Found {len(resources)} virtual network interface(s)"
        
        self.exit_json()


def main():
    """Main module execution."""
    argument_spec = get_common_argument_spec()
    argument_spec.update({
        'name': {'type': 'str', 'required': False},
        'id': {'type': 'str', 'required': False}
    })
    
    # Remove state parameter as this is an info module
    if 'state' in argument_spec:
        del argument_spec['state']
    
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        mutually_exclusive=[['name', 'id']]
    )
    
    info_module = IBMVirtualNetworkInterfaceInfoModule(module)
    info_module.run()


if __name__ == '__main__':
    main()

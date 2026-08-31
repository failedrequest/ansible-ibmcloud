#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, IBM Cloud Team
# BSD 2-Clause License (see LICENSE or https://opensource.org/licenses/BSD-2-Clause)

DOCUMENTATION = r'''
---
module: ibm_is_subnet_reserved_ip_info
short_description: List reserved IPs within an IBM Cloud VPC subnet
version_added: "1.0.0"
description:
    - List reserved IPs within an IBM Cloud VPC subnet.
    - This is a read-only info module that does not modify resources.
    - Optionally filter by owner type (user or provider).
requirements:
    - ibm-vpc >= 0.33.0
    - ibm-cloud-sdk-core >= 3.20.0
options:
    subnet_id:
        description:
            - ID of the subnet to query.
        type: str
        required: true
    owner:
        description:
            - Filter by owner type.
            - C(user) — only user-created reserved IPs (safe to bind to a VNI).
            - C(provider) — only provider-managed IPs (gateway, etc.).
            - Omit to return all reserved IPs.
        type: str
        required: false
        choices: ['user', 'provider']
    ibmcloud_api_key:
        description:
            - IBM Cloud API key.
            - Can also be set via IC_API_KEY or IBMCLOUD_API_KEY environment variable.
        type: str
        required: false
        no_log: true
    region:
        description:
            - IBM Cloud region.
        type: str
        default: 'us-south'
        choices: ['us-south', 'us-east', 'eu-gb', 'eu-de', 'jp-tok', 'au-syd', 'jp-osa', 'ca-tor', 'br-sao']
author:
    - IBM Cloud Team
'''

EXAMPLES = r'''
- name: List all reserved IPs in a subnet
  ibm_is_subnet_reserved_ip_info:
    subnet_id: 0717-aabbccdd-1234-1234-1234-aabbccddeeff
    region: us-south
  register: all_rips

- name: List only user-owned reserved IPs (safe to bind to VNIs)
  ibm_is_subnet_reserved_ip_info:
    subnet_id: 0717-aabbccdd-1234-1234-1234-aabbccddeeff
    owner: user
    region: us-south
  register: user_rips

- name: Build a map of reserved IP name -> ID
  set_fact:
    rip_id_map: "{{ user_rips.resources | items2dict(key_name='name', value_name='id') }}"
'''

RETURN = r'''
resources:
    description: List of reserved IP resources.
    returned: always
    type: list
    elements: dict
    contains:
        id:
            description: Reserved IP ID.
            type: str
            sample: "0717-11223344-aaaa-bbbb-cccc-112233445566"
        name:
            description: Reserved IP name.
            type: str
            sample: "my-reserved-ip"
        address:
            description: The reserved IP address.
            type: str
            sample: "10.240.0.10"
        owner:
            description: The owner of the reserved IP (user or provider).
            type: str
            sample: "user"
        auto_delete:
            description: Whether the reserved IP is automatically deleted with its target.
            type: bool
        lifecycle_state:
            description: Lifecycle state of the reserved IP.
            type: str
            sample: "stable"
        target:
            description: The target this reserved IP is bound to.
            type: dict
found:
    description: Whether any resources were found.
    returned: always
    type: bool
msg:
    description: Status message.
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


class IBMSubnetReservedIPInfoModule(IBMCloudSDKModule):
    """IBM Cloud VPC Subnet Reserved IP info module implementation."""

    def __init__(self, module):
        """Initialize the module."""
        super().__init__(module)

        if not HAS_IBM_VPC:
            self.fail_json(msg="ibm-vpc Python SDK is required")

        self.vpc_service = VpcV1(authenticator=self.auth.get_authenticator())
        self.vpc_service.set_service_url(f'https://{self.region}.iaas.cloud.ibm.com/v1')

        self.subnet_id = self.params.get('subnet_id')

    def list_resources(self):
        """List reserved IPs in the subnet, optionally filtered by owner."""
        try:
            response = self.vpc_service.list_subnet_reserved_ips(subnet_id=self.subnet_id)
            rips = response.get_result().get('reserved_ips', [])
            owner_filter = self.params.get('owner')
            if owner_filter:
                rips = [r for r in rips if r.get('owner') == owner_filter]
            return rips
        except ApiException as e:
            self.handle_api_exception(e, f"list reserved IPs in subnet {self.subnet_id}")
            return None

    def run(self):
        """Execute the module logic."""
        resources = self.list_resources()
        self.result['resources'] = resources
        self.result['found'] = len(resources) > 0

        owner_filter = self.params.get('owner')
        if owner_filter:
            self.result['msg'] = (
                f"Found {len(resources)} reserved IP(s) with owner='{owner_filter}'"
                f" in subnet {self.subnet_id}"
            )
        else:
            self.result['msg'] = f"Found {len(resources)} reserved IP(s) in subnet {self.subnet_id}"

        self.exit_json()


def main():
    """Main module execution."""
    argument_spec = get_common_argument_spec()
    argument_spec.update({
        'subnet_id': {'type': 'str', 'required': True},
        'owner': {'type': 'str', 'required': False, 'choices': ['user', 'provider']},
    })

    # Remove state parameter as this is an info module
    if 'state' in argument_spec:
        del argument_spec['state']

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True
    )

    info_module = IBMSubnetReservedIPInfoModule(module)
    info_module.run()


if __name__ == '__main__':
    main()

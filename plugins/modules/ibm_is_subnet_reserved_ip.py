#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, IBM Cloud Team
# BSD 2-Clause License (see LICENSE or https://opensource.org/licenses/BSD-2-Clause)

DOCUMENTATION = r'''
---
module: ibm_is_subnet_reserved_ip
short_description: Manage IBM Cloud VPC Subnet Reserved IPs
version_added: "2.0.5"
description:
    - Create, update, or delete a reserved IP within an IBM Cloud VPC subnet
    - This module uses the native IBM Cloud Python SDK (no Terraform dependency)
    - Supports idempotent operations
    - Reserved IPs are scoped to a subnet; C(subnet_id) is always required
requirements:
    - ibm-vpc >= 0.33.0
    - ibm-cloud-sdk-core >= 3.20.0
options:
    subnet_id:
        description:
            - ID of the subnet that the reserved IP belongs to
        type: str
        required: true
    name:
        description:
            - Name of the reserved IP
            - Used to look up an existing reserved IP when C(id) is not provided
        type: str
        required: false
    id:
        description:
            - ID of the reserved IP
            - When provided, the module operates directly on this resource
        type: str
        required: false
    address:
        description:
            - The IP address to reserve within the subnet CIDR
            - If not provided IBM Cloud assigns a free address automatically
        type: str
        required: false
    auto_delete:
        description:
            - Whether the reserved IP is automatically deleted when the target it is bound
              to is deleted
            - Defaults to C(true) when the reserved IP is bound to a target; C(false) otherwise
        type: bool
        required: false
    target:
        description:
            - ID of the target resource to bind the reserved IP to (e.g. a virtual network
              interface or an endpoint gateway IP)
        type: str
        required: false
author:
    - IBM Cloud Team
'''

EXAMPLES = r'''
- name: Reserve a specific IP address in a subnet
  ibm_is_subnet_reserved_ip:
    subnet_id: 0717-aabbccdd-1234-1234-1234-aabbccddeeff
    name: my-reserved-ip
    address: 10.240.0.10
    state: present

- name: Reserve an automatically assigned IP address
  ibm_is_subnet_reserved_ip:
    subnet_id: 0717-aabbccdd-1234-1234-1234-aabbccddeeff
    name: my-auto-reserved-ip
    state: present

- name: Update the name of an existing reserved IP
  ibm_is_subnet_reserved_ip:
    subnet_id: 0717-aabbccdd-1234-1234-1234-aabbccddeeff
    id: 0717-11223344-aaaa-bbbb-cccc-112233445566
    name: my-renamed-reserved-ip
    state: present

- name: Delete a reserved IP by ID
  ibm_is_subnet_reserved_ip:
    subnet_id: 0717-aabbccdd-1234-1234-1234-aabbccddeeff
    id: 0717-11223344-aaaa-bbbb-cccc-112233445566
    state: absent

- name: Delete a reserved IP by name
  ibm_is_subnet_reserved_ip:
    subnet_id: 0717-aabbccdd-1234-1234-1234-aabbccddeeff
    name: my-reserved-ip
    state: absent
'''

RETURN = r'''
resource:
    description: Reserved IP resource information
    returned: always
    type: dict
    contains:
        id:
            description: Reserved IP ID
            type: str
            sample: "0717-11223344-aaaa-bbbb-cccc-112233445566"
        name:
            description: Reserved IP name
            type: str
            sample: "my-reserved-ip"
        address:
            description: The reserved IP address
            type: str
            sample: "10.240.0.10"
        auto_delete:
            description: Whether the reserved IP is automatically deleted with its target
            type: bool
        created_at:
            description: Creation timestamp
            type: str
        href:
            description: The URL for this reserved IP
            type: str
        lifecycle_state:
            description: The lifecycle state of the reserved IP
            type: str
            sample: "stable"
        owner:
            description: The owner of the reserved IP
            type: str
            sample: "user"
        resource_type:
            description: The resource type
            type: str
            sample: "subnet_reserved_ip"
        target:
            description: The target this reserved IP is bound to
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


class IBMSubnetReservedIPModule(IBMCloudSDKModule):
    """IBM Cloud VPC Subnet Reserved IP module implementation."""

    def __init__(self, module):
        """Initialize the module."""
        super().__init__(module)

        if not HAS_IBM_VPC:
            self.fail_json(msg="ibm-vpc Python SDK is required")

        self.vpc_service = VpcV1(authenticator=self.auth.get_authenticator())
        self.vpc_service.set_service_url(f'https://{self.region}.iaas.cloud.ibm.com/v1')

        self.subnet_id = self.params.get('subnet_id')
        self.resource_id = self.params.get('id')
        self.resource_name = self.params.get('name')

    def get_resource(self, resource_id: str):
        """Get a reserved IP by ID."""
        try:
            response = self.vpc_service.get_subnet_reserved_ip(
                subnet_id=self.subnet_id,
                id=resource_id
            )
            return response.get_result()
        except ApiException as e:
            if e.code == 404:
                return None
            self.handle_api_exception(e, f"retrieve reserved IP {resource_id}")

    def list_resources(self):
        """List all reserved IPs in the subnet."""
        try:
            response = self.vpc_service.list_subnet_reserved_ips(subnet_id=self.subnet_id)
            return response.get_result().get('reserved_ips', [])
        except ApiException as e:
            self.handle_api_exception(e, f"list reserved IPs in subnet {self.subnet_id}")

    def create_resource(self):
        """Create a new reserved IP."""
        self.check_mode_exit(
            changed=True,
            msg=f"Would create reserved IP '{self.resource_name}' in subnet {self.subnet_id}"
        )

        kwargs = {}
        if self.resource_name:
            kwargs['name'] = self.resource_name
        if self.params.get('address'):
            kwargs['address'] = self.params['address']
        if self.params.get('auto_delete') is not None:
            kwargs['auto_delete'] = self.params['auto_delete']
        if self.params.get('target'):
            kwargs['target'] = {'id': self.params['target']}

        try:
            response = self.vpc_service.create_subnet_reserved_ip(
                subnet_id=self.subnet_id,
                **kwargs
            )
            resource = response.get_result()

            self.result['changed'] = True
            self.result['resource'] = resource
            self.result['msg'] = (
                f"Reserved IP '{resource.get('name', resource['id'])}' created successfully"
                f" in subnet {self.subnet_id}"
            )
        except ApiException as e:
            self.handle_api_exception(
                e, f"create reserved IP in subnet {self.subnet_id}"
            )

    def update_resource(self, resource):
        """Update an existing reserved IP."""
        changed = False
        updates = {}

        if self.resource_name and resource.get('name') != self.resource_name:
            updates['name'] = self.resource_name
            changed = True

        if self.params.get('auto_delete') is not None and \
                resource.get('auto_delete') != self.params['auto_delete']:
            updates['auto_delete'] = self.params['auto_delete']
            changed = True

        if updates:
            self.check_mode_exit(
                changed=True,
                msg=f"Would update reserved IP {resource['id']}"
            )

            try:
                response = self.vpc_service.update_subnet_reserved_ip(
                    subnet_id=self.subnet_id,
                    id=resource['id'],
                    reserved_ip_patch=updates
                )
                resource = response.get_result()
            except ApiException as e:
                self.handle_api_exception(e, f"update reserved IP {resource['id']}")

        self.result['changed'] = changed
        self.result['resource'] = resource
        self.result['msg'] = (
            f"Reserved IP '{resource.get('name', resource['id'])}' "
            + ("updated" if changed else "unchanged")
        )

    def delete_resource(self, resource_id: str):
        """Delete a reserved IP."""
        self.check_mode_exit(
            changed=True,
            msg=f"Would delete reserved IP {resource_id} from subnet {self.subnet_id}"
        )

        try:
            self.vpc_service.delete_subnet_reserved_ip(
                subnet_id=self.subnet_id,
                id=resource_id
            )
            self.result['changed'] = True
            self.result['msg'] = f"Reserved IP {resource_id} deleted successfully"
        except ApiException as e:
            self.handle_api_exception(e, f"delete reserved IP {resource_id}")

    def run(self):
        """Execute the module logic."""
        existing_resource = None

        if self.resource_id:
            existing_resource = self.get_resource(self.resource_id)
        elif self.resource_name:
            reserved_ips = self.list_resources()
            for rip in reserved_ips:
                if rip.get('name') == self.resource_name:
                    existing_resource = rip
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
                self.result['msg'] = "Reserved IP not found"

        self.exit_json()


def main():
    """Main module execution."""
    argument_spec = get_common_argument_spec()
    argument_spec.update({
        'subnet_id': {'type': 'str', 'required': True},
        'name': {'type': 'str', 'required': False},
        'id': {'type': 'str', 'required': False},
        'address': {'type': 'str', 'required': False},
        'auto_delete': {'type': 'bool', 'required': False},
        'target': {'type': 'str', 'required': False},
    })

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_one_of=[['name', 'id']]
    )

    resource_module = IBMSubnetReservedIPModule(module)
    resource_module.run()


if __name__ == '__main__':
    main()

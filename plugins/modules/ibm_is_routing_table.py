#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, IBM Cloud Team
# BSD 2-Clause License (see LICENSE or https://opensource.org/licenses/BSD-2-Clause)

DOCUMENTATION = r'''
---
module: ibm_is_routing_table
short_description: Manage IBM Cloud VPC Routing Tables
version_added: "1.0.0"
description:
    - Create, update, or delete a routing table within an IBM Cloud VPC
    - This module uses the native IBM Cloud Python SDK (no Terraform dependency)
    - Supports idempotent operations
requirements:
    - ibm-vpc >= 0.33.0
    - ibm-cloud-sdk-core >= 3.20.0
options:
    vpc_id:
        description:
            - ID of the VPC that owns this routing table
            - Required for all operations
        type: str
        required: true
    name:
        description:
            - Name of the routing table
            - Used to look up an existing routing table when id is not provided
        type: str
        required: false
    id:
        description:
            - ID of the routing table
            - When provided, the module operates directly on this resource
        type: str
        required: false
    route_direct_link_ingress:
        description:
            - Whether this routing table is used to route traffic that originates
              from Direct Link to this VPC
        type: bool
        required: false
    route_transit_gateway_ingress:
        description:
            - Whether this routing table is used to route traffic that originates
              from Transit Gateway to this VPC
        type: bool
        required: false
    route_vpc_zone_ingress:
        description:
            - Whether this routing table is used to route traffic that originates
              from subnets in other zones in this VPC
        type: bool
        required: false
author:
    - IBM Cloud Team
'''

EXAMPLES = r'''
- name: Create a custom routing table in a VPC
  ibm_is_routing_table:
    vpc_id: "r006-12345678-1234-1234-1234-123456789012"
    name: my-custom-rt
    state: present
  register: rt

- name: Delete a routing table by ID
  ibm_is_routing_table:
    vpc_id: "r006-12345678-1234-1234-1234-123456789012"
    id: "{{ rt.resource.id }}"
    state: absent
'''

RETURN = r'''
resource:
    description: Routing table resource information
    returned: when state is present
    type: dict
    contains:
        id:
            description: Routing table ID
            type: str
        name:
            description: Routing table name
            type: str
        is_default:
            description: Whether this is the VPC default routing table
            type: bool
        lifecycle_state:
            description: Lifecycle state of the routing table
            type: str
changed:
    description: Whether the resource was changed
    returned: always
    type: bool
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


class IBMRoutingTableModule(IBMCloudSDKModule):
    """IBM Cloud VPC Routing Table module implementation."""

    def __init__(self, module):
        super().__init__(module)

        if not HAS_IBM_VPC:
            self.fail_json(msg="ibm-vpc Python SDK is required")

        self.vpc_service = VpcV1(authenticator=self.auth.get_authenticator())
        self.vpc_service.set_service_url(self.vpc_url)

        self.vpc_id = self.params.get('vpc_id')
        self.resource_id = self.params.get('id')
        self.resource_name = self.params.get('name')

    def get_resource(self, resource_id: str):
        """Get routing table by ID."""
        try:
            response = self.vpc_service.get_vpc_routing_table(
                vpc_id=self.vpc_id,
                id=resource_id
            )
            return response.get_result()
        except ApiException as e:
            if e.code == 404:
                return None
            self.handle_api_exception(e, f"retrieve routing_table {resource_id}")
            return None

    def list_resources(self):
        """List all routing tables for this VPC."""
        try:
            response = self.vpc_service.list_vpc_routing_tables(vpc_id=self.vpc_id)
            return response.get_result().get('routing_tables', [])
        except ApiException as e:
            self.handle_api_exception(e, "list routing_tables")
            return None

    def create_resource(self):
        """Create a new routing table."""
        self.check_mode_exit(changed=True, msg=f"Would create routing_table: {self.resource_name}")

        kwargs = {'vpc_id': self.vpc_id}
        if self.resource_name:
            kwargs['name'] = self.resource_name

        for param in ('route_direct_link_ingress', 'route_transit_gateway_ingress', 'route_vpc_zone_ingress'):
            val = self.params.get(param)
            if val is not None:
                kwargs[param] = val

        try:
            response = self.vpc_service.create_vpc_routing_table(**kwargs)
            resource = response.get_result()
            self.result['changed'] = True
            self.result['found'] = True
            self.result['resource'] = resource
            self.result['msg'] = f"routing_table {self.resource_name} created successfully"
        except ApiException as e:
            self.handle_api_exception(e, f"create routing_table {self.resource_name}")

    def update_resource(self, resource):
        """Update an existing routing table."""
        changed = False
        updates = {}

        if self.resource_name and resource.get('name') != self.resource_name:
            updates['name'] = self.resource_name
            changed = True

        if updates:
            self.check_mode_exit(changed=True, msg=f"Would update routing_table: {resource['id']}")
            try:
                response = self.vpc_service.update_vpc_routing_table(
                    vpc_id=self.vpc_id,
                    id=resource['id'],
                    routing_table_patch=updates
                )
                resource = response.get_result()
            except ApiException as e:
                self.handle_api_exception(e, f"update routing_table {resource['id']}")

        self.result['changed'] = changed
        self.result['found'] = True
        self.result['resource'] = resource
        self.result['msg'] = f"routing_table {resource['name']} " + ("updated" if changed else "unchanged")

    def delete_resource(self, resource_id: str):
        """Delete a routing table."""
        self.check_mode_exit(changed=True, msg=f"Would delete routing_table: {resource_id}")
        try:
            self.vpc_service.delete_vpc_routing_table(vpc_id=self.vpc_id, id=resource_id)
            self.result['changed'] = True
            self.result['msg'] = f"routing_table {resource_id} deleted successfully"
        except ApiException as e:
            if e.code == 404:
                self.result['msg'] = f"routing_table {resource_id} already deleted"
                return
            self.handle_api_exception(e, f"delete routing_table {resource_id}")

    def run(self):
        """Execute the module logic."""
        if not self.vpc_id:
            self.fail_json(msg="vpc_id is required")

        existing_resource = None
        if self.resource_id:
            existing_resource = self.get_resource(self.resource_id)
        elif self.resource_name:
            resources = self.list_resources()
            for res in (resources or []):
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
                self.result['msg'] = "routing_table not found"

        self.exit_json()


def main():
    """Main module execution."""
    argument_spec = get_common_argument_spec()
    argument_spec.update({
        'vpc_id': {'type': 'str', 'required': True},
        'name': {'type': 'str', 'required': False},
        'id': {'type': 'str', 'required': False},
        'route_direct_link_ingress': {'type': 'bool', 'required': False},
        'route_transit_gateway_ingress': {'type': 'bool', 'required': False},
        'route_vpc_zone_ingress': {'type': 'bool', 'required': False},
    })

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_one_of=[['name', 'id']]
    )

    resource_module = IBMRoutingTableModule(module)
    resource_module.run()


if __name__ == '__main__':
    main()

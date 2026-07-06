#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, IBM Cloud Team
# BSD 2-Clause License (see LICENSE or https://opensource.org/licenses/BSD-2-Clause)

DOCUMENTATION = r'''
---
module: ibm_tg_route_report
short_description: Manage IBM Cloud Tg Route Report
version_added: "1.0.0"
description:
    - Create, update, or delete IBM Cloud Tg Route Report
    - Part of IBM Cloud Transit Gateway service
    - Uses native IBM Cloud Python SDK
requirements:
    - ibm-platform-services >= 0.50.0
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
author:
    - IBM Cloud Team
'''

EXAMPLES = r'''
- name: Create Tg Route Report
  ibm_tg_route_report:
    name: my-tg-route-report
    state: present

- name: Delete Tg Route Report
  ibm_tg_route_report:
    id: resource-id-123
    state: absent

'''

RETURN = r'''
resource:
    description: Tg Route Report information
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
    from ibm_platform_services import TransitGatewayApisV1
    from ibm_cloud_sdk_core import ApiException
    HAS_IBM_SDK = True
except ImportError:
    HAS_IBM_SDK = False


class IBMTgRouteReportModule(IBMCloudSDKModule):
    """IBM Cloud Tg Route Report module implementation."""
    
    def __init__(self, module):
        """Initialize the module."""
        super().__init__(module)
        
        if not HAS_IBM_SDK:
            self.fail_json(msg="ibm-platform-services Python SDK is required")
        
        self.service = TransitGatewayApisV1(authenticator=self.auth.get_authenticator())
        
        self.resource_id = self.params.get('id')
        self.resource_name = self.params.get('name')
    
    def get_resource(self, resource_id: str):
        """Get resource by ID."""
        try:
            response = self.service.get_transit_gateway_route_report(id=resource_id)
            return response.get_result()
        except ApiException as e:
            if e.code == 404:
                return None
            self.handle_api_exception(e, f"retrieve tg_route_report {resource_id}")
    
    def list_resources(self):
        """List all resources."""
        try:
            response = self.service.list_transit_gateway_route_reports()
            return response.get_result().get('route_reports', [])
        except ApiException as e:
            self.handle_api_exception(e, f"list tg_route_reports")
    
    def create_resource(self):
        """Create a new resource."""
        self.check_mode_exit(changed=True, msg=f"Would create tg_route_report: {self.resource_name}")
        
        try:
            prototype = {
            'name': self.resource_name
        }
            
            response = self.service.create_transit_gateway_route_report(**prototype)
            resource = response.get_result()
            
            self.result['changed'] = True
            self.result['resource'] = resource
            self.result['msg'] = f"tg_route_report {self.resource_name} created successfully"
            
        except ApiException as e:
            self.handle_api_exception(e, f"create tg_route_report {self.resource_name}")
    
    def update_resource(self, resource):
        """Update an existing resource."""
        changed = False
        updates = {}
        
        if self.resource_name and resource.get('name') != self.resource_name:
            updates['name'] = self.resource_name
            changed = True
        
        if updates and 'None' != 'None':
            self.check_mode_exit(changed=True, msg=f"Would update tg_route_report: {resource['id']}")
            
            try:
                response = self.service.None(
                    id=resource['id'],
                    **updates
                )
                resource = response.get_result()
                changed = True
            except ApiException as e:
                self.handle_api_exception(e, f"update tg_route_report {resource['id']}")
        
        self.result['changed'] = changed
        self.result['resource'] = resource
        self.result['msg'] = f"tg_route_report {resource.get('name', resource['id'])} " + ("updated" if changed else "unchanged")
    
    def delete_resource(self, resource_id: str):
        """Delete a resource."""
        self.check_mode_exit(changed=True, msg=f"Would delete tg_route_report: {resource_id}")
        
        try:
            self.service.delete_transit_gateway_route_report(id=resource_id)
            self.result['changed'] = True
            self.result['msg'] = f"tg_route_report {resource_id} deleted successfully"
        except ApiException as e:
            self.handle_api_exception(e, f"delete tg_route_report {resource_id}")
    
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
                self.result['msg'] = f"tg_route_report not found"
        
        self.exit_json()


def main():
    """Main module execution."""
    argument_spec = get_common_argument_spec()
    argument_spec.update({
        'name': {'type': 'str', 'required': True},
        'id': {'type': 'str', 'required': False}
    })
    
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True
    )
    
    resource_module = IBMTgRouteReportModule(module)
    resource_module.run()


if __name__ == '__main__':
    main()

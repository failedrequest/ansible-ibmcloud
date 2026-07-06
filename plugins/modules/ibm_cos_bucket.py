#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, IBM Cloud Team
# BSD 2-Clause License (see LICENSE or https://opensource.org/licenses/BSD-2-Clause)

DOCUMENTATION = r'''
---
module: ibm_cos_bucket
short_description: Manage IBM Cloud Cos Bucket
version_added: "1.0.0"
description:
    - Create, update, or delete IBM Cloud Cos Bucket
    - Part of IBM Cloud COS service
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
    storage_class:
        description:
            - Storage Class
        type: str
        required: false
    location_constraint:
        description:
            - Location Constraint
        type: str
        required: false
    object_versioning:
        description:
            - Object Versioning
        type: str
        required: false
author:
    - IBM Cloud Team
'''

EXAMPLES = r'''
- name: Create Cos Bucket
  ibm_cos_bucket:
    name: my-cos_bucket
    state: present

- name: Delete Cos Bucket
  ibm_cos_bucket:
    id: resource-id-123
    state: absent

'''

RETURN = r'''
resource:
    description: Cos Bucket information
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
    from ibm_platform_services import ResourceConfigurationV1
    from ibm_cloud_sdk_core import ApiException
    HAS_IBM_SDK = True
except ImportError:
    HAS_IBM_SDK = False


class IBMCosBucketModule(IBMCloudSDKModule):
    """IBM Cloud Cos Bucket module implementation."""
    
    def __init__(self, module):
        """Initialize the module."""
        super().__init__(module)
        
        if not HAS_IBM_SDK:
            self.fail_json(msg="ibm-platform-services Python SDK is required")
        
        self.service = ResourceConfigurationV1(authenticator=self.auth.get_authenticator())
        
        self.resource_id = self.params.get('id')
        self.resource_name = self.params.get('name')
    
    def get_resource(self, resource_id: str):
        """Get resource by ID."""
        try:
            response = self.service.get_bucket_config(id=resource_id)
            return response.get_result()
        except ApiException as e:
            if e.code == 404:
                return None
            self.handle_api_exception(e, f"retrieve cos_bucket {resource_id}")
    
    def list_resources(self):
        """List all resources."""
        try:
            response = self.service.list_buckets()
            return response.get_result().get('buckets', [])
        except ApiException as e:
            self.handle_api_exception(e, f"list cos_buckets")
    
    def create_resource(self):
        """Create a new resource."""
        self.check_mode_exit(changed=True, msg=f"Would create cos_bucket: {self.resource_name}")
        
        try:
            prototype = {
            'name': self.resource_name,
            'ibm_service_instance_id': self.params.get('ibm_service_instance_id')
        }
            
            response = self.service.create_bucket(**prototype)
            resource = response.get_result()
            
            self.result['changed'] = True
            self.result['resource'] = resource
            self.result['msg'] = f"cos_bucket {self.resource_name} created successfully"
            
        except ApiException as e:
            self.handle_api_exception(e, f"create cos_bucket {self.resource_name}")
    
    def update_resource(self, resource):
        """Update an existing resource."""
        changed = False
        updates = {}
        
        if self.resource_name and resource.get('name') != self.resource_name:
            updates['name'] = self.resource_name
            changed = True
        
        if updates:
            self.check_mode_exit(changed=True, msg=f"Would update cos_bucket: {resource['id']}")
            
            try:
                response = self.service.update_bucket_config(
                    id=resource['id'],
                    **updates
                )
                resource = response.get_result()
                changed = True
            except ApiException as e:
                self.handle_api_exception(e, f"update cos_bucket {resource['id']}")
        
        self.result['changed'] = changed
        self.result['resource'] = resource
        self.result['msg'] = f"cos_bucket {resource['name']} " + ("updated" if changed else "unchanged")
    
    def delete_resource(self, resource_id: str):
        """Delete a resource."""
        self.check_mode_exit(changed=True, msg=f"Would delete cos_bucket: {resource_id}")
        
        try:
            self.service.delete_bucket(id=resource_id)
            self.result['changed'] = True
            self.result['msg'] = f"cos_bucket {resource_id} deleted successfully"
        except ApiException as e:
            self.handle_api_exception(e, f"delete cos_bucket {resource_id}")
    
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
                self.result['msg'] = f"cos_bucket not found"
        
        self.exit_json()


def main():
    """Main module execution."""
    argument_spec = get_common_argument_spec()
    argument_spec.update({
        'name': {'type': 'str', 'required': True},
        'id': {'type': 'str', 'required': False},
        'storage_class': {'type': 'str', 'required': False},
        'location_constraint': {'type': 'str', 'required': False},
        'object_versioning': {'type': 'str', 'required': False}
    })
    
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True
    )
    
    resource_module = IBMCosBucketModule(module)
    resource_module.run()


if __name__ == '__main__':
    main()

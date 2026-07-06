#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, IBM Cloud Team
# BSD 2-Clause License (see LICENSE or https://opensource.org/licenses/BSD-2-Clause)

DOCUMENTATION = r'''
---
module: ibm_is_image_info
short_description: Retrieve information about IBM Cloud VPC image resources
version_added: "1.0.0"
description:
    - Retrieve information about IBM Cloud VPC image resources
    - This is a read-only info module that does not modify resources
    - Can retrieve a specific image by ID or name, or list all images
requirements:
    - ibm-vpc >= 0.33.0
    - ibm-cloud-sdk-core >= 3.20.0
options:
    name:
        description:
            - Name of the image to retrieve
            - Mutually exclusive with id
        type: str
        required: false
    id:
        description:
            - ID of the image to retrieve
            - Mutually exclusive with name
        type: str
        required: false
    visibility:
        description:
            - Filter images by visibility
        type: str
        choices: ['public', 'private']
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
- name: Get information about a specific image by name
  ibm_is_image_info:
    name: ibm-ubuntu-20-04-minimal-amd64-1
    region: us-south
  register: image_info

- name: Get information about a specific image by ID
  ibm_is_image_info:
    id: r006-12345678-1234-1234-1234-123456789012
    region: us-south
  register: image_info

- name: List all public images
  ibm_is_image_info:
    visibility: public
    region: us-south
  register: public_images

- name: Use image info in instance creation
  ibm_is_instance:
    name: my-instance
    image: "{{ image_info.resource.id }}"
    vpc: "{{ vpc_id }}"
    zone: us-south-1
    profile: bx2-2x8
    state: present
'''

RETURN = r'''
resource:
    description: Image resource information (when querying by name or id)
    returned: when name or id is specified
    type: dict
    contains:
        id:
            description: Image ID
            type: str
            sample: "r006-12345678-1234-1234-1234-123456789012"
        name:
            description: Image name
            type: str
            sample: "ibm-ubuntu-20-04-minimal-amd64-1"
        crn:
            description: Cloud Resource Name
            type: str
        status:
            description: Image status
            type: str
            sample: "available"
        visibility:
            description: Image visibility
            type: str
            sample: "public"
        operating_system:
            description: Operating system information
            type: dict
        architecture:
            description: Architecture
            type: str
            sample: "amd64"
        created_at:
            description: Creation timestamp
            type: str
resources:
    description: List of all image resources (when listing all)
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


class IBMImageInfoModule(IBMCloudSDKModule):
    """IBM Cloud Image info module implementation."""
    
    def __init__(self, module):
        """Initialize the module."""
        super().__init__(module)
        
        if not HAS_IBM_VPC:
            self.fail_json(msg="ibm-vpc Python SDK is required")
        
        self.vpc_service = VpcV1(authenticator=self.auth.get_authenticator())
        self.vpc_service.set_service_url(f'https://{self.region}.iaas.cloud.ibm.com/v1')
        
        self.resource_id = self.params.get('id')
        self.resource_name = self.params.get('name')
        self.visibility = self.params.get('visibility')
    
    def get_resource_by_id(self, resource_id: str):
        """Get image by ID."""
        try:
            response = self.vpc_service.get_image(id=resource_id)
            return response.get_result()
        except ApiException as e:
            if e.code == 404:
                return None
            self.handle_api_exception(e, f"retrieve image {resource_id}")
    
    def get_resource_by_name(self, resource_name: str):
        """Get image by name."""
        try:
            response = self.vpc_service.list_images()
            images = response.get_result().get('images', [])
            
            for image in images:
                if image.get('name') == resource_name:
                    return image
            
            return None
        except ApiException as e:
            self.handle_api_exception(e, f"list images to find {resource_name}")
    
    def list_all_resources(self):
        """List all images, optionally filtered by visibility."""
        try:
            kwargs = {}
            if self.visibility:
                kwargs['visibility'] = self.visibility
            
            response = self.vpc_service.list_images(**kwargs)
            return response.get_result().get('images', [])
        except ApiException as e:
            self.handle_api_exception(e, "list images")
    
    def run(self):
        """Execute the module logic."""
        # If both name and id are provided, fail
        if self.resource_id and self.resource_name:
            self.fail_json(msg="Parameters 'id' and 'name' are mutually exclusive")
        
        # Get specific image by ID
        if self.resource_id:
            resource = self.get_resource_by_id(self.resource_id)
            if resource:
                self.result['resource'] = resource
                self.result['found'] = True
                self.result['msg'] = f"Image {self.resource_id} found"
            else:
                self.result['found'] = False
                self.result['msg'] = f"Image {self.resource_id} not found"
        
        # Get specific image by name
        elif self.resource_name:
            resource = self.get_resource_by_name(self.resource_name)
            if resource:
                self.result['resource'] = resource
                self.result['found'] = True
                self.result['msg'] = f"Image '{self.resource_name}' found"
            else:
                self.result['found'] = False
                self.result['msg'] = f"Image '{self.resource_name}' not found"
        
        # List all images
        else:
            resources = self.list_all_resources()
            self.result['resources'] = resources
            self.result['found'] = len(resources) > 0
            
            if self.visibility:
                self.result['msg'] = f"Found {len(resources)} {self.visibility} image(s)"
            else:
                self.result['msg'] = f"Found {len(resources)} image(s)"
        
        self.exit_json()


def main():
    """Main module execution."""
    argument_spec = get_common_argument_spec()
    argument_spec.update({
        'name': {'type': 'str', 'required': False},
        'id': {'type': 'str', 'required': False},
        'visibility': {'type': 'str', 'choices': ['public', 'private'], 'required': False}
    })
    
    # Remove state parameter as this is an info module
    if 'state' in argument_spec:
        del argument_spec['state']
    
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        mutually_exclusive=[['name', 'id']]
    )
    
    info_module = IBMImageInfoModule(module)
    info_module.run()


if __name__ == '__main__':
    main()

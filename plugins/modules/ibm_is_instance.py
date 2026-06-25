#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, IBM Cloud Team
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r'''
---
module: ibm_is_instance
short_description: Manage IBM Cloud VPC virtual server instances
version_added: "1.0.0"
description:
    - Create, update, or delete IBM Cloud VPC virtual server instances
    - This module uses the native IBM Cloud Python SDK (no Terraform dependency)
    - Supports idempotent operations
requirements:
    - ibm-vpc >= 0.33.0
    - ibm-cloud-sdk-core >= 3.20.0
options:
    name:
        description:
            - Name of the instance
        type: str
        required: true
    id:
        description:
            - ID of the instance
            - Required when updating or deleting
        type: str
        required: false
    vpc:
        description:
            - VPC ID or name where instance will be created
        type: str
        required: false
    zone:
        description:
            - Zone name where instance will be created
        type: str
        required: false
    profile:
        description:
            - Instance profile name (e.g., bx2-2x8, cx2-4x8)
        type: str
        required: false
    image:
        description:
            - Image ID or name for the instance
        type: str
        required: false
    primary_network_interface:
        description:
            - Primary network interface configuration
        type: dict
        required: false
        suboptions:
            subnet:
                description: Subnet ID
                type: str
                required: true
            name:
                description: Interface name
                type: str
            security_groups:
                description: List of security group IDs
                type: list
                elements: str
    keys:
        description:
            - List of SSH key IDs to add to the instance
        type: list
        elements: str
        required: false
    user_data:
        description:
            - User data for cloud-init
        type: str
        required: false
    boot_volume:
        description:
            - Boot volume configuration
        type: dict
        required: false
    volumes:
        description:
            - List of data volume attachments
        type: list
        elements: dict
        required: false
    tags:
        description:
            - List of tags
        type: list
        elements: str
        required: false
    ibmcloud_api_key:
        description:
            - IBM Cloud API key
        type: str
        required: false
        no_log: true
    region:
        description:
            - IBM Cloud region
        type: str
        default: 'us-south'
    resource_group:
        description:
            - Resource group ID
        type: str
        required: false
    state:
        description:
            - Desired state of the instance
        type: str
        default: 'present'
        choices: ['present', 'absent', 'running', 'stopped']
author:
    - IBM Cloud Team
'''

EXAMPLES = r'''
- name: Create a VPC instance
  ibm_is_instance:
    name: my-instance
    vpc: my-vpc-id
    zone: us-south-1
    profile: bx2-2x8
    image: ibm-ubuntu-20-04-minimal-amd64-1
    primary_network_interface:
      subnet: subnet-id-123
      security_groups:
        - sg-id-456
    keys:
      - ssh-key-id-789
    state: present

- name: Stop an instance
  ibm_is_instance:
    id: instance-id-123
    state: stopped

- name: Delete an instance
  ibm_is_instance:
    id: instance-id-123
    state: absent
'''

RETURN = r'''
resource:
    description: Instance resource information
    returned: always
    type: dict
    contains:
        id:
            description: Instance ID
            type: str
        name:
            description: Instance name
            type: str
        status:
            description: Instance status
            type: str
        vpc:
            description: VPC information
            type: dict
        zone:
            description: Zone information
            type: dict
        profile:
            description: Profile information
            type: dict
changed:
    description: Whether the instance was changed
    returned: always
    type: bool
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


class IBMInstanceModule(IBMCloudSDKModule):
    """IBM Cloud VPC Instance module implementation."""
    
    def __init__(self, module):
        """Initialize the instance module."""
        super().__init__(module)
        
        if not HAS_IBM_VPC:
            self.fail_json(msg="ibm-vpc Python SDK is required")
        
        self.vpc_service = VpcV1(authenticator=self.auth.get_authenticator())
        self.vpc_service.set_service_url(f'https://{self.region}.iaas.cloud.ibm.com/v1')
        
        self.instance_id = self.params.get('id')
        self.instance_name = self.params.get('name')
    
    def get_instance(self, instance_id: str):
        """Get instance by ID."""
        try:
            response = self.vpc_service.get_instance(id=instance_id)
            return response.get_result()
        except ApiException as e:
            if e.code == 404:
                return None
            self.handle_api_exception(e, f"retrieve instance {instance_id}")
    
    def find_instance_by_name(self, instance_name: str):
        """Find instance by name."""
        try:
            # List all instances in the region
            response = self.vpc_service.list_instances()
            instances = response.get_result().get('instances', [])
            
            for instance in instances:
                if instance.get('name') == instance_name:
                    return instance
            
            return None
        except ApiException as e:
            self.handle_api_exception(e, f"list instances to find {instance_name}")
    
    def create_instance(self):
        """Create a new instance."""
        self.check_mode_exit(changed=True, msg=f"Would create instance: {self.instance_name}")
        
        try:
            from ibm_vpc.vpc_v1 import (
                InstancePrototypeInstanceByImageInstanceByImageInstanceByNetworkInterface,
                ImageIdentityById,
                ZoneIdentityByName,
                NetworkInterfacePrototype,
                SubnetIdentityById,
                InstanceProfileIdentityByName,
                VPCIdentityById,
                KeyIdentityById
            )
            
            # Build primary network interface
            subnet_identity = SubnetIdentityById(id=self.params['primary_network_interface']['subnet'])
            primary_ni = NetworkInterfacePrototype(subnet=subnet_identity)
            
            # Build image, zone, profile identities
            image_identity = ImageIdentityById(id=self.params['image'])
            zone_identity = ZoneIdentityByName(name=self.params['zone'])
            profile_identity = InstanceProfileIdentityByName(name=self.params['profile'])
            
            # Build keys list if provided
            keys = None
            if self.params.get('keys'):
                keys = [KeyIdentityById(id=k) for k in self.params['keys']]
            
            # Build VPC identity if provided
            vpc_identity = None
            if self.params.get('vpc'):
                vpc_identity = VPCIdentityById(id=self.params['vpc'])
            
            # Create instance prototype
            instance_prototype = InstancePrototypeInstanceByImageInstanceByImageInstanceByNetworkInterface(
                image=image_identity,
                zone=zone_identity,
                primary_network_interface=primary_ni,
                name=self.instance_name,
                profile=profile_identity,
                keys=keys,
                vpc=vpc_identity,
                user_data=self.params.get('user_data')
            )
            
            response = self.vpc_service.create_instance(instance_prototype=instance_prototype)
            instance = response.get_result()
            
            self.result['changed'] = True
            self.result['resource'] = instance
            self.result['msg'] = f"Instance {self.instance_name} created successfully"
            
        except ApiException as e:
            self.handle_api_exception(e, f"create instance {self.instance_name}")
    
    def delete_instance(self, instance_id: str):
        """Delete an instance."""
        self.check_mode_exit(changed=True, msg=f"Would delete instance: {instance_id}")
        
        try:
            self.vpc_service.delete_instance(id=instance_id)
            self.result['changed'] = True
            self.result['msg'] = f"Instance {instance_id} deleted successfully"
        except ApiException as e:
            self.handle_api_exception(e, f"delete instance {instance_id}")
    
    def stop_instance(self, instance_id: str):
        """Stop an instance."""
        try:
            self.vpc_service.create_instance_action(
                instance_id=instance_id,
                type='stop'
            )
            self.result['changed'] = True
            self.result['msg'] = f"Instance {instance_id} stopped"
        except ApiException as e:
            self.handle_api_exception(e, f"stop instance {instance_id}")
    
    def start_instance(self, instance_id: str):
        """Start an instance."""
        try:
            self.vpc_service.create_instance_action(
                instance_id=instance_id,
                type='start'
            )
            self.result['changed'] = True
            self.result['msg'] = f"Instance {instance_id} started"
        except ApiException as e:
            self.handle_api_exception(e, f"start instance {instance_id}")
    
    def run(self):
        """Execute the module logic."""
        existing_instance = None
        
        # Always try to find by name first if no ID provided
        if self.instance_id:
            existing_instance = self.get_instance(self.instance_id)
        else:
            # If no ID provided, try to find by name
            existing_instance = self.find_instance_by_name(self.instance_name)
        
        # Preserve all debug fields that were set during lookup
        # (they're already in self.result from find_instance_by_name)
        
        if self.state == 'present':
            if not existing_instance:
                self.create_instance()
            else:
                self.result['resource'] = existing_instance
                self.result['msg'] = f"Instance {self.instance_name} already exists"
        
        elif self.state == 'absent':
            if existing_instance:
                self.delete_instance(existing_instance['id'])
            else:
                # Instance not found - debug info already in self.result
                self.result['msg'] = f"Instance '{self.instance_name}' not found in region '{self.region}'"
        
        elif self.state == 'stopped':
            if existing_instance:
                if existing_instance.get('status') != 'stopped':
                    self.stop_instance(existing_instance['id'])
                else:
                    self.result['msg'] = "Instance already stopped"
        
        elif self.state == 'running':
            if existing_instance:
                if existing_instance.get('status') != 'running':
                    self.start_instance(existing_instance['id'])
                else:
                    self.result['msg'] = "Instance already running"
        
        self.exit_json()


def main():
    """Main module execution."""
    argument_spec = get_common_argument_spec()
    argument_spec.update({
        'name': {'type': 'str', 'required': True},
        'id': {'type': 'str', 'required': False},
        'vpc': {'type': 'str', 'required': False},
        'zone': {'type': 'str', 'required': False},
        'profile': {'type': 'str', 'required': False},
        'image': {'type': 'str', 'required': False},
        'primary_network_interface': {'type': 'dict', 'required': False},
        'keys': {'type': 'list', 'elements': 'str', 'required': False},
        'user_data': {'type': 'str', 'required': False},
        'boot_volume': {'type': 'dict', 'required': False},
        'volumes': {'type': 'list', 'elements': 'dict', 'required': False},
        'tags': {'type': 'list', 'elements': 'str', 'required': False}
    })
    
    argument_spec['state']['choices'] = ['present', 'absent', 'running', 'stopped']
    
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True
    )
    
    instance_module = IBMInstanceModule(module)
    instance_module.run()


if __name__ == '__main__':
    main()

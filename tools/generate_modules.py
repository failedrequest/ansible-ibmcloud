#!/usr/bin/env python3
"""
Module Generator for IBM Cloud VPC (IS) Services

This script generates Ansible modules for all IBM Cloud VPC services
by analyzing the IBM VPC Python SDK and creating standardized module files.

Usage:
    python generate_modules.py
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Any
import json

# Module template
MODULE_TEMPLATE = '''#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, IBM Cloud Team
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r\'\'\'
---
module: {module_name}
short_description: Manage IBM Cloud {resource_name}
version_added: "1.0.0"
description:
    - Create, update, or delete IBM Cloud {resource_name}
    - This module uses the native IBM Cloud Python SDK (no Terraform dependency)
    - Supports idempotent operations
requirements:
    - ibm-vpc >= 0.33.0
    - ibm-cloud-sdk-core >= 3.20.0
options:
{options}
author:
    - IBM Cloud Team
\'\'\'

EXAMPLES = r\'\'\'
{examples}
\'\'\'

RETURN = r\'\'\'
resource:
    description: {resource_name} information
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
\'\'\'

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


class {class_name}(IBMCloudSDKModule):
    """IBM Cloud {resource_name} module implementation."""
    
    def __init__(self, module):
        """Initialize the module."""
        super().__init__(module)
        
        if not HAS_IBM_VPC:
            self.fail_json(msg="ibm-vpc Python SDK is required")
        
        self.vpc_service = VpcV1(authenticator=self.auth.get_authenticator())
        self.vpc_service.set_service_url(f'https://{{self.region}}.iaas.cloud.ibm.com/v1')
        
        self.resource_id = self.params.get('id')
        self.resource_name = self.params.get('name')
    
    def get_resource(self, resource_id: str):
        """Get resource by ID."""
        try:
            response = self.vpc_service.{get_method}(id=resource_id)
            return response.get_result()
        except ApiException as e:
            if e.code == 404:
                return None
            self.handle_api_exception(e, f"retrieve {resource_type} {{resource_id}}")
    
    def list_resources(self):
        """List all resources."""
        try:
            response = self.vpc_service.{list_method}()
            return response.get_result().get('{list_key}', [])
        except ApiException as e:
            self.handle_api_exception(e, f"list {resource_type}s")
    
    def create_resource(self):
        """Create a new resource."""
        self.check_mode_exit(changed=True, msg=f"Would create {resource_type}: {{self.resource_name}}")
        
        try:
            prototype = {prototype}
            
            response = self.vpc_service.{create_method}(**prototype)
            resource = response.get_result()
            
            self.result['changed'] = True
            self.result['resource'] = resource
            self.result['msg'] = f"{resource_type} {{self.resource_name}} created successfully"
            
        except ApiException as e:
            self.handle_api_exception(e, f"create {resource_type} {{self.resource_name}}")
    
    def update_resource(self, resource):
        """Update an existing resource."""
        changed = False
        updates = {{}}
        
        if self.resource_name and resource.get('name') != self.resource_name:
            updates['name'] = self.resource_name
            changed = True
        
        if updates:
            self.check_mode_exit(changed=True, msg=f"Would update {resource_type}: {{resource['id']}}")
            
            try:
                response = self.vpc_service.{update_method}(
                    id=resource['id'],
                    {update_param}=updates
                )
                resource = response.get_result()
                changed = True
            except ApiException as e:
                self.handle_api_exception(e, f"update {resource_type} {{resource['id']}}")
        
        self.result['changed'] = changed
        self.result['resource'] = resource
        self.result['msg'] = f"{resource_type} {{resource['name']}} " + ("updated" if changed else "unchanged")
    
    def delete_resource(self, resource_id: str):
        """Delete a resource."""
        self.check_mode_exit(changed=True, msg=f"Would delete {resource_type}: {{resource_id}}")
        
        try:
            self.vpc_service.{delete_method}(id=resource_id)
            self.result['changed'] = True
            self.result['msg'] = f"{resource_type} {{resource_id}} deleted successfully"
        except ApiException as e:
            self.handle_api_exception(e, f"delete {resource_type} {{resource_id}}")
    
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
                self.result['msg'] = f"{resource_type} not found"
        
        self.exit_json()


def main():
    """Main module execution."""
    argument_spec = get_common_argument_spec()
    argument_spec.update({{
{argument_spec}
    }})
    
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True
    )
    
    resource_module = {class_name}(module)
    resource_module.run()


if __name__ == '__main__':
    main()
'''

# VPC IS resource definitions
VPC_RESOURCES = {
    'subnet': {
        'get_method': 'get_subnet',
        'list_method': 'list_subnets',
        'create_method': 'create_subnet',
        'update_method': 'update_subnet',
        'delete_method': 'delete_subnet',
        'list_key': 'subnets',
        'required_params': ['name', 'vpc', 'ipv4_cidr_block', 'zone'],
        'optional_params': ['network_acl', 'public_gateway', 'routing_table', 'resource_group']
    },
    'security_group': {
        'get_method': 'get_security_group',
        'list_method': 'list_security_groups',
        'create_method': 'create_security_group',
        'update_method': 'update_security_group',
        'delete_method': 'delete_security_group',
        'list_key': 'security_groups',
        'required_params': ['name', 'vpc'],
        'optional_params': ['resource_group']
    },
    'security_group_rule': {
        'get_method': 'get_security_group_rule',
        'list_method': 'list_security_group_rules',
        'create_method': 'create_security_group_rule',
        'update_method': 'update_security_group_rule',
        'delete_method': 'delete_security_group_rule',
        'list_key': 'rules',
        'required_params': ['security_group', 'direction', 'protocol'],
        'optional_params': ['port_min', 'port_max', 'remote', 'code', 'type']
    },
    'public_gateway': {
        'get_method': 'get_public_gateway',
        'list_method': 'list_public_gateways',
        'create_method': 'create_public_gateway',
        'update_method': 'update_public_gateway',
        'delete_method': 'delete_public_gateway',
        'list_key': 'public_gateways',
        'required_params': ['name', 'vpc', 'zone'],
        'optional_params': ['floating_ip', 'resource_group']
    },
    'floating_ip': {
        'get_method': 'get_floating_ip',
        'list_method': 'list_floating_ips',
        'create_method': 'create_floating_ip',
        'update_method': 'update_floating_ip',
        'delete_method': 'delete_floating_ip',
        'list_key': 'floating_ips',
        'required_params': ['name'],
        'optional_params': ['target', 'zone', 'resource_group']
    },
    'network_acl': {
        'get_method': 'get_network_acl',
        'list_method': 'list_network_acls',
        'create_method': 'create_network_acl',
        'update_method': 'update_network_acl',
        'delete_method': 'delete_network_acl',
        'list_key': 'network_acls',
        'required_params': ['name'],
        'optional_params': ['vpc', 'source_network_acl', 'resource_group']
    },
    'vpn_gateway': {
        'get_method': 'get_vpn_gateway',
        'list_method': 'list_vpn_gateways',
        'create_method': 'create_vpn_gateway',
        'update_method': 'update_vpn_gateway',
        'delete_method': 'delete_vpn_gateway',
        'list_key': 'vpn_gateways',
        'required_params': ['name', 'subnet'],
        'optional_params': ['mode', 'resource_group']
    },
    'vpn_gateway_connection': {
        'get_method': 'get_vpn_gateway_connection',
        'list_method': 'list_vpn_gateway_connections',
        'create_method': 'create_vpn_gateway_connection',
        'update_method': 'update_vpn_gateway_connection',
        'delete_method': 'delete_vpn_gateway_connection',
        'list_key': 'connections',
        'required_params': ['vpn_gateway', 'name', 'peer_address', 'preshared_key'],
        'optional_params': ['local_cidrs', 'peer_cidrs', 'admin_state_up']
    },
    'load_balancer': {
        'get_method': 'get_load_balancer',
        'list_method': 'list_load_balancers',
        'create_method': 'create_load_balancer',
        'update_method': 'update_load_balancer',
        'delete_method': 'delete_load_balancer',
        'list_key': 'load_balancers',
        'required_params': ['name', 'subnets'],
        'optional_params': ['is_public', 'listeners', 'pools', 'resource_group']
    },
    'volume': {
        'get_method': 'get_volume',
        'list_method': 'list_volumes',
        'create_method': 'create_volume',
        'update_method': 'update_volume',
        'delete_method': 'delete_volume',
        'list_key': 'volumes',
        'required_params': ['name', 'profile', 'zone'],
        'optional_params': ['capacity', 'encryption_key', 'iops', 'resource_group']
    },
    'ssh_key': {
        'get_method': 'get_key',
        'list_method': 'list_keys',
        'create_method': 'create_key',
        'update_method': 'update_key',
        'delete_method': 'delete_key',
        'list_key': 'keys',
        'required_params': ['name', 'public_key'],
        'optional_params': ['resource_group', 'type']
    },
    'image': {
        'get_method': 'get_image',
        'list_method': 'list_images',
        'create_method': 'create_image',
        'update_method': 'update_image',
        'delete_method': 'delete_image',
        'list_key': 'images',
        'required_params': ['name'],
        'optional_params': ['file', 'operating_system', 'resource_group']
    },
    'flow_log': {
        'get_method': 'get_flow_log_collector',
        'list_method': 'list_flow_log_collectors',
        'create_method': 'create_flow_log_collector',
        'update_method': 'update_flow_log_collector',
        'delete_method': 'delete_flow_log_collector',
        'list_key': 'flow_log_collectors',
        'required_params': ['name', 'target', 'storage_bucket'],
        'optional_params': ['active', 'resource_group']
    }
}


def generate_module(resource_type: str, config: Dict[str, Any], output_dir: Path):
    """Generate a single module file."""
    
    module_name = f"ibm_is_{resource_type}"
    class_name = f"IBM{resource_type.replace('_', ' ').title().replace(' ', '')}Module"
    resource_name = resource_type.replace('_', ' ').title()
    
    # Generate options documentation
    options = []
    options.append("    name:\n        description:\n            - Name of the resource\n        type: str\n        required: true")
    options.append("    id:\n        description:\n            - ID of the resource\n        type: str\n        required: false")
    
    for param in config.get('optional_params', []):
        options.append(f"    {param}:\n        description:\n            - {param.replace('_', ' ').title()}\n        type: str\n        required: false")
    
    options_str = "\n".join(options)
    
    # Generate examples
    examples = f"""- name: Create {resource_name}
  {module_name}:
    name: my-{resource_type}
    state: present

- name: Delete {resource_name}
  {module_name}:
    id: resource-id-123
    state: absent
"""
    
    # Generate argument spec
    arg_spec = []
    arg_spec.append("        'name': {'type': 'str', 'required': True}")
    arg_spec.append("        'id': {'type': 'str', 'required': False}")
    
    for param in config.get('optional_params', []):
        arg_spec.append(f"        '{param}': {{'type': 'str', 'required': False}}")
    
    argument_spec_str = ",\n".join(arg_spec)
    
    # Generate prototype
    prototype_items = ["'name': self.resource_name"]
    for param in config.get('required_params', [])[1:]:  # Skip 'name'
        prototype_items.append(f"'{param}': self.params.get('{param}')")
    
    prototype_str = "{\n            " + ",\n            ".join(prototype_items) + "\n        }"
    
    # Generate module content
    content = MODULE_TEMPLATE.format(
        module_name=module_name,
        resource_name=resource_name,
        class_name=class_name,
        resource_type=resource_type,
        get_method=config['get_method'],
        list_method=config['list_method'],
        create_method=config['create_method'],
        update_method=config['update_method'],
        delete_method=config['delete_method'],
        list_key=config['list_key'],
        options=options_str,
        examples=examples,
        argument_spec=argument_spec_str,
        prototype=prototype_str,
        update_param=f"{resource_type}_patch"
    )
    
    # Write module file
    module_file = output_dir / f"{module_name}.py"
    module_file.write_text(content)
    print(f"✓ Generated: {module_name}.py")


def main():
    """Main generator function."""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    modules_dir = project_root / "plugins" / "modules"
    
    print("=" * 60)
    print("IBM Cloud VPC Module Generator")
    print("=" * 60)
    print(f"\nGenerating modules in: {modules_dir}")
    print(f"Total resources to generate: {len(VPC_RESOURCES)}\n")
    
    modules_dir.mkdir(parents=True, exist_ok=True)
    
    for resource_type, config in VPC_RESOURCES.items():
        try:
            generate_module(resource_type, config, modules_dir)
        except Exception as e:
            print(f"✗ Failed to generate {resource_type}: {e}")
    
    print(f"\n{'=' * 60}")
    print(f"Generation complete! {len(VPC_RESOURCES)} modules created.")
    print(f"{'=' * 60}\n")
    
    # Generate index file
    index_content = f"""# IBM Cloud VPC Modules

This directory contains {len(VPC_RESOURCES)} auto-generated Ansible modules for IBM Cloud VPC services.

## Available Modules

"""
    for resource_type in sorted(VPC_RESOURCES.keys()):
        index_content += f"- `ibm_is_{resource_type}` - Manage {resource_type.replace('_', ' ').title()}\n"
    
    index_file = modules_dir / "README.md"
    index_file.write_text(index_content)
    print(f"✓ Generated module index: {index_file}")


if __name__ == '__main__':
    main()

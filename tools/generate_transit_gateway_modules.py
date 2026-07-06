#!/usr/bin/env python3
"""
Transit Gateway Module Generator for IBM Cloud

Generates Ansible modules for IBM Cloud Transit Gateway service including:
- Transit Gateways
- Gateway Connections
- Connection Prefix Filters
- Route Reports
- Location information
"""

import sys
from pathlib import Path

# Import the base generator
sys.path.insert(0, str(Path(__file__).parent))
from generate_modules import MODULE_TEMPLATE

# Transit Gateway resource definitions
TRANSIT_GATEWAY_RESOURCES = {
    'tg_gateway': {
        'service': 'transit_gateway',
        'sdk_class': 'TransitGatewayApisV1',
        'get_method': 'get_transit_gateway',
        'list_method': 'list_transit_gateways',
        'create_method': 'create_transit_gateway',
        'update_method': 'update_transit_gateway',
        'delete_method': 'delete_transit_gateway',
        'list_key': 'transit_gateways',
        'required_params': ['name', 'location'],
        'optional_params': ['global_', 'resource_group']
    },
    'tg_connection': {
        'service': 'transit_gateway',
        'sdk_class': 'TransitGatewayApisV1',
        'get_method': 'get_transit_gateway_connection',
        'list_method': 'list_transit_gateway_connections',
        'create_method': 'create_transit_gateway_connection',
        'update_method': 'update_transit_gateway_connection',
        'delete_method': 'delete_transit_gateway_connection',
        'list_key': 'connections',
        'required_params': ['transit_gateway_id', 'network_type', 'name'],
        'optional_params': ['network_id', 'network_account_id', 'base_connection_id', 'local_gateway_ip', 'local_tunnel_ip', 'remote_gateway_ip', 'remote_tunnel_ip', 'zone']
    },
    'tg_connection_prefix_filter': {
        'service': 'transit_gateway',
        'sdk_class': 'TransitGatewayApisV1',
        'get_method': 'get_transit_gateway_connection_prefix_filter',
        'list_method': 'list_transit_gateway_connection_prefix_filters',
        'create_method': 'create_transit_gateway_connection_prefix_filter',
        'update_method': 'replace_transit_gateway_connection_prefix_filter',
        'delete_method': 'delete_transit_gateway_connection_prefix_filter',
        'list_key': 'prefix_filters',
        'required_params': ['transit_gateway_id', 'connection_id', 'action', 'prefix'],
        'optional_params': ['before', 'ge', 'le']
    },
    'tg_route_report': {
        'service': 'transit_gateway',
        'sdk_class': 'TransitGatewayApisV1',
        'get_method': 'get_transit_gateway_route_report',
        'list_method': 'list_transit_gateway_route_reports',
        'create_method': 'create_transit_gateway_route_report',
        'update_method': None,
        'delete_method': 'delete_transit_gateway_route_report',
        'list_key': 'route_reports',
        'required_params': ['transit_gateway_id'],
        'optional_params': []
    }
}


def generate_tg_module(resource_type: str, config: dict, output_dir: Path):
    """Generate a Transit Gateway module."""
    
    module_name = f"ibm_{resource_type}"
    class_name = f"IBM{resource_type.replace('_', ' ').title().replace(' ', '')}Module"
    resource_name = resource_type.replace('_', ' ').title()
    service = config['service']
    
    # Generate module using template
    options = []
    options.append("    name:\n        description:\n            - Name of the resource\n        type: str\n        required: true")
    options.append("    id:\n        description:\n            - ID of the resource\n        type: str\n        required: false")
    
    for param in config.get('optional_params', []):
        param_desc = param.replace('_', ' ').title()
        if param == 'global_':
            param_desc = "Enable global routing"
        options.append(f"    {param}:\n        description:\n            - {param_desc}\n        type: str\n        required: false")
    
    options_str = "\n".join(options)
    
    examples = f"""- name: Create {resource_name}
  {module_name}:
    name: my-{resource_type.replace('_', '-')}
    state: present

- name: Delete {resource_name}
  {module_name}:
    id: resource-id-123
    state: absent
"""
    
    arg_spec = []
    arg_spec.append("        'name': {'type': 'str', 'required': True}")
    arg_spec.append("        'id': {'type': 'str', 'required': False}")
    
    for param in config.get('optional_params', []):
        arg_spec.append(f"        '{param}': {{'type': 'str', 'required': False}}")
    
    argument_spec_str = ",\n".join(arg_spec)
    
    prototype_items = ["'name': self.resource_name"]
    for param in config.get('required_params', [])[1:]:
        prototype_items.append(f"'{param}': self.params.get('{param}')")
    
    prototype_str = "{\n            " + ",\n            ".join(prototype_items) + "\n        }"
    
    # Custom template for Transit Gateway services
    content = f'''#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, IBM Cloud Team
# BSD 2-Clause License (see LICENSE or https://opensource.org/licenses/BSD-2-Clause)

DOCUMENTATION = r\'\'\'
---
module: {module_name}
short_description: Manage IBM Cloud {resource_name}
version_added: "1.0.0"
description:
    - Create, update, or delete IBM Cloud {resource_name}
    - Part of IBM Cloud Transit Gateway service
    - Uses native IBM Cloud Python SDK
requirements:
    - ibm-platform-services >= 0.50.0
    - ibm-cloud-sdk-core >= 3.20.0
options:
{options_str}
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
    from ibm_platform_services import {config['sdk_class']}
    from ibm_cloud_sdk_core import ApiException
    HAS_IBM_SDK = True
except ImportError:
    HAS_IBM_SDK = False


class {class_name}(IBMCloudSDKModule):
    """IBM Cloud {resource_name} module implementation."""
    
    def __init__(self, module):
        """Initialize the module."""
        super().__init__(module)
        
        if not HAS_IBM_SDK:
            self.fail_json(msg="ibm-platform-services Python SDK is required")
        
        self.service = {config['sdk_class']}(authenticator=self.auth.get_authenticator())
        
        self.resource_id = self.params.get('id')
        self.resource_name = self.params.get('name')
    
    def get_resource(self, resource_id: str):
        """Get resource by ID."""
        try:
            response = self.service.{config['get_method']}(id=resource_id)
            return response.get_result()
        except ApiException as e:
            if e.code == 404:
                return None
            self.handle_api_exception(e, f"retrieve {resource_type} {{resource_id}}")
    
    def list_resources(self):
        """List all resources."""
        try:
            response = self.service.{config['list_method']}()
            return response.get_result().get('{config['list_key']}', [])
        except ApiException as e:
            self.handle_api_exception(e, f"list {resource_type}s")
    
    def create_resource(self):
        """Create a new resource."""
        self.check_mode_exit(changed=True, msg=f"Would create {resource_type}: {{self.resource_name}}")
        
        try:
            prototype = {prototype_str}
            
            response = self.service.{config['create_method']}(**prototype)
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
        
        if updates and '{config['update_method']}' != 'None':
            self.check_mode_exit(changed=True, msg=f"Would update {resource_type}: {{resource['id']}}")
            
            try:
                response = self.service.{config['update_method']}(
                    id=resource['id'],
                    **updates
                )
                resource = response.get_result()
                changed = True
            except ApiException as e:
                self.handle_api_exception(e, f"update {resource_type} {{resource['id']}}")
        
        self.result['changed'] = changed
        self.result['resource'] = resource
        self.result['msg'] = f"{resource_type} {{resource.get('name', resource['id'])}} " + ("updated" if changed else "unchanged")
    
    def delete_resource(self, resource_id: str):
        """Delete a resource."""
        self.check_mode_exit(changed=True, msg=f"Would delete {resource_type}: {{resource_id}}")
        
        try:
            self.service.{config['delete_method']}(id=resource_id)
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
{argument_spec_str}
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
    
    module_file = output_dir / f"{module_name}.py"
    module_file.write_text(content)
    print(f"✓ Generated: {module_name}.py")


def main():
    """Main generator function for Transit Gateway modules."""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    modules_dir = project_root / "plugins" / "modules"
    
    print("=" * 60)
    print("IBM Cloud Transit Gateway Module Generator")
    print("=" * 60)
    print(f"\nGenerating Transit Gateway modules in: {modules_dir}")
    print(f"Total resources to generate: {len(TRANSIT_GATEWAY_RESOURCES)}\n")
    
    modules_dir.mkdir(parents=True, exist_ok=True)
    
    generated = 0
    failed = 0
    
    for resource_type, config in TRANSIT_GATEWAY_RESOURCES.items():
        try:
            generate_tg_module(resource_type, config, modules_dir)
            generated += 1
        except Exception as e:
            print(f"✗ Failed to generate {resource_type}: {e}")
            failed += 1
    
    print(f"\n{'=' * 60}")
    print(f"Transit Gateway generation complete!")
    print(f"  Generated: {generated} modules")
    print(f"  Failed: {failed} modules")
    print(f"{'=' * 60}\n")


if __name__ == '__main__':
    main()

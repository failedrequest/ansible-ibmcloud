#!/usr/bin/env python3
"""
Platform Module Generator for IBM Cloud Services

Generates Ansible modules for core IBM Cloud platform services including:
- Cloud Object Storage (COS)
- Identity and Access Management (IAM)
- Resource Management
- Key Management (KMS)
- Databases
- Container Registry
- Event Notifications
- Secrets Manager
"""

import sys
from pathlib import Path

# Import the base generator
sys.path.insert(0, str(Path(__file__).parent))
from generate_modules import MODULE_TEMPLATE

# Platform service resource definitions
PLATFORM_RESOURCES = {
    # Cloud Object Storage (COS)
    'cos_bucket': {
        'service': 'cos',
        'sdk_class': 'ResourceConfigurationV1',
        'get_method': 'get_bucket_config',
        'list_method': 'list_buckets',
        'create_method': 'create_bucket',
        'update_method': 'update_bucket_config',
        'delete_method': 'delete_bucket',
        'list_key': 'buckets',
        'required_params': ['name', 'ibm_service_instance_id'],
        'optional_params': ['storage_class', 'location_constraint', 'object_versioning']
    },
    
    # IAM - Identity and Access Management
    'iam_access_group': {
        'service': 'iam',
        'sdk_class': 'IamAccessGroupsV2',
        'get_method': 'get_access_group',
        'list_method': 'list_access_groups',
        'create_method': 'create_access_group',
        'update_method': 'update_access_group',
        'delete_method': 'delete_access_group',
        'list_key': 'groups',
        'required_params': ['name', 'account_id'],
        'optional_params': ['description']
    },
    'iam_access_group_rule': {
        'service': 'iam',
        'sdk_class': 'IamAccessGroupsV2',
        'get_method': 'get_access_group_rule',
        'list_method': 'list_access_group_rules',
        'create_method': 'add_access_group_rule',
        'update_method': 'replace_access_group_rule',
        'delete_method': 'remove_access_group_rule',
        'list_key': 'rules',
        'required_params': ['access_group_id', 'name', 'expiration', 'conditions'],
        'optional_params': ['realm_name']
    },
    'iam_service_id': {
        'service': 'iam',
        'sdk_class': 'IamIdentityV1',
        'get_method': 'get_service_id',
        'list_method': 'list_service_ids',
        'create_method': 'create_service_id',
        'update_method': 'update_service_id',
        'delete_method': 'delete_service_id',
        'list_key': 'serviceids',
        'required_params': ['name', 'account_id'],
        'optional_params': ['description', 'unique_instance_crns']
    },
    'iam_api_key': {
        'service': 'iam',
        'sdk_class': 'IamIdentityV1',
        'get_method': 'get_api_key',
        'list_method': 'list_api_keys',
        'create_method': 'create_api_key',
        'update_method': 'update_api_key',
        'delete_method': 'delete_api_key',
        'list_key': 'apikeys',
        'required_params': ['name', 'iam_id'],
        'optional_params': ['description', 'account_id', 'store_value']
    },
    'iam_policy': {
        'service': 'iam',
        'sdk_class': 'IamPolicyManagementV1',
        'get_method': 'get_policy',
        'list_method': 'list_policies',
        'create_method': 'create_policy',
        'update_method': 'replace_policy',
        'delete_method': 'delete_policy',
        'list_key': 'policies',
        'required_params': ['type', 'subjects', 'roles', 'resources'],
        'optional_params': ['description']
    },
    
    # Resource Management
    'resource_group': {
        'service': 'resource_manager',
        'sdk_class': 'ResourceManagerV2',
        'get_method': 'get_resource_group',
        'list_method': 'list_resource_groups',
        'create_method': 'create_resource_group',
        'update_method': 'update_resource_group',
        'delete_method': 'delete_resource_group',
        'list_key': 'resources',
        'required_params': ['name', 'account_id'],
        'optional_params': []
    },
    'resource_instance': {
        'service': 'resource_controller',
        'sdk_class': 'ResourceControllerV2',
        'get_method': 'get_resource_instance',
        'list_method': 'list_resource_instances',
        'create_method': 'create_resource_instance',
        'update_method': 'update_resource_instance',
        'delete_method': 'delete_resource_instance',
        'list_key': 'resources',
        'required_params': ['name', 'target', 'resource_group', 'resource_plan_id'],
        'optional_params': ['parameters', 'tags']
    },
    'resource_key': {
        'service': 'resource_controller',
        'sdk_class': 'ResourceControllerV2',
        'get_method': 'get_resource_key',
        'list_method': 'list_resource_keys',
        'create_method': 'create_resource_key',
        'update_method': 'update_resource_key',
        'delete_method': 'delete_resource_key',
        'list_key': 'resources',
        'required_params': ['name', 'source'],
        'optional_params': ['parameters', 'role']
    },
    'resource_binding': {
        'service': 'resource_controller',
        'sdk_class': 'ResourceControllerV2',
        'get_method': 'get_resource_binding',
        'list_method': 'list_resource_bindings',
        'create_method': 'create_resource_binding',
        'update_method': 'update_resource_binding',
        'delete_method': 'delete_resource_binding',
        'list_key': 'resources',
        'required_params': ['name', 'source', 'target'],
        'optional_params': ['parameters', 'role']
    },
    
    # Key Management Service (KMS)
    'kms_key': {
        'service': 'kms',
        'sdk_class': 'IbmKeyProtectApiV2',
        'get_method': 'get_key',
        'list_method': 'get_keys',
        'create_method': 'create_key',
        'update_method': 'patch_key',
        'delete_method': 'delete_key',
        'list_key': 'resources',
        'required_params': ['name', 'instance_id'],
        'optional_params': ['key_ring_id', 'payload', 'extractable', 'expiration_date']
    },
    'kms_key_ring': {
        'service': 'kms',
        'sdk_class': 'IbmKeyProtectApiV2',
        'get_method': 'get_key_ring',
        'list_method': 'list_key_rings',
        'create_method': 'create_key_ring',
        'update_method': None,
        'delete_method': 'delete_key_ring',
        'list_key': 'key_rings',
        'required_params': ['key_ring_id', 'instance_id'],
        'optional_params': []
    },
    
    # Databases
    'database_instance': {
        'service': 'cloud_databases',
        'sdk_class': 'CloudDatabasesV5',
        'get_method': 'get_deployment_info',
        'list_method': 'list_deployments',
        'create_method': 'create_database_deployment',
        'update_method': 'update_database_configuration',
        'delete_method': 'delete_database_deployment',
        'list_key': 'deployments',
        'required_params': ['name', 'service_id', 'plan_id', 'location'],
        'optional_params': ['version', 'members_memory_allocation_mb', 'members_disk_allocation_mb']
    },
    'database_user': {
        'service': 'cloud_databases',
        'sdk_class': 'CloudDatabasesV5',
        'get_method': 'get_connection',
        'list_method': 'list_database_users',
        'create_method': 'create_database_user',
        'update_method': 'update_database_user',
        'delete_method': 'delete_database_user',
        'list_key': 'users',
        'required_params': ['deployment_id', 'username'],
        'optional_params': ['password']
    },
    
    # Container Registry
    'cr_namespace': {
        'service': 'container_registry',
        'sdk_class': 'ContainerRegistryV1',
        'get_method': 'get_namespace',
        'list_method': 'list_namespaces',
        'create_method': 'create_namespace',
        'update_method': None,
        'delete_method': 'delete_namespace',
        'list_key': 'namespaces',
        'required_params': ['name'],
        'optional_params': ['resource_group_id']
    },
    'cr_retention_policy': {
        'service': 'container_registry',
        'sdk_class': 'ContainerRegistryV1',
        'get_method': 'get_retention_policy',
        'list_method': 'list_retention_policies',
        'create_method': 'set_retention_policy',
        'update_method': 'set_retention_policy',
        'delete_method': 'delete_retention_policy',
        'list_key': 'policies',
        'required_params': ['namespace', 'images_per_repo'],
        'optional_params': ['retain_untagged']
    },
    
    # Event Notifications
    'en_destination': {
        'service': 'event_notifications',
        'sdk_class': 'EventNotificationsV1',
        'get_method': 'get_destination',
        'list_method': 'list_destinations',
        'create_method': 'create_destination',
        'update_method': 'update_destination',
        'delete_method': 'delete_destination',
        'list_key': 'destinations',
        'required_params': ['instance_id', 'name', 'type', 'config'],
        'optional_params': ['description']
    },
    'en_topic': {
        'service': 'event_notifications',
        'sdk_class': 'EventNotificationsV1',
        'get_method': 'get_topic',
        'list_method': 'list_topics',
        'create_method': 'create_topic',
        'update_method': 'replace_topic',
        'delete_method': 'delete_topic',
        'list_key': 'topics',
        'required_params': ['instance_id', 'name'],
        'optional_params': ['description', 'sources']
    },
    'en_subscription': {
        'service': 'event_notifications',
        'sdk_class': 'EventNotificationsV1',
        'get_method': 'get_subscription',
        'list_method': 'list_subscriptions',
        'create_method': 'create_subscription',
        'update_method': 'update_subscription',
        'delete_method': 'delete_subscription',
        'list_key': 'subscriptions',
        'required_params': ['instance_id', 'name', 'destination_id', 'topic_id'],
        'optional_params': ['description', 'attributes']
    },
    
    # Secrets Manager
    'sm_secret_group': {
        'service': 'secrets_manager',
        'sdk_class': 'SecretsManagerV2',
        'get_method': 'get_secret_group',
        'list_method': 'list_secret_groups',
        'create_method': 'create_secret_group',
        'update_method': 'update_secret_group',
        'delete_method': 'delete_secret_group',
        'list_key': 'secret_groups',
        'required_params': ['instance_id', 'name'],
        'optional_params': ['description']
    },
    'sm_secret': {
        'service': 'secrets_manager',
        'sdk_class': 'SecretsManagerV2',
        'get_method': 'get_secret',
        'list_method': 'list_secrets',
        'create_method': 'create_secret',
        'update_method': 'update_secret',
        'delete_method': 'delete_secret',
        'list_key': 'secrets',
        'required_params': ['instance_id', 'name', 'secret_type'],
        'optional_params': ['secret_group_id', 'labels', 'expiration_date', 'payload']
    }
}


def generate_platform_module(resource_type: str, config: dict, output_dir: Path):
    """Generate a platform service module."""
    
    module_name = f"ibm_{resource_type}"
    class_name = f"IBM{resource_type.replace('_', ' ').title().replace(' ', '')}Module"
    resource_name = resource_type.replace('_', ' ').title()
    service = config['service']
    
    # Generate module using template
    options = []
    options.append("    name:\n        description:\n            - Name of the resource\n        type: str\n        required: true")
    options.append("    id:\n        description:\n            - ID of the resource\n        type: str\n        required: false")
    
    for param in config.get('optional_params', []):
        options.append(f"    {param}:\n        description:\n            - {param.replace('_', ' ').title()}\n        type: str\n        required: false")
    
    options_str = "\n".join(options)
    
    examples = f"""- name: Create {resource_name}
  {module_name}:
    name: my-{resource_type}
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
    
    # Custom template for platform services
    content = f'''#!/usr/bin/python
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
    - Part of IBM Cloud {service.upper()} service
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
        
        if updates:
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
        self.result['msg'] = f"{resource_type} {{resource['name']}} " + ("updated" if changed else "unchanged")
    
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
    """Main generator function for platform modules."""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    modules_dir = project_root / "plugins" / "modules"
    
    print("=" * 60)
    print("IBM Cloud Platform Services Module Generator")
    print("=" * 60)
    print(f"\nGenerating platform modules in: {modules_dir}")
    print(f"Total resources to generate: {len(PLATFORM_RESOURCES)}\n")
    
    modules_dir.mkdir(parents=True, exist_ok=True)
    
    generated = 0
    failed = 0
    
    # Group by service
    services = {}
    for resource_type, config in PLATFORM_RESOURCES.items():
        service = config['service']
        if service not in services:
            services[service] = []
        services[service].append(resource_type)
    
    print("Services covered:")
    for service, resources in services.items():
        print(f"  - {service.upper()}: {len(resources)} modules")
    print()
    
    for resource_type, config in PLATFORM_RESOURCES.items():
        try:
            generate_platform_module(resource_type, config, modules_dir)
            generated += 1
        except Exception as e:
            print(f"✗ Failed to generate {resource_type}: {e}")
            failed += 1
    
    print(f"\n{'=' * 60}")
    print(f"Platform generation complete!")
    print(f"  Generated: {generated} modules")
    print(f"  Failed: {failed} modules")
    print(f"  Services: {len(services)}")
    print(f"{'=' * 60}\n")


if __name__ == '__main__':
    main()

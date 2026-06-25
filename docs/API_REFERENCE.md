# API Reference - IBM Cloud Native Ansible Collection

## Module Utilities

### IBMCloudAuth

Authentication handler for IBM Cloud services.

```python
from ansible_collections.ibm.cloudcollection.plugins.module_utils.ibm_cloud_sdk import IBMCloudAuth

# Initialize with API key
auth = IBMCloudAuth(api_key="your-api-key")

# Get authenticator for SDK clients
authenticator = auth.get_authenticator()
```

### IBMCloudSDKModule

Base class for all IBM Cloud modules.

```python
from ansible_collections.ibm.cloudcollection.plugins.module_utils.ibm_cloud_sdk import IBMCloudSDKModule

class MyModule(IBMCloudSDKModule):
    def __init__(self, module):
        super().__init__(module)
        # Your initialization
    
    def run(self):
        # Your module logic
        pass
```

#### Methods

- `handle_api_exception(e, operation)` - Handle IBM Cloud API exceptions
- `exit_json(**kwargs)` - Exit with success
- `fail_json(msg, **kwargs)` - Exit with failure
- `check_mode_exit(changed, msg)` - Exit if in check mode
- `get_resource_id(resource)` - Extract resource ID
- `compare_resources(current, desired, ignore_keys)` - Compare resource states

## Common Parameters

All modules support these parameters:

```yaml
ibmcloud_api_key: string (optional, no_log)
  IBM Cloud API key. Can be set via IC_API_KEY environment variable.

region: string (optional, default: us-south)
  IBM Cloud region. Choices: us-south, us-east, eu-gb, eu-de, jp-tok, au-syd, jp-osa, ca-tor, br-sao

resource_group: string (optional)
  Resource group ID for the resource.

state: string (optional, default: present)
  Desired state. Choices: present, absent
```

## Module: ibm_is_vpc

Manage IBM Cloud VPC resources.

### Parameters

```yaml
name: string (required)
  Name of the VPC

id: string (optional)
  VPC ID for updates/deletes

address_prefix_management: string (optional, default: auto)
  Address prefix management mode. Choices: auto, manual

classic_access: boolean (optional, default: false)
  Enable classic infrastructure access

default_network_acl_name: string (optional)
  Name for default network ACL

default_routing_table_name: string (optional)
  Name for default routing table

default_security_group_name: string (optional)
  Name for default security group

dns: dict (optional)
  DNS configuration

tags: list (optional)
  List of tags
```

### Return Values

```yaml
resource:
  type: dict
  description: VPC resource information
  contains:
    id: VPC ID
    name: VPC name
    crn: Cloud Resource Name
    status: VPC status
    created_at: Creation timestamp

changed:
  type: bool
  description: Whether the VPC was changed

msg:
  type: string
  description: Status message
```

### Examples

```yaml
# Create VPC
- ibm_is_vpc:
    name: my-vpc
    region: us-south
    state: present

# Delete VPC
- ibm_is_vpc:
    id: vpc-id-123
    state: absent
```

## Module: ibm_is_instance

Manage IBM Cloud VPC virtual server instances.

### Parameters

```yaml
name: string (required)
  Instance name

id: string (optional)
  Instance ID for updates/deletes

vpc: string (optional)
  VPC ID

zone: string (optional)
  Zone name (e.g., us-south-1)

profile: string (optional)
  Instance profile (e.g., bx2-2x8)

image: string (optional)
  Image ID or name

primary_network_interface: dict (optional)
  Primary network interface configuration
  subnet: string (required) - Subnet ID
  name: string (optional) - Interface name
  security_groups: list (optional) - Security group IDs

keys: list (optional)
  SSH key IDs

user_data: string (optional)
  Cloud-init user data

state: string (optional, default: present)
  Choices: present, absent, running, stopped
```

### Return Values

```yaml
resource:
  type: dict
  description: Instance information
  contains:
    id: Instance ID
    name: Instance name
    status: Instance status
    vpc: VPC information
    zone: Zone information
    profile: Profile information

changed:
  type: bool
  description: Whether the instance was changed
```

### Examples

```yaml
# Create instance
- ibm_is_instance:
    name: web-server
    vpc: vpc-id
    zone: us-south-1
    profile: bx2-2x8
    image: ubuntu-20-04
    primary_network_interface:
      subnet: subnet-id
    keys:
      - ssh-key-id
    state: present

# Stop instance
- ibm_is_instance:
    id: instance-id
    state: stopped

# Delete instance
- ibm_is_instance:
    id: instance-id
    state: absent
```

## Using IBM Cloud CLI Integration

The modules can work alongside IBM Cloud CLI:

```yaml
---
- name: Use CLI to get resource info
  hosts: localhost
  tasks:
    - name: Get VPC list using CLI
      command: ibmcloud is vpcs --output json
      register: vpcs_cli
      changed_when: false

    - name: Parse VPC data
      set_fact:
        vpc_list: "{{ vpcs_cli.stdout | from_json }}"

    - name: Create instance in existing VPC
      ibm_is_instance:
        name: new-instance
        vpc: "{{ vpc_list[0].id }}"
        zone: us-south-1
        profile: bx2-2x8
        image: ubuntu-20-04
        state: present
```

## Error Handling

All modules provide detailed error messages:

```yaml
- name: Handle errors
  block:
    - name: Create VPC
      ibm_is_vpc:
        name: my-vpc
        state: present
      register: result
  
  rescue:
    - name: Log error
      debug:
        msg: "Failed to create VPC: {{ ansible_failed_result.msg }}"
    
    - name: Cleanup on failure
      ibm_is_vpc:
        id: "{{ result.resource.id }}"
        state: absent
      when: result.resource.id is defined
```

## Best Practices

### 1. Use Variables

```yaml
vars:
  ibm_config:
    region: us-south
    resource_group: rg-id-123
    tags:
      - env:prod
      - managed-by:ansible

tasks:
  - ibm_is_vpc:
      name: my-vpc
      region: "{{ ibm_config.region }}"
      resource_group: "{{ ibm_config.resource_group }}"
      tags: "{{ ibm_config.tags }}"
```

### 2. Use Check Mode

```bash
ansible-playbook playbook.yml --check --diff
```

### 3. Register Results

```yaml
- name: Create VPC
  ibm_is_vpc:
    name: my-vpc
    state: present
  register: vpc_result

- name: Use VPC ID
  ibm_is_subnet:
    vpc: "{{ vpc_result.resource.id }}"
    name: my-subnet
```

### 4. Handle Idempotency

Modules are idempotent - safe to run multiple times:

```yaml
- name: Ensure VPC exists
  ibm_is_vpc:
    name: my-vpc
    state: present
  # Will create if missing, skip if exists
```

## SDK Integration

Direct SDK usage in custom modules:

```python
from ibm_vpc import VpcV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

# Initialize
authenticator = IAMAuthenticator('your-api-key')
vpc_service = VpcV1(authenticator=authenticator)
vpc_service.set_service_url('https://us-south.iaas.cloud.ibm.com/v1')

# List VPCs
response = vpc_service.list_vpcs()
vpcs = response.get_result()['vpcs']

# Create VPC
vpc_prototype = {
    'name': 'my-vpc',
    'address_prefix_management': 'auto'
}
response = vpc_service.create_vpc(**vpc_prototype)
vpc = response.get_result()
```

## Debugging

Enable verbose output:

```bash
# Level 1: Basic info
ansible-playbook playbook.yml -v

# Level 2: More details
ansible-playbook playbook.yml -vv

# Level 3: Debug info
ansible-playbook playbook.yml -vvv

# Level 4: Connection debugging
ansible-playbook playbook.yml -vvvv
```

## Performance Tips

1. **Parallel Execution**: Use `async` for independent tasks
2. **Fact Caching**: Enable fact caching for repeated runs
3. **Batch Operations**: Group similar operations together
4. **Resource Reuse**: Store and reuse resource IDs

## Support Matrix

| Module | Create | Read | Update | Delete | State Management |
|--------|--------|------|--------|--------|------------------|
| ibm_is_vpc | ✓ | ✓ | ✓ | ✓ | ✓ |
| ibm_is_instance | ✓ | ✓ | Partial | ✓ | ✓ |
| ibm_is_subnet | ✓ | ✓ | ✓ | ✓ | ✓ |
| ibm_is_security_group | ✓ | ✓ | ✓ | ✓ | ✓ |

## Version Compatibility

- Python: 3.10+
- Ansible Core: 2.14+
- IBM Cloud SDK Core: 3.20.0+
- IBM VPC SDK: 0.33.0+

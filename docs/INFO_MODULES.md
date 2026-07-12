# IBM Cloud Info Modules

This guide covers the IBM Cloud info modules for read-only resource lookups. These modules eliminate the need for shell commands and provide native Ansible integration for discovering existing resources.

## Overview

Info modules are read-only modules that retrieve information about existing IBM Cloud resources without modifying them. They are essential for:

- Looking up resource IDs by name
- Discovering existing infrastructure
- Validating resource existence before operations
- Building dynamic inventories
- Creating dependencies between resources

## Available Info Modules

### 1. ibm_is_vpc_info

Retrieve information about VPC resources.

**Parameters:**
- `name` (optional) - VPC name to look up
- `id` (optional) - VPC ID to look up
- `region` (optional) - IBM Cloud region (default: us-south)

**Examples:**

```yaml
# Get VPC by name
- name: Get VPC information
  ibm_is_vpc_info:
    name: production-vpc
    region: us-south
  register: vpc_info

# Get VPC by ID
- name: Get VPC by ID
  ibm_is_vpc_info:
    id: r006-12345678-1234-1234-1234-123456789012
    region: us-south
  register: vpc_info

# List all VPCs
- name: List all VPCs
  ibm_is_vpc_info:
    region: us-south
  register: all_vpcs

# Use in subsequent tasks
- name: Create subnet in VPC
  ibm_is_subnet:
    name: my-subnet
    vpc: "{{ vpc_info.resource.id }}"
    zone: us-south-1
    ipv4_cidr_block: 10.240.0.0/24
    state: present
```

### 2. ibm_is_subnet_info

Retrieve information about subnet resources.

**Parameters:**
- `name` (optional) - Subnet name to look up
- `id` (optional) - Subnet ID to look up
- `vpc` (optional) - Filter by VPC name or ID
- `region` (optional) - IBM Cloud region (default: us-south)

**Examples:**

```yaml
# Get subnet by name
- name: Get subnet information
  ibm_is_subnet_info:
    name: web-subnet
    region: us-south
  register: subnet_info

# Get subnet by ID
- name: Get subnet by ID
  ibm_is_subnet_info:
    id: 0717-12345678-1234-1234-1234-123456789012
    region: us-south
  register: subnet_info

# List all subnets in a VPC
- name: List subnets in VPC
  ibm_is_subnet_info:
    vpc: production-vpc
    region: us-south
  register: vpc_subnets

# Use in VNI creation
- name: Create VNI in subnet
  ibm_is_virtual_network_interface:
    name: my-vni
    subnet: "{{ subnet_info.resource.id }}"
    primary_ip_address: 10.240.0.100
    state: present
```

### 3. ibm_is_virtual_network_interface_info

Retrieve information about Virtual Network Interface resources.

**Parameters:**
- `name` (optional) - VNI name to look up
- `id` (optional) - VNI ID to look up
- `region` (optional) - IBM Cloud region (default: us-south)

**Examples:**

```yaml
# Get VNI by name
- name: Get VNI information
  ibm_is_virtual_network_interface_info:
    name: cluster-vni
    region: us-south
  register: vni_info

# Get VNI by ID
- name: Get VNI by ID
  ibm_is_virtual_network_interface_info:
    id: r006-12345678-1234-1234-1234-123456789012
    region: us-south
  register: vni_info

# List all VNIs
- name: List all VNIs
  ibm_is_virtual_network_interface_info:
    region: us-south
  register: all_vnis

# Use in cluster attachment
- name: Attach VNI to cluster
  ibm_ks_cluster_vni:
    cluster: my-cluster
    vni_id: "{{ vni_info.resource.id }}"
    vni_subnet_id: "{{ vni_info.resource.subnet.id }}"
    state: present
```

### 4. ibm_is_image_info

Retrieve information about image resources.

**Parameters:**
- `name` (optional) - Image name to look up
- `id` (optional) - Image ID to look up
- `visibility` (optional) - Filter by visibility (public/private)
- `region` (optional) - IBM Cloud region (default: us-south)

**Examples:**

```yaml
# Get image by name
- name: Get image information
  ibm_is_image_info:
    name: ibm-ubuntu-20-04-minimal-amd64-1
    region: us-south
  register: image_info

# Get image by ID
- name: Get image by ID
  ibm_is_image_info:
    id: r006-12345678-1234-1234-1234-123456789012
    region: us-south
  register: image_info

# List all public images
- name: List public images
  ibm_is_image_info:
    visibility: public
    region: us-south
  register: public_images

# Use in instance creation
- name: Create instance with image
  ibm_is_instance:
    name: web-server
    vpc: "{{ vpc_id }}"
    zone: us-south-1
    profile: bx2-2x8
    image: "{{ image_info.resource.id }}"
    state: present
```

## Common Patterns

### Pattern 1: Resource Discovery Chain

```yaml
- name: Discover and use resources
  hosts: localhost
  tasks:
    - name: Find VPC
      ibm_is_vpc_info:
        name: production-vpc
      register: vpc

    - name: Find subnet in VPC
      ibm_is_subnet_info:
        name: web-subnet
        vpc: "{{ vpc.resource.id }}"
      register: subnet

    - name: Create instance in subnet
      ibm_is_instance:
        name: web-server
        vpc: "{{ vpc.resource.id }}"
        zone: us-south-1
        profile: bx2-2x8
        primary_network_interface:
          subnet: "{{ subnet.resource.id }}"
        state: present
```

### Pattern 2: Conditional Resource Creation

```yaml
- name: Create resource only if it doesn't exist
  hosts: localhost
  tasks:
    - name: Check if VPC exists
      ibm_is_vpc_info:
        name: my-vpc
      register: vpc_check

    - name: Create VPC if not found
      ibm_is_vpc:
        name: my-vpc
        state: present
      when: not vpc_check.found
      register: vpc_result

    - name: Set VPC ID
      set_fact:
        vpc_id: "{{ vpc_result.resource.id if vpc_result.changed else vpc_check.resource.id }}"
```

### Pattern 3: Bulk Resource Discovery

```yaml
- name: Discover multiple resources
  hosts: localhost
  vars:
    subnet_names:
      - web-subnet
      - app-subnet
      - db-subnet
  tasks:
    - name: Get all subnet information
      ibm_is_subnet_info:
        name: "{{ item }}"
      loop: "{{ subnet_names }}"
      register: subnets

    - name: Display subnet IDs
      debug:
        msg: "{{ item.item }}: {{ item.resource.id }}"
      loop: "{{ subnets.results }}"
      when: item.found
```

### Pattern 4: Resource Validation

```yaml
- name: Validate resources before deployment
  hosts: localhost
  tasks:
    - name: Check VPC exists
      ibm_is_vpc_info:
        name: production-vpc
      register: vpc

    - name: Fail if VPC not found
      fail:
        msg: "VPC 'production-vpc' not found"
      when: not vpc.found

    - name: Check subnet exists
      ibm_is_subnet_info:
        name: web-subnet
        vpc: "{{ vpc.resource.id }}"
      register: subnet

    - name: Fail if subnet not found
      fail:
        msg: "Subnet 'web-subnet' not found in VPC"
      when: not subnet.found

    - name: Proceed with deployment
      debug:
        msg: "All prerequisites validated, proceeding..."
```

## Return Values

All info modules return a consistent structure:

```yaml
resource:          # Single resource (when name or id specified)
  id: "..."
  name: "..."
  # ... other resource attributes

resources:         # List of resources (when listing all)
  - id: "..."
    name: "..."
  - id: "..."
    name: "..."

found: true/false  # Whether resource(s) were found
msg: "..."         # Status message
```

## Best Practices

### 1. Always Check `found` Status

```yaml
- name: Get resource
  ibm_is_vpc_info:
    name: my-vpc
  register: result

- name: Fail if not found
  fail:
    msg: "Resource not found"
  when: not result.found
```

### 2. Use Info Modules Instead of Shell Commands

**Before (using shell):**
```yaml
- name: Get VPC ID
  shell: |
    ibmcloud is vpcs --output json | jq -r '.[] | select(.name=="my-vpc") | .id'
  register: vpc_id
```

**After (using info module):**
```yaml
- name: Get VPC information
  ibm_is_vpc_info:
    name: my-vpc
  register: vpc_info

- name: Use VPC ID
  debug:
    msg: "{{ vpc_info.resource.id }}"
```

### 3. Cache Resource Lookups

```yaml
- name: Get VPC once
  ibm_is_vpc_info:
    name: production-vpc
  register: vpc_info
  run_once: true

- name: Use VPC in multiple tasks
  ibm_is_subnet:
    name: "subnet-{{ item }}"
    vpc: "{{ vpc_info.resource.id }}"
    state: present
  loop: [1, 2, 3]
```

### 4. Handle Missing Resources Gracefully

```yaml
- name: Get optional resource
  ibm_is_subnet_info:
    name: optional-subnet
  register: subnet
  failed_when: false

- name: Use resource if found
  debug:
    msg: "Subnet found: {{ subnet.resource.id }}"
  when: subnet.found

- name: Handle missing resource
  debug:
    msg: "Subnet not found, using default"
  when: not subnet.found
```

## Comparison: Shell Commands vs Info Modules

| Aspect | Shell Commands | Info Modules |
|--------|---------------|--------------|
| Dependencies | Requires ibmcloud CLI + jq | Pure Python, no external deps |
| Error Handling | Manual parsing of stderr | Native Ansible error handling |
| Idempotency | Not guaranteed | Fully idempotent |
| Performance | Slower (subprocess overhead) | Faster (direct API calls) |
| Testing | Difficult to mock | Easy to test with check mode |
| Portability | Platform-dependent | Cross-platform |
| Output Format | String parsing required | Structured dict/list |

## Troubleshooting

### Resource Not Found

**Problem:** Info module returns `found: false`

**Solutions:**
1. Verify resource name spelling
2. Check region is correct
3. Verify API key has proper permissions
4. List all resources to see what's available

```yaml
- name: List all VPCs to debug
  ibm_is_vpc_info:
    region: us-south
  register: all_vpcs

- name: Show available VPCs
  debug:
    var: all_vpcs.resources
```

### Authentication Issues

**Problem:** API authentication failures

**Solutions:**
1. Set API key environment variable:
   ```bash
   export IC_API_KEY="your-api-key"
   ```

2. Or provide in playbook:
   ```yaml
   ibmcloud_api_key: "{{ lookup('env', 'IC_API_KEY') }}"
   ```

### Region Mismatch

**Problem:** Resource exists but not found

**Solution:** Ensure region matches where resource was created:

```yaml
- name: Try multiple regions
  ibm_is_vpc_info:
    name: my-vpc
    region: "{{ item }}"
  loop:
    - us-south
    - us-east
    - eu-gb
  register: vpc_search
  when: vpc_search is not defined or not vpc_search.found
```

## Integration Examples

### With Terraform State

```yaml
- name: Import from Terraform
  hosts: localhost
  tasks:
    - name: Read Terraform state
      command: terraform output -json
      register: tf_output

    - name: Parse VPC name
      set_fact:
        vpc_name: "{{ (tf_output.stdout | from_json).vpc_name.value }}"

    - name: Get VPC details
      ibm_is_vpc_info:
        name: "{{ vpc_name }}"
      register: vpc_info
```

### With Dynamic Inventory

```yaml
- name: Build dynamic inventory
  hosts: localhost
  tasks:
    - name: List all VPCs
      ibm_is_vpc_info:
      register: vpcs

    - name: Add VPCs to inventory
      add_host:
        name: "{{ item.name }}"
        groups: vpcs
        vpc_id: "{{ item.id }}"
      loop: "{{ vpcs.resources }}"
```

## Reference

### Related Modules

- `ibm_is_vpc` - Manage VPCs
- `ibm_is_subnet` - Manage subnets
- `ibm_is_virtual_network_interface` - Manage VNIs
- `ibm_is_image` - Manage images
- `ibm_ks_cluster_vni` - Attach VNIs to clusters

### External Resources

- [IBM Cloud VPC API](https://cloud.ibm.com/apidocs/vpc)
- [Ansible Best Practices](https://docs.ansible.com/ansible/latest/user_guide/playbooks_best_practices.html)
- [IBM Cloud SDK for Python](https://github.com/IBM/ibm-cloud-sdk-python)

---

**Last Updated**: 2024
**Module Version**: 2.0.5

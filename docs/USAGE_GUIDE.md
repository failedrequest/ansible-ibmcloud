# Usage Guide - IBM Cloud Ansible Collection

Complete guide for using the IBM Cloud Ansible Collection with `ansible-playbook`.

## Collection Overview

**Namespace**: `ibm.cloudcollection`  
**Version**: 2.0.5  
**Total Modules**: 67 (42 VPC + 4 Transit Gateway + 21 Platform Services)

## Installation Verification

```bash
# Verify collection is installed
.venv/bin/ansible-galaxy collection list | grep ibm

# Expected output:
# ibm.cloudcollection 2.0.5
```

## Using the Collection

### Method 1: Collections Declaration (Recommended)

```yaml
---
- name: Manage IBM Cloud Resources
  hosts: localhost
  connection: local
  gather_facts: no
  collections:
    - ibm.cloudcollection
  
  tasks:
    - name: Create VPC
      ibm_is_vpc:
        name: my-vpc
        region: us-south
        state: present
```

### Method 2: Fully Qualified Collection Name (FQCN)

```yaml
---
- name: Manage IBM Cloud Resources
  hosts: localhost
  connection: local
  
  tasks:
    - name: Create VPC
      ibm.cloudcollection.ibm_is_vpc:
        name: my-vpc
        region: us-south
        state: present
```

## Running Playbooks

### Basic Execution

```bash
# Run playbook
.venv/bin/ansible-playbook my-playbook.yml

# With verbose output
.venv/bin/ansible-playbook my-playbook.yml -v
.venv/bin/ansible-playbook my-playbook.yml -vv
.venv/bin/ansible-playbook my-playbook.yml -vvv
```

### Check Mode (Dry Run)

```bash
# Test without making changes
.venv/bin/ansible-playbook my-playbook.yml --check

# Check mode with diff
.venv/bin/ansible-playbook my-playbook.yml --check --diff
```

### Using Tags

```yaml
---
- name: Infrastructure Setup
  hosts: localhost
  collections:
    - ibm.cloudcollection
  
  tasks:
    - name: Create VPC
      ibm_is_vpc:
        name: my-vpc
        state: present
      tags: [vpc, network]
    
    - name: Create Subnet
      ibm_is_subnet:
        name: my-subnet
        vpc: "{{ vpc_id }}"
        state: present
      tags: [subnet, network]
    
    - name: Create Instance
      ibm_is_instance:
        name: my-instance
        state: present
      tags: [compute]
```

```bash
# Run only VPC tasks
.venv/bin/ansible-playbook playbook.yml --tags vpc

# Run network tasks
.venv/bin/ansible-playbook playbook.yml --tags network

# Skip compute tasks
.venv/bin/ansible-playbook playbook.yml --skip-tags compute
```

## Complete Examples

### Example 1: VPC Infrastructure

```yaml
---
- name: Create Complete VPC Infrastructure
  hosts: localhost
  connection: local
  gather_facts: no
  collections:
    - ibm.cloudcollection
  
  vars:
    region: us-south
    zone: us-south-1
    vpc_name: production-vpc
    subnet_cidr: 10.240.0.0/24
  
  tasks:
    - name: Create VPC
      ibm_is_vpc:
        name: "{{ vpc_name }}"
        region: "{{ region }}"
        state: present
      register: vpc
    
    - name: Create Subnet
      ibm_is_subnet:
        name: "{{ vpc_name }}-subnet"
        vpc: "{{ vpc.resource.id }}"
        zone: "{{ zone }}"
        ipv4_cidr_block: "{{ subnet_cidr }}"
        state: present
      register: subnet
    
    - name: Create Security Group
      ibm_is_security_group:
        name: "{{ vpc_name }}-sg"
        vpc: "{{ vpc.resource.id }}"
        state: present
      register: sg
    
    - name: Allow SSH
      ibm_is_security_group_rule:
        security_group: "{{ sg.resource.id }}"
        direction: inbound
        protocol: tcp
        port_min: 22
        port_max: 22
        state: present
    
    - name: Allow HTTP
      ibm_is_security_group_rule:
        security_group: "{{ sg.resource.id }}"
        direction: inbound
        protocol: tcp
        port_min: 80
        port_max: 80
        state: present
    
    - name: Create SSH Key
      ibm_is_ssh_key:
        name: "{{ vpc_name }}-key"
        public_key: "{{ lookup('file', '~/.ssh/id_rsa.pub') }}"
        state: present
      register: ssh_key
    
    - name: Create Instance
      ibm_is_instance:
        name: "{{ vpc_name }}-instance"
        vpc: "{{ vpc.resource.id }}"
        zone: "{{ zone }}"
        profile: cx2-2x4
        image: ibm-ubuntu-22-04-minimal-amd64-1
        primary_network_interface:
          subnet: "{{ subnet.resource.id }}"
          security_groups:
            - "{{ sg.resource.id }}"
        keys:
          - "{{ ssh_key.resource.id }}"
        state: present
      register: instance
    
    - name: Display Results
      debug:
        msg:
          - "VPC ID: {{ vpc.resource.id }}"
          - "Subnet ID: {{ subnet.resource.id }}"
          - "Instance ID: {{ instance.resource.id }}"
```

### Example 2: Transit Gateway Multi-VPC

```yaml
---
- name: Connect Multiple VPCs with Transit Gateway
  hosts: localhost
  connection: local
  collections:
    - ibm.cloudcollection
  
  vars:
    region: us-south
  
  tasks:
    - name: Create Transit Gateway
      ibm_tg_gateway:
        name: multi-vpc-gateway
        location: "{{ region }}"
        global: false
        state: present
      register: tg
    
    - name: Connect VPC 1
      ibm_tg_connection:
        gateway: "{{ tg.resource.id }}"
        name: vpc1-connection
        network_type: vpc
        network_id: "{{ vpc1_id }}"
        state: present
    
    - name: Connect VPC 2
      ibm_tg_connection:
        gateway: "{{ tg.resource.id }}"
        name: vpc2-connection
        network_type: vpc
        network_id: "{{ vpc2_id }}"
        state: present
    
    - name: Add Prefix Filter
      ibm_tg_connection_prefix_filter:
        gateway: "{{ tg.resource.id }}"
        connection: "{{ connection_id }}"
        action: permit
        prefix: 10.240.0.0/16
        state: present
```

### Example 3: Platform Services

```yaml
---
- name: Setup Platform Services
  hosts: localhost
  connection: local
  collections:
    - ibm.cloudcollection
  
  tasks:
    - name: Create Resource Group
      ibm_resource_group:
        name: production-rg
        state: present
      register: rg
    
    - name: Create COS Instance
      ibm_resource_instance:
        name: production-cos
        service: cloud-object-storage
        plan: standard
        location: global
        resource_group: "{{ rg.resource.id }}"
        state: present
      register: cos
    
    - name: Create COS Bucket
      ibm_cos_bucket:
        name: production-data-bucket
        instance: "{{ cos.resource.id }}"
        region: us-south
        storage_class: standard
        state: present
    
    - name: Create IAM Access Group
      ibm_iam_access_group:
        name: developers
        description: Developer access group
        state: present
      register: group
    
    - name: Create IAM Policy
      ibm_iam_policy:
        type: access
        subjects:
          - access_group_id: "{{ group.resource.id }}"
        roles:
          - role_id: crn:v1:bluemix:public:iam::::role:Viewer
        resources:
          - resource_group_id: "{{ rg.resource.id }}"
        state: present
```

## Advanced Usage

### Using Variables Files

**vars.yml:**
```yaml
region: us-south
zone: us-south-1
vpc_name: production-vpc
instance_profile: cx2-2x4
image_name: ibm-ubuntu-22-04-minimal-amd64-1
```

**playbook.yml:**
```yaml
---
- name: Deploy Infrastructure
  hosts: localhost
  collections:
    - ibm.cloudcollection
  vars_files:
    - vars.yml
  
  tasks:
    - name: Create VPC
      ibm_is_vpc:
        name: "{{ vpc_name }}"
        region: "{{ region }}"
        state: present
```

```bash
.venv/bin/ansible-playbook playbook.yml
```

### Using Ansible Vault for Secrets

```bash
# Create encrypted vault
.venv/bin/ansible-vault create secrets.yml

# Add API key
ibmcloud_api_key: your-api-key-here

# Use in playbook
.venv/bin/ansible-playbook playbook.yml --ask-vault-pass
```

### Using Environment Variables

```yaml
---
- name: Use Environment Variables
  hosts: localhost
  collections:
    - ibm.cloudcollection
  
  vars:
    api_key: "{{ lookup('env', 'IC_API_KEY') }}"
    region: "{{ lookup('env', 'IC_REGION') | default('us-south') }}"
  
  tasks:
    - name: Create VPC
      ibm_is_vpc:
        name: my-vpc
        region: "{{ region }}"
        ibmcloud_api_key: "{{ api_key }}"
        state: present
```

### Error Handling

```yaml
---
- name: Infrastructure with Error Handling
  hosts: localhost
  collections:
    - ibm.cloudcollection
  
  tasks:
    - name: Create VPC
      ibm_is_vpc:
        name: my-vpc
        state: present
      register: vpc
      ignore_errors: yes
    
    - name: Handle VPC creation failure
      debug:
        msg: "VPC creation failed: {{ vpc.msg }}"
      when: vpc.failed
    
    - name: Continue if VPC exists
      block:
        - name: Create Subnet
          ibm_is_subnet:
            name: my-subnet
            vpc: "{{ vpc.resource.id }}"
            state: present
      rescue:
        - name: Handle subnet error
          debug:
            msg: "Subnet creation failed"
      always:
        - name: Cleanup on failure
          debug:
            msg: "Performing cleanup"
```

### Loops and Iteration

```yaml
---
- name: Create Multiple Resources
  hosts: localhost
  collections:
    - ibm.cloudcollection
  
  vars:
    subnets:
      - name: web-subnet
        cidr: 10.240.0.0/24
        zone: us-south-1
      - name: app-subnet
        cidr: 10.240.1.0/24
        zone: us-south-2
      - name: db-subnet
        cidr: 10.240.2.0/24
        zone: us-south-3
  
  tasks:
    - name: Create VPC
      ibm_is_vpc:
        name: multi-tier-vpc
        state: present
      register: vpc
    
    - name: Create Subnets
      ibm_is_subnet:
        name: "{{ item.name }}"
        vpc: "{{ vpc.resource.id }}"
        zone: "{{ item.zone }}"
        ipv4_cidr_block: "{{ item.cidr }}"
        state: present
      loop: "{{ subnets }}"
      register: subnet_results
```

## Module Return Values

All modules return:

```yaml
{
  "changed": true,           # Whether resource was modified
  "resource": {              # Resource details
    "id": "r006-xxx",
    "name": "my-resource",
    "crn": "crn:v1:...",
    # ... other resource attributes
  },
  "msg": "Resource created"  # Status message
}
```

## Common Patterns

### Idempotent Operations

```yaml
# Safe to run multiple times
- name: Ensure VPC exists
  ibm_is_vpc:
    name: my-vpc
    state: present
  # Only creates if doesn't exist
```

### Resource Dependencies

```yaml
- name: Create VPC
  ibm_is_vpc:
    name: my-vpc
    state: present
  register: vpc

- name: Create Subnet (depends on VPC)
  ibm_is_subnet:
    name: my-subnet
    vpc: "{{ vpc.resource.id }}"  # Use VPC ID
    state: present
```

### Conditional Execution

```yaml
- name: Create VPC
  ibm_is_vpc:
    name: my-vpc
    state: present
  register: vpc
  when: create_vpc | default(true)

- name: Skip if VPC exists
  ibm_is_subnet:
    name: my-subnet
    vpc: "{{ vpc.resource.id }}"
    state: present
  when: vpc.changed
```

## Troubleshooting

### Enable Debug Output

```bash
# Verbose mode
.venv/bin/ansible-playbook playbook.yml -vvv

# Debug specific task
- name: Create VPC
  ibm_is_vpc:
    name: my-vpc
    state: present
  register: result
  
- debug:
    var: result
```

### Common Issues

**Issue**: Module not found
```bash
# Solution: Verify collection installation
.venv/bin/ansible-galaxy collection list | grep ibm
```

**Issue**: Authentication failed
```bash
# Solution: Check API key
echo $IC_API_KEY
export IC_API_KEY="your-key"
```

**Issue**: Resource already exists
```yaml
# Solution: Use idempotent operations
- name: Ensure resource exists
  ibm_is_vpc:
    name: my-vpc
    state: present  # Creates or updates
```

## Best Practices

1. **Use Check Mode First**: Always test with `--check`
2. **Handle Errors**: Use `ignore_errors` and `rescue` blocks
3. **Use Variables**: Store configuration in vars files
4. **Secure Secrets**: Use Ansible Vault for API keys
5. **Tag Tasks**: Use tags for selective execution
6. **Register Results**: Capture output for dependent tasks
7. **Use FQCN**: Fully qualified names prevent conflicts

## Next Steps

- Review [INSTALLATION.md](INSTALLATION.md) for setup details
- Check [examples/](../examples/) for more playbooks
- View [HTML docs](html/index.html) for module reference
- Read [TRANSIT_GATEWAY.md](TRANSIT_GATEWAY.md) for networking
- See [PLATFORM_SERVICES.md](PLATFORM_SERVICES.md) for services

## Support

- **Documentation**: `docs/` directory
- **Examples**: `examples/` directory
- **IBM Cloud**: https://cloud.ibm.com/docs

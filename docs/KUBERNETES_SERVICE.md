# IBM Cloud Kubernetes Service (ROKS) Module

This guide covers the IBM Cloud Kubernetes Service module for managing Virtual Network Interface (VNI) attachments to ROKS clusters.

## Overview

The `ibm_ks_cluster_vni` module allows you to attach and detach Virtual Network Interfaces (VNIs) to IBM Cloud Kubernetes Service (ROKS) clusters. This enables advanced networking configurations for your Kubernetes workloads.

## Module: ibm_ks_cluster_vni

### Description

Manage VNI attachments to IBM Cloud Kubernetes Service clusters using the IBM Cloud CLI (`ibmcloud ks` plugin).

### Requirements

- IBM Cloud CLI (`ibmcloud`) installed and configured
- IBM Cloud Kubernetes Service plugin (`ibmcloud plugin install kubernetes-service`)
- Valid IBM Cloud API key or authenticated session
- Ansible 2.14+

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `cluster` | string | yes | - | Name or ID of the Kubernetes cluster |
| `vni_id` | string | yes | - | ID of the Virtual Network Interface |
| `vni_subnet_id` | string | conditional | - | ID of the subnet where VNI resides (required for attach) |
| `state` | string | no | present | Desired state: `present` (attach) or `absent` (detach) |
| `ibmcloud_api_key` | string | no | - | IBM Cloud API key (if not already authenticated) |
| `region` | string | no | - | IBM Cloud region |

### Return Values

| Key | Type | Description |
|-----|------|-------------|
| `cluster` | string | Cluster name or ID |
| `vni_id` | string | VNI ID that was attached/detached |
| `changed` | boolean | Whether the resource was changed |
| `msg` | string | Status message |
| `vni_info` | dict | VNI attachment information (when attached) |

## Examples

### Basic VNI Attachment

```yaml
- name: Attach VNI to ROKS cluster
  ibm_ks_cluster_vni:
    cluster: my-roks-cluster
    vni_id: r006-12345678-1234-1234-1234-123456789abc
    vni_subnet_id: 0717-abcd1234-5678-90ab-cdef-1234567890ab
    state: present
```

### VNI Detachment

```yaml
- name: Detach VNI from ROKS cluster
  ibm_ks_cluster_vni:
    cluster: my-roks-cluster
    vni_id: r006-12345678-1234-1234-1234-123456789abc
    state: absent
```

### With API Key Authentication

**Option 1: Using Environment Variables (Recommended)**
```yaml
- name: Attach VNI with environment variables
  ibm_ks_cluster_vni:
    cluster: "{{ lookup('env', 'CLUSTER_NAME') }}"
    vni_id: r006-12345678-1234-1234-1234-123456789abc
    vni_subnet_id: 0717-abcd1234-5678-90ab-cdef-1234567890ab
    ibmcloud_api_key: "{{ lookup('env', 'IC_API_KEY') }}"
    region: us-south
    state: present
```

**Option 2: Using Playbook Variables**
```yaml
vars:
  ibmcloud_api_key: "{{ lookup('env', 'IC_API_KEY') }}"
  cluster_name: "{{ lookup('env', 'CLUSTER_NAME') }}"

tasks:
  - name: Attach VNI with playbook variables
    ibm_ks_cluster_vni:
      cluster: "{{ cluster_name }}"
      vni_id: r006-12345678-1234-1234-1234-123456789abc
      vni_subnet_id: 0717-abcd1234-5678-90ab-cdef-1234567890ab
      ibmcloud_api_key: "{{ ibmcloud_api_key }}"
      region: us-south
      state: present
```

### Complete Workflow: Create VNI and Attach to Cluster

```yaml
---
- name: Create VNI and Attach to ROKS Cluster
  hosts: localhost
  gather_facts: false
  collections:
    - ibm.cloudcollection
  
  vars:
    ibm_region: us-south
    vpc_name: production-vpc
    cluster_name: my-roks-cluster
    subnet_name: cluster-subnet
    vni_name: cluster-vni
    reserved_ip: 10.240.1.100

  tasks:
    - name: Get subnet ID
      shell: |
        ibmcloud is subnets --output json | jq -r '.[] | select(.name=="{{ subnet_name }}") | .id'
      register: subnet_lookup
      changed_when: false

    - name: Create VNI with reserved IP
      ibm_is_virtual_network_interface:
        name: "{{ vni_name }}"
        subnet: "{{ subnet_lookup.stdout }}"
        primary_ip_address: "{{ reserved_ip }}"
        primary_ip_name: "{{ vni_name }}-ip"
        enable_infrastructure_nat: true
        region: "{{ ibm_region }}"
        state: present
      register: vni_result

    - name: Attach VNI to ROKS cluster
      ibm_ks_cluster_vni:
        cluster: "{{ cluster_name }}"
        vni_id: "{{ vni_result.resource.id }}"
        vni_subnet_id: "{{ subnet_lookup.stdout }}"
        region: "{{ ibm_region }}"
        state: present
      register: attach_result

    - name: Display results
      debug:
        msg: |
          VNI {{ vni_name }} ({{ vni_result.resource.id }}) 
          attached to cluster {{ cluster_name }}
          IP Address: {{ vni_result.resource.primary_ip.address }}
```

## Use Cases

### 1. Multi-Tier Application Networking

Attach VNIs to ROKS clusters for dedicated network interfaces per application tier:

```yaml
- name: Setup multi-tier networking
  hosts: localhost
  tasks:
    - name: Attach web tier VNI
      ibm_ks_cluster_vni:
        cluster: production-cluster
        vni_id: "{{ web_vni_id }}"
        vni_subnet_id: "{{ web_subnet_id }}"
        state: present

    - name: Attach app tier VNI
      ibm_ks_cluster_vni:
        cluster: production-cluster
        vni_id: "{{ app_vni_id }}"
        vni_subnet_id: "{{ app_subnet_id }}"
        state: present

    - name: Attach database tier VNI
      ibm_ks_cluster_vni:
        cluster: production-cluster
        vni_id: "{{ db_vni_id }}"
        vni_subnet_id: "{{ db_subnet_id }}"
        state: present
```

### 2. Network Isolation

Create isolated network paths for different workloads:

```yaml
- name: Setup isolated networks
  hosts: localhost
  tasks:
    - name: Attach production VNI
      ibm_ks_cluster_vni:
        cluster: prod-cluster
        vni_id: "{{ prod_vni_id }}"
        vni_subnet_id: "{{ prod_subnet_id }}"
        state: present

    - name: Attach development VNI
      ibm_ks_cluster_vni:
        cluster: dev-cluster
        vni_id: "{{ dev_vni_id }}"
        vni_subnet_id: "{{ dev_subnet_id }}"
        state: present
```

### 3. Disaster Recovery Setup

Attach VNIs for cross-region connectivity:

```yaml
- name: Setup DR networking
  hosts: localhost
  tasks:
    - name: Attach primary region VNI
      ibm_ks_cluster_vni:
        cluster: primary-cluster
        vni_id: "{{ primary_vni_id }}"
        vni_subnet_id: "{{ primary_subnet_id }}"
        region: us-south
        state: present

    - name: Attach DR region VNI
      ibm_ks_cluster_vni:
        cluster: dr-cluster
        vni_id: "{{ dr_vni_id }}"
        vni_subnet_id: "{{ dr_subnet_id }}"
        region: us-east
        state: present
```

## Best Practices

### 1. VNI Naming Convention

Use descriptive names that indicate purpose and cluster:

```yaml
vni_name: "{{ cluster_name }}-{{ tier }}-vni"
# Example: prod-cluster-web-vni
```

### 2. Reserved IP Management

Assign specific IPs for predictable networking:

```yaml
- name: Create VNI with reserved IP
  ibm_is_virtual_network_interface:
    name: cluster-vni
    subnet: "{{ subnet_id }}"
    primary_ip_address: 10.240.1.100
    primary_ip_name: cluster-vni-ip
    state: present
```

### 3. Security Group Configuration

Configure security groups before attaching VNIs:

```yaml
- name: Configure security group
  ibm_is_security_group_rule:
    security_group: "{{ sg_id }}"
    direction: inbound
    protocol: tcp
    port_min: 443
    port_max: 443
    state: present

- name: Attach VNI with security group
  ibm_is_virtual_network_interface:
    name: cluster-vni
    subnet: "{{ subnet_id }}"
    security_groups:
      - "{{ sg_id }}"
    state: present
```

### 4. Idempotent Operations

The module is idempotent - safe to run multiple times:

```yaml
- name: Ensure VNI is attached
  ibm_ks_cluster_vni:
    cluster: my-cluster
    vni_id: "{{ vni_id }}"
    vni_subnet_id: "{{ subnet_id }}"
    state: present
  # Will only attach if not already attached
```

### 5. Check Mode Support

Test changes before applying:

```bash
ansible-playbook attach-vni.yml --check
```

## Troubleshooting

### VNI Not Attaching

**Problem**: VNI attachment fails

**Solutions**:
1. Verify cluster exists and is accessible:
   ```bash
   ibmcloud ks cluster get --cluster my-cluster
   ```

2. Check VNI exists and is in correct subnet:
   ```bash
   ibmcloud is virtual-network-interface my-vni
   ```

3. Verify subnet is in same VPC as cluster:
   ```bash
   ibmcloud is subnet my-subnet
   ```

4. Check IAM permissions for cluster and VPC

### CLI Not Found

**Problem**: `ibmcloud: command not found`

**Solution**: Install IBM Cloud CLI:
```bash
# macOS
brew install ibmcloud-cli

# Linux
curl -fsSL https://clis.cloud.ibm.com/install/linux | sh

# Windows
# Download from https://cloud.ibm.com/docs/cli
```

### Plugin Not Installed

**Problem**: `ks plugin not found`

**Solution**: Install Kubernetes Service plugin:
```bash
ibmcloud plugin install kubernetes-service
```

### Authentication Issues

**Problem**: Authentication failures

**Solutions**:
1. Set API key environment variable:
   ```bash
   export IBMCLOUD_API_KEY="your-api-key"
   ```

2. Or provide in playbook:
   ```yaml
   ibmcloud_api_key: "{{ lookup('env', 'IBMCLOUD_API_KEY') }}"
   ```

3. Or login manually:
   ```bash
   ibmcloud login --apikey your-api-key -r us-south
   ```

## Integration with Other Modules

### With VPC Modules

```yaml
- name: Complete VPC and Cluster Setup
  hosts: localhost
  tasks:
    - name: Create VPC
      ibm_is_vpc:
        name: cluster-vpc
        state: present
      register: vpc

    - name: Create subnet
      ibm_is_subnet:
        name: cluster-subnet
        vpc: "{{ vpc.resource.id }}"
        zone: us-south-1
        ipv4_cidr_block: 10.240.0.0/24
        state: present
      register: subnet

    - name: Create VNI
      ibm_is_virtual_network_interface:
        name: cluster-vni
        subnet: "{{ subnet.resource.id }}"
        state: present
      register: vni

    - name: Attach to cluster
      ibm_ks_cluster_vni:
        cluster: my-cluster
        vni_id: "{{ vni.resource.id }}"
        vni_subnet_id: "{{ subnet.resource.id }}"
        state: present
```

### With Security Groups

```yaml
- name: Setup secure cluster networking
  hosts: localhost
  tasks:
    - name: Create security group
      ibm_is_security_group:
        name: cluster-sg
        vpc: "{{ vpc_id }}"
        state: present
      register: sg

    - name: Add security rules
      ibm_is_security_group_rule:
        security_group: "{{ sg.resource.id }}"
        direction: inbound
        protocol: tcp
        port_min: 443
        port_max: 443
        state: present

    - name: Create VNI with security group
      ibm_is_virtual_network_interface:
        name: cluster-vni
        subnet: "{{ subnet_id }}"
        security_groups:
          - "{{ sg.resource.id }}"
        state: present
      register: vni

    - name: Attach to cluster
      ibm_ks_cluster_vni:
        cluster: my-cluster
        vni_id: "{{ vni.resource.id }}"
        vni_subnet_id: "{{ subnet_id }}"
        state: present
```

## Reference

### IBM Cloud CLI Commands

The module uses these IBM Cloud CLI commands:

```bash
# Attach VNI
ibmcloud ks cluster vni attach --cluster CLUSTER --vni VNI_ID --subnet SUBNET_ID

# Detach VNI
ibmcloud ks cluster vni detach --cluster CLUSTER --vni VNI_ID

# List cluster details
ibmcloud ks cluster get --cluster CLUSTER --output json
```

### Related Modules

- `ibm_is_virtual_network_interface` - Create and manage VNIs
- `ibm_is_subnet` - Manage VPC subnets
- `ibm_is_security_group` - Manage security groups
- `ibm_is_vpc` - Manage VPCs

### External Resources

- [IBM Cloud Kubernetes Service Documentation](https://cloud.ibm.com/docs/containers)
- [VPC Networking Documentation](https://cloud.ibm.com/docs/vpc)
- [IBM Cloud CLI Reference](https://cloud.ibm.com/docs/cli)
- [Kubernetes Service CLI Plugin](https://cloud.ibm.com/docs/containers?topic=containers-cli-plugin-kubernetes-service-cli)

---

**Last Updated**: 2024
**Module Version**: 2.0.5

# IBM Cloud VPC (IS) Module Reference

Complete reference for all 42+ IBM Cloud VPC Infrastructure Services modules.

## Module Categories

### Core VPC Infrastructure (15 modules)

#### VPC Management
- **ibm_is_vpc** - Manage Virtual Private Clouds
- **ibm_is_subnet** - Manage VPC subnets
- **ibm_is_address_prefix** - Manage VPC address prefixes
- **ibm_is_routing_table** - Manage VPC routing tables
- **ibm_is_route** - Manage VPC routes

#### Security
- **ibm_is_security_group** - Manage security groups
- **ibm_is_security_group_rule** - Manage security group rules
- **ibm_is_network_acl** - Manage network ACLs

#### Networking
- **ibm_is_public_gateway** - Manage public gateways
- **ibm_is_floating_ip** - Manage floating IPs
- **ibm_is_endpoint_gateway** - Manage VPC endpoint gateways
- **ibm_is_network_interface** - Manage instance network interfaces
- **ibm_is_virtual_network_interface** - Manage virtual network interfaces

#### Flow Logs
- **ibm_is_flow_log** - Manage VPC flow log collectors

### Compute Resources (8 modules)

#### Virtual Server Instances
- **ibm_is_instance** - Manage virtual server instances
- **ibm_is_instance_template** - Manage instance templates
- **ibm_is_instance_group** - Manage instance groups
- **ibm_is_instance_group_manager** - Manage instance group managers

#### Bare Metal Servers
- **ibm_is_bare_metal_server** - Manage bare metal servers
- **ibm_is_bare_metal_server_network_interface** - Manage bare metal network interfaces

#### Dedicated Hosts
- **ibm_is_dedicated_host_group** - Manage dedicated host groups
- **ibm_is_dedicated_host** - Manage dedicated hosts

### Storage (7 modules)

#### Block Storage
- **ibm_is_volume** - Manage block storage volumes

#### Snapshots & Backups
- **ibm_is_snapshot** - Manage volume snapshots
- **ibm_is_snapshot_consistency_group** - Manage snapshot consistency groups
- **ibm_is_backup_policy** - Manage backup policies
- **ibm_is_backup_policy_plan** - Manage backup policy plans

#### File Storage
- **ibm_is_share** - Manage file shares
- **ibm_is_share_mount_target** - Manage share mount targets

### Load Balancing (4 modules)

- **ibm_is_load_balancer** - Manage load balancers
- **ibm_is_lb_listener** - Manage load balancer listeners
- **ibm_is_lb_pool** - Manage load balancer pools
- **ibm_is_lb_pool_member** - Manage load balancer pool members

### VPN Services (5 modules)

- **ibm_is_vpn_gateway** - Manage VPN gateways
- **ibm_is_vpn_gateway_connection** - Manage VPN gateway connections
- **ibm_is_vpn_server** - Manage VPN servers
- **ibm_is_ike_policy** - Manage IKE policies
- **ibm_is_ipsec_policy** - Manage IPSec policies

### Resource Management (3 modules)

- **ibm_is_ssh_key** - Manage SSH keys
- **ibm_is_image** - Manage custom images
- **ibm_is_placement_group** - Manage placement groups
- **ibm_is_reservation** - Manage capacity reservations

## Quick Reference Table

| Module | Create | Read | Update | Delete | Info Module |
|--------|--------|------|--------|--------|-------------|
| ibm_is_vpc | ✓ | ✓ | ✓ | ✓ | ibm_is_vpcs_info |
| ibm_is_subnet | ✓ | ✓ | ✓ | ✓ | ibm_is_subnets_info |
| ibm_is_instance | ✓ | ✓ | ✓ | ✓ | ibm_is_instances_info |
| ibm_is_security_group | ✓ | ✓ | ✓ | ✓ | ibm_is_security_groups_info |
| ibm_is_load_balancer | ✓ | ✓ | ✓ | ✓ | ibm_is_load_balancers_info |
| ibm_is_volume | ✓ | ✓ | ✓ | ✓ | ibm_is_volumes_info |
| ibm_is_floating_ip | ✓ | ✓ | ✓ | ✓ | ibm_is_floating_ips_info |
| ibm_is_vpn_gateway | ✓ | ✓ | ✓ | ✓ | ibm_is_vpn_gateways_info |
| ibm_is_snapshot | ✓ | ✓ | ✓ | ✓ | ibm_is_snapshots_info |
| ibm_is_backup_policy | ✓ | ✓ | ✓ | ✓ | ibm_is_backup_policies_info |

## Common Parameters

All modules support these standard parameters:

```yaml
ibmcloud_api_key: string
  IBM Cloud API key (can use IC_API_KEY env var)

region: string (default: us-south)
  IBM Cloud region

resource_group: string
  Resource group ID

state: string (default: present)
  Desired state: present, absent

name: string
  Resource name (required for creation)

id: string
  Resource ID (required for updates/deletes)
```

## Usage Examples

### Create Complete VPC Infrastructure

```yaml
---
- name: Deploy VPC Infrastructure
  hosts: localhost
  tasks:
    # 1. Create VPC
    - name: Create VPC
      ibm_is_vpc:
        name: production-vpc
        region: us-south
        state: present
      register: vpc

    # 2. Create Subnet
    - name: Create Subnet
      ibm_is_subnet:
        name: web-subnet
        vpc: "{{ vpc.resource.id }}"
        zone: us-south-1
        ipv4_cidr_block: 10.240.0.0/24
        state: present
      register: subnet

    # 3. Create Security Group
    - name: Create Security Group
      ibm_is_security_group:
        name: web-sg
        vpc: "{{ vpc.resource.id }}"
        state: present
      register: sg

    # 4. Add Security Rules
    - name: Allow SSH
      ibm_is_security_group_rule:
        security_group: "{{ sg.resource.id }}"
        direction: inbound
        protocol: tcp
        port_min: 22
        port_max: 22
        remote: 0.0.0.0/0
        state: present

    # 5. Create Instance
    - name: Create Instance
      ibm_is_instance:
        name: web-server
        vpc: "{{ vpc.resource.id }}"
        zone: us-south-1
        profile: bx2-2x8
        image: ibm-ubuntu-20-04-minimal-amd64-1
        primary_network_interface:
          subnet: "{{ subnet.resource.id }}"
          security_groups:
            - "{{ sg.resource.id }}"
        state: present
```

### Create Load Balanced Application

```yaml
---
- name: Deploy Load Balanced App
  hosts: localhost
  tasks:
    - name: Create Load Balancer
      ibm_is_load_balancer:
        name: app-lb
        subnets:
          - "{{ subnet_id }}"
        is_public: true
        state: present
      register: lb

    - name: Create Backend Pool
      ibm_is_lb_pool:
        load_balancer: "{{ lb.resource.id }}"
        name: app-pool
        algorithm: round_robin
        protocol: http
        health_monitor:
          delay: 5
          max_retries: 2
          timeout: 2
          type: http
        state: present
      register: pool

    - name: Add Pool Members
      ibm_is_lb_pool_member:
        load_balancer: "{{ lb.resource.id }}"
        pool: "{{ pool.resource.id }}"
        port: 80
        target: "{{ item }}"
        state: present
      loop: "{{ instance_ids }}"

    - name: Create Listener
      ibm_is_lb_listener:
        load_balancer: "{{ lb.resource.id }}"
        protocol: http
        port: 80
        default_pool: "{{ pool.resource.id }}"
        state: present
```

### Backup and Snapshot Management

```yaml
---
- name: Configure Backups
  hosts: localhost
  tasks:
    - name: Create Backup Policy
      ibm_is_backup_policy:
        name: daily-backups
        match_resource_types:
          - volume
        state: present
      register: policy

    - name: Create Backup Plan
      ibm_is_backup_policy_plan:
        backup_policy: "{{ policy.resource.id }}"
        name: daily-plan
        cron_spec: "0 2 * * *"
        active: true
        state: present

    - name: Create Volume Snapshot
      ibm_is_snapshot:
        name: volume-snapshot-{{ ansible_date_time.epoch }}
        source_volume: "{{ volume_id }}"
        state: present
```

### VPN Configuration

```yaml
---
- name: Setup VPN
  hosts: localhost
  tasks:
    - name: Create IKE Policy
      ibm_is_ike_policy:
        name: ike-policy
        authentication_algorithm: sha256
        encryption_algorithm: aes256
        dh_group: 14
        ike_version: 2
        state: present
      register: ike

    - name: Create IPSec Policy
      ibm_is_ipsec_policy:
        name: ipsec-policy
        authentication_algorithm: sha256
        encryption_algorithm: aes256
        pfs: group_14
        state: present
      register: ipsec

    - name: Create VPN Gateway
      ibm_is_vpn_gateway:
        name: vpn-gateway
        subnet: "{{ subnet_id }}"
        mode: route
        state: present
      register: vpn

    - name: Create VPN Connection
      ibm_is_vpn_gateway_connection:
        vpn_gateway: "{{ vpn.resource.id }}"
        name: site-to-site
        peer_address: 203.0.113.1
        preshared_key: "{{ vault_psk }}"
        local_cidrs:
          - 10.240.0.0/24
        peer_cidrs:
          - 192.168.1.0/24
        state: present
```

## Module Development

All modules follow a consistent pattern:

```python
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ibm.cloudcollection.plugins.module_utils.ibm_cloud_sdk import (
    IBMCloudSDKModule,
    get_common_argument_spec
)

class MyModule(IBMCloudSDKModule):
    def run(self):
        # Module logic here
        pass

def main():
    argument_spec = get_common_argument_spec()
    argument_spec.update({
        # Module-specific parameters
    })
    
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True
    )
    
    my_module = MyModule(module)
    my_module.run()
```

## Testing Modules

```bash
# Check mode (dry run)
ansible-playbook playbook.yml --check

# Verbose output
ansible-playbook playbook.yml -vvv

# Syntax check
ansible-playbook playbook.yml --syntax-check

# List tasks
ansible-playbook playbook.yml --list-tasks
```

## Module Naming Convention

- **ibm_is_*** - VPC Infrastructure Services
- **ibm_cos_*** - Cloud Object Storage
- **ibm_iam_*** - Identity and Access Management
- **ibm_kms_*** - Key Management Service
- **ibm_database_*** - Cloud Databases

## Support and Documentation

- Module Documentation: `ansible-doc ibm_is_vpc`
- IBM Cloud API Docs: https://cloud.ibm.com/apidocs
- IBM VPC SDK: https://github.com/IBM/vpc-python-sdk
- Collection Repository: [GitHub URL]

## Version Compatibility

- Python: 3.10+
- Ansible Core: 2.14+
- IBM Cloud SDK Core: 3.20.0+
- IBM VPC SDK: 0.33.0+

## Contributing

To add new modules:

1. Use the module generator: `python tools/generate_modules.py`
2. Customize the generated module
3. Add tests and documentation
4. Submit a pull request

## License

BSD 2-Clause License

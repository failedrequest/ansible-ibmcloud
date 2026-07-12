# IBM Cloud Native Ansible Collection

A comprehensive, pure Python Ansible collection for managing IBM Cloud infrastructure and platform services. **No Terraform dependencies** - uses native IBM Cloud Python SDKs for direct API integration.

## 🎯 Features

- ✅ **72 Production-Ready Modules** covering VPC, Transit Gateway, Kubernetes Service, Platform services, and Info modules
- ✅ **Pure Python Implementation** - Direct IBM Cloud SDK integration
- ✅ **No Terraform Dependency** - Native API calls only
- ✅ **Idempotent Operations** - Safe to run multiple times
- ✅ **Check Mode Support** - Dry-run capability for all modules
- ✅ **Python 3.10+ Compatible** (tested up to 3.14)
- ✅ **Comprehensive Documentation** - Full examples and guides
- ✅ **Auto-Generated Modules** - Easy to extend

## 📦 Module Inventory

### VPC Infrastructure Services (42 modules)

#### Info Modules (4 modules)
- `ibm_is_vpc_info` - Retrieve VPC information
- `ibm_is_subnet_info` - Retrieve subnet information
- `ibm_is_virtual_network_interface_info` - Retrieve VNI information
- `ibm_is_image_info` - Retrieve image information

#### Core VPC (15 modules)
- `ibm_is_vpc` - Virtual Private Clouds
- `ibm_is_subnet` - VPC subnets
- `ibm_is_address_prefix` - Address prefixes
- `ibm_is_routing_table` - Routing tables
- `ibm_is_route` - Routes
- `ibm_is_security_group` - Security groups
- `ibm_is_security_group_rule` - Security rules
- `ibm_is_network_acl` - Network ACLs
- `ibm_is_public_gateway` - Public gateways
- `ibm_is_floating_ip` - Floating IPs
- `ibm_is_endpoint_gateway` - VPC endpoints
- `ibm_is_network_interface` - Network interfaces
- `ibm_is_virtual_network_interface` - Virtual network interfaces
- `ibm_is_flow_log` - Flow log collectors

#### Compute (8 modules)
- `ibm_is_instance` - Virtual server instances
- `ibm_is_instance_template` - Instance templates
- `ibm_is_instance_group` - Instance groups
- `ibm_is_instance_group_manager` - Auto-scaling managers
- `ibm_is_bare_metal_server` - Bare metal servers
- `ibm_is_bare_metal_server_network_interface` - Bare metal networking
- `ibm_is_dedicated_host_group` - Dedicated host groups
- `ibm_is_dedicated_host` - Dedicated hosts

#### Storage (7 modules)
- `ibm_is_volume` - Block storage volumes
- `ibm_is_snapshot` - Volume snapshots
- `ibm_is_snapshot_consistency_group` - Snapshot groups
- `ibm_is_backup_policy` - Backup policies
- `ibm_is_backup_policy_plan` - Backup plans
- `ibm_is_share` - File shares
- `ibm_is_share_mount_target` - Share mount targets

#### Load Balancing (4 modules)
- `ibm_is_load_balancer` - Load balancers
- `ibm_is_lb_listener` - LB listeners
- `ibm_is_lb_pool` - LB pools
- `ibm_is_lb_pool_member` - Pool members

#### VPN (5 modules)
- `ibm_is_vpn_gateway` - VPN gateways
- `ibm_is_vpn_gateway_connection` - VPN connections
- `ibm_is_vpn_server` - VPN servers
- `ibm_is_ike_policy` - IKE policies
- `ibm_is_ipsec_policy` - IPSec policies

#### Resource Management (3 modules)
- `ibm_is_ssh_key` - SSH keys
- `ibm_is_image` - Custom images
- `ibm_is_placement_group` - Placement groups
- `ibm_is_reservation` - Capacity reservations

### Transit Gateway (4 modules)
- `ibm_tg_gateway` - Transit Gateway instances
- `ibm_tg_connection` - Gateway connections (VPC, Direct Link, GRE)
- `ibm_tg_connection_prefix_filter` - Route filtering
- `ibm_tg_route_report` - Route reports

### Kubernetes Service (1 module)
- `ibm_ks_cluster_vni` - Attach/detach VNIs to ROKS clusters

### Platform Services (21 modules)

#### Cloud Object Storage (1 module)
- `ibm_cos_bucket` - COS buckets

#### Identity & Access Management (5 modules)
- `ibm_iam_access_group` - Access groups
- `ibm_iam_access_group_rule` - Dynamic rules
- `ibm_iam_service_id` - Service IDs
- `ibm_iam_api_key` - API keys
- `ibm_iam_policy` - Access policies

#### Resource Management (4 modules)
- `ibm_resource_group` - Resource groups
- `ibm_resource_instance` - Service instances
- `ibm_resource_key` - Service credentials
- `ibm_resource_binding` - Service bindings

#### Key Management (2 modules)
- `ibm_kms_key` - Encryption keys
- `ibm_kms_key_ring` - Key rings

#### Databases (2 modules)
- `ibm_database_instance` - Database deployments
- `ibm_database_user` - Database users

#### Container Registry (2 modules)
- `ibm_cr_namespace` - Registry namespaces
- `ibm_cr_retention_policy` - Retention policies

#### Event Notifications (3 modules)
- `ibm_en_destination` - Notification destinations
- `ibm_en_topic` - Notification topics
- `ibm_en_subscription` - Topic subscriptions

#### Secrets Manager (2 modules)
- `ibm_sm_secret_group` - Secret groups
- `ibm_sm_secret` - Secrets

## 🚀 Quick Start

### Installation

#### Option 1: Install from Pre-built Collection (Recommended)

> **Note:** This collection uses version 2.x to avoid conflicts with the official IBM Cloud Ansible collection. The version bump ensures both collections can coexist if needed.


```bash
# Install Python dependencies
pip install -r requirements.txt

# Install the collection tarball
ansible-galaxy collection install ibm-cloudcollection-2.0.5.tar.gz

# Set your IBM Cloud API key
export IC_API_KEY="your-api-key-here"
```

#### Option 2: Build and Install from Source

```bash
# Clone the repository
git clone <repository-url>
cd ansible-ibmcloud

# Install Python dependencies
pip install -r requirements.txt

# Build the collection
ansible-galaxy collection build

# Install the built collection
ansible-galaxy collection install ibm-cloudcollection-2.0.5.tar.gz

# Set your IBM Cloud API key
export IC_API_KEY="your-api-key-here"
```

#### Option 3: Development Setup

```bash
# Clone the repository
git clone <repository-url>
cd ansible-ibmcloud

# Run setup script (creates virtual environment)
chmod +x setup.sh
./setup.sh

# Activate virtual environment
source build/venv/bin/activate

# Set your IBM Cloud API key
export IC_API_KEY="your-api-key-here"
```

### Configuration

Set your IBM Cloud API key:

```bash
export IC_API_KEY="your-api-key-here"
```

Or use in playbooks:

```yaml
vars:
  ibmcloud_api_key: "{{ lookup('env', 'IC_API_KEY') }}"
```

### Basic Usage

```yaml
---
- name: Create VPC Infrastructure
  hosts: localhost
  tasks:
    - name: Create VPC
      ibm_is_vpc:
        name: production-vpc
        region: us-south
        state: present
      register: vpc

    - name: Create Subnet
      ibm_is_subnet:
        name: web-subnet
        vpc: "{{ vpc.resource.id }}"
        zone: us-south-1
        ipv4_cidr_block: 10.240.0.0/24
        state: present
      register: subnet

    - name: Create Instance
      ibm_is_instance:
        name: web-server
        vpc: "{{ vpc.resource.id }}"
        zone: us-south-1
        profile: bx2-2x8
        image: ibm-ubuntu-20-04-minimal-amd64-1
        primary_network_interface:
          subnet: "{{ subnet.resource.id }}"
        state: present
```

## 📚 Documentation

- **[Getting Started Guide](docs/GETTING_STARTED.md)** - Installation and basic usage
- **[VPC Module Reference](docs/MODULE_REFERENCE.md)** - Complete VPC module documentation
- **[Transit Gateway Guide](docs/TRANSIT_GATEWAY.md)** - Transit Gateway networking
- **[Platform Services Guide](docs/PLATFORM_SERVICES.md)** - Platform service modules
- **[API Reference](docs/API_REFERENCE.md)** - Detailed API documentation

## 🏗️ Architecture

```
ansible-ibmcloud/
├── plugins/
│   ├── modules/              # 63 Ansible modules
│   │   ├── ibm_is_*.py      # VPC Infrastructure (42)
│   │   ├── ibm_cos_*.py     # Cloud Object Storage (1)
│   │   ├── ibm_iam_*.py     # IAM (5)
│   │   ├── ibm_resource_*.py # Resource Management (4)
│   │   ├── ibm_kms_*.py     # Key Management (2)
│   │   ├── ibm_database_*.py # Databases (2)
│   │   ├── ibm_cr_*.py      # Container Registry (2)
│   │   ├── ibm_en_*.py      # Event Notifications (3)
│   │   └── ibm_sm_*.py      # Secrets Manager (2)
│   └── module_utils/
│       └── ibm_cloud_sdk.py # Core SDK integration
├── tools/
│   ├── generate_modules.py          # VPC module generator
│   ├── generate_extended_modules.py # Extended VPC generator
│   └── generate_platform_modules.py # Platform service generator
├── examples/                 # Example playbooks
├── docs/                    # Documentation
└── tests/                   # Test suite
```

## 🔧 Requirements

### Python Dependencies
- Python 3.10 or higher
- ibm-vpc >= 0.33.0
- ibm-platform-services >= 0.50.0
- ibm-cloud-sdk-core >= 3.20.0
- ansible-core >= 2.14

### System Requirements
- Linux, macOS, or Windows with WSL
- IBM Cloud account with API key
- Network access to IBM Cloud APIs

## 💡 Examples

### Complete VPC Infrastructure

```yaml
---
- name: Deploy Complete VPC Infrastructure
  hosts: localhost
  vars:
    region: us-south
    zone: us-south-1
  
  tasks:
    - name: Create VPC
      ibm_is_vpc:
        name: production-vpc
        region: "{{ region }}"
        state: present
      register: vpc

    - name: Create Security Group
      ibm_is_security_group:
        name: web-sg
        vpc: "{{ vpc.resource.id }}"
        state: present
      register: sg

    - name: Allow HTTPS
      ibm_is_security_group_rule:
        security_group: "{{ sg.resource.id }}"
        direction: inbound
        protocol: tcp
        port_min: 443
        port_max: 443
        remote: 0.0.0.0/0
        state: present

    - name: Create Subnet
      ibm_is_subnet:
        name: web-subnet
        vpc: "{{ vpc.resource.id }}"
        zone: "{{ zone }}"
        ipv4_cidr_block: 10.240.0.0/24
        state: present
      register: subnet

    - name: Create Load Balancer
      ibm_is_load_balancer:
        name: web-lb
        subnets:
          - "{{ subnet.resource.id }}"
        is_public: true
        state: present
```

### Platform Services Setup

```yaml
---
- name: Setup Platform Services
  hosts: localhost
  tasks:
    - name: Create Resource Group
      ibm_resource_group:
        name: production
        account_id: "{{ account_id }}"
        state: present
      register: rg

    - name: Create KMS Instance
      ibm_resource_instance:
        name: production-kms
        target: us-south
        resource_group: "{{ rg.resource.id }}"
        resource_plan_id: "{{ kms_plan_id }}"
        state: present
      register: kms

    - name: Create Encryption Key
      ibm_kms_key:
        name: data-key
        instance_id: "{{ kms.resource.guid }}"
        extractable: false
        state: present

    - name: Create Database
      ibm_database_instance:
        name: production-db
        service_id: databases-for-postgresql
        plan_id: standard
        location: us-south
        version: "14"
        state: present
```

## 🧪 Testing

```bash
# Syntax check
ansible-playbook playbook.yml --syntax-check

# Check mode (dry run)
ansible-playbook playbook.yml --check

# Run with verbose output
ansible-playbook playbook.yml -vvv

# List all tasks
ansible-playbook playbook.yml --list-tasks
```

## 🔨 Development

### Adding New Modules

The collection includes generators for creating new modules:

```bash
# Generate VPC modules
python tools/generate_modules.py

# Generate extended VPC modules
python tools/generate_extended_modules.py

# Generate platform service modules
python tools/generate_platform_modules.py
```

### Module Structure

All modules follow a consistent pattern:

```python
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ibm.cloudcollection.plugins.module_utils.ibm_cloud_sdk import (
    IBMCloudSDKModule,
    get_common_argument_spec
)

class MyModule(IBMCloudSDKModule):
    def run(self):
        # Module implementation
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

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Update documentation
5. Submit a pull request

## 📝 License

BSD 2-Clause License

See [LICENSE](LICENSE) for full details.

## 🆘 Support

- **Documentation**: See [docs/](docs/) directory
- **Issues**: Report bugs via GitHub Issues
- **IBM Cloud Docs**: https://cloud.ibm.com/docs
- **IBM Cloud API**: https://cloud.ibm.com/apidocs

## 🎯 Roadmap

- [x] Add info modules for read-only operations (VPC, Subnet, VNI, Image)
- [x] Implement Kubernetes/OpenShift modules (VNI attachment)
- [ ] Add Cloud Functions modules
- [ ] Implement Code Engine modules
- [ ] Add Satellite modules
- [ ] Expand test coverage
- [ ] Add CI/CD pipeline examples

## 📊 Module Statistics

| Category | Modules | Status |
|----------|---------|--------|
| VPC Infrastructure | 42 | ✅ Complete |
| VPC Info Modules | 4 | ✅ Complete |
| Transit Gateway | 4 | ✅ Complete |
| Kubernetes Service | 1 | ✅ Complete |
| Platform Services | 21 | ✅ Complete |
| **Total** | **72** | **✅ Production Ready** |

## 🔐 Security

- All modules support IBM Cloud IAM authentication
- API keys should be stored securely (use Ansible Vault)
- Check mode available for safe testing
- No credentials stored in module code
- Supports service IDs and API keys

## ⚡ Performance

- Direct SDK calls (no Terraform overhead)
- Efficient API usage with proper pagination
- Idempotent operations minimize API calls
- Parallel execution support via Ansible

## 🌍 Supported Regions

All IBM Cloud regions are supported:
- us-south, us-east
- eu-gb, eu-de
- jp-tok, jp-osa
- au-syd
- ca-tor
- br-sao

## 📈 Version History

- **v2.0.5** - Version bump to avoid conflicts with official IBM collection, bug fixes and VPC routes support
  - 42 VPC Infrastructure modules
  - 4 VPC Info modules (read-only resource lookups)
  - 4 Transit Gateway modules
  - 1 Kubernetes Service module
  - 21 Platform service modules
  - Pure Python implementation
  - Complete documentation
  - No shell command dependencies for resource lookups

---

**Built with ❤️ for the IBM Cloud community**
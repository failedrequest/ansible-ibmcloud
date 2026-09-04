# IBM Cloud Native Ansible Collection

A comprehensive, pure Python Ansible collection for managing IBM Cloud infrastructure and platform services. **No Terraform dependencies** — uses native IBM Cloud Python SDKs for direct API integration.

## 🎯 Features

- ✅ **74 Production-Ready Modules** covering VPC, Transit Gateway, Kubernetes Service, Platform services, and Info modules
- ✅ **Pure Python Implementation** — Direct IBM Cloud SDK integration
- ✅ **No Terraform Dependency** — Native API calls only
- ✅ **Idempotent Operations** — Safe to run multiple times
- ✅ **Check Mode Support** — Dry-run capability for all modules
- ✅ **module_defaults group support** — Set `ibmcloud_api_key` and `region` once for all tasks
- ✅ **Python 3.9–3.14 Compatible** (see requirements.txt for per-version ansible-core pins)
- ✅ **Comprehensive Documentation** — Full examples and guides

## 🚀 Installation

### Step 1 — Install Python dependencies

```bash
pip install ibm-cloud-sdk-core ibm-vpc ibm-platform-services ibm-cloud-networking-services
```

Or using the bundled requirements file (if you have the repo):

```bash
pip install -r requirements.txt
```

### Step 2 — Install the collection

```bash
ansible-galaxy collection install ibm-cloudcollection-2.0.18.tar.gz
```

> **Upgrading?** Add `--force` to overwrite a previous version:
> ```bash
> ansible-galaxy collection install --force ibm-cloudcollection-2.0.18.tar.gz
> ```

### Step 3 — Set your IBM Cloud API key

```bash
export IC_API_KEY="your-api-key-here"
```

### Step 4 — Verify

```bash
ansible-galaxy collection list | grep ibm
# ibm.cloudcollection   2.0.18
```

---

## ⚡ Quick Start

```yaml
---
- name: Create IBM Cloud VPC
  hosts: localhost
  gather_facts: false

  module_defaults:
    group/ibm.cloudcollection.ibm:
      ibmcloud_api_key: "{{ lookup('env', 'IC_API_KEY') }}"
      region: us-south

  tasks:
    - name: Create VPC
      ibm.cloudcollection.ibm_is_vpc:
        name: my-vpc
        state: present
      register: vpc

    - name: Create Subnet
      ibm.cloudcollection.ibm_is_subnet:
        name: my-subnet
        vpc: "{{ vpc.resource.id }}"
        zone: us-south-1
        ipv4_cidr_block: 10.240.0.0/24
        state: present
```

Run it:

```bash
ansible-playbook my-vpc.yml
```

---

## 📦 Module Inventory

### VPC Infrastructure Services (44 modules)

#### Info Modules (5 modules)
- `ibm_is_vpc_info` — Retrieve VPC information (with server-side name filter)
- `ibm_is_subnet_info` — Retrieve subnet information (with VPC filter + pagination)
- `ibm_is_virtual_network_interface_info` — Retrieve VNI information (with resource_group filter + pagination)
- `ibm_is_image_info` — Retrieve image information
- `ibm_is_subnet_reserved_ip_info` — List reserved IPs in a subnet (with owner filter)

#### Core VPC (15 modules)
- `ibm_is_vpc` — Virtual Private Clouds
- `ibm_is_subnet` — VPC subnets
- `ibm_is_address_prefix` — Address prefixes
- `ibm_is_routing_table` — Routing tables
- `ibm_is_route` — Routes
- `ibm_is_security_group` — Security groups
- `ibm_is_security_group_rule` — Security rules
- `ibm_is_network_acl` — Network ACLs
- `ibm_is_public_gateway` — Public gateways
- `ibm_is_floating_ip` — Floating IPs
- `ibm_is_endpoint_gateway` — VPC endpoints
- `ibm_is_network_interface` — Network interfaces
- `ibm_is_virtual_network_interface` — Virtual network interfaces (bind by reserved IP ID)
- `ibm_is_subnet_reserved_ip` — Subnet reserved IPs (list mode + owner filter)
- `ibm_is_flow_log` — Flow log collectors

#### Compute (8 modules)
- `ibm_is_instance` — Virtual server instances
- `ibm_is_instance_template` — Instance templates
- `ibm_is_instance_group` — Instance groups
- `ibm_is_instance_group_manager` — Auto-scaling managers
- `ibm_is_bare_metal_server` — Bare metal servers
- `ibm_is_bare_metal_server_network_interface` — Bare metal networking
- `ibm_is_dedicated_host_group` — Dedicated host groups
- `ibm_is_dedicated_host` — Dedicated hosts

#### Storage (7 modules)
- `ibm_is_volume` — Block storage volumes
- `ibm_is_snapshot` — Volume snapshots
- `ibm_is_snapshot_consistency_group` — Snapshot groups
- `ibm_is_backup_policy` — Backup policies
- `ibm_is_backup_policy_plan` — Backup plans
- `ibm_is_share` — File shares
- `ibm_is_share_mount_target` — Share mount targets

#### Load Balancing (4 modules)
- `ibm_is_load_balancer` — Load balancers
- `ibm_is_lb_listener` — LB listeners
- `ibm_is_lb_pool` — LB pools
- `ibm_is_lb_pool_member` — Pool members

#### VPN (5 modules)
- `ibm_is_vpn_gateway` — VPN gateways
- `ibm_is_vpn_gateway_connection` — VPN connections
- `ibm_is_vpn_server` — VPN servers
- `ibm_is_ike_policy` — IKE policies
- `ibm_is_ipsec_policy` — IPSec policies

#### Resource Management (4 modules)
- `ibm_is_ssh_key` — SSH keys
- `ibm_is_image` — Custom images
- `ibm_is_placement_group` — Placement groups
- `ibm_is_reservation` — Capacity reservations

### Transit Gateway (4 modules)
- `ibm_tg_gateway` — Transit Gateway instances
- `ibm_tg_connection` — Gateway connections (VPC, Direct Link, GRE)
- `ibm_tg_connection_prefix_filter` — Route filtering
- `ibm_tg_route_report` — Route reports

### Kubernetes Service (1 module)
- `ibm_ks_cluster_vni` — Attach/detach VNIs to ROKS clusters (bare metal + VLAN support)

### Platform Services (21 modules)

#### Cloud Object Storage (1 module)
- `ibm_cos_bucket` — COS buckets

#### Identity & Access Management (5 modules)
- `ibm_iam_access_group` — Access groups
- `ibm_iam_access_group_rule` — Dynamic rules
- `ibm_iam_service_id` — Service IDs
- `ibm_iam_api_key` — API keys
- `ibm_iam_policy` — Access policies

#### Resource Management (4 modules)
- `ibm_resource_group` — Resource groups
- `ibm_resource_instance` — Service instances
- `ibm_resource_key` — Service credentials
- `ibm_resource_binding` — Service bindings

#### Key Management (2 modules)
- `ibm_kms_key` — Encryption keys
- `ibm_kms_key_ring` — Key rings

#### Databases (2 modules)
- `ibm_database_instance` — Database deployments
- `ibm_database_user` — Database users

#### Container Registry (2 modules)
- `ibm_cr_namespace` — Registry namespaces
- `ibm_cr_retention_policy` — Retention policies

#### Event Notifications (3 modules)
- `ibm_en_destination` — Notification destinations
- `ibm_en_topic` — Notification topics
- `ibm_en_subscription` — Topic subscriptions

#### Secrets Manager (2 modules)
- `ibm_sm_secret_group` — Secret groups
- `ibm_sm_secret` — Secrets

---

## 🔑 Authentication

### Recommended: environment variable

```bash
export IC_API_KEY="your-ibm-cloud-api-key"
```

### In playbooks via `module_defaults` (apply to all tasks at once)

```yaml
module_defaults:
  group/ibm.cloudcollection.ibm:
    ibmcloud_api_key: "{{ lookup('env', 'IC_API_KEY') }}"
    region: us-south
```

### Ansible Vault (most secure)

```bash
ansible-vault create secrets.yml
# Add: ibmcloud_api_key: your-key
ansible-playbook playbook.yml --ask-vault-pass
```

---

## 📚 Documentation

- **[Installation Guide](docs/INSTALLATION.md)** — Full installation and configuration
- **[Getting Started](docs/GETTING_STARTED.md)** — Your first playbook
- **[Quick Start](docs/QUICK_START.md)** — 5-minute guide
- **[Module Reference](docs/MODULE_REFERENCE.md)** — Complete module documentation
- **[API Reference](docs/API_REFERENCE.md)** — Detailed API documentation

---

## 🔧 Requirements

| Requirement | Version |
|-------------|---------|
| Python | 3.9–3.14 |
| ansible-core | 2.16.x (Python 3.9) · 2.21.x (Python 3.10+) |
| ibm-vpc | ≥ 0.35.0 |
| ibm-cloud-sdk-core | ≥ 3.26.0 |
| ibm-platform-services | ≥ 0.75.0 |
| ibm-cloud-networking-services | ≥ 0.34.0 |

---

## 🌍 Supported Regions

`us-south` · `us-east` · `eu-gb` · `eu-de` · `jp-tok` · `jp-osa` · `au-syd` · `ca-tor` · `br-sao`

---

## 📊 Module Statistics

| Category | Modules | Status |
|----------|---------|--------|
| VPC Infrastructure | 39 | ✅ Complete |
| VPC Info Modules | 5 | ✅ Complete |
| Transit Gateway | 4 | ✅ Complete |
| Kubernetes Service | 1 | ✅ Complete |
| Platform Services | 21 | ✅ Complete |
| **Total** | **70** | **✅ Production Ready** |

---

## 📈 Version History

- **v2.0.18** — Staging / non-production environment support; Python 3.9–3.14 compatibility
  - Fix: all 48 `ibm_is_*` modules now read `IBMCLOUD_IS_NG_API_ENDPOINT` for the VPC URL instead of hardcoding `iaas.cloud.ibm.com`
  - Fix: `IAMAuthenticator` reads `IBMCLOUD_IAM_API_ENDPOINT` / `IC_IAM_TOKEN_URL` to override the IAM token endpoint
  - Fix: `ibm_is_subnet_info` VPC ID detection — replaced `startswith('r0')` with a full `rNNN-<uuid>` regex so staging IDs (e.g. `r134-...`) are not mistaken for names
  - Fix: `requirements.txt` uses `python_version` markers to install ansible-core 2.16 on Python 3.9 and 2.21 on Python 3.10+, resolving `ast.Str` removal incompatibility with Python 3.14
  - Docs: new troubleshooting guide for `test.cloud.ibm.com`, env var reference in INSTALLATION.md and GETTING_STARTED.md

- **v2.0.13** — Fix `ibm_is_routing_table`; rewrite test-vpc-routes playbook

- **v2.0.12** — Fix `ibm_is_virtual_network_interface` delete: singular → plural SDK method name

- **v2.0.11** — Fix `ibm_is_vpc_info`: remove `name=` param incompatible with ibm-vpc SDK 0.35; client-side filter with full pagination

- **v2.0.10** — Fix `found` key missing from result; fix empty-subnet guard

- **v2.0.9** — `meta/runtime.yml` + `module_defaults` group support; reserved IP list mode; VNI bare metal attach fixes
  - New: `meta/runtime.yml` declaring `action_groups.ibm` — resolves `could not resolve the module_defaults group ibm.cloudcollection.ibm`
  - New: `ibm_is_subnet_reserved_ip_info` — read-only list module with `owner` filter
  - Fix: `ibm_is_virtual_network_interface` — add `primary_ip_id`; fix async DELETE poll; singular SDK method
  - Fix: `ibm_is_subnet_reserved_ip` — remove `required_one_of`, add list mode + `owner` filter
  - Fix: `ibm_ks_cluster_vni` — `--cluster-id` flag; `baremetal` subcommand; `-f -q` on detach; `vni ls` for idempotency check
  - Fix: `ibm_is_vpc_info` — server-side `name=` filter eliminates cross-account VPC collision
  - Improvement: `ibm_is_subnet_info`, `ibm_is_vpc_info`, `ibm_is_virtual_network_interface_info` — full pagination

- **v2.0.8** — Add `meta/runtime.yml` (intermediate build, superseded by 2.0.9)

- **v2.0.6** — Add standalone `ibm_is_subnet_reserved_ip` module; 73 total modules; 14-test unit suite

- **v2.0.5** — Version bump to avoid conflicts with official IBM collection; VPC routes support; 72 modules

---

## 🔐 Security

- All modules use IBM Cloud IAM authentication
- API keys should be stored in Ansible Vault or environment variables
- Check mode available for safe dry-run testing
- No credentials stored in module code

---

## 📝 License

BSD 2-Clause License — see [LICENSE](LICENSE) for full details.

---

**Built with ❤️ for the IBM Cloud community**

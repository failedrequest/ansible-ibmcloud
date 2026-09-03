# Getting Started — IBM Cloud Ansible Collection v2.0.9

## Install in two commands

```bash
pip install "ibm-cloud-sdk-core>=3.20.0" "ibm-vpc>=0.33.0" \
            "ibm-platform-services>=0.75.0" "ibm-cloud-networking-services>=0.34.0"

ansible-galaxy collection install ibm-cloudcollection-2.0.9.tar.gz
```

Full installation details: [INSTALLATION.md](INSTALLATION.md)

---

## Set your API key

```bash
export IC_API_KEY="your-ibm-cloud-api-key"
```

**How to get an API key:**
1. Log in to [IBM Cloud](https://cloud.ibm.com)
2. Go to **Manage → Access (IAM) → API keys**
3. Click **Create an IBM Cloud API key** and copy it immediately

---

## Use `module_defaults` to avoid repeating credentials

Add this to every playbook once and all collection tasks inherit it automatically:

```yaml
module_defaults:
  group/ibm.cloudcollection.ibm:
    ibmcloud_api_key: "{{ lookup('env', 'IC_API_KEY') }}"
    region: us-south
```

---

## Your first playbook

```yaml
---
- name: Create my first IBM Cloud VPC
  hosts: localhost
  gather_facts: false

  module_defaults:
    group/ibm.cloudcollection.ibm:
      ibmcloud_api_key: "{{ lookup('env', 'IC_API_KEY') }}"
      region: us-south

  tasks:
    - name: Create VPC
      ibm.cloudcollection.ibm_is_vpc:
        name: my-first-vpc
        state: present
      register: vpc

    - name: Show VPC ID
      ansible.builtin.debug:
        msg: "VPC created: {{ vpc.resource.id }}"
```

**Dry run first (no changes made):**
```bash
ansible-playbook my-first-vpc.yml --check
```

**Create for real:**
```bash
ansible-playbook my-first-vpc.yml
```

---

## Common patterns

### Look up an existing resource by name

```yaml
- name: Get VPC info
  ibm.cloudcollection.ibm_is_vpc_info:
    name: my-existing-vpc
  register: vpc_info

- name: Use the VPC ID
  ansible.builtin.debug:
    msg: "{{ vpc_info.resource.id }}"
```

### Create a full VPC stack

```yaml
---
- name: VPC stack
  hosts: localhost
  gather_facts: false

  module_defaults:
    group/ibm.cloudcollection.ibm:
      ibmcloud_api_key: "{{ lookup('env', 'IC_API_KEY') }}"
      region: us-south

  tasks:
    - name: Create VPC
      ibm.cloudcollection.ibm_is_vpc:
        name: prod-vpc
        state: present
      register: vpc

    - name: Create security group
      ibm.cloudcollection.ibm_is_security_group:
        name: prod-sg
        vpc: "{{ vpc.resource.id }}"
        state: present
      register: sg

    - name: Allow inbound HTTPS
      ibm.cloudcollection.ibm_is_security_group_rule:
        security_group: "{{ sg.resource.id }}"
        direction: inbound
        protocol: tcp
        port_min: 443
        port_max: 443
        state: present

    - name: Create subnet
      ibm.cloudcollection.ibm_is_subnet:
        name: prod-subnet
        vpc: "{{ vpc.resource.id }}"
        zone: us-south-1
        ipv4_cidr_block: 10.240.0.0/24
        state: present
      register: subnet
```

### Reserve IPs and bind to VNIs

```yaml
    - name: Reserve an IP
      ibm.cloudcollection.ibm_is_subnet_reserved_ip:
        subnet_id: "{{ subnet.resource.id }}"
        name: vni-primary-ip
        state: present
      register: rip

    - name: Create VNI bound to the reserved IP
      ibm.cloudcollection.ibm_is_virtual_network_interface:
        name: my-vni
        subnet: "{{ subnet.resource.id }}"
        primary_ip_id: "{{ rip.resource.id }}"
        state: present
```

### List reserved IPs with owner filter

```yaml
    - name: List only user-created reserved IPs
      ibm.cloudcollection.ibm_is_subnet_reserved_ip_info:
        subnet_id: "{{ subnet.resource.id }}"
        owner: user
      register: user_rips

    - name: Build name → ID map
      ansible.builtin.set_fact:
        rip_id_map: "{{ rip_id_map | default({}) | combine({item.name: item.id}) }}"
      loop: "{{ user_rips.resources }}"
```

---

## Check mode (dry run)

Every module supports `--check`. Use it before any destructive run:

```bash
ansible-playbook my-playbook.yml --check
```

---

## Regions

| Code | Location |
|------|----------|
| `us-south` | Dallas |
| `us-east` | Washington DC |
| `eu-gb` | London |
| `eu-de` | Frankfurt |
| `jp-tok` | Tokyo |
| `jp-osa` | Osaka |
| `au-syd` | Sydney |
| `ca-tor` | Toronto |
| `br-sao` | São Paulo |

---

## Troubleshooting

### Module not found
```bash
ansible-galaxy collection list | grep ibm
# If missing: ansible-galaxy collection install ibm-cloudcollection-2.0.9.tar.gz
```

### Authentication error
```bash
echo $IC_API_KEY   # must be non-empty
```

If running against `test.cloud.ibm.com`, see
[Troubleshooting: test.cloud.ibm.com](troubleshooting-api-key-old-venv.md).

### `module_defaults group` error
You have a version older than 2.0.9 installed. Upgrade:
```bash
ansible-galaxy collection install --force ibm-cloudcollection-2.0.17.tar.gz
```

### Non-production / staging environment

Set the IBM Cloud CLI endpoint variables before running the playbook:

```bash
export IBMCLOUD_IAM_API_ENDPOINT=https://iam.test.cloud.ibm.com
export IBMCLOUD_IS_NG_API_ENDPOINT=https://us-south-stage01.iaasdev.cloud.ibm.com/v1
```

No playbook changes required. See
[Troubleshooting: test.cloud.ibm.com](troubleshooting-api-key-old-venv.md) for
details.

---

## Next steps

- **[Quick Start](QUICK_START.md)** — 5-minute guide
- **[Module Reference](MODULE_REFERENCE.md)** — Full module documentation
- **Examples**: `examples/` in the collection
- **IBM Cloud Docs**: https://cloud.ibm.com/docs

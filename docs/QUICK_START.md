# Quick Start — IBM Cloud Ansible Collection v2.0.9

Get up and running in 5 minutes.

---

## 1 — Install

```bash
# Install Python dependencies
pip install "ibm-cloud-sdk-core>=3.20.0" "ibm-vpc>=0.33.0" \
            "ibm-platform-services>=0.75.0" "ibm-cloud-networking-services>=0.34.0"

# Install the collection
ansible-galaxy collection install ibm-cloudcollection-2.0.9.tar.gz

# Verify
ansible-galaxy collection list | grep ibm
# ibm.cloudcollection   2.0.9
```

---

## 2 — Set your API key

```bash
export IC_API_KEY="your-ibm-cloud-api-key"
```

---

## 3 — Write a playbook

Save as `my-vpc.yml`:

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

    - name: Create subnet
      ibm.cloudcollection.ibm_is_subnet:
        name: my-subnet
        vpc: "{{ vpc.resource.id }}"
        zone: us-south-1
        ipv4_cidr_block: 10.240.0.0/24
        state: present

    - name: Create security group
      ibm.cloudcollection.ibm_is_security_group:
        name: my-sg
        vpc: "{{ vpc.resource.id }}"
        state: present
```

---

## 4 — Run it

```bash
# Dry run — see what would happen, no changes made
ansible-playbook my-vpc.yml --check

# Create for real
ansible-playbook my-vpc.yml
```

---

## Key concepts

### `module_defaults` — set credentials once

```yaml
module_defaults:
  group/ibm.cloudcollection.ibm:
    ibmcloud_api_key: "{{ lookup('env', 'IC_API_KEY') }}"
    region: us-south
```

Every collection module task inherits `ibmcloud_api_key` and `region` automatically.

### Fully Qualified Collection Names (FQCN)

```yaml
ibm.cloudcollection.ibm_is_vpc:   # explicit — always works
ibm_is_vpc:                        # short name — works inside collections: block
```

### Idempotency

All modules are idempotent. Running the same playbook twice produces no changes
on the second run if the desired state already exists.

---

## Common commands

```bash
# List all installed collections
ansible-galaxy collection list

# View built-in module documentation
ansible-doc ibm.cloudcollection.ibm_is_vpc
ansible-doc ibm.cloudcollection.ibm_is_subnet

# Run with verbose output
ansible-playbook my-vpc.yml -v

# Run specific tasks by tag
ansible-playbook my-vpc.yml --tags create

# List all tasks without running them
ansible-playbook my-vpc.yml --list-tasks
```

---

## Upgrading

```bash
ansible-galaxy collection install --force ibm-cloudcollection-2.0.9.tar.gz
```

---

## More reading

- **[Installation Guide](INSTALLATION.md)** — full install, troubleshooting, vault setup
- **[Getting Started](GETTING_STARTED.md)** — common patterns and examples
- **[Module Reference](MODULE_REFERENCE.md)** — every parameter documented

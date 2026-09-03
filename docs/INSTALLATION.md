# Installation Guide — IBM Cloud Ansible Collection v2.0.9

## Prerequisites

| Requirement | Version |
|-------------|---------|
| Python | 3.10 or higher |
| ansible-core | ≥ 2.14 |
| pip | current |
| IBM Cloud account | API key required |

---

## Install from the Pre-built Tarball

This is the only installation method you need. The collection ships as a
single self-contained tarball — no cloning, no building, no toolchain required.

### 1 — Install Python dependencies

```bash
pip install \
  "ibm-cloud-sdk-core>=3.20.0" \
  "ibm-vpc>=0.33.0" \
  "ibm-platform-services>=0.75.0" \
  "ibm-cloud-networking-services>=0.34.0"
```

### 2 — Install the collection

```bash
ansible-galaxy collection install ibm-cloudcollection-2.0.9.tar.gz
```

The collection installs to:
```
~/.ansible/collections/ansible_collections/ibm/cloudcollection/
```

**Upgrading from a previous version:**
```bash
ansible-galaxy collection install --force ibm-cloudcollection-2.0.9.tar.gz
```

### 3 — Set your IBM Cloud API key

```bash
export IC_API_KEY="your-ibm-cloud-api-key"
```

Add this to your shell profile (`~/.zshrc`, `~/.bashrc`) to persist it.

### 4 — Verify the installation

```bash
# Confirm the collection is installed
ansible-galaxy collection list | grep ibm
# Expected: ibm.cloudcollection   2.0.9

# View a module's built-in documentation
ansible-doc ibm.cloudcollection.ibm_is_vpc
```

---

## Configuration

### API Key — three options

**Option A: Environment variable (recommended)**
```bash
export IC_API_KEY="your-ibm-cloud-api-key"
```

**Option B: `module_defaults` in your playbook (apply to every task at once)**
```yaml
module_defaults:
  group/ibm.cloudcollection.ibm:
    ibmcloud_api_key: "{{ lookup('env', 'IC_API_KEY') }}"
    region: us-south
```

**Option C: Ansible Vault (most secure)**
```bash
# Create an encrypted secrets file
ansible-vault create secrets.yml
# Add inside: ibmcloud_api_key: your-ibm-cloud-api-key

# Reference it in your playbook
vars_files:
  - secrets.yml

# Run with vault password prompt
ansible-playbook playbook.yml --ask-vault-pass
```

### ansible.cfg (optional)

```ini
[defaults]
collections_paths = ~/.ansible/collections
```

---

## First Playbook

Save this as `test-install.yml` and run it to confirm everything works:

```yaml
---
- name: Verify IBM Cloud collection is ready
  hosts: localhost
  gather_facts: false

  module_defaults:
    group/ibm.cloudcollection.ibm:
      ibmcloud_api_key: "{{ lookup('env', 'IC_API_KEY') }}"
      region: us-south

  tasks:
    - name: List VPCs (check mode — no changes made)
      ibm.cloudcollection.ibm_is_vpc_info:
      register: vpcs
      check_mode: false

    - name: Show result
      ansible.builtin.debug:
        msg: "Collection working — found {{ vpcs.resources | default([]) | length }} VPC(s)"
```

```bash
ansible-playbook test-install.yml
```

---

## Troubleshooting

### `could not resolve the module_defaults group ibm.cloudcollection.ibm`

Your installed version is older than 2.0.9. Reinstall:
```bash
ansible-galaxy collection install --force ibm-cloudcollection-2.0.9.tar.gz
```

### `ModuleNotFoundError: No module named 'ibm_vpc'`

Python dependencies are missing:
```bash
pip install "ibm-vpc>=0.33.0" "ibm-cloud-sdk-core>=3.20.0"
```

### `ERROR! couldn't resolve module/action 'ibm.cloudcollection.ibm_is_vpc'`

Collection is not installed or installed to a different Python environment:
```bash
# Check where ansible is running from
which ansible-playbook

# Check which collections it sees
ansible-galaxy collection list | grep ibm

# Reinstall against the correct Python/pip
ansible-galaxy collection install ibm-cloudcollection-2.0.9.tar.gz
```

### Authentication errors (401 / missing API key)

```bash
# Verify the key is exported in the current shell
echo $IC_API_KEY

# Test the key directly
curl -s -X GET \
  "https://iam.cloud.ibm.com/identity/.well-known/openid-configuration" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['issuer'])"
```

---

## Upgrading

```bash
ansible-galaxy collection install --force ibm-cloudcollection-2.0.9.tar.gz
```

## Uninstalling

```bash
rm -rf ~/.ansible/collections/ansible_collections/ibm/cloudcollection
```

---

## Environment Variables Reference

| Variable | Description | Required |
|----------|-------------|----------|
| `IC_API_KEY` | IBM Cloud API key | Yes (unless passed inline) |
| `IBMCLOUD_API_KEY` | Alternate name for IBM Cloud API key | No |
| `IBMCLOUD_IAM_API_ENDPOINT` | Override IAM token endpoint (e.g. for `test.cloud.ibm.com`) | No |
| `IC_IAM_TOKEN_URL` | Alternate name for IAM endpoint override | No |
| `IBMCLOUD_IS_NG_API_ENDPOINT` | Override VPC/IS API endpoint (IBM Cloud CLI standard) | No |
| `IBMCLOUD_VPC_URL` / `IC_VPC_URL` | Alternate names for VPC endpoint override | No |
| `ANSIBLE_COLLECTIONS_PATHS` | Override collection search path | No |

### Using a Non-Production Environment (test.cloud.ibm.com)

The collection reads the same endpoint variables that the IBM Cloud CLI sets.
No playbook changes are needed — set the variables before running:

```bash
export IC_API_KEY="<your-test-environment-api-key>"
export IBMCLOUD_IAM_API_ENDPOINT=https://iam.test.cloud.ibm.com
export IBMCLOUD_IS_NG_API_ENDPOINT=https://us-south-stage01.iaasdev.cloud.ibm.com/v1

ansible-playbook -e@vars.yml playbook.yml
```

See [Troubleshooting: test.cloud.ibm.com](troubleshooting-api-key-old-venv.md) for
error reference and version history.

---

## Next Steps

- **[Quick Start](QUICK_START.md)** — First real playbook in 5 minutes
- **[Getting Started](GETTING_STARTED.md)** — Common patterns and examples
- **[Module Reference](MODULE_REFERENCE.md)** — Full module documentation
- **Examples**: see the `examples/` directory in the collection

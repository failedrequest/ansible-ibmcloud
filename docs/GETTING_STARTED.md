# Getting Started with IBM Cloud Native Ansible Collection

## Prerequisites

- Python 3.10 or higher
- IBM Cloud account with API key
- Basic knowledge of Ansible and IBM Cloud

## Installation

### Quick Setup

Run the provided setup script:

```bash
./setup.sh
```

This will:
1. Create a virtual environment
2. Install all dependencies
3. Configure Ansible collection paths

### Manual Setup

```bash
# Create virtual environment
python3 -m venv build/venv
source build/venv/bin/activate

# Install dependencies
pip install -r requirements.txt


```

## Configuration

### Set IBM Cloud API Key

```bash
export IC_API_KEY="your-ibm-cloud-api-key"
```

Or create a `.env` file (not tracked in git):

```bash
IC_API_KEY=your-ibm-cloud-api-key
IC_REGION=us-south
```

### Get Your API Key

1. Log in to IBM Cloud: https://cloud.ibm.com
2. Navigate to: Manage → Access (IAM) → API keys
3. Click "Create an IBM Cloud API key"
4. Copy the API key (you won't be able to see it again)

## Your First Playbook

Create a file `my_first_vpc.yml`:

```yaml
---
- name: Create my first VPC
  hosts: localhost
  tasks:
    - name: Create VPC
      ibm_is_vpc:
        name: my-first-vpc
        region: us-south
        state: present
      register: result

    - name: Show VPC ID
      debug:
        msg: "VPC ID: {{ result.resource.id }}"
```

Run it:

```bash
ansible-playbook my_first_vpc.yml
```

## Testing Without Changes

Use check mode to see what would happen:

```bash
ansible-playbook my_first_vpc.yml --check
```

## Common Use Cases

### 1. Create Complete VPC Infrastructure

```bash
ansible-playbook examples/create_vpc_infrastructure.yml
```

### 2. Manage Multiple Environments

```yaml
---
- name: Multi-environment setup
  hosts: localhost
  vars_files:
    - vars/{{ env }}.yml
  tasks:
    - name: Create VPC
      ibm_is_vpc:
        name: "{{ vpc_name }}"
        region: "{{ region }}"
        tags: "{{ tags }}"
        state: present
```

Run with:
```bash
ansible-playbook multi-env.yml -e env=dev
ansible-playbook multi-env.yml -e env=prod
```

### 3. Using Ansible Vault for Secrets

```bash
# Create encrypted file
ansible-vault create secrets.yml

# Add your API key
ibm_api_key: your-secret-key

# Use in playbook
ansible-playbook playbook.yml --ask-vault-pass
```

## Troubleshooting

### Module Not Found

```bash
# Ensure virtual environment is activated
source build/venv/bin/activate

# Verify installation
python -c "import ibm_vpc; print('OK')"
```

### Authentication Errors

```bash
# Verify API key is set
echo $IC_API_KEY

# Test API key
ibmcloud login --apikey $IC_API_KEY
```

### Region Issues

Ensure you're using a valid region:
- us-south (Dallas)
- us-east (Washington DC)
- eu-gb (London)
- eu-de (Frankfurt)
- jp-tok (Tokyo)
- au-syd (Sydney)

## Next Steps

1. Review the [README.md](../README.md) for full documentation
2. Explore [examples/](../examples/) directory
3. Check module documentation: `ansible-doc ibm_is_vpc`
4. Join IBM Cloud community forums

## Resources

- [IBM Cloud Documentation](https://cloud.ibm.com/docs)
- [IBM Cloud Python SDK](https://github.com/IBM/ibm-cloud-sdk-common)
- [Ansible Documentation](https://docs.ansible.com)

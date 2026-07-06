# Installation Guide

Complete guide for installing and using the IBM Cloud Ansible Collection.

## Prerequisites

- Python 3.10 or higher
- Ansible Core 2.14 or higher
- IBM Cloud account with API key
- pip (Python package manager)

## Installation Methods

### Method 1: Install from Pre-built Collection Tarball (Recommended)

This is the simplest method for production use. The collection is distributed as a pre-built tarball (`ibm-cloudcollection-1.0.0.tar.gz`).

#### Step 1: Install Python Dependencies

```bash
# Ensure Python 3.10+ is installed
python3 --version

# Install required Python packages
pip install -r requirements.txt
```

The `requirements.txt` includes:
- `ibm-cloud-sdk-core>=3.20.0` - Core IBM Cloud SDK
- `ibm-vpc>=0.33.0` - VPC service SDK
- `ibm-platform-services>=0.75.0` - Platform services SDK
- `ibm-cloud-networking-services>=0.34.0` - Networking services SDK
- `ansible-core>=2.14,<2.16` - Ansible core
- `requests>=2.28.0` - HTTP library
- `PyYAML>=6.0` - YAML parser

#### Step 2: Install the Collection

```bash
# Install the pre-built collection tarball
ansible-galaxy collection install ibm-cloudcollection-1.0.0.tar.gz

# Verify installation
ansible-galaxy collection list | grep ibm
```

The collection will be installed to:
- `~/.ansible/collections/ansible_collections/ibm/cloudcollection/` (default)
- Or the path specified in `ANSIBLE_COLLECTIONS_PATHS`

#### Step 3: Set IBM Cloud API Key

```bash
# Set your IBM Cloud API key
export IC_API_KEY="your-api-key-here"

# Verify it's set
echo $IC_API_KEY
```

#### Step 4: Test the Installation

```bash
# Create a test playbook
cat > test-collection.yml <<EOF
---
- name: Test IBM Cloud Collection
  hosts: localhost
  collections:
    - ibm.cloudcollection
  
  tasks:
    - name: Display collection info
      debug:
        msg: "IBM Cloud collection is ready to use"
EOF

# Run the test playbook
ansible-playbook test-collection.yml
```

### Method 2: Build and Install from Source

Use this method if you want to build the collection yourself or make modifications.

#### Step 1: Clone the Repository

```bash
# Clone the repository
git clone https://github.com/IBM/ansible-ibmcloud.git
cd ansible-ibmcloud
```

#### Step 2: Install Python Dependencies

```bash
# Install required Python packages
pip install -r requirements.txt
```

#### Step 3: Build the Collection

```bash
# Build the collection tarball
ansible-galaxy collection build

# This creates: ibm-cloudcollection-1.0.0.tar.gz
```

The build process:
1. Reads `galaxy.yml` for collection metadata
2. Packages all modules from `plugins/modules/`
3. Includes module utilities from `plugins/module_utils/`
4. Bundles documentation from `docs/`
5. Creates a compressed tarball

#### Step 4: Install the Built Collection

```bash
# Install the newly built collection
ansible-galaxy collection install ibm-cloudcollection-1.0.0.tar.gz

# Or force reinstall if already installed
ansible-galaxy collection install --force ibm-cloudcollection-1.0.0.tar.gz
```

#### Step 5: Set IBM Cloud API Key

```bash
export IC_API_KEY="your-api-key-here"
```

### Method 3: Development Setup with Virtual Environment

Use this method for active development and testing.

#### Step 1: Clone and Setup

```bash
# Clone the repository
git clone https://github.com/IBM/ansible-ibmcloud.git
cd ansible-ibmcloud

# Run the setup script (creates virtual environment in build/venv)
chmod +x setup.sh
./setup.sh
```

The setup script:
- Checks Python version (3.10+ required)
- Creates a virtual environment in `build/venv/`
- Installs all dependencies from `requirements.txt`
- Sets up Ansible collection paths
- Verifies the installation

#### Step 2: Activate Virtual Environment

```bash
# Activate the virtual environment
source build/venv/bin/activate

# Your prompt should change to show (venv)
```

#### Step 3: Set IBM Cloud API Key

```bash
export IC_API_KEY="your-api-key-here"
```

#### Step 4: Test in Development Mode

```bash
# Run example playbooks
ansible-playbook examples/create_vpc_infrastructure.yml --check

# Test specific modules
ansible-doc ibm.cloudcollection.ibm_is_vpc
```

### Method 4: Install from Ansible Galaxy (Future)

Once published to Ansible Galaxy:

```bash
# Install from Ansible Galaxy
ansible-galaxy collection install ibm.cloudcollection

# Install specific version
ansible-galaxy collection install ibm.cloudcollection:1.0.0
```

## Configuration

### 1. Set IBM Cloud API Key

**Option A: Environment Variable (Recommended)**
```bash
export IC_API_KEY="your-ibm-cloud-api-key"
```

**Option B: In Playbook**
```yaml
vars:
  ibmcloud_api_key: "{{ lookup('env', 'IC_API_KEY') }}"
```

**Option C: Ansible Vault (Most Secure)**
```bash
# Create encrypted vault file
ansible-vault create secrets.yml

# Add your API key
ibmcloud_api_key: your-ibm-cloud-api-key

# Use in playbook
ansible-playbook playbook.yml --ask-vault-pass
```

### 2. Configure Ansible

Create or update `ansible.cfg`:

```ini
[defaults]
collections_paths = ~/.ansible/collections:/usr/share/ansible/collections

[inventory]
enable_plugins = host_list, script, auto, yaml, ini, toml
```

### 3. Verify Installation

```bash
# List installed collections
ansible-galaxy collection list

# Verify IBM Cloud collection
ansible-doc ibm.cloudcollection.ibm_is_vpc
```

## Directory Structure After Installation

```
~/.ansible/collections/ansible_collections/ibm/cloudcollection/
├── plugins/
│   ├── modules/              # 67 Ansible modules
│   │   ├── ibm_is_*.py      # VPC modules (42)
│   │   ├── ibm_tg_*.py      # Transit Gateway (4)
│   │   └── ibm_*.py         # Platform services (21)
│   └── module_utils/
│       └── ibm_cloud_sdk.py # Core SDK integration
├── docs/                     # Documentation
├── examples/                 # Example playbooks
├── galaxy.yml               # Collection metadata
└── README.md                # Collection README
```

## Python Dependencies

The collection requires these Python packages:

```
ansible-core>=2.14.0
ibm-vpc>=0.33.0
ibm-platform-services>=0.50.0
ibm-cloud-sdk-core>=3.20.0
```

### Install Dependencies Manually

```bash
pip install -r requirements.txt
```



## Usage in Playbooks

### Basic Playbook Structure

```yaml
---
- name: IBM Cloud Infrastructure Management
  hosts: localhost
  connection: local
  collections:
    - ibm.cloudcollection
  
  vars:
    ibmcloud_api_key: "{{ lookup('env', 'IC_API_KEY') }}"
    region: us-south
  
  tasks:
    - name: Create VPC
      ibm_is_vpc:
        name: production-vpc
        region: "{{ region }}"
        state: present
      register: vpc
```

### Using Fully Qualified Collection Names (FQCN)

```yaml
- name: Create VPC with FQCN
  ibm.cloudcollection.ibm_is_vpc:
    name: production-vpc
    region: us-south
    state: present
```

## Testing the Installation

### 1. Create Test Playbook

Create `test-installation.yml`:

```yaml
---
- name: Test IBM Cloud Collection
  hosts: localhost
  connection: local
  collections:
    - ibm.cloudcollection
  
  tasks:
    - name: Test module availability
      debug:
        msg: "IBM Cloud collection is installed and ready"
    
    - name: List available modules
      command: ansible-doc -l ibm.cloudcollection
      register: modules
    
    - name: Display modules
      debug:
        var: modules.stdout_lines
```

### 2. Run Test Playbook

```bash
ansible-playbook test-installation.yml
```

### 3. Test with Check Mode

```bash
# Create a simple VPC test
cat > test-vpc.yml <<EOF
---
- name: Test VPC Creation
  hosts: localhost
  collections:
    - ibm.cloudcollection
  
  tasks:
    - name: Create test VPC
      ibm_is_vpc:
        name: test-vpc
        region: us-south
        state: present
      check_mode: yes
EOF

# Run in check mode (dry run)
ansible-playbook test-vpc.yml --check
```

## Troubleshooting

### Collection Not Found

```bash
# Check collection path
ansible-config dump | grep COLLECTIONS_PATHS

# Verify installation
ansible-galaxy collection list | grep ibm

# Reinstall if needed
ansible-galaxy collection install --force .
```

### Module Import Errors

```bash
# Verify Python dependencies
pip list | grep ibm

# Install missing dependencies
pip install -r requirements.txt

# Check Python path
python -c "import ibm_vpc; print(ibm_vpc.__version__)"
```

### Authentication Errors

```bash
# Verify API key is set
echo $IC_API_KEY

# Test API key
curl -X GET \
  "https://us-south.iaas.cloud.ibm.com/v1/vpcs?version=2024-01-01&generation=2" \
  -H "Authorization: Bearer $(ibmcloud iam oauth-tokens --output json | jq -r .iam_token)"
```

### Permission Errors

```bash
# Check file permissions
ls -la ~/.ansible/collections/ansible_collections/ibm/cloudcollection/

# Fix permissions if needed
chmod -R 755 ~/.ansible/collections/ansible_collections/ibm/cloudcollection/
```

## Upgrading

### Upgrade from Source

```bash
cd ansible-ibmcloud
git pull origin main
./setup.sh
```

### Upgrade Collection

```bash
# Rebuild and reinstall
ansible-galaxy collection build --force
ansible-galaxy collection install --force ibm-cloudcollection-1.0.0.tar.gz
```

## Uninstallation

### Remove Collection

```bash
# Remove from default location
rm -rf ~/.ansible/collections/ansible_collections/ibm/cloudcollection

# Or use ansible-galaxy (if supported)
ansible-galaxy collection remove ibm.cloudcollection
```

### Remove Python Dependencies

```bash
pip uninstall ibm-vpc ibm-platform-services ibm-cloud-sdk-core
```

## Development Setup

For contributing or development:

```bash
# Clone repository
git clone https://github.com/IBM/ansible-ibmcloud.git
cd ansible-ibmcloud

# Install in development mode
pip install -e .



# Run tests
pytest tests/

# Generate modules
python tools/generate_modules.py
```

## Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `IC_API_KEY` | IBM Cloud API key | Yes | None |
| `IC_REGION` | Default IBM Cloud region | No | us-south |
| `ANSIBLE_COLLECTIONS_PATHS` | Collection search paths | No | ~/.ansible/collections |

## Next Steps

1. **Read Documentation**: Check [docs/](../docs/) for module references
2. **Try Examples**: Run playbooks from [examples/](../examples/)
3. **View HTML Docs**: Open [docs/html/index.html](../docs/html/index.html)
4. **Join Community**: Report issues on GitHub

## Support

- **Documentation**: [docs/](../docs/)
- **Examples**: [examples/](../examples/)
- **Issues**: GitHub Issues
- **IBM Cloud Docs**: https://cloud.ibm.com/docs

## License

BSD 2-Clause License

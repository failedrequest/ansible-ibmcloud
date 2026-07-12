# Quick Start Guide

Get started with the IBM Cloud Ansible Collection in 5 minutes.

## Installation

```bash
# 1. Clone and setup
git clone https://github.com/IBM/ansible-ibmcloud.git
cd ansible-ibmcloud
./setup.sh
source .venv/bin/activate

> **Note:** This collection uses version 2.x to avoid conflicts with the official IBM Cloud Ansible collection. The version bump ensures both collections can coexist if needed.


# 2. Build and install collection
.venv/bin/ansible-galaxy collection build --force
.venv/bin/ansible-galaxy collection install ibm-cloudcollection-2.0.5.tar.gz --force

# 3. Verify installation
.venv/bin/ansible-galaxy collection list | grep ibm
```

## Configuration

```bash
# Set your IBM Cloud API key
export IC_API_KEY="your-ibm-cloud-api-key-here"
```

## Your First Playbook

Create `my-first-vpc.yml`:

```yaml
---
- name: Create IBM Cloud VPC Infrastructure
  hosts: localhost
  connection: local
  gather_facts: no
  collections:
    - ibm.cloudcollection
  
  vars:
    vpc_name: my-production-vpc
    region: us-south
  
  tasks:
    - name: Create VPC
      ibm_is_vpc:
        name: "{{ vpc_name }}"
        region: "{{ region }}"
        state: present
      register: vpc
    
    - name: Display VPC information
      debug:
        msg: "VPC created with ID: {{ vpc.resource.id }}"
```

## Run Your Playbook

```bash
# Dry run (check mode)
.venv/bin/ansible-playbook my-first-vpc.yml --check

# Actually create resources
.venv/bin/ansible-playbook my-first-vpc.yml
```

## Available Modules

### VPC Infrastructure (42 modules)
- `ibm_is_vpc` - Virtual Private Cloud
- `ibm_is_subnet` - Subnets
- `ibm_is_instance` - Virtual Server Instances
- `ibm_is_security_group` - Security Groups
- `ibm_is_load_balancer` - Load Balancers
- `ibm_is_vpn_gateway` - VPN Gateways
- And 36 more...

### Transit Gateway (4 modules)
- `ibm_tg_gateway` - Transit Gateway
- `ibm_tg_connection` - Gateway Connections
- `ibm_tg_connection_prefix_filter` - Route Filters
- `ibm_tg_route_report` - Route Reports

### Platform Services (21 modules)
- `ibm_cos_bucket` - Cloud Object Storage
- `ibm_iam_access_group` - IAM Access Groups
- `ibm_resource_instance` - Service Instances
- `ibm_kms_key` - Encryption Keys
- `ibm_database_instance` - Database Services
- And 16 more...

## Complete Example

```yaml
---
- name: Complete VPC Infrastructure
  hosts: localhost
  connection: local
  collections:
    - ibm.cloudcollection
  
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
    
    - name: Create Subnet
      ibm_is_subnet:
        name: web-subnet
        vpc: "{{ vpc.resource.id }}"
        zone: "{{ zone }}"
        ipv4_cidr_block: 10.240.0.0/24
        state: present
      register: subnet
    
    - name: Create Security Group
      ibm_is_security_group:
        name: web-sg
        vpc: "{{ vpc.resource.id }}"
        state: present
      register: sg
    
    - name: Allow HTTP traffic
      ibm_is_security_group_rule:
        security_group: "{{ sg.resource.id }}"
        direction: inbound
        protocol: tcp
        port_min: 80
        port_max: 80
        state: present
    
    - name: Create Virtual Server
      ibm_is_instance:
        name: web-server-1
        vpc: "{{ vpc.resource.id }}"
        zone: "{{ zone }}"
        profile: cx2-2x4
        image: ibm-ubuntu-22-04-minimal-amd64-1
        primary_network_interface:
          subnet: "{{ subnet.resource.id }}"
          security_groups:
            - "{{ sg.resource.id }}"
        state: present
```

## Next Steps

1. **Explore Examples**: Check `examples/` directory
2. **Read Documentation**: See `docs/` for detailed guides
3. **View HTML Docs**: Open `docs/html/index.html` in browser
4. **Try Transit Gateway**: Connect multiple VPCs
5. **Add Platform Services**: IAM, COS, Databases

## Common Commands

```bash
# List all modules
.venv/bin/ansible-doc -l ibm.cloudcollection

# View module documentation (note: DOCUMENTATION strings need to be added)
.venv/bin/ansible-doc ibm.cloudcollection.ibm_is_vpc

# Run with verbose output
.venv/bin/ansible-playbook playbook.yml -v

# Run in check mode (dry run)
.venv/bin/ansible-playbook playbook.yml --check

# Run specific tasks with tags
.venv/bin/ansible-playbook playbook.yml --tags vpc,subnet
```

## Troubleshooting

### Collection not found
```bash
# Verify installation
.venv/bin/ansible-galaxy collection list | grep ibm

# Reinstall if needed
.venv/bin/ansible-galaxy collection install ibm-cloudcollection-2.0.5.tar.gz --force
```

### API authentication errors
```bash
# Verify API key is set
echo $IC_API_KEY

# Test with IBM Cloud CLI
ibmcloud login --apikey $IC_API_KEY
```

### Module errors
```bash
# Check Python dependencies
pip list | grep ibm

# Reinstall dependencies
pip install -r requirements.txt
```

## Support

- **Documentation**: `docs/` directory
- **Examples**: `examples/` directory  
- **HTML Docs**: `docs/html/index.html`
- **IBM Cloud Docs**: https://cloud.ibm.com/docs

## Success! 🎉

You're now ready to manage IBM Cloud infrastructure with Ansible!

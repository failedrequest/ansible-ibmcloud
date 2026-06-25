# IBM Cloud Ansible Collection - Example Playbooks

This directory contains example playbooks demonstrating various IBM Cloud infrastructure automation scenarios using the `ibm.cloudcollection` Ansible collection.

## Prerequisites

1. **IBM Cloud Account**: Active IBM Cloud account with appropriate permissions
2. **API Key**: IBM Cloud API key with VPC Infrastructure and Kubernetes Service permissions
3. **Ansible**: Ansible 2.9 or higher installed
4. **Collection**: `ibm.cloudcollection` v1.0.3 or higher installed

## Setup

### 1. Install the Collection

```bash
ansible-galaxy collection install ibm.cloudcollection
```

### 2. Set Environment Variables

You can provide credentials and configuration in two ways:

**Option 1: Environment Variables (Recommended)**
```bash
# Required: IBM Cloud API Key
export IC_API_KEY="your-ibm-cloud-api-key"

# Required for ROKS operations: Cluster Name
export CLUSTER_NAME="your-roks-cluster-name"
```

**Option 2: Playbook Variables**
Edit the playbook's `vars` section and uncomment/set the variables:
```yaml
vars:
  ibmcloud_api_key: "your-api-key-here"
  cluster_name: "your-cluster-name-here"
```

**Note**: Environment variables are recommended for security. Never commit API keys to version control.

### 3. List Your Resources

Before running playbooks, identify your existing resources:

```bash
# List your ROKS clusters
ibmcloud ks clusters

# List your VPCs
ibmcloud is vpcs

# List subnets in a VPC
ibmcloud is subnets --vpc <vpc-name>
```

## Example Playbooks

### 1. VPC Infrastructure Creation

**File**: `create_vpc_infrastructure.yml`

Creates a complete VPC infrastructure including VPC, subnets, security groups, and public gateway.

**Usage**:
```bash
ansible-playbook create_vpc_infrastructure.yml
```

**What it creates**:
- VPC with custom address prefixes
- Multiple subnets across zones
- Security group with rules
- Public gateway
- Floating IP

---

### 2. VNI with Reserved IPs

**File**: `create_vni_with_reserved_ips.yml`

Creates a Virtual Network Interface (VNI) with reserved IP addresses.

**Usage**:
```bash
ansible-playbook create_vni_with_reserved_ips.yml
```

**What it creates**:
- VNI with primary IP
- Reserved IP addresses
- Security group attachment

---

### 3. Attach VNI to ROKS Cluster

**File**: `attach_vni_to_roks_cluster.yml`

Attaches a Virtual Network Interface to an existing ROKS (Red Hat OpenShift on IBM Cloud) cluster.

**Prerequisites**:
- Existing ROKS cluster
- VPC and subnet in the same region as the cluster

**Usage**:
```bash
# Set your cluster name
export CLUSTER_NAME="your-actual-cluster-name"

# Run the playbook
ansible-playbook attach_vni_to_roks_cluster.yml
```

**Important Notes**:
- Replace `CLUSTER_NAME` with your actual cluster name from `ibmcloud ks clusters`
- The playbook will fail early if cluster name is not provided or cluster doesn't exist
- VNI must be in the same VPC and region as the cluster

**What it does**:
1. Looks up existing VPC and subnet
2. Creates a VNI with reserved IP
3. Validates cluster exists
4. Attaches VNI to the ROKS cluster

---

### 4. Detach VNI from ROKS Cluster

**File**: `detach_vni_from_roks_cluster.yml`

Detaches and cleans up a VNI from a ROKS cluster.

**Usage**:
```bash
# Set your cluster name
export CLUSTER_NAME="your-actual-cluster-name"

# Run the playbook
ansible-playbook detach_vni_from_roks_cluster.yml
```

**What it does**:
1. Looks up VNI by name
2. Detaches VNI from cluster
3. Deletes the VNI
4. Cleans up reserved IPs

---

### 5. Cleanup Playbooks

**VPC Infrastructure Cleanup**: `cleanup_vpc_infrastructure.yml`
```bash
ansible-playbook cleanup_vpc_infrastructure.yml
```

**VPC Custom Prefix Cleanup**: `cleanup_vpc_custom_prefix.yml`
```bash
ansible-playbook cleanup_vpc_custom_prefix.yml
```

**VNI with Reserved IPs Cleanup**: `cleanup_vni_with_reserved_ips.yml`
```bash
ansible-playbook cleanup_vni_with_reserved_ips.yml
```

## Common Variables

All playbooks use these common variables that you can customize:

```yaml
vars:
  # IBM Cloud Configuration
  ibm_region: us-south          # Change to your region
  ibm_zone: us-south-1          # Change to your zone
  
  # Resource naming
  vpc_name: custom-prefix-vpc   # Your VPC name
  cluster_name: "{{ lookup('env', 'CLUSTER_NAME') }}"  # From environment
```

## Troubleshooting

### Cluster Not Found Error

```
FAILED! => {"msg": "Cluster 'my-cluster' not found or not accessible"}
```

**Solution**: 
1. List your clusters: `ibmcloud ks clusters`
2. Set the correct cluster name: `export CLUSTER_NAME="actual-cluster-name"`
3. Verify you have access to the cluster

### Authentication Error

```
FAILED! => {"msg": "Failed to authenticate with IBM Cloud"}
```

**Solution**:
1. Verify your API key is set: `echo $IC_API_KEY`
2. Test authentication: `ibmcloud login --apikey $IC_API_KEY`
3. Ensure API key has required permissions

### VNI Already Attached

```
{"msg": "VNI r006-xxx is already attached to cluster"}
```

**Solution**: This is expected behavior (idempotent). The playbook detects the VNI is already attached and skips the operation.

## Best Practices

1. **Always use environment variables** for sensitive data like API keys
2. **Verify resource names** before running playbooks
3. **Use check mode** to preview changes: `ansible-playbook --check playbook.yml`
4. **Run cleanup playbooks** to remove test resources and avoid charges
5. **Review variables** at the top of each playbook before running

## Additional Resources

- [IBM Cloud Ansible Collection Documentation](../docs/)
- [IBM Cloud VPC Documentation](https://cloud.ibm.com/docs/vpc)
- [IBM Cloud Kubernetes Service Documentation](https://cloud.ibm.com/docs/containers)
- [Ansible Documentation](https://docs.ansible.com/)

## Support

For issues or questions:
1. Check the [module documentation](../docs/)
2. Review the [collection README](../README.md)
3. Open an issue on the project repository

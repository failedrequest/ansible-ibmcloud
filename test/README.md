# Test Playbooks

This directory contains test playbooks for the IBM Cloud Ansible Collection.

## Available Test Playbooks

- `test-vpc-routes.yml` - Tests VPC routing functionality
- `test-vpc-routes-existing.yml` - Tests VPC routes with existing infrastructure
- `test-collection-install.yml` - Tests collection installation
- `test-instance-lookup.yml` - Tests instance lookup functionality
- `test-playbook.yml` - General test playbook

## Running Tests

### Prerequisites

1. Install the collection:
   ```bash
   ansible-galaxy collection install ibm.cloudcollection
   ```

2. Set up IBM Cloud credentials:
   ```bash
   export IC_API_KEY="your-api-key"
   ```

### Running a Test Playbook

```bash
ansible-playbook test/test-vpc-routes.yml
```

## Cleanup

Most test playbooks include commented-out cleanup sections. Uncomment these sections to delete test resources after validation.

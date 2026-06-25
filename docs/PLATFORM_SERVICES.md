# IBM Cloud Platform Services Module Reference

Complete reference for 21 IBM Cloud platform service modules covering core cloud services.

## Overview

This collection provides Ansible modules for managing IBM Cloud platform services including:
- Cloud Object Storage (COS)
- Identity and Access Management (IAM)
- Resource Management
- Key Management Service (KMS)
- Cloud Databases
- Container Registry
- Event Notifications
- Secrets Manager

## Module Categories

### Cloud Object Storage (1 module)

#### ibm_cos_bucket
Manage Cloud Object Storage buckets

**Parameters:**
- `name` (required) - Bucket name
- `ibm_service_instance_id` (required) - COS instance ID
- `storage_class` - Storage class (standard, vault, cold, flex)
- `location_constraint` - Bucket location
- `object_versioning` - Enable versioning

**Example:**
```yaml
- name: Create COS bucket
  ibm_cos_bucket:
    name: my-data-bucket
    ibm_service_instance_id: "{{ cos_instance_id }}"
    storage_class: standard
    location_constraint: us-south
    state: present
```

### Identity and Access Management (5 modules)

#### ibm_iam_access_group
Manage IAM access groups for organizing users and service IDs

**Parameters:**
- `name` (required) - Access group name
- `account_id` (required) - IBM Cloud account ID
- `description` - Group description

**Example:**
```yaml
- name: Create access group
  ibm_iam_access_group:
    name: developers
    account_id: "{{ account_id }}"
    description: Development team access
    state: present
```

#### ibm_iam_access_group_rule
Manage dynamic rules for access groups

**Parameters:**
- `access_group_id` (required) - Access group ID
- `name` (required) - Rule name
- `expiration` (required) - Rule expiration hours
- `conditions` (required) - Rule conditions
- `realm_name` - Identity provider realm

**Example:**
```yaml
- name: Add dynamic rule
  ibm_iam_access_group_rule:
    access_group_id: "{{ group_id }}"
    name: federated-users
    expiration: 24
    conditions:
      claim: blueGroups
      operator: CONTAINS
      value: developers
    state: present
```

#### ibm_iam_service_id
Manage service IDs for application authentication

**Parameters:**
- `name` (required) - Service ID name
- `account_id` (required) - Account ID
- `description` - Service ID description
- `unique_instance_crns` - Bound service instances

**Example:**
```yaml
- name: Create service ID
  ibm_iam_service_id:
    name: app-service-id
    account_id: "{{ account_id }}"
    description: Application service identity
    state: present
```

#### ibm_iam_api_key
Manage API keys for users and service IDs

**Parameters:**
- `name` (required) - API key name
- `iam_id` (required) - User or service ID
- `description` - Key description
- `account_id` - Account ID
- `store_value` - Store key value in result

**Example:**
```yaml
- name: Create API key
  ibm_iam_api_key:
    name: deployment-key
    iam_id: "{{ service_id }}"
    description: CI/CD deployment key
    store_value: true
    state: present
  register: api_key
```

#### ibm_iam_policy
Manage IAM access policies

**Parameters:**
- `type` (required) - Policy type (access, authorization)
- `subjects` (required) - Policy subjects
- `roles` (required) - IAM roles
- `resources` (required) - Target resources
- `description` - Policy description

**Example:**
```yaml
- name: Grant access policy
  ibm_iam_policy:
    type: access
    subjects:
      - attributes:
          - name: iam_id
            value: "{{ service_id }}"
    roles:
      - role_id: crn:v1:bluemix:public:iam::::role:Editor
    resources:
      - attributes:
          - name: serviceName
            value: cloud-object-storage
    state: present
```

### Resource Management (4 modules)

#### ibm_resource_group
Manage resource groups for organizing resources

**Parameters:**
- `name` (required) - Resource group name
- `account_id` (required) - Account ID

**Example:**
```yaml
- name: Create resource group
  ibm_resource_group:
    name: production
    account_id: "{{ account_id }}"
    state: present
```

#### ibm_resource_instance
Manage service instances

**Parameters:**
- `name` (required) - Instance name
- `target` (required) - Target location
- `resource_group` (required) - Resource group ID
- `resource_plan_id` (required) - Service plan ID
- `parameters` - Service-specific parameters
- `tags` - Resource tags

**Example:**
```yaml
- name: Create COS instance
  ibm_resource_instance:
    name: my-cos-instance
    target: global
    resource_group: "{{ rg_id }}"
    resource_plan_id: "{{ cos_plan_id }}"
    tags:
      - env:production
    state: present
```

#### ibm_resource_key
Manage service credentials

**Parameters:**
- `name` (required) - Credential name
- `source` (required) - Service instance ID
- `parameters` - Credential parameters
- `role` - IAM role for credentials

**Example:**
```yaml
- name: Create service credentials
  ibm_resource_key:
    name: app-credentials
    source: "{{ instance_id }}"
    role: Writer
    state: present
  register: credentials
```

#### ibm_resource_binding
Manage service bindings

**Parameters:**
- `name` (required) - Binding name
- `source` (required) - Service instance ID
- `target` (required) - Target resource ID
- `parameters` - Binding parameters
- `role` - IAM role

**Example:**
```yaml
- name: Bind service to app
  ibm_resource_binding:
    name: app-db-binding
    source: "{{ db_instance_id }}"
    target: "{{ app_id }}"
    role: Manager
    state: present
```

### Key Management Service (2 modules)

#### ibm_kms_key
Manage encryption keys

**Parameters:**
- `name` (required) - Key name
- `instance_id` (required) - KMS instance ID
- `key_ring_id` - Key ring ID
- `payload` - Key material (for import)
- `extractable` - Whether key is extractable
- `expiration_date` - Key expiration

**Example:**
```yaml
- name: Create root key
  ibm_kms_key:
    name: root-key
    instance_id: "{{ kms_instance_id }}"
    key_ring_id: default
    extractable: false
    state: present
```

#### ibm_kms_key_ring
Manage key rings for organizing keys

**Parameters:**
- `key_ring_id` (required) - Key ring ID
- `instance_id` (required) - KMS instance ID

**Example:**
```yaml
- name: Create key ring
  ibm_kms_key_ring:
    key_ring_id: production-keys
    instance_id: "{{ kms_instance_id }}"
    state: present
```

### Cloud Databases (2 modules)

#### ibm_database_instance
Manage database deployments (PostgreSQL, MongoDB, Redis, etc.)

**Parameters:**
- `name` (required) - Database name
- `service_id` (required) - Database service type
- `plan_id` (required) - Service plan
- `location` (required) - Deployment location
- `version` - Database version
- `members_memory_allocation_mb` - Memory per member
- `members_disk_allocation_mb` - Disk per member

**Example:**
```yaml
- name: Create PostgreSQL database
  ibm_database_instance:
    name: production-db
    service_id: databases-for-postgresql
    plan_id: standard
    location: us-south
    version: "14"
    members_memory_allocation_mb: 4096
    members_disk_allocation_mb: 20480
    state: present
```

#### ibm_database_user
Manage database users

**Parameters:**
- `deployment_id` (required) - Database deployment ID
- `username` (required) - Username
- `password` - User password

**Example:**
```yaml
- name: Create database user
  ibm_database_user:
    deployment_id: "{{ db_id }}"
    username: appuser
    password: "{{ vault_db_password }}"
    state: present
```

### Container Registry (2 modules)

#### ibm_cr_namespace
Manage container registry namespaces

**Parameters:**
- `name` (required) - Namespace name
- `resource_group_id` - Resource group

**Example:**
```yaml
- name: Create registry namespace
  ibm_cr_namespace:
    name: production-images
    resource_group_id: "{{ rg_id }}"
    state: present
```

#### ibm_cr_retention_policy
Manage image retention policies

**Parameters:**
- `namespace` (required) - Namespace name
- `images_per_repo` (required) - Images to retain
- `retain_untagged` - Retain untagged images

**Example:**
```yaml
- name: Set retention policy
  ibm_cr_retention_policy:
    namespace: production-images
    images_per_repo: 10
    retain_untagged: false
    state: present
```

### Event Notifications (3 modules)

#### ibm_en_destination
Manage notification destinations

**Parameters:**
- `instance_id` (required) - Event Notifications instance
- `name` (required) - Destination name
- `type` (required) - Destination type (webhook, email, sms)
- `config` (required) - Destination configuration
- `description` - Destination description

**Example:**
```yaml
- name: Create webhook destination
  ibm_en_destination:
    instance_id: "{{ en_instance_id }}"
    name: slack-alerts
    type: webhook
    config:
      url: https://hooks.slack.com/services/xxx
      verb: POST
    state: present
```

#### ibm_en_topic
Manage notification topics

**Parameters:**
- `instance_id` (required) - Event Notifications instance
- `name` (required) - Topic name
- `description` - Topic description
- `sources` - Event sources

**Example:**
```yaml
- name: Create topic
  ibm_en_topic:
    instance_id: "{{ en_instance_id }}"
    name: security-alerts
    description: Security event notifications
    state: present
```

#### ibm_en_subscription
Manage topic subscriptions

**Parameters:**
- `instance_id` (required) - Event Notifications instance
- `name` (required) - Subscription name
- `destination_id` (required) - Destination ID
- `topic_id` (required) - Topic ID
- `description` - Subscription description
- `attributes` - Subscription attributes

**Example:**
```yaml
- name: Subscribe destination to topic
  ibm_en_subscription:
    instance_id: "{{ en_instance_id }}"
    name: slack-security-sub
    destination_id: "{{ dest_id }}"
    topic_id: "{{ topic_id }}"
    state: present
```

### Secrets Manager (2 modules)

#### ibm_sm_secret_group
Manage secret groups

**Parameters:**
- `instance_id` (required) - Secrets Manager instance
- `name` (required) - Group name
- `description` - Group description

**Example:**
```yaml
- name: Create secret group
  ibm_sm_secret_group:
    instance_id: "{{ sm_instance_id }}"
    name: production-secrets
    description: Production environment secrets
    state: present
```

#### ibm_sm_secret
Manage secrets

**Parameters:**
- `instance_id` (required) - Secrets Manager instance
- `name` (required) - Secret name
- `secret_type` (required) - Secret type (arbitrary, username_password, iam_credentials)
- `secret_group_id` - Secret group
- `labels` - Secret labels
- `expiration_date` - Expiration date
- `payload` - Secret data

**Example:**
```yaml
- name: Store API key
  ibm_sm_secret:
    instance_id: "{{ sm_instance_id }}"
    name: external-api-key
    secret_type: arbitrary
    secret_group_id: "{{ group_id }}"
    payload: "{{ api_key_value }}"
    labels:
      - external
      - api
    state: present
```

## Complete Infrastructure Example

```yaml
---
- name: Deploy Complete IBM Cloud Infrastructure
  hosts: localhost
  vars:
    account_id: "{{ lookup('env', 'IBM_ACCOUNT_ID') }}"
    region: us-south
  
  tasks:
    # 1. Resource Organization
    - name: Create resource group
      ibm_resource_group:
        name: production
        account_id: "{{ account_id }}"
        state: present
      register: rg

    # 2. IAM Setup
    - name: Create service ID
      ibm_iam_service_id:
        name: app-service-id
        account_id: "{{ account_id }}"
        description: Application identity
        state: present
      register: service_id

    - name: Create API key
      ibm_iam_api_key:
        name: app-api-key
        iam_id: "{{ service_id.resource.id }}"
        store_value: true
        state: present
      register: api_key

    # 3. Key Management
    - name: Create KMS instance
      ibm_resource_instance:
        name: production-kms
        target: "{{ region }}"
        resource_group: "{{ rg.resource.id }}"
        resource_plan_id: "{{ kms_plan_id }}"
        state: present
      register: kms

    - name: Create encryption key
      ibm_kms_key:
        name: data-encryption-key
        instance_id: "{{ kms.resource.guid }}"
        extractable: false
        state: present
      register: key

    # 4. Storage
    - name: Create COS instance
      ibm_resource_instance:
        name: production-storage
        target: global
        resource_group: "{{ rg.resource.id }}"
        resource_plan_id: "{{ cos_plan_id }}"
        state: present
      register: cos

    - name: Create encrypted bucket
      ibm_cos_bucket:
        name: production-data
        ibm_service_instance_id: "{{ cos.resource.guid }}"
        storage_class: standard
        location_constraint: "{{ region }}"
        state: present

    # 5. Database
    - name: Create PostgreSQL database
      ibm_database_instance:
        name: production-db
        service_id: databases-for-postgresql
        plan_id: standard
        location: "{{ region }}"
        version: "14"
        members_memory_allocation_mb: 4096
        state: present
      register: db

    - name: Create database user
      ibm_database_user:
        deployment_id: "{{ db.resource.id }}"
        username: appuser
        password: "{{ vault_db_password }}"
        state: present

    # 6. Secrets Management
    - name: Create Secrets Manager instance
      ibm_resource_instance:
        name: production-secrets
        target: "{{ region }}"
        resource_group: "{{ rg.resource.id }}"
        resource_plan_id: "{{ sm_plan_id }}"
        state: present
      register: sm

    - name: Store database credentials
      ibm_sm_secret:
        instance_id: "{{ sm.resource.guid }}"
        name: db-credentials
        secret_type: username_password
        payload:
          username: appuser
          password: "{{ vault_db_password }}"
        state: present

    # 7. Container Registry
    - name: Create registry namespace
      ibm_cr_namespace:
        name: production-apps
        resource_group_id: "{{ rg.resource.id }}"
        state: present

    # 8. Event Notifications
    - name: Create Event Notifications instance
      ibm_resource_instance:
        name: production-events
        target: "{{ region }}"
        resource_group: "{{ rg.resource.id }}"
        resource_plan_id: "{{ en_plan_id }}"
        state: present
      register: en

    - name: Create notification topic
      ibm_en_topic:
        instance_id: "{{ en.resource.guid }}"
        name: security-alerts
        description: Security notifications
        state: present
      register: topic

    - name: Create webhook destination
      ibm_en_destination:
        instance_id: "{{ en.resource.guid }}"
        name: slack-webhook
        type: webhook
        config:
          url: "{{ slack_webhook_url }}"
        state: present
      register: dest

    - name: Subscribe to alerts
      ibm_en_subscription:
        instance_id: "{{ en.resource.guid }}"
        name: slack-security-sub
        destination_id: "{{ dest.resource.id }}"
        topic_id: "{{ topic.resource.id }}"
        state: present
```

## Module Development Pattern

All platform modules follow this consistent pattern:

```python
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ibm.cloudcollection.plugins.module_utils.ibm_cloud_sdk import (
    IBMCloudSDKModule,
    get_common_argument_spec
)
from ibm_platform_services import ServiceClass

class MyPlatformModule(IBMCloudSDKModule):
    def __init__(self, module):
        super().__init__(module)
        self.service = ServiceClass(authenticator=self.auth.get_authenticator())
    
    def run(self):
        # Module logic
        pass
```

## Common Parameters

All platform modules support:

```yaml
ibmcloud_api_key: string
  IBM Cloud API key (or IC_API_KEY env var)

region: string (default: us-south)
  IBM Cloud region

state: string (default: present)
  Desired state: present, absent

name: string
  Resource name (required for creation)

id: string
  Resource ID (for updates/deletes)
```

## SDK Requirements

Platform modules require:
- `ibm-platform-services >= 0.50.0`
- `ibm-cloud-sdk-core >= 3.20.0`
- Python 3.10+

## Testing

```bash
# Syntax check
ansible-playbook playbook.yml --syntax-check

# Check mode (dry run)
ansible-playbook playbook.yml --check

# Verbose output
ansible-playbook playbook.yml -vvv
```

## Support

- IBM Cloud API Documentation: https://cloud.ibm.com/apidocs
- IBM Platform Services SDK: https://github.com/IBM/platform-services-python-sdk
- Collection Repository: [GitHub URL]

## License

GNU General Public License v3.0+

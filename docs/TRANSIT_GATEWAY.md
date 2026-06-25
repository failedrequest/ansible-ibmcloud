# IBM Cloud Transit Gateway Module Reference

Complete reference for IBM Cloud Transit Gateway service modules for connecting VPCs and on-premises networks.

## Overview

IBM Cloud Transit Gateway provides a way to interconnect IBM Cloud VPCs and on-premises networks. These modules allow you to manage Transit Gateway resources through Ansible.

**4 Transit Gateway modules available:**
- Gateway management
- Connection management
- Prefix filtering
- Route reporting

## Modules

### ibm_tg_gateway

Manage Transit Gateway instances for network interconnection.

**Description:**
Transit Gateway enables you to connect multiple VPCs and on-premises networks through a single gateway, providing centralized routing and network management.

**Parameters:**
- `name` (required) - Transit Gateway name
- `location` (required) - Gateway location (e.g., us-south, us-east)
- `global_` - Enable global routing (default: false)
- `resource_group` - Resource group ID

**Example:**
```yaml
- name: Create Transit Gateway
  ibm_tg_gateway:
    name: production-tgw
    location: us-south
    global_: true
    resource_group: "{{ rg_id }}"
    state: present
  register: tgw
```

**Use Cases:**
- Multi-VPC connectivity
- Hybrid cloud networking
- Cross-region connectivity
- Network segmentation

### ibm_tg_connection

Manage connections to Transit Gateway (VPCs, Direct Link, etc.).

**Description:**
Connections attach networks to a Transit Gateway, enabling traffic flow between connected resources.

**Parameters:**
- `transit_gateway_id` (required) - Transit Gateway ID
- `network_type` (required) - Type of network (vpc, classic, directlink, gre_tunnel, unbound_gre_tunnel)
- `name` (required) - Connection name
- `network_id` - Network resource ID (VPC CRN, Direct Link ID)
- `network_account_id` - Account ID for cross-account connections
- `base_connection_id` - Base connection for redundant GRE tunnels
- `local_gateway_ip` - Local gateway IP for GRE tunnels
- `local_tunnel_ip` - Local tunnel IP for GRE tunnels
- `remote_gateway_ip` - Remote gateway IP for GRE tunnels
- `remote_tunnel_ip` - Remote tunnel IP for GRE tunnels
- `zone` - Availability zone

**Example - VPC Connection:**
```yaml
- name: Connect VPC to Transit Gateway
  ibm_tg_connection:
    transit_gateway_id: "{{ tgw.resource.id }}"
    network_type: vpc
    name: vpc-connection
    network_id: "{{ vpc.resource.crn }}"
    state: present
```

**Example - GRE Tunnel:**
```yaml
- name: Create GRE tunnel connection
  ibm_tg_connection:
    transit_gateway_id: "{{ tgw.resource.id }}"
    network_type: gre_tunnel
    name: on-prem-tunnel
    local_gateway_ip: 10.10.10.1
    local_tunnel_ip: 192.168.1.1
    remote_gateway_ip: 203.0.113.1
    remote_tunnel_ip: 192.168.1.2
    zone: us-south-1
    state: present
```

**Example - Cross-Account Connection:**
```yaml
- name: Connect VPC from another account
  ibm_tg_connection:
    transit_gateway_id: "{{ tgw.resource.id }}"
    network_type: vpc
    name: partner-vpc
    network_id: "{{ partner_vpc_crn }}"
    network_account_id: "{{ partner_account_id }}"
    state: present
```

### ibm_tg_connection_prefix_filter

Manage prefix filters for Transit Gateway connections to control route advertisements.

**Description:**
Prefix filters allow you to control which routes are advertised to and from a connection, providing fine-grained routing control.

**Parameters:**
- `transit_gateway_id` (required) - Transit Gateway ID
- `connection_id` (required) - Connection ID
- `action` (required) - Filter action (permit, deny)
- `prefix` (required) - IP prefix in CIDR notation
- `before` - Filter ID to insert before
- `ge` - Minimum prefix length to match
- `le` - Maximum prefix length to match

**Example - Permit Specific Prefix:**
```yaml
- name: Allow specific subnet
  ibm_tg_connection_prefix_filter:
    transit_gateway_id: "{{ tgw.resource.id }}"
    connection_id: "{{ connection.resource.id }}"
    action: permit
    prefix: 10.240.0.0/24
    state: present
```

**Example - Deny Range:**
```yaml
- name: Block private range
  ibm_tg_connection_prefix_filter:
    transit_gateway_id: "{{ tgw.resource.id }}"
    connection_id: "{{ connection.resource.id }}"
    action: deny
    prefix: 172.16.0.0/12
    state: present
```

**Example - Match Prefix Length:**
```yaml
- name: Permit /24 subnets only
  ibm_tg_connection_prefix_filter:
    transit_gateway_id: "{{ tgw.resource.id }}"
    connection_id: "{{ connection.resource.id }}"
    action: permit
    prefix: 10.0.0.0/8
    ge: 24
    le: 24
    state: present
```

### ibm_tg_route_report

Generate and manage route reports for Transit Gateway.

**Description:**
Route reports provide visibility into the routing table of a Transit Gateway, showing all learned and advertised routes.

**Parameters:**
- `transit_gateway_id` (required) - Transit Gateway ID

**Example:**
```yaml
- name: Generate route report
  ibm_tg_route_report:
    transit_gateway_id: "{{ tgw.resource.id }}"
    state: present
  register: report

- name: Display routes
  debug:
    var: report.resource
```

## Complete Transit Gateway Setup

```yaml
---
- name: Deploy Transit Gateway Infrastructure
  hosts: localhost
  vars:
    region: us-south
  
  tasks:
    # 1. Create Transit Gateway
    - name: Create Transit Gateway
      ibm_tg_gateway:
        name: enterprise-tgw
        location: "{{ region }}"
        global_: true
        state: present
      register: tgw

    # 2. Connect Production VPC
    - name: Connect production VPC
      ibm_tg_connection:
        transit_gateway_id: "{{ tgw.resource.id }}"
        network_type: vpc
        name: production-vpc-connection
        network_id: "{{ prod_vpc_crn }}"
        state: present
      register: prod_conn

    # 3. Connect Development VPC
    - name: Connect development VPC
      ibm_tg_connection:
        transit_gateway_id: "{{ tgw.resource.id }}"
        network_type: vpc
        name: dev-vpc-connection
        network_id: "{{ dev_vpc_crn }}"
        state: present
      register: dev_conn

    # 4. Connect On-Premises via GRE Tunnel
    - name: Create GRE tunnel to on-premises
      ibm_tg_connection:
        transit_gateway_id: "{{ tgw.resource.id }}"
        network_type: gre_tunnel
        name: datacenter-tunnel
        local_gateway_ip: 10.10.10.1
        local_tunnel_ip: 192.168.100.1
        remote_gateway_ip: 203.0.113.50
        remote_tunnel_ip: 192.168.100.2
        zone: us-south-1
        state: present
      register: gre_conn

    # 5. Configure Prefix Filters for Production
    - name: Allow production subnets
      ibm_tg_connection_prefix_filter:
        transit_gateway_id: "{{ tgw.resource.id }}"
        connection_id: "{{ prod_conn.resource.id }}"
        action: permit
        prefix: 10.240.0.0/16
        state: present

    - name: Deny default route from production
      ibm_tg_connection_prefix_filter:
        transit_gateway_id: "{{ tgw.resource.id }}"
        connection_id: "{{ prod_conn.resource.id }}"
        action: deny
        prefix: 0.0.0.0/0
        state: present

    # 6. Configure Prefix Filters for Development
    - name: Allow dev subnets
      ibm_tg_connection_prefix_filter:
        transit_gateway_id: "{{ tgw.resource.id }}"
        connection_id: "{{ dev_conn.resource.id }}"
        action: permit
        prefix: 10.241.0.0/16
        state: present

    # 7. Generate Route Report
    - name: Generate routing report
      ibm_tg_route_report:
        transit_gateway_id: "{{ tgw.resource.id }}"
        state: present
      register: routes

    - name: Display routing information
      debug:
        msg: "Route report generated: {{ routes.resource.id }}"
```

## Multi-Region Transit Gateway

```yaml
---
- name: Multi-Region Transit Gateway Setup
  hosts: localhost
  tasks:
    # Create Transit Gateway in US
    - name: Create US Transit Gateway
      ibm_tg_gateway:
        name: us-tgw
        location: us-south
        global_: true
        state: present
      register: us_tgw

    # Create Transit Gateway in EU
    - name: Create EU Transit Gateway
      ibm_tg_gateway:
        name: eu-tgw
        location: eu-de
        global_: true
        state: present
      register: eu_tgw

    # Connect US VPCs
    - name: Connect US production VPC
      ibm_tg_connection:
        transit_gateway_id: "{{ us_tgw.resource.id }}"
        network_type: vpc
        name: us-prod-vpc
        network_id: "{{ us_prod_vpc_crn }}"
        state: present

    # Connect EU VPCs
    - name: Connect EU production VPC
      ibm_tg_connection:
        transit_gateway_id: "{{ eu_tgw.resource.id }}"
        network_type: vpc
        name: eu-prod-vpc
        network_id: "{{ eu_prod_vpc_crn }}"
        state: present

    # Global routing enables cross-region connectivity
```

## Hybrid Cloud Architecture

```yaml
---
- name: Hybrid Cloud with Transit Gateway
  hosts: localhost
  tasks:
    - name: Create Transit Gateway
      ibm_tg_gateway:
        name: hybrid-tgw
        location: us-south
        global_: false
        state: present
      register: tgw

    # Connect IBM Cloud VPCs
    - name: Connect cloud VPCs
      ibm_tg_connection:
        transit_gateway_id: "{{ tgw.resource.id }}"
        network_type: vpc
        name: "{{ item.name }}"
        network_id: "{{ item.crn }}"
        state: present
      loop:
        - { name: 'web-tier-vpc', crn: '{{ web_vpc_crn }}' }
        - { name: 'app-tier-vpc', crn: '{{ app_vpc_crn }}' }
        - { name: 'data-tier-vpc', crn: '{{ data_vpc_crn }}' }

    # Connect Direct Link for on-premises
    - name: Connect Direct Link
      ibm_tg_connection:
        transit_gateway_id: "{{ tgw.resource.id }}"
        network_type: directlink
        name: datacenter-dl
        network_id: "{{ direct_link_id }}"
        state: present
      register: dl_conn

    # Filter routes from on-premises
    - name: Allow corporate networks
      ibm_tg_connection_prefix_filter:
        transit_gateway_id: "{{ tgw.resource.id }}"
        connection_id: "{{ dl_conn.resource.id }}"
        action: permit
        prefix: 192.168.0.0/16
        state: present

    - name: Deny internet routes
      ibm_tg_connection_prefix_filter:
        transit_gateway_id: "{{ tgw.resource.id }}"
        connection_id: "{{ dl_conn.resource.id }}"
        action: deny
        prefix: 0.0.0.0/0
        state: present
```

## Network Segmentation

```yaml
---
- name: Segmented Network Architecture
  hosts: localhost
  tasks:
    - name: Create Transit Gateway
      ibm_tg_gateway:
        name: segmented-tgw
        location: us-south
        state: present
      register: tgw

    # Production segment
    - name: Connect production VPC
      ibm_tg_connection:
        transit_gateway_id: "{{ tgw.resource.id }}"
        network_type: vpc
        name: production
        network_id: "{{ prod_vpc_crn }}"
        state: present
      register: prod

    # Development segment
    - name: Connect development VPC
      ibm_tg_connection:
        transit_gateway_id: "{{ tgw.resource.id }}"
        network_type: vpc
        name: development
        network_id: "{{ dev_vpc_crn }}"
        state: present
      register: dev

    # Shared services segment
    - name: Connect shared services VPC
      ibm_tg_connection:
        transit_gateway_id: "{{ tgw.resource.id }}"
        network_type: vpc
        name: shared-services
        network_id: "{{ shared_vpc_crn }}"
        state: present
      register: shared

    # Allow production to shared services only
    - name: Production to shared services
      ibm_tg_connection_prefix_filter:
        transit_gateway_id: "{{ tgw.resource.id }}"
        connection_id: "{{ prod.resource.id }}"
        action: permit
        prefix: "{{ shared_vpc_cidr }}"
        state: present

    - name: Block production to dev
      ibm_tg_connection_prefix_filter:
        transit_gateway_id: "{{ tgw.resource.id }}"
        connection_id: "{{ prod.resource.id }}"
        action: deny
        prefix: "{{ dev_vpc_cidr }}"
        state: present
```

## Best Practices

### Gateway Design
1. **Use global routing** for multi-region connectivity
2. **Plan CIDR blocks** to avoid overlaps
3. **Implement prefix filters** for security
4. **Monitor route reports** regularly

### Connection Management
1. **Name connections clearly** for easy identification
2. **Use cross-account connections** for partner integration
3. **Implement redundant GRE tunnels** for high availability
4. **Document network topology**

### Security
1. **Apply prefix filters** to control route advertisements
2. **Use deny rules** for sensitive networks
3. **Implement network segmentation**
4. **Regular security audits**

### Performance
1. **Choose appropriate locations** for gateways
2. **Monitor connection status**
3. **Use Direct Link** for high-bandwidth requirements
4. **Optimize routing policies**

## Common Parameters

All Transit Gateway modules support:

```yaml
ibmcloud_api_key: string
  IBM Cloud API key

region: string (default: us-south)
  IBM Cloud region

state: string (default: present)
  Desired state: present, absent

name: string
  Resource name

id: string
  Resource ID (for updates/deletes)
```

## Troubleshooting

### Connection Issues
```yaml
- name: Check gateway status
  ibm_tg_gateway:
    id: "{{ tgw_id }}"
    state: present
  register: gateway

- name: Verify connections
  debug:
    msg: "Gateway status: {{ gateway.resource.status }}"
```

### Route Verification
```yaml
- name: Generate route report
  ibm_tg_route_report:
    transit_gateway_id: "{{ tgw_id }}"
    state: present
  register: routes

- name: Check learned routes
  debug:
    var: routes.resource
```

## SDK Requirements

- `ibm-platform-services >= 0.50.0`
- `ibm-cloud-sdk-core >= 3.20.0`
- Python 3.10+

## Related Documentation

- [VPC Module Reference](MODULE_REFERENCE.md)
- [Platform Services Guide](PLATFORM_SERVICES.md)
- [IBM Transit Gateway Docs](https://cloud.ibm.com/docs/transit-gateway)

## License

GNU General Public License v3.0+

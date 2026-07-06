#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, IBM Cloud Team
# BSD 2-Clause License (see LICENSE or https://opensource.org/licenses/BSD-2-Clause)

DOCUMENTATION = r'''
---
module: ibm_is_route
short_description: Manage IBM Cloud VPC Route
version_added: "1.0.0"
description:
    - Create, update, or delete IBM Cloud VPC Route in a routing table
    - This module uses the native IBM Cloud Python SDK (no Terraform dependency)
    - Supports idempotent operations
    - Routes control traffic flow within a VPC routing table
requirements:
    - ibm-vpc >= 0.33.0
    - ibm-cloud-sdk-core >= 3.20.0
options:
    vpc_id:
        description:
            - The VPC identifier
            - Required for all operations
        type: str
        required: true
    routing_table_id:
        description:
            - The routing table identifier
            - Required for all operations
        type: str
        required: true
    name:
        description:
            - The name of the route
            - Must be unique within the routing table
        type: str
        required: false
    id:
        description:
            - The route identifier
            - Used for update and delete operations
        type: str
        required: false
    destination:
        description:
            - The destination CIDR of the route
            - Required when creating a route
            - Example: 10.2.0.0/24
        type: str
        required: false
    zone:
        description:
            - The zone name where the route applies
            - Required when creating a route with next_hop as an IP address
            - Example: us-south-1
        type: str
        required: false
    action:
        description:
            - The action to perform with a packet matching the route
            - 'deliver' - Deliver the packet to the next hop
            - 'drop' - Drop the packet
            - 'delegate' - Delegate to system-provided routes
            - 'delegate_vpc' - Delegate to system-provided routes, ignoring Internet-bound routes
        type: str
        required: false
        choices: ['deliver', 'drop', 'delegate', 'delegate_vpc']
        default: 'deliver'
    next_hop:
        description:
            - The next hop for the route
            - Can be an IP address (requires zone) or a VPN gateway/connection ID
            - Required when action is 'deliver'
            - For IP address format: 10.0.0.5
            - For VPN gateway: ID of the VPN gateway
            - For VPN connection: ID of the VPN gateway connection
        type: dict
        required: false
        suboptions:
            address:
                description:
                    - The IP address of the next hop
                    - Requires zone parameter to be set
                type: str
                required: false
            id:
                description:
                    - The ID of the VPN gateway or VPN gateway connection
                type: str
                required: false
    priority:
        description:
            - The route priority
            - Only applicable when action is 'delegate'
            - Smaller values have higher priority
            - Range: 0-4
        type: int
        required: false
    advertise:
        description:
            - Whether to advertise this route to ingress sources
            - Applicable for ingress routing tables
            - Transit gateway and direct link routes
        type: bool
        required: false
        default: false
author:
    - IBM Cloud Team
'''

EXAMPLES = r'''
# Create a route with IP address next hop
- name: Create route to subnet
  ibm_is_route:
    vpc_id: "r006-12345678-1234-1234-1234-123456789012"
    routing_table_id: "r006-87654321-4321-4321-4321-210987654321"
    name: "route-to-subnet"
    destination: "10.2.0.0/24"
    zone: "us-south-1"
    next_hop:
      address: "10.0.0.5"
    action: "deliver"
    state: present

# Create a route with VPN gateway next hop
- name: Create route via VPN
  ibm_is_route:
    vpc_id: "r006-12345678-1234-1234-1234-123456789012"
    routing_table_id: "r006-87654321-4321-4321-4321-210987654321"
    name: "route-via-vpn"
    destination: "192.168.0.0/16"
    next_hop:
      id: "r006-vpn-gateway-id"
    action: "deliver"
    state: present

# Create a drop route
- name: Create drop route
  ibm_is_route:
    vpc_id: "r006-12345678-1234-1234-1234-123456789012"
    routing_table_id: "r006-87654321-4321-4321-4321-210987654321"
    name: "drop-route"
    destination: "172.16.0.0/12"
    action: "drop"
    state: present

# Create a delegate route with priority
- name: Create delegate route
  ibm_is_route:
    vpc_id: "r006-12345678-1234-1234-1234-123456789012"
    routing_table_id: "r006-87654321-4321-4321-4321-210987654321"
    name: "delegate-route"
    destination: "0.0.0.0/0"
    action: "delegate"
    priority: 2
    state: present

# Update route name and advertise setting
- name: Update route
  ibm_is_route:
    vpc_id: "r006-12345678-1234-1234-1234-123456789012"
    routing_table_id: "r006-87654321-4321-4321-4321-210987654321"
    id: "r006-route-id"
    name: "updated-route-name"
    advertise: true
    state: present

# Delete a route by ID
- name: Delete route by ID
  ibm_is_route:
    vpc_id: "r006-12345678-1234-1234-1234-123456789012"
    routing_table_id: "r006-87654321-4321-4321-4321-210987654321"
    id: "r006-route-id"
    state: absent

# Delete a route by name
- name: Delete route by name
  ibm_is_route:
    vpc_id: "r006-12345678-1234-1234-1234-123456789012"
    routing_table_id: "r006-87654321-4321-4321-4321-210987654321"
    name: "route-to-delete"
    state: absent
'''

RETURN = r'''
resource:
    description: Route information
    returned: when state is present
    type: dict
    sample:
        id: "r006-12345678-1234-1234-1234-123456789012"
        name: "my-route"
        destination: "10.2.0.0/24"
        action: "deliver"
        zone:
            name: "us-south-1"
        next_hop:
            address: "10.0.0.5"
        priority: 0
        advertise: false
        created_at: "2024-01-15T12:30:00Z"
        lifecycle_state: "stable"
changed:
    description: Whether the resource was changed
    returned: always
    type: bool
msg:
    description: Status message
    returned: always
    type: str
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ibm.cloudcollection.plugins.module_utils.ibm_cloud_sdk import (
    IBMCloudSDKModule,
    get_common_argument_spec
)

try:
    from ibm_vpc import VpcV1
    from ibm_cloud_sdk_core import ApiException
    HAS_IBM_VPC = True
except ImportError:
    HAS_IBM_VPC = False


class IBMRouteModule(IBMCloudSDKModule):
    """IBM Cloud VPC Route module implementation."""
    
    def __init__(self, module):
        """Initialize the module."""
        super().__init__(module)
        
        if not HAS_IBM_VPC:
            self.fail_json(msg="ibm-vpc Python SDK is required")
        
        self.vpc_service = VpcV1(authenticator=self.auth.get_authenticator())
        self.vpc_service.set_service_url(f'https://{self.region}.iaas.cloud.ibm.com/v1')
        
        self.vpc_id = self.params.get('vpc_id')
        self.routing_table_id = self.params.get('routing_table_id')
        self.resource_id = self.params.get('id')
        self.resource_name = self.params.get('name')
    
    def get_resource(self, resource_id: str):
        """Get route by ID."""
        try:
            response = self.vpc_service.get_vpc_routing_table_route(
                vpc_id=self.vpc_id,
                routing_table_id=self.routing_table_id,
                id=resource_id
            )
            return response.get_result()
        except ApiException as e:
            if e.code == 404:
                return None
            self.handle_api_exception(e, f"retrieve route {resource_id}")
    
    def list_resources(self):
        """List all routes in the routing table."""
        try:
            response = self.vpc_service.list_vpc_routing_table_routes(
                vpc_id=self.vpc_id,
                routing_table_id=self.routing_table_id
            )
            return response.get_result().get('routes', [])
        except ApiException as e:
            self.handle_api_exception(e, f"list routes")
    
    def create_resource(self):
        """Create a new route."""
        self.check_mode_exit(changed=True, msg=f"Would create route: {self.resource_name}")
        
        # Validate required parameters for creation
        destination = self.params.get('destination')
        if not destination:
            self.fail_json(msg="destination is required when creating a route")
        
        action = self.params.get('action', 'deliver')
        
        try:
            # Build the route prototype
            prototype = {
                'destination': destination,
                'action': action
            }
            
            # Add name if provided
            if self.resource_name:
                prototype['name'] = self.resource_name
            
            # Handle next_hop based on action
            if action == 'deliver':
                next_hop = self.params.get('next_hop')
                if not next_hop:
                    self.fail_json(msg="next_hop is required when action is 'deliver'")
                
                if 'address' in next_hop:
                    # IP address next hop requires zone
                    zone = self.params.get('zone')
                    if not zone:
                        self.fail_json(msg="zone is required when next_hop is an IP address")
                    
                    from ibm_vpc.vpc_v1 import (
                        RouteNextHopPrototypeRouteNextHopIPRouteNextHopIPUnicastIP,
                        ZoneIdentityByName
                    )
                    prototype['next_hop'] = RouteNextHopPrototypeRouteNextHopIPRouteNextHopIPUnicastIP(
                        address=next_hop['address']
                    )
                    prototype['zone'] = ZoneIdentityByName(name=zone)
                    
                elif 'id' in next_hop:
                    # VPN gateway or connection next hop
                    from ibm_vpc.vpc_v1 import RouteNextHopPrototypeVPNGatewayConnectionIdentity
                    prototype['next_hop'] = RouteNextHopPrototypeVPNGatewayConnectionIdentity(
                        id=next_hop['id']
                    )
            
            # Handle priority for delegate action
            if action == 'delegate':
                priority = self.params.get('priority')
                if priority is not None:
                    if priority < 0 or priority > 4:
                        self.fail_json(msg="priority must be between 0 and 4")
                    prototype['priority'] = priority
                
                # For delegate action, zone is still required by SDK even though not used
                zone = self.params.get('zone')
                if zone:
                    from ibm_vpc.vpc_v1 import ZoneIdentityByName
                    prototype['zone'] = ZoneIdentityByName(name=zone)
            
            # Handle advertise setting
            advertise = self.params.get('advertise')
            if advertise is not None:
                prototype['advertise'] = advertise
            
            # Call the SDK method - build kwargs dynamically
            create_kwargs = {
                'vpc_id': self.vpc_id,
                'routing_table_id': self.routing_table_id,
                'destination': destination,
                'action': action
            }
            
            # Add optional parameters only if they are set
            if prototype.get('zone'):
                create_kwargs['zone'] = prototype['zone']
            if prototype.get('name'):
                create_kwargs['name'] = prototype['name']
            if prototype.get('next_hop'):
                create_kwargs['next_hop'] = prototype['next_hop']
            if prototype.get('priority') is not None:
                create_kwargs['priority'] = prototype['priority']
            if prototype.get('advertise') is not None:
                create_kwargs['advertise'] = prototype['advertise']
            
            response = self.vpc_service.create_vpc_routing_table_route(**create_kwargs)
            resource = response.get_result()
            
            self.result['changed'] = True
            self.result['resource'] = resource
            self.result['msg'] = f"Route {resource.get('name', resource['id'])} created successfully"
            
        except ApiException as e:
            self.handle_api_exception(e, f"create route {self.resource_name}")
    
    def update_resource(self, resource):
        """Update an existing route."""
        changed = False
        updates = {}
        
        # Check for name update
        if self.resource_name and resource.get('name') != self.resource_name:
            updates['name'] = self.resource_name
            changed = True
        
        # Check for priority update (only for delegate action)
        if resource.get('action') == 'delegate':
            priority = self.params.get('priority')
            if priority is not None and resource.get('priority') != priority:
                if priority < 0 or priority > 4:
                    self.fail_json(msg="priority must be between 0 and 4")
                updates['priority'] = priority
                changed = True
        
        # Check for advertise update
        advertise = self.params.get('advertise')
        if advertise is not None and resource.get('advertise') != advertise:
            updates['advertise'] = advertise
            changed = True
        
        if updates:
            self.check_mode_exit(changed=True, msg=f"Would update route: {resource['id']}")
            
            try:
                response = self.vpc_service.update_vpc_routing_table_route(
                    vpc_id=self.vpc_id,
                    routing_table_id=self.routing_table_id,
                    id=resource['id'],
                    route_patch=updates
                )
                resource = response.get_result()
                changed = True
            except ApiException as e:
                self.handle_api_exception(e, f"update route {resource['id']}")
        
        self.result['changed'] = changed
        self.result['resource'] = resource
        self.result['msg'] = f"Route {resource.get('name', resource['id'])} " + ("updated" if changed else "unchanged")
    
    def delete_resource(self, resource_id: str):
        """Delete a route."""
        self.check_mode_exit(changed=True, msg=f"Would delete route: {resource_id}")
        
        try:
            self.vpc_service.delete_vpc_routing_table_route(
                vpc_id=self.vpc_id,
                routing_table_id=self.routing_table_id,
                id=resource_id
            )
            self.result['changed'] = True
            self.result['msg'] = f"Route {resource_id} deleted successfully"
        except ApiException as e:
            self.handle_api_exception(e, f"delete route {resource_id}")
    
    def run(self):
        """Execute the module logic."""
        # Validate required parameters
        if not self.vpc_id:
            self.fail_json(msg="vpc_id is required")
        if not self.routing_table_id:
            self.fail_json(msg="routing_table_id is required")
        
        existing_resource = None
        if self.resource_id:
            existing_resource = self.get_resource(self.resource_id)
        elif self.resource_name:
            resources = self.list_resources()
            for res in resources:
                if res.get('name') == self.resource_name:
                    existing_resource = res
                    break
        
        if self.state == 'present':
            if existing_resource:
                self.update_resource(existing_resource)
            else:
                self.create_resource()
        
        elif self.state == 'absent':
            if existing_resource:
                self.delete_resource(existing_resource['id'])
            else:
                self.result['msg'] = f"Route not found"
        
        self.exit_json()


def main():
    """Main module execution."""
    argument_spec = get_common_argument_spec()
    argument_spec.update({
        'vpc_id': {'type': 'str', 'required': True},
        'routing_table_id': {'type': 'str', 'required': True},
        'name': {'type': 'str', 'required': False},
        'id': {'type': 'str', 'required': False},
        'destination': {'type': 'str', 'required': False},
        'zone': {'type': 'str', 'required': False},
        'action': {
            'type': 'str',
            'required': False,
            'default': 'deliver',
            'choices': ['deliver', 'drop', 'delegate', 'delegate_vpc']
        },
        'next_hop': {
            'type': 'dict',
            'required': False,
            'options': {
                'address': {'type': 'str', 'required': False},
                'id': {'type': 'str', 'required': False}
            }
        },
        'priority': {'type': 'int', 'required': False},
        'advertise': {'type': 'bool', 'required': False, 'default': False}
    })
    
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[
            ['state', 'absent', ['id', 'name'], True]
        ]
    )
    
    resource_module = IBMRouteModule(module)
    resource_module.run()


if __name__ == '__main__':
    main()
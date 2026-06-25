#!/usr/bin/env python3
"""
Extended Module Generator for IBM Cloud VPC (IS) Services

Generates additional modules for comprehensive IBM Cloud VPC coverage including:
- Bare metal servers
- Dedicated hosts
- Instance groups and templates
- Snapshots and backups
- Load balancer components
- VPN components
- Network interfaces
- Placement groups
- Reservations
"""

import sys
from pathlib import Path

# Import the base generator
sys.path.insert(0, str(Path(__file__).parent))
from generate_modules import generate_module, MODULE_TEMPLATE

# Extended VPC IS resource definitions
EXTENDED_VPC_RESOURCES = {
    # Instance Management
    'instance_template': {
        'get_method': 'get_instance_template',
        'list_method': 'list_instance_templates',
        'create_method': 'create_instance_template',
        'update_method': 'update_instance_template',
        'delete_method': 'delete_instance_template',
        'list_key': 'templates',
        'required_params': ['name', 'vpc', 'profile', 'zone', 'image'],
        'optional_params': ['keys', 'primary_network_interface', 'user_data', 'boot_volume']
    },
    'instance_group': {
        'get_method': 'get_instance_group',
        'list_method': 'list_instance_groups',
        'create_method': 'create_instance_group',
        'update_method': 'update_instance_group',
        'delete_method': 'delete_instance_group',
        'list_key': 'instance_groups',
        'required_params': ['name', 'instance_template', 'subnets'],
        'optional_params': ['membership_count', 'application_port', 'load_balancer_pool']
    },
    'instance_group_manager': {
        'get_method': 'get_instance_group_manager',
        'list_method': 'list_instance_group_managers',
        'create_method': 'create_instance_group_manager',
        'update_method': 'update_instance_group_manager',
        'delete_method': 'delete_instance_group_manager',
        'list_key': 'managers',
        'required_params': ['instance_group', 'name'],
        'optional_params': ['max_membership_count', 'min_membership_count', 'aggregation_window']
    },
    
    # Bare Metal Servers
    'bare_metal_server': {
        'get_method': 'get_bare_metal_server',
        'list_method': 'list_bare_metal_servers',
        'create_method': 'create_bare_metal_server',
        'update_method': 'update_bare_metal_server',
        'delete_method': 'delete_bare_metal_server',
        'list_key': 'bare_metal_servers',
        'required_params': ['name', 'profile', 'zone', 'primary_network_interface'],
        'optional_params': ['image', 'keys', 'user_data', 'vpc', 'resource_group']
    },
    'bare_metal_server_network_interface': {
        'get_method': 'get_bare_metal_server_network_interface',
        'list_method': 'list_bare_metal_server_network_interfaces',
        'create_method': 'create_bare_metal_server_network_interface',
        'update_method': 'update_bare_metal_server_network_interface',
        'delete_method': 'delete_bare_metal_server_network_interface',
        'list_key': 'network_interfaces',
        'required_params': ['bare_metal_server', 'subnet'],
        'optional_params': ['name', 'security_groups', 'allow_ip_spoofing']
    },
    
    # Dedicated Hosts
    'dedicated_host_group': {
        'get_method': 'get_dedicated_host_group',
        'list_method': 'list_dedicated_host_groups',
        'create_method': 'create_dedicated_host_group',
        'update_method': 'update_dedicated_host_group',
        'delete_method': 'delete_dedicated_host_group',
        'list_key': 'groups',
        'required_params': ['name', 'family', 'zone'],
        'optional_params': ['class', 'resource_group']
    },
    'dedicated_host': {
        'get_method': 'get_dedicated_host',
        'list_method': 'list_dedicated_hosts',
        'create_method': 'create_dedicated_host',
        'update_method': 'update_dedicated_host',
        'delete_method': 'delete_dedicated_host',
        'list_key': 'dedicated_hosts',
        'required_params': ['name', 'profile', 'group'],
        'optional_params': ['instance_placement_enabled', 'resource_group']
    },
    
    # Snapshots and Backups
    'snapshot': {
        'get_method': 'get_snapshot',
        'list_method': 'list_snapshots',
        'create_method': 'create_snapshot',
        'update_method': 'update_snapshot',
        'delete_method': 'delete_snapshot',
        'list_key': 'snapshots',
        'required_params': ['name', 'source_volume'],
        'optional_params': ['resource_group', 'user_tags']
    },
    'snapshot_consistency_group': {
        'get_method': 'get_snapshot_consistency_group',
        'list_method': 'list_snapshot_consistency_groups',
        'create_method': 'create_snapshot_consistency_group',
        'update_method': 'update_snapshot_consistency_group',
        'delete_method': 'delete_snapshot_consistency_group',
        'list_key': 'snapshot_consistency_groups',
        'required_params': ['name', 'snapshots'],
        'optional_params': ['resource_group', 'delete_snapshots_on_delete']
    },
    'backup_policy': {
        'get_method': 'get_backup_policy',
        'list_method': 'list_backup_policies',
        'create_method': 'create_backup_policy',
        'update_method': 'update_backup_policy',
        'delete_method': 'delete_backup_policy',
        'list_key': 'backup_policies',
        'required_params': ['name', 'match_resource_types'],
        'optional_params': ['match_user_tags', 'resource_group']
    },
    'backup_policy_plan': {
        'get_method': 'get_backup_policy_plan',
        'list_method': 'list_backup_policy_plans',
        'create_method': 'create_backup_policy_plan',
        'update_method': 'update_backup_policy_plan',
        'delete_method': 'delete_backup_policy_plan',
        'list_key': 'plans',
        'required_params': ['backup_policy', 'name', 'cron_spec'],
        'optional_params': ['active', 'attach_user_tags', 'copy_user_tags', 'deletion_trigger']
    },
    
    # Load Balancer Components
    'lb_listener': {
        'get_method': 'get_load_balancer_listener',
        'list_method': 'list_load_balancer_listeners',
        'create_method': 'create_load_balancer_listener',
        'update_method': 'update_load_balancer_listener',
        'delete_method': 'delete_load_balancer_listener',
        'list_key': 'listeners',
        'required_params': ['load_balancer', 'protocol', 'port'],
        'optional_params': ['default_pool', 'certificate_instance', 'connection_limit']
    },
    'lb_pool': {
        'get_method': 'get_load_balancer_pool',
        'list_method': 'list_load_balancer_pools',
        'create_method': 'create_load_balancer_pool',
        'update_method': 'update_load_balancer_pool',
        'delete_method': 'delete_load_balancer_pool',
        'list_key': 'pools',
        'required_params': ['load_balancer', 'name', 'algorithm', 'protocol', 'health_monitor'],
        'optional_params': ['members', 'session_persistence']
    },
    'lb_pool_member': {
        'get_method': 'get_load_balancer_pool_member',
        'list_method': 'list_load_balancer_pool_members',
        'create_method': 'create_load_balancer_pool_member',
        'update_method': 'update_load_balancer_pool_member',
        'delete_method': 'delete_load_balancer_pool_member',
        'list_key': 'members',
        'required_params': ['load_balancer', 'pool', 'port', 'target'],
        'optional_params': ['weight']
    },
    
    # VPN Components
    'ike_policy': {
        'get_method': 'get_ike_policy',
        'list_method': 'list_ike_policies',
        'create_method': 'create_ike_policy',
        'update_method': 'update_ike_policy',
        'delete_method': 'delete_ike_policy',
        'list_key': 'ike_policies',
        'required_params': ['name', 'authentication_algorithm', 'encryption_algorithm', 'dh_group', 'ike_version'],
        'optional_params': ['key_lifetime', 'resource_group']
    },
    'ipsec_policy': {
        'get_method': 'get_ipsec_policy',
        'list_method': 'list_ipsec_policies',
        'create_method': 'create_ipsec_policy',
        'update_method': 'update_ipsec_policy',
        'delete_method': 'delete_ipsec_policy',
        'list_key': 'ipsec_policies',
        'required_params': ['name', 'authentication_algorithm', 'encryption_algorithm', 'pfs'],
        'optional_params': ['key_lifetime', 'resource_group']
    },
    'vpn_server': {
        'get_method': 'get_vpn_server',
        'list_method': 'list_vpn_servers',
        'create_method': 'create_vpn_server',
        'update_method': 'update_vpn_server',
        'delete_method': 'delete_vpn_server',
        'list_key': 'vpn_servers',
        'required_params': ['name', 'certificate', 'client_authentication', 'client_ip_pool', 'subnets'],
        'optional_params': ['client_dns_server_ips', 'enable_split_tunneling', 'port', 'protocol']
    },
    
    # Network Components
    'network_interface': {
        'get_method': 'get_instance_network_interface',
        'list_method': 'list_instance_network_interfaces',
        'create_method': 'create_instance_network_interface',
        'update_method': 'update_instance_network_interface',
        'delete_method': 'delete_instance_network_interface',
        'list_key': 'network_interfaces',
        'required_params': ['instance', 'subnet'],
        'optional_params': ['name', 'security_groups', 'allow_ip_spoofing']
    },
    'virtual_network_interface': {
        'get_method': 'get_virtual_network_interface',
        'list_method': 'list_virtual_network_interfaces',
        'create_method': 'create_virtual_network_interface',
        'update_method': 'update_virtual_network_interface',
        'delete_method': 'delete_virtual_network_interface',
        'list_key': 'virtual_network_interfaces',
        'required_params': ['name'],
        'optional_params': ['subnet', 'security_groups', 'enable_infrastructure_nat']
    },
    'endpoint_gateway': {
        'get_method': 'get_endpoint_gateway',
        'list_method': 'list_endpoint_gateways',
        'create_method': 'create_endpoint_gateway',
        'update_method': 'update_endpoint_gateway',
        'delete_method': 'delete_endpoint_gateway',
        'list_key': 'endpoint_gateways',
        'required_params': ['name', 'target', 'vpc'],
        'optional_params': ['ips', 'resource_group']
    },
    
    # Placement and Reservations
    'placement_group': {
        'get_method': 'get_placement_group',
        'list_method': 'list_placement_groups',
        'create_method': 'create_placement_group',
        'update_method': 'update_placement_group',
        'delete_method': 'delete_placement_group',
        'list_key': 'placement_groups',
        'required_params': ['name', 'strategy'],
        'optional_params': ['resource_group']
    },
    'reservation': {
        'get_method': 'get_reservation',
        'list_method': 'list_reservations',
        'create_method': 'create_reservation',
        'update_method': 'update_reservation',
        'delete_method': 'delete_reservation',
        'list_key': 'reservations',
        'required_params': ['name', 'capacity', 'committed_use', 'profile', 'zone'],
        'optional_params': ['affinity_policy', 'resource_group']
    },
    
    # Routing
    'routing_table': {
        'get_method': 'get_vpc_routing_table',
        'list_method': 'list_vpc_routing_tables',
        'create_method': 'create_vpc_routing_table',
        'update_method': 'update_vpc_routing_table',
        'delete_method': 'delete_vpc_routing_table',
        'list_key': 'routing_tables',
        'required_params': ['vpc', 'name'],
        'optional_params': ['route_direct_link_ingress', 'route_transit_gateway_ingress', 'route_vpc_zone_ingress']
    },
    'route': {
        'get_method': 'get_vpc_routing_table_route',
        'list_method': 'list_vpc_routing_table_routes',
        'create_method': 'create_vpc_routing_table_route',
        'update_method': 'update_vpc_routing_table_route',
        'delete_method': 'delete_vpc_routing_table_route',
        'list_key': 'routes',
        'required_params': ['vpc', 'routing_table', 'destination', 'zone', 'next_hop'],
        'optional_params': ['action', 'name', 'priority']
    },
    
    # Address Prefixes
    'address_prefix': {
        'get_method': 'get_vpc_address_prefix',
        'list_method': 'list_vpc_address_prefixes',
        'create_method': 'create_vpc_address_prefix',
        'update_method': 'update_vpc_address_prefix',
        'delete_method': 'delete_vpc_address_prefix',
        'list_key': 'address_prefixes',
        'required_params': ['vpc', 'cidr', 'zone'],
        'optional_params': ['name', 'is_default']
    },
    
    # Shares (File Storage)
    'share': {
        'get_method': 'get_share',
        'list_method': 'list_shares',
        'create_method': 'create_share',
        'update_method': 'update_share',
        'delete_method': 'delete_share',
        'list_key': 'shares',
        'required_params': ['name', 'profile', 'size', 'zone'],
        'optional_params': ['encryption_key', 'iops', 'mount_targets', 'resource_group']
    },
    'share_mount_target': {
        'get_method': 'get_share_mount_target',
        'list_method': 'list_share_mount_targets',
        'create_method': 'create_share_mount_target',
        'update_method': 'update_share_mount_target',
        'delete_method': 'delete_share_mount_target',
        'list_key': 'mount_targets',
        'required_params': ['share', 'name', 'vpc'],
        'optional_params': ['subnet']
    }
}


def main():
    """Main generator function for extended modules."""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    modules_dir = project_root / "plugins" / "modules"
    
    print("=" * 60)
    print("IBM Cloud VPC Extended Module Generator")
    print("=" * 60)
    print(f"\nGenerating extended modules in: {modules_dir}")
    print(f"Total resources to generate: {len(EXTENDED_VPC_RESOURCES)}\n")
    
    modules_dir.mkdir(parents=True, exist_ok=True)
    
    generated = 0
    failed = 0
    
    for resource_type, config in EXTENDED_VPC_RESOURCES.items():
        try:
            generate_module(resource_type, config, modules_dir)
            generated += 1
        except Exception as e:
            print(f"✗ Failed to generate {resource_type}: {e}")
            failed += 1
    
    print(f"\n{'=' * 60}")
    print(f"Extended generation complete!")
    print(f"  Generated: {generated} modules")
    print(f"  Failed: {failed} modules")
    print(f"{'=' * 60}\n")


if __name__ == '__main__':
    main()

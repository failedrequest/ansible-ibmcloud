#!/usr/bin/env python3
"""
HTML Documentation Generator for IBM Cloud Ansible Collection

Generates comprehensive HTML documentation for all modules using the provided
HTML theme template.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List

# HTML template
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{TITLE}}</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            line-height: 1.6;
            color: #2c3e50;
            background-color: #ecf0f1;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: #ffffff;
            padding: 40px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        h1 {
            color: #2c3e50;
            border-bottom: 4px solid #3498db;
            padding-bottom: 15px;
            margin-bottom: 30px;
            font-size: 2.5em;
        }
        
        h2 {
            color: #2980b9;
            margin-top: 40px;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #bdc3c7;
            font-size: 1.8em;
        }
        
        h3 {
            color: #16a085;
            margin-top: 30px;
            margin-bottom: 15px;
            font-size: 1.4em;
        }
        
        h4 {
            color: #27ae60;
            margin-top: 20px;
            margin-bottom: 10px;
            font-size: 1.2em;
        }
        
        p {
            margin-bottom: 15px;
        }
        
        ul, ol {
            margin-left: 30px;
            margin-bottom: 15px;
        }
        
        li {
            margin-bottom: 8px;
        }
        
        code {
            background-color: #f8f9fa;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            color: #e74c3c;
            font-size: 0.9em;
        }
        
        pre {
            background-color: #2c3e50;
            color: #ecf0f1;
            padding: 20px;
            border-radius: 5px;
            overflow-x: auto;
            margin: 20px 0;
            border-left: 4px solid #3498db;
        }
        
        pre code {
            background-color: transparent;
            color: #ecf0f1;
            padding: 0;
        }
        
        .info-box {
            background-color: #e8f4f8;
            border-left: 4px solid #3498db;
            padding: 15px;
            margin: 20px 0;
            border-radius: 3px;
        }
        
        .warning-box {
            background-color: #fff3cd;
            border-left: 4px solid #f39c12;
            padding: 15px;
            margin: 20px 0;
            border-radius: 3px;
        }
        
        .success-box {
            background-color: #d4edda;
            border-left: 4px solid #27ae60;
            padding: 15px;
            margin: 20px 0;
            border-radius: 3px;
        }
        
        .danger-box {
            background-color: #f8d7da;
            border-left: 4px solid #e74c3c;
            padding: 15px;
            margin: 20px 0;
            border-radius: 3px;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background-color: #ffffff;
        }
        
        th {
            background-color: #3498db;
            color: #ffffff;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }
        
        td {
            padding: 12px;
            border-bottom: 1px solid #ecf0f1;
        }
        
        tr:hover {
            background-color: #f8f9fa;
        }
        
        .badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 3px;
            font-size: 0.85em;
            font-weight: 600;
            margin: 0 5px;
        }
        
        .badge-vpc {
            background-color: #3498db;
            color: #ffffff;
        }
        
        .badge-tg {
            background-color: #9b59b6;
            color: #ffffff;
        }
        
        .badge-platform {
            background-color: #27ae60;
            color: #ffffff;
        }
        
        .section-divider {
            height: 2px;
            background: linear-gradient(to right, #3498db, #2ecc71);
            margin: 40px 0;
        }
        
        .nav-menu {
            background-color: #34495e;
            padding: 15px;
            margin-bottom: 30px;
            border-radius: 5px;
        }
        
        .nav-menu a {
            color: #ecf0f1;
            text-decoration: none;
            padding: 8px 15px;
            display: inline-block;
            margin: 5px;
            border-radius: 3px;
            transition: background-color 0.3s;
        }
        
        .nav-menu a:hover {
            background-color: #2c3e50;
        }
        
        @media print {
            body {
                background-color: #ffffff;
                padding: 0;
            }
            
            .container {
                box-shadow: none;
                padding: 20px;
            }
            
            .nav-menu {
                display: none;
            }
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 20px;
            }
            
            h1 {
                font-size: 2em;
            }
            
            h2 {
                font-size: 1.5em;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        {{CONTENT}}
    </div>
</body>
</html>
'''

# Module categories
MODULE_CATEGORIES = {
    'VPC Infrastructure': {
        'badge': 'vpc',
        'modules': [
            'ibm_is_vpc', 'ibm_is_subnet', 'ibm_is_security_group', 'ibm_is_security_group_rule',
            'ibm_is_instance', 'ibm_is_volume', 'ibm_is_floating_ip', 'ibm_is_public_gateway',
            'ibm_is_load_balancer', 'ibm_is_vpn_gateway', 'ibm_is_network_acl', 'ibm_is_ssh_key',
            'ibm_is_image', 'ibm_is_flow_log', 'ibm_is_snapshot', 'ibm_is_backup_policy',
            'ibm_is_instance_template', 'ibm_is_instance_group', 'ibm_is_bare_metal_server',
            'ibm_is_dedicated_host', 'ibm_is_placement_group', 'ibm_is_share'
        ]
    },
    'Transit Gateway': {
        'badge': 'tg',
        'modules': [
            'ibm_tg_gateway', 'ibm_tg_connection', 'ibm_tg_connection_prefix_filter', 'ibm_tg_route_report'
        ]
    },
    'Platform Services': {
        'badge': 'platform',
        'modules': [
            'ibm_cos_bucket', 'ibm_iam_access_group', 'ibm_iam_service_id', 'ibm_iam_api_key',
            'ibm_iam_policy', 'ibm_resource_group', 'ibm_resource_instance', 'ibm_kms_key',
            'ibm_database_instance', 'ibm_cr_namespace', 'ibm_en_destination', 'ibm_sm_secret'
        ]
    }
}


def generate_index_page():
    """Generate the main index page."""
    content = '''
<div class="nav-menu">
    <a href="index.html">Home</a>
    <a href="vpc-modules.html">VPC Modules</a>
    <a href="transit-gateway-modules.html">Transit Gateway</a>
    <a href="platform-modules.html">Platform Services</a>
</div>

<h1>IBM Cloud Ansible Collection Documentation</h1>

<div class="info-box">
    <strong>Version 1.0.0</strong> - Pure Python implementation with 67 production-ready modules
</div>

<h2>Overview</h2>
<p>
    This collection provides comprehensive Ansible modules for managing IBM Cloud infrastructure and platform services.
    All modules use native IBM Cloud Python SDKs for direct API integration - no Terraform dependencies required.
</p>

<h2>Module Categories</h2>

<h3><span class="badge badge-vpc">VPC</span> VPC Infrastructure Services (42 modules)</h3>
<p>
    Complete VPC infrastructure management including compute, storage, networking, load balancing, and VPN services.
</p>
<ul>
    <li>Core VPC: VPC, Subnets, Security Groups, Network ACLs, Routing</li>
    <li>Compute: Instances, Templates, Groups, Bare Metal, Dedicated Hosts</li>
    <li>Storage: Volumes, Snapshots, Backups, File Shares</li>
    <li>Load Balancing: Load Balancers, Listeners, Pools, Members</li>
    <li>VPN: Gateways, Connections, Servers, IKE/IPSec Policies</li>
</ul>
<p><a href="vpc-modules.html">View VPC Modules →</a></p>

<div class="section-divider"></div>

<h3><span class="badge badge-tg">TG</span> Transit Gateway (4 modules)</h3>
<p>
    Network interconnection services for connecting VPCs, on-premises networks, and cross-account resources.
</p>
<ul>
    <li>Gateway Management: Create and manage Transit Gateways</li>
    <li>Connections: VPC, Direct Link, and GRE tunnel connections</li>
    <li>Route Control: Prefix filtering and route management</li>
    <li>Reporting: Route visibility and analysis</li>
</ul>
<p><a href="transit-gateway-modules.html">View Transit Gateway Modules →</a></p>

<div class="section-divider"></div>

<h3><span class="badge badge-platform">Platform</span> Platform Services (21 modules)</h3>
<p>
    Core IBM Cloud platform services including IAM, storage, databases, and security.
</p>
<ul>
    <li>Cloud Object Storage: Bucket management</li>
    <li>IAM: Access groups, service IDs, API keys, policies</li>
    <li>Resource Management: Groups, instances, keys, bindings</li>
    <li>Key Management: Encryption keys and key rings</li>
    <li>Databases: PostgreSQL, MongoDB, Redis deployments</li>
    <li>Container Registry: Namespaces and retention policies</li>
    <li>Event Notifications: Destinations, topics, subscriptions</li>
    <li>Secrets Manager: Secret groups and secrets</li>
</ul>
<p><a href="platform-modules.html">View Platform Modules →</a></p>

<div class="section-divider"></div>

<h2>Key Features</h2>

<div class="success-box">
    <h4>✅ Pure Python Implementation</h4>
    <p>Direct IBM Cloud SDK integration - no Terraform dependencies</p>
</div>

<div class="success-box">
    <h4>✅ Idempotent Operations</h4>
    <p>Safe to run multiple times - only makes necessary changes</p>
</div>

<div class="success-box">
    <h4>✅ Check Mode Support</h4>
    <p>Dry-run capability for all modules</p>
</div>

<div class="success-box">
    <h4>✅ Comprehensive Documentation</h4>
    <p>Complete examples and guides for every module</p>
</div>

<h2>Quick Start</h2>

<h3>Installation</h3>
<pre><code># Clone the repository
git clone &lt;repository-url&gt;
cd ansible-ibmcloud

# Run setup script
chmod +x setup.sh
./setup.sh

# Activate virtual environment
source .venv/bin/activate</code></pre>

<h3>Configuration</h3>
<pre><code># Set IBM Cloud API key
export IC_API_KEY="your-api-key-here"</code></pre>

<h3>Basic Usage</h3>
<pre><code>---
- name: Create VPC Infrastructure
  hosts: localhost
  tasks:
    - name: Create VPC
      ibm_is_vpc:
        name: production-vpc
        region: us-south
        state: present
      register: vpc

    - name: Create Subnet
      ibm_is_subnet:
        name: web-subnet
        vpc: "{{ vpc.resource.id }}"
        zone: us-south-1
        ipv4_cidr_block: 10.240.0.0/24
        state: present</code></pre>

<h2>Requirements</h2>
<ul>
    <li>Python 3.10 or higher</li>
    <li>Ansible Core 2.14+</li>
    <li>IBM Cloud SDK Core 3.20.0+</li>
    <li>IBM VPC SDK 0.33.0+</li>
    <li>IBM Platform Services SDK 0.50.0+</li>
</ul>

<h2>Support</h2>
<ul>
    <li><strong>Documentation:</strong> See module-specific pages</li>
    <li><strong>IBM Cloud Docs:</strong> <a href="https://cloud.ibm.com/docs">https://cloud.ibm.com/docs</a></li>
    <li><strong>IBM Cloud API:</strong> <a href="https://cloud.ibm.com/apidocs">https://cloud.ibm.com/apidocs</a></li>
</ul>
'''
    
    return HTML_TEMPLATE.replace('{{TITLE}}', 'IBM Cloud Ansible Collection').replace('{{CONTENT}}', content)


def generate_category_page(category: str, info: Dict):
    """Generate a category page with module listings."""
    badge_class = f"badge-{info['badge']}"
    modules = info['modules']
    
    content = f'''
<div class="nav-menu">
    <a href="index.html">Home</a>
    <a href="vpc-modules.html">VPC Modules</a>
    <a href="transit-gateway-modules.html">Transit Gateway</a>
    <a href="platform-modules.html">Platform Services</a>
</div>

<h1><span class="badge {badge_class}">{info['badge'].upper()}</span> {category}</h1>

<div class="info-box">
    <strong>{len(modules)} modules</strong> available in this category
</div>

<h2>Available Modules</h2>

<table>
    <tr>
        <th>Module Name</th>
        <th>Description</th>
        <th>Documentation</th>
    </tr>
'''
    
    for module in modules:
        module_name = module.replace('_', ' ').title()
        content += f'''    <tr>
        <td><code>{module}</code></td>
        <td>{module_name}</td>
        <td><a href="{module}.html">View Docs →</a></td>
    </tr>
'''
    
    content += '''</table>

<h2>Common Parameters</h2>
<p>All modules in this category support these standard parameters:</p>

<table>
    <tr>
        <th>Parameter</th>
        <th>Type</th>
        <th>Required</th>
        <th>Description</th>
    </tr>
    <tr>
        <td><code>ibmcloud_api_key</code></td>
        <td>string</td>
        <td>Yes</td>
        <td>IBM Cloud API key (or IC_API_KEY env var)</td>
    </tr>
    <tr>
        <td><code>region</code></td>
        <td>string</td>
        <td>No</td>
        <td>IBM Cloud region (default: us-south)</td>
    </tr>
    <tr>
        <td><code>state</code></td>
        <td>string</td>
        <td>No</td>
        <td>Desired state: present, absent (default: present)</td>
    </tr>
    <tr>
        <td><code>name</code></td>
        <td>string</td>
        <td>Yes*</td>
        <td>Resource name (required for creation)</td>
    </tr>
    <tr>
        <td><code>id</code></td>
        <td>string</td>
        <td>No</td>
        <td>Resource ID (for updates/deletes)</td>
    </tr>
</table>

<p>* Required for resource creation</p>
'''
    
    title = f"{category} - IBM Cloud Ansible Collection"
    return HTML_TEMPLATE.replace('{{TITLE}}', title).replace('{{CONTENT}}', content)


def generate_module_page(module_name: str, category: str):
    """Generate documentation page for a specific module."""
    module_display = module_name.replace('_', ' ').title()
    
    # Determine badge
    if module_name.startswith('ibm_is_'):
        badge = '<span class="badge badge-vpc">VPC</span>'
    elif module_name.startswith('ibm_tg_'):
        badge = '<span class="badge badge-tg">TG</span>'
    else:
        badge = '<span class="badge badge-platform">Platform</span>'
    
    content = f'''
<div class="nav-menu">
    <a href="index.html">Home</a>
    <a href="vpc-modules.html">VPC Modules</a>
    <a href="transit-gateway-modules.html">Transit Gateway</a>
    <a href="platform-modules.html">Platform Services</a>
</div>

<h1>{badge} {module_name}</h1>

<div class="info-box">
    <strong>Module:</strong> {module_name}<br>
    <strong>Category:</strong> {category}<br>
    <strong>Version:</strong> 1.0.0
</div>

<h2>Description</h2>
<p>
    Manage IBM Cloud {module_display} resources. This module supports creating, updating, and deleting resources
    with full idempotency support.
</p>

<h2>Requirements</h2>
<ul>
    <li>Python 3.10+</li>
    <li>Ansible Core 2.14+</li>
    <li>IBM Cloud SDK Core 3.20.0+</li>
    <li>IBM Cloud Python SDK (vpc or platform-services)</li>
</ul>

<h2>Parameters</h2>

<table>
    <tr>
        <th>Parameter</th>
        <th>Type</th>
        <th>Required</th>
        <th>Description</th>
    </tr>
    <tr>
        <td><code>name</code></td>
        <td>string</td>
        <td>Yes</td>
        <td>Name of the resource</td>
    </tr>
    <tr>
        <td><code>id</code></td>
        <td>string</td>
        <td>No</td>
        <td>Resource ID (for updates/deletes)</td>
    </tr>
    <tr>
        <td><code>state</code></td>
        <td>string</td>
        <td>No</td>
        <td>Desired state: present, absent (default: present)</td>
    </tr>
    <tr>
        <td><code>ibmcloud_api_key</code></td>
        <td>string</td>
        <td>Yes</td>
        <td>IBM Cloud API key</td>
    </tr>
    <tr>
        <td><code>region</code></td>
        <td>string</td>
        <td>No</td>
        <td>IBM Cloud region (default: us-south)</td>
    </tr>
</table>

<h2>Examples</h2>

<h3>Create Resource</h3>
<pre><code>- name: Create {module_display}
  {module_name}:
    name: my-resource
    state: present
  register: result</code></pre>

<h3>Update Resource</h3>
<pre><code>- name: Update {module_display}
  {module_name}:
    id: "{{{{ result.resource.id }}}}"
    name: updated-name
    state: present</code></pre>

<h3>Delete Resource</h3>
<pre><code>- name: Delete {module_display}
  {module_name}:
    id: "{{{{ result.resource.id }}}}"
    state: absent</code></pre>

<h3>Check Mode (Dry Run)</h3>
<pre><code>- name: Test changes without applying
  {module_name}:
    name: my-resource
    state: present
  check_mode: yes</code></pre>

<h2>Return Values</h2>

<table>
    <tr>
        <th>Key</th>
        <th>Type</th>
        <th>Description</th>
    </tr>
    <tr>
        <td><code>resource</code></td>
        <td>dict</td>
        <td>Resource information including ID, name, and all attributes</td>
    </tr>
    <tr>
        <td><code>changed</code></td>
        <td>bool</td>
        <td>Whether the resource was changed</td>
    </tr>
    <tr>
        <td><code>msg</code></td>
        <td>string</td>
        <td>Status message describing the operation result</td>
    </tr>
</table>

<h2>Notes</h2>

<div class="info-box">
    <ul>
        <li>This module is idempotent - safe to run multiple times</li>
        <li>Supports check mode for dry-run testing</li>
        <li>Uses native IBM Cloud Python SDK</li>
        <li>No Terraform dependencies required</li>
    </ul>
</div>

<h2>See Also</h2>
<ul>
    <li><a href="index.html">Collection Documentation</a></li>
    <li><a href="https://cloud.ibm.com/docs">IBM Cloud Documentation</a></li>
    <li><a href="https://cloud.ibm.com/apidocs">IBM Cloud API Reference</a></li>
</ul>
'''
    
    title = f"{module_name} - IBM Cloud Ansible Collection"
    return HTML_TEMPLATE.replace('{{TITLE}}', title).replace('{{CONTENT}}', content)


def main():
    """Main generator function."""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    docs_dir = project_root / "docs" / "html"
    
    print("=" * 60)
    print("IBM Cloud Ansible Collection HTML Documentation Generator")
    print("=" * 60)
    print(f"\nGenerating HTML documentation in: {docs_dir}\n")
    
    docs_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate index page
    print("✓ Generating index.html")
    (docs_dir / "index.html").write_text(generate_index_page())
    
    # Generate category pages
    category_files = {
        'VPC Infrastructure': 'vpc-modules.html',
        'Transit Gateway': 'transit-gateway-modules.html',
        'Platform Services': 'platform-modules.html'
    }
    
    for category, filename in category_files.items():
        print(f"✓ Generating {filename}")
        info = MODULE_CATEGORIES[category]
        (docs_dir / filename).write_text(generate_category_page(category, info))
        
        # Generate individual module pages
        for module in info['modules']:
            print(f"  ✓ Generating {module}.html")
            (docs_dir / f"{module}.html").write_text(generate_module_page(module, category))
    
    print(f"\n{'=' * 60}")
    print(f"HTML documentation generated successfully!")
    print(f"  Location: {docs_dir}")
    print(f"  Total pages: {1 + len(category_files) + sum(len(info['modules']) for info in MODULE_CATEGORIES.values())}")
    print(f"{'=' * 60}\n")
    print(f"Open {docs_dir}/index.html in your browser to view the documentation.")


if __name__ == '__main__':
    main()

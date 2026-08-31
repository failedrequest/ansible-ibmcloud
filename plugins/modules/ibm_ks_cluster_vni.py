#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, IBM Cloud Team
# BSD 2-Clause License (see LICENSE or https://opensource.org/licenses/BSD-2-Clause)

DOCUMENTATION = r'''
---
module: ibm_ks_cluster_vni
short_description: Manage IBM Cloud Kubernetes Service (ROKS) cluster VNI attachments
version_added: "1.0.0"
description:
    - Attach or detach Virtual Network Interfaces (VNIs) to/from IBM Cloud Kubernetes Service clusters
    - This module uses the IBM Cloud CLI (ibmcloud ks) to manage VNI attachments
    - Supports idempotent operations
requirements:
    - ibmcloud CLI installed
    - ibmcloud ks plugin installed
    - IBM Cloud API key
notes:
    - This module uses the IBM Cloud CLI because VNI attachment operations are not available in the Python SDK
    - Authentication is handled automatically using the provided API key
    - The module will login, perform the operation, and logout
options:
    cluster:
        description:
            - Name or ID of the Kubernetes cluster
        type: str
        required: true
    vni_id:
        description:
            - ID of the Virtual Network Interface to attach/detach
        type: str
        required: true
    vni_subnet_id:
        description:
            - ID of the subnet where the VNI resides
            - Required when attaching a VNI without --vlan (non-baremetal path)
        type: str
        required: false
    vlan:
        description:
            - VLAN ID to tag the attachment on bare metal ROKS nodes.
            - Required for OVN-K Localnet secondary networks.
            - Passed as --vlan to ibmcloud ks vni attach baremetal.
        type: int
        required: false
    state:
        description:
            - Desired state of the VNI attachment
        type: str
        choices: ['present', 'absent']
        default: present
    ibmcloud_api_key:
        description:
            - IBM Cloud API key
            - Required for authentication
        type: str
        required: true
        no_log: true
    region:
        description:
            - IBM Cloud region
        type: str
        required: false
author:
    - IBM Cloud Team
'''

EXAMPLES = r'''
- name: Attach VNI to ROKS cluster (standard)
  ibm_ks_cluster_vni:
    cluster: my-roks-cluster
    vni_id: r006-12345678-1234-1234-1234-123456789abc
    vni_subnet_id: 0717-abcd1234-5678-90ab-cdef-1234567890ab
    state: present

- name: Attach VNI to bare metal ROKS cluster with VLAN tag
  ibm_ks_cluster_vni:
    cluster: my-roks-cluster
    vni_id: r006-12345678-1234-1234-1234-123456789abc
    vlan: 4001
    ibmcloud_api_key: "{{ lookup('env', 'IBMCLOUD_API_KEY') }}"
    region: us-south
    state: present

- name: Detach VNI from ROKS cluster
  ibm_ks_cluster_vni:
    cluster: my-roks-cluster
    vni_id: r006-12345678-1234-1234-1234-123456789abc
    state: absent
'''

RETURN = r'''
cluster:
    description: Cluster name or ID
    returned: always
    type: str
vni_id:
    description: VNI ID that was attached/detached
    returned: always
    type: str
changed:
    description: Whether the resource was changed
    returned: always
    type: bool
msg:
    description: Status message
    returned: always
    type: str
vni_info:
    description: Information about the VNI attachment
    returned: when state is present and changed is true
    type: dict
'''

import json
import subprocess
from ansible.module_utils.basic import AnsibleModule


class IBMKSClusterVNIModule:
    """IBM Cloud Kubernetes Service Cluster VNI module implementation."""

    def __init__(self, module):
        """Initialize the module."""
        self.module = module
        self.cluster = module.params.get('cluster')
        self.vni_id = module.params.get('vni_id')
        self.vni_subnet_id = module.params.get('vni_subnet_id')
        self.vlan = module.params.get('vlan')
        self.state = module.params.get('state')
        self.api_key = module.params.get('ibmcloud_api_key')
        self.region = module.params.get('region')

        self.result = {
            'changed': False,
            'cluster': self.cluster,
            'vni_id': self.vni_id,
            'msg': ''
        }

        # Always authenticate with provided API key
        self._authenticate()

        # Set region after authentication if provided
        if self.region:
            self._set_region()

    def _run_command(self, cmd, check_rc=True):
        """Run a shell command and return the result."""
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                check=check_rc
            )
            return result.returncode, result.stdout.strip(), result.stderr.strip()
        except subprocess.CalledProcessError as e:
            if check_rc:
                self.module.fail_json(
                    msg=f"Command failed: {cmd}",
                    stdout=e.stdout,
                    stderr=e.stderr,
                    rc=e.returncode
                )
            return e.returncode, e.stdout, e.stderr

    def _authenticate(self):
        """Authenticate with IBM Cloud using API key."""
        cmd = f"ibmcloud login --apikey '{self.api_key}' --no-region"
        rc, stdout, stderr = self._run_command(cmd)
        if rc != 0:
            self.module.fail_json(
                msg="Failed to authenticate with IBM Cloud",
                stdout=stdout,
                stderr=stderr
            )

    def _set_region(self):
        """Set the IBM Cloud region."""
        cmd = f"ibmcloud target -r {self.region}"
        rc, stdout, stderr = self._run_command(cmd)
        if rc != 0:
            self.module.fail_json(
                msg=f"Failed to set region to {self.region}",
                stdout=stdout,
                stderr=stderr
            )

    def _check_cli_installed(self):
        """Check if ibmcloud CLI and ks plugin are installed."""
        # Check ibmcloud CLI
        rc, _, _ = self._run_command("which ibmcloud", check_rc=False)
        if rc != 0:
            self.module.fail_json(
                msg="ibmcloud CLI is not installed. Please install it from https://cloud.ibm.com/docs/cli"
            )

        # Check ks plugin
        rc, stdout, _ = self._run_command("ibmcloud plugin list", check_rc=False)
        if 'kubernetes-service' not in stdout and 'container-service' not in stdout:
            self.module.fail_json(
                msg="ibmcloud ks plugin is not installed. Run: ibmcloud plugin install kubernetes-service"
            )

    def _validate_cluster_exists(self):
        """Validate that the cluster exists and is accessible."""
        cmd = f"ibmcloud ks cluster get --cluster {self.cluster} --output json"
        rc, stdout, stderr = self._run_command(cmd, check_rc=False)

        if rc != 0:
            self.module.fail_json(
                msg=(
                    f"Cluster '{self.cluster}' not found or not accessible."
                    " Please verify the cluster name with 'ibmcloud ks clusters'"
                ),
                stdout=stdout,
                stderr=stderr,
                rc=rc
            )

        try:
            cluster_info = json.loads(stdout)
            return cluster_info
        except json.JSONDecodeError:
            self.module.fail_json(
                msg=f"Failed to parse cluster information for '{self.cluster}'",
                stdout=stdout
            )
            return None

    def _get_attached_vni_ids(self):
        """Return set of VNI IDs currently attached to the cluster."""
        cmd = f"ibmcloud ks vni ls --cluster-id {self.cluster} --output json"
        rc, stdout, stderr = self._run_command(cmd, check_rc=False)
        if rc != 0:
            self.module.fail_json(
                msg=f"Failed to list VNIs for cluster {self.cluster}: {stderr}",
                stdout=stdout,
                stderr=stderr,
                rc=rc
            )
            return set()
        try:
            data = json.loads(stdout)
            edges = (
                data.get('data', {})
                    .get('node', {})
                    .get('networkAttachments', {})
                    .get('edges', [])
            )
            return {
                edge['node']['virtualNetworkInterface']['externalID']
                for edge in edges
                if edge.get('node', {})
                         .get('virtualNetworkInterface', {})
                         .get('externalID')
            }
        except (KeyError, ValueError, json.JSONDecodeError) as exc:
            self.module.fail_json(
                msg=f"Failed to parse VNI list for cluster {self.cluster}: {exc}",
                stdout=stdout
            )
            return set()

    def _is_vni_attached(self):
        """Check if VNI is already attached to the cluster."""
        return self.vni_id in self._get_attached_vni_ids()

    def attach_vni(self):
        """Attach VNI to the cluster."""
        # Validate cluster exists first
        self._validate_cluster_exists()

        # Check if already attached
        if self._is_vni_attached():
            self.result['msg'] = f"VNI {self.vni_id} is already attached to cluster {self.cluster}"
            return

        # Validate required parameters
        if self.vlan is None and not self.vni_subnet_id:
            self.module.fail_json(
                msg="Either vlan (for baremetal) or vni_subnet_id (for standard) is required when attaching a VNI"
            )

        # Check mode
        if self.module.check_mode:
            self.result['changed'] = True
            self.result['msg'] = f"Would attach VNI {self.vni_id} to cluster {self.cluster}"
            return

        # Build the attach command
        if self.vlan is not None:
            # Bare metal ROKS nodes require the baremetal subcommand and --vlan
            cmd = (
                f"ibmcloud ks vni attach baremetal"
                f" --cluster-id {self.cluster}"
                f" --vni {self.vni_id}"
                f" --vlan {self.vlan}"
                f" -q"
            )
        else:
            cmd = (
                f"ibmcloud ks vni attach"
                f" --cluster-id {self.cluster}"
                f" --vni {self.vni_id}"
                f" --subnet {self.vni_subnet_id}"
                f" -q"
            )

        rc, stdout, stderr = self._run_command(cmd, check_rc=False)

        if rc != 0:
            self.module.fail_json(
                msg=f"Failed to attach VNI {self.vni_id} to cluster {self.cluster}",
                stdout=stdout,
                stderr=stderr,
                rc=rc
            )

        self.result['changed'] = True
        self.result['msg'] = f"VNI {self.vni_id} attached to cluster {self.cluster} successfully"
        self.result['vni_info'] = {
            'vni_id': self.vni_id,
            'subnet_id': self.vni_subnet_id,
            'vlan': self.vlan,
            'cluster': self.cluster
        }

    def detach_vni(self):
        """Detach VNI from the cluster."""
        # Validate cluster exists first
        self._validate_cluster_exists()

        # Check if attached
        if not self._is_vni_attached():
            self.result['msg'] = f"VNI {self.vni_id} is not attached to cluster {self.cluster}"
            return

        # Check mode
        if self.module.check_mode:
            self.result['changed'] = True
            self.result['msg'] = f"Would detach VNI {self.vni_id} from cluster {self.cluster}"
            return

        # Detach VNI — -f bypasses confirmation prompt in non-interactive mode
        cmd = f"ibmcloud ks vni detach --cluster-id {self.cluster} --vni {self.vni_id} -f -q"
        rc, stdout, stderr = self._run_command(cmd, check_rc=False)

        if rc != 0:
            self.module.fail_json(
                msg=f"Failed to detach VNI {self.vni_id} from cluster {self.cluster}",
                stdout=stdout,
                stderr=stderr,
                rc=rc
            )

        self.result['changed'] = True
        self.result['msg'] = f"VNI {self.vni_id} detached from cluster {self.cluster} successfully"

    def run(self):
        """Execute the module logic."""
        # Check prerequisites
        self._check_cli_installed()

        # Execute based on state
        if self.state == 'present':
            self.attach_vni()
        elif self.state == 'absent':
            self.detach_vni()

        self.module.exit_json(**self.result)


def main():
    """Main module execution."""
    argument_spec = {
        'cluster': {'type': 'str', 'required': True},
        'vni_id': {'type': 'str', 'required': True},
        'vni_subnet_id': {'type': 'str', 'required': False},
        'vlan': {'type': 'int', 'required': False},
        'state': {'type': 'str', 'choices': ['present', 'absent'], 'default': 'present'},
        'ibmcloud_api_key': {'type': 'str', 'required': False, 'no_log': True},
        'region': {'type': 'str', 'required': False}
    }

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True
    )

    resource_module = IBMKSClusterVNIModule(module)
    resource_module.run()


if __name__ == '__main__':
    main()

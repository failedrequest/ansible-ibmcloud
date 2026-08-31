# Collection Gap Remediation Plan
## `failedrequest/ansible-ibmcloud` — fixes required to replace `ansible.builtin.uri`

This document describes the exact code changes needed in the collection so the
playbooks (`net-cloud.yml`, `net-cloud-cleanup.yml`) can use collection modules
instead of raw `ansible.builtin.uri` REST calls.

Each gap is self-contained. They can be fixed independently.

---

## Gap 1 — `ibm_is_virtual_network_interface`: add `primary_ip_id` parameter

### File
`plugins/modules/ibm_is_virtual_network_interface.py`

### Problem
The module can set a VNI's primary IP by **address** or **name**, but not by
**reserved IP ID**.  The playbook pre-creates reserved IP objects then binds
VNIs to them by ID (`primary_ip: {id: "<rip_id>"}`).  Binding by address/name
causes the VPC to create a *new* reserved IP instead of linking to the existing
one, resulting in duplicate IPs or an API collision error.

### Current `argument_spec` (bottom of file)
```python
argument_spec.update({
    'name': {'type': 'str', 'required': True},
    'id': {'type': 'str', 'required': False},
    'subnet': {'type': 'str', 'required': False},
    'security_groups': {'type': 'list', 'elements': 'str', 'required': False},
    'enable_infrastructure_nat': {'type': 'bool', 'required': False, 'default': True},
    'primary_ip_address': {'type': 'str', 'required': False},
    'primary_ip_name': {'type': 'str', 'required': False}
})
```

### Required changes

**1. Add `primary_ip_id` to `argument_spec`**
```python
argument_spec.update({
    'name': {'type': 'str', 'required': True},
    'id': {'type': 'str', 'required': False},
    'subnet': {'type': 'str', 'required': False},
    'security_groups': {'type': 'list', 'elements': 'str', 'required': False},
    'enable_infrastructure_nat': {'type': 'bool', 'required': False, 'default': True},
    'primary_ip_id': {'type': 'str', 'required': False},        # ← ADD
    'primary_ip_address': {'type': 'str', 'required': False},
    'primary_ip_name': {'type': 'str', 'required': False}
})
```

**2. Add `primary_ip_id` to `DOCUMENTATION` options block**
```yaml
    primary_ip_id:
        description:
            - ID of an existing reserved IP to use as the primary IP.
            - Mutually exclusive with primary_ip_address and primary_ip_name.
            - Use this when the reserved IP was pre-created and must be bound by ID.
        type: str
        required: false
```

**3. Update `create_resource()` to wire in `primary_ip_id`**

Current block (lines ~137–146):
```python
reserved_ip_address = self.params.get('primary_ip_address')
reserved_ip_name = self.params.get('primary_ip_name')

if reserved_ip_address or reserved_ip_name:
    primary_ip = {}
    if reserved_ip_address:
        primary_ip['address'] = reserved_ip_address
    if reserved_ip_name:
        primary_ip['name'] = reserved_ip_name
    prototype_kwargs['primary_ip'] = primary_ip
```

Replace with:
```python
reserved_ip_id      = self.params.get('primary_ip_id')
reserved_ip_address = self.params.get('primary_ip_address')
reserved_ip_name    = self.params.get('primary_ip_name')

if reserved_ip_id or reserved_ip_address or reserved_ip_name:
    primary_ip = {}
    if reserved_ip_id:
        primary_ip['id'] = reserved_ip_id          # binds existing reserved IP by ID
    if reserved_ip_address:
        primary_ip['address'] = reserved_ip_address
    if reserved_ip_name:
        primary_ip['name'] = reserved_ip_name
    prototype_kwargs['primary_ip'] = primary_ip
```

**4. Add `mutually_exclusive` guard to `AnsibleModule` constructor**
```python
module = AnsibleModule(
    argument_spec=argument_spec,
    supports_check_mode=True,
    mutually_exclusive=[
        ['primary_ip_id', 'primary_ip_address'],
        ['primary_ip_id', 'primary_ip_name'],
    ]
)
```

### Playbook usage after fix
```yaml
- name: Create VNI bound to pre-existing reserved IP
  ibm_is_virtual_network_interface:
    name: "{{ vni_name }}"
    subnet: "{{ subnet_id }}"
    primary_ip_id: "{{ rip_id_map[item.name] }}"   # replaces uri primary_ip.id
    security_groups:
      - "{{ vpc_default_security_group_id }}"
    enable_infrastructure_nat: true
    state: present
```

---

## Gap 2 — `ibm_is_virtual_network_interface`: handle `202 Accepted` on DELETE

### File
`plugins/modules/ibm_is_virtual_network_interface.py`

### Problem
The VPC API returns `202 Accepted` (async) for VNI DELETE — not `204`.  The
current `delete_resource()` calls `delete_virtual_network_interfaces(id=...)`,
which the SDK treats as complete when it returns (it doesn't poll the async
operation).  If cleanup continues immediately to delete the subnet, the DELETE
may not have propagated yet and the subnet delete fails with
`409 vni_in_use_target_exists`.

Additionally, the SDK method name is wrong: the API operation for a single VNI
is `DELETE /virtual_network_interfaces/{id}`, which maps to the SDK as
`delete_virtual_network_interface` (singular), not
`delete_virtual_network_interfaces` (plural — that doesn't exist).

### Current `delete_resource()` (lines ~196–208)
```python
def delete_resource(self, resource_id: str):
    self.check_mode_exit(changed=True, msg=f"Would delete virtual_network_interface: {resource_id}")

    try:
        # Use the correct SDK method name (plural)   ← comment is wrong, plural is the bug
        self.vpc_service.delete_virtual_network_interfaces(
            id=resource_id
        )
        self.result['changed'] = True
        self.result['msg'] = f"virtual_network_interface {resource_id} deleted successfully"
    except ApiException as e:
        self.handle_api_exception(e, f"delete virtual_network_interface {resource_id}")
```

### Required changes

**1. Fix SDK method name (plural → singular)**

**2. Add polling loop that waits until `get_virtual_network_interface` returns 404**

Replace the entire `delete_resource()` method:
```python
def delete_resource(self, resource_id: str):
    """Delete a VNI and poll until the async deletion completes."""
    import time

    self.check_mode_exit(changed=True, msg=f"Would delete virtual_network_interface: {resource_id}")

    try:
        self.vpc_service.delete_virtual_network_interface(id=resource_id)   # singular, correct
    except ApiException as e:
        if e.code == 404:
            self.result['msg'] = f"virtual_network_interface {resource_id} already deleted"
            return
        self.handle_api_exception(e, f"delete virtual_network_interface {resource_id}")

    # Poll until the VNI is gone (API returns 202 async; subnet delete needs it fully gone)
    wait_seconds = self.params.get('delete_wait_seconds', 60)
    poll_interval = 5
    elapsed = 0
    while elapsed < wait_seconds:
        time.sleep(poll_interval)
        elapsed += poll_interval
        try:
            self.vpc_service.get_virtual_network_interface(id=resource_id)
            # Still exists — keep waiting
        except ApiException as e:
            if e.code == 404:
                break   # deletion confirmed
            self.handle_api_exception(e, f"poll virtual_network_interface {resource_id}")
    else:
        self.fail_json(
            msg=f"virtual_network_interface {resource_id} still exists after {wait_seconds}s wait"
        )

    self.result['changed'] = True
    self.result['msg'] = f"virtual_network_interface {resource_id} deleted successfully"
```

**3. Add `delete_wait_seconds` to `argument_spec`**
```python
'delete_wait_seconds': {'type': 'int', 'required': False, 'default': 60}
```

**4. Add to `DOCUMENTATION`**
```yaml
    delete_wait_seconds:
        description:
            - How long (in seconds) to poll after issuing a DELETE before giving up.
            - VNI DELETE is asynchronous (API returns 202); this ensures the resource
              is fully removed before the module returns, so dependent subnet deletes
              do not race.
        type: int
        required: false
        default: 60
```

---

## Gap 3 — `ibm_is_virtual_network_interface_info`: add `resource_group` filter

### File
`plugins/modules/ibm_is_virtual_network_interface_info.py`

### Problem
`list_virtual_network_interfaces()` is called with no filters — it returns
**all VNIs in the region across all resource groups**.  In the current playbooks
this is acceptable because VNI names are unique enough, but in an account with
multiple workloads it will be slow and can return stale results from other
resource groups.  The VPC SDK supports a `resource_group_id` query parameter on
`list_virtual_network_interfaces`.

### Current `list_all_resources()` (lines ~195–203)
```python
def list_all_resources(self):
    try:
        response = self.vpc_service.list_virtual_network_interfaces()
        return response.get_result().get('virtual_network_interfaces', [])
    except ApiException as e:
        self.handle_api_exception(e, "list virtual network interfaces")
```

### Required changes

**1. Pass `resource_group_id` when provided**
```python
def list_all_resources(self):
    try:
        kwargs = {}
        if self.resource_group_id:
            kwargs['resource_group_id'] = self.resource_group_id
        response = self.vpc_service.list_virtual_network_interfaces(**kwargs)
        return response.get_result().get('virtual_network_interfaces', [])
    except ApiException as e:
        self.handle_api_exception(e, "list virtual network interfaces")
```

`self.resource_group_id` is already set by the base class
`IBMCloudSDKModule.__init__` from the `resource_group` parameter, so no
additional `argument_spec` changes are needed.

---

## Gap 4 — `ibm_is_subnet_info` / `ibm_is_vpc_info` / `ibm_is_virtual_network_interface_info`: add pagination

### Files
- `plugins/modules/ibm_is_subnet_info.py`
- `plugins/modules/ibm_is_vpc_info.py`
- `plugins/modules/ibm_is_virtual_network_interface_info.py`

### Problem
All three `list_*` calls use a single `.list_*()` SDK call with no pagination.
The VPC API returns a maximum of 50 items per page by default (up to 100 with
`limit=100`).  With many subnets, VPCs, or VNIs the list is silently truncated.

Additionally, `ibm_is_subnet_info.list_all_resources()` and
`ibm_is_subnet_info.get_resource_by_name()` both call `list_subnets()` with no
`vpc_id` parameter, which fetches every subnet in the region.  The VPC SDK
supports `vpc_id` as a server-side query filter.

### Required changes — same pattern for all three modules

Replace every `list_*()` call with a paginator loop, and pass `vpc_id` where
the SDK supports it:

**Pattern (applicable to all three modules):**
```python
def _paginate(self, list_fn, result_key, **kwargs):
    """Fetch all pages from a VPC list endpoint."""
    results = []
    start = None
    while True:
        if start:
            kwargs['start'] = start
        response = list_fn(**kwargs)
        page = response.get_result()
        results.extend(page.get(result_key, []))
        next_page = page.get('next')
        if next_page:
            # 'next' is a dict with an 'href' containing ?start=<token>
            from urllib.parse import urlparse, parse_qs
            start = parse_qs(urlparse(next_page['href']).query).get('start', [None])[0]
        if not next_page or not start:
            break
    return results
```

**`ibm_is_subnet_info` — specific additional fix:**

`get_resource_by_name()` and `list_all_resources()` should pass `vpc_id` to
`list_subnets()` as a server-side filter when available:

```python
def list_all_resources(self, vpc_id: str = None):
    try:
        kwargs = {}
        if vpc_id:
            kwargs['vpc_id'] = vpc_id          # server-side filter — no client-side loop needed
        return self._paginate(self.vpc_service.list_subnets, 'subnets', **kwargs)
    except ApiException as e:
        self.handle_api_exception(e, "list subnets")
```

Remove the current client-side `if vpc_id: subnets = [s for s in subnets ...]`
filter — the server-side `vpc_id` parameter replaces it.

**`ibm_is_vpc_info`** — `list_vpcs()` does not support a name filter in the SDK
(the REST API does via `?name=`).  Add a `name` query parameter using the
`name` kwarg if the SDK version supports it, otherwise keep the linear scan but
use pagination:

```python
def get_resource_by_name(self, resource_name: str):
    try:
        # VPC SDK >= 0.33 supports name= as a server-side filter on list_vpcs
        vpcs = self._paginate(self.vpc_service.list_vpcs, 'vpcs', name=resource_name)
        return vpcs[0] if vpcs else None
    except ApiException as e:
        self.handle_api_exception(e, f"list VPCs to find {resource_name}")
```

This replaces the linear scan with a server-side filtered call, eliminating the
cross-account collision risk entirely (same guarantee as the `?name=` query the
playbook currently uses directly).

---

## Gap 5 — `ibm_ks_cluster_vni`: add `--vlan` flag to attach command

### File
`plugins/modules/ibm_ks_cluster_vni.py`

### Problem
The `attach_vni()` method builds the CLI command as:
```python
cmd = f"ibmcloud ks vni attach --cluster {self.cluster} --vni {self.vni_id} --subnet {self.vni_subnet_id}"
```

The playbook uses `ibmcloud ks vni attach baremetal` with a `--vlan` flag — the
VLAN ID is mandatory for Localnet/OVN-K attachment on bare metal ROKS nodes.
Without `--vlan`, the VNI is attached without a VLAN tag and the Localnet
network cannot function.

> Note: the current playbooks do NOT use `ibm_ks_cluster_vni` — they call
> `ansible.builtin.command` directly.  This gap must be fixed before the module
> is usable as a replacement.

### Current `attach_vni()` (lines ~268–307)
```python
def attach_vni(self):
    ...
    cmd = f"ibmcloud ks vni attach --cluster {self.cluster} --vni {self.vni_id} --subnet {self.vni_subnet_id}"
```

### Required changes

**1. Add `vlan` parameter to `argument_spec`**
```python
'vlan': {'type': 'int', 'required': False}
```

**2. Add to `DOCUMENTATION`**
```yaml
    vlan:
        description:
            - VLAN ID to tag the attachment on bare metal ROKS nodes.
            - Required for OVN-K Localnet secondary networks.
            - Passed as --vlan to ibmcloud ks vni attach baremetal.
        type: int
        required: false
```

**3. Store `vlan` in `__init__`**
```python
self.vlan = module.params.get('vlan')
```

**4. Update `attach_vni()` to include `baremetal` subcommand and `--vlan` flag**
```python
def attach_vni(self):
    ...
    # Build the attach command
    if self.vlan is not None:
        # Bare metal ROKS nodes require the baremetal subcommand and --vlan
        cmd = (
            f"ibmcloud ks vni attach baremetal"
            f" --cluster {self.cluster}"
            f" --vni {self.vni_id}"
            f" --vlan {self.vlan}"
            f" -q"
        )
    else:
        cmd = (
            f"ibmcloud ks vni attach"
            f" --cluster {self.cluster}"
            f" --vni {self.vni_id}"
            f" --subnet {self.vni_subnet_id}"
            f" -q"
        )
```

**5. Update `detach_vni()` to add `-f` force flag**

The detach command requires `-f` to bypass the confirmation prompt in
non-interactive mode (the current code omits it and will hang):
```python
cmd = f"ibmcloud ks vni detach --cluster {self.cluster} --vni {self.vni_id} -f -q"
```

**6. Fix `_is_vni_attached()` — it uses `cluster get` not `vni ls`**

The current `_get_cluster_vnis()` and `_is_vni_attached()` parse the output of
`ibmcloud ks cluster get`, which does not reliably list VNI attachments in all
cluster versions.  Replace with `ibmcloud ks vni ls`:

```python
def _get_attached_vni_ids(self):
    """Return set of VNI IDs currently attached to the cluster."""
    cmd = f"ibmcloud ks vni ls --cluster-id {self.cluster} --output json"
    rc, stdout, stderr = self.module.run_command(cmd)
    if rc != 0:
        self.fail_json(msg=f"Failed to list VNIs for cluster {self.cluster}: {stderr}")
    try:
        data = json.loads(stdout)
        edges = (
            data.get('data', {})
                .get('node', {})
                .get('networkAttachments', {})
                .get('edges', [])
        )
        return {
            e['node']['virtualNetworkInterface']['externalID']
            for e in edges
            if e.get('node', {}).get('virtualNetworkInterface', {}).get('externalID')
        }
    except (KeyError, ValueError) as e:
        self.fail_json(msg=f"Failed to parse VNI list for cluster {self.cluster}: {e}")

def _is_vni_attached(self):
    return self.vni_id in self._get_attached_vni_ids()
```

### Playbook usage after fix
```yaml
- name: Attach VNI to ROKS cluster
  ibm_ks_cluster_vni:
    cluster: "{{ cluster_name }}"
    vni_id: "{{ item.value.id }}"
    vlan: "{{ item.value.vlan }}"
    state: present
  loop: "{{ vni_map | dict2items }}"
  loop_control:
    label: "{{ item.key }} → {{ cluster_name }} (vlan {{ item.value.vlan }})"
  when: item.value.id not in attached_vni_ids
```

---

## Gap 6 — `ibm_is_subnet_reserved_ip`: add `owner` filter for list operations

### File
`plugins/modules/ibm_is_subnet_reserved_ip.py`

### Problem
`list_resources()` returns all reserved IPs in a subnet, including
VPC-managed ones (`owner: provider`).  The playbook filters these out with
`selectattr('owner', 'equalto', 'user')` before building the `rip_id_map`.
Without this filter, provider-managed IPs (gateway, broadcast, etc.) could end
up in the map and be passed as `primary_ip_id` to VNI creation, which would
fail.

There is currently no `_info` companion module for reserved IPs, so the only
way to list all reserved IPs in a subnet is to use the CRUD module with no
`name`/`id` — which it does not support (it has `required_one_of=[['name', 'id']]`).

### Required changes

**1. Create a companion `ibm_is_subnet_reserved_ip_info.py` module** (new file)

This mirrors the pattern of `ibm_is_subnet_info.py`.  It accepts `subnet_id`
and an optional `owner` filter (`user` or `provider`), returns a `resources`
list, and does not modify state.

Minimum viable module:
```python
DOCUMENTATION = r'''
---
module: ibm_is_subnet_reserved_ip_info
short_description: List reserved IPs within an IBM Cloud VPC subnet
options:
    subnet_id:
        description: ID of the subnet to query.
        type: str
        required: true
    owner:
        description:
            - Filter by owner type.
            - "user"     — only user-created reserved IPs (safe to bind to a VNI)
            - "provider" — only provider-managed IPs (gateway, etc.)
            - Omit to return all reserved IPs.
        type: str
        required: false
        choices: ['user', 'provider']
'''
```

Core implementation:
```python
def list_resources(self):
    try:
        response = self.vpc_service.list_subnet_reserved_ips(subnet_id=self.subnet_id)
        rips = response.get_result().get('reserved_ips', [])
        owner_filter = self.params.get('owner')
        if owner_filter:
            rips = [r for r in rips if r.get('owner') == owner_filter]
        return rips
    except ApiException as e:
        self.handle_api_exception(e, f"list reserved IPs in subnet {self.subnet_id}")
```

**2. Alternatively: relax `required_one_of` in the existing module**

If a new module file is not desired, remove `required_one_of=[['name', 'id']]`
from `ibm_is_subnet_reserved_ip` and add a `list` mode when neither `name` nor
`id` is given, returning `result['resources']`.  The `owner` filter parameter
described above should still be added.

---

## Summary of changes by file

| File | Change type | Gap |
|---|---|---|
| `plugins/modules/ibm_is_virtual_network_interface.py` | Modify | Gap 1 — add `primary_ip_id` parameter |
| `plugins/modules/ibm_is_virtual_network_interface.py` | Modify | Gap 2 — fix DELETE (singular SDK method + async poll) |
| `plugins/modules/ibm_is_virtual_network_interface_info.py` | Modify | Gap 3 — pass `resource_group_id` to list call |
| `plugins/modules/ibm_is_subnet_info.py` | Modify | Gap 4 — pagination + server-side `vpc_id` filter |
| `plugins/modules/ibm_is_vpc_info.py` | Modify | Gap 4 — pagination + server-side `name` filter |
| `plugins/modules/ibm_is_virtual_network_interface_info.py` | Modify | Gap 4 — pagination |
| `plugins/modules/ibm_ks_cluster_vni.py` | Modify | Gap 5 — `baremetal` subcommand, `--vlan` flag, `-f` on detach, fix `_is_vni_attached` |
| `plugins/modules/ibm_is_subnet_reserved_ip_info.py` | **New file** | Gap 6 — list reserved IPs with `owner` filter |

Fixing **Gap 1**, **Gap 2**, and **Gap 5** unblocks the three hard-blocker `uri`
calls.  Gaps 3, 4, and 6 are correctness/robustness improvements that matter at
scale but are not strict blockers for the current playbooks to function.

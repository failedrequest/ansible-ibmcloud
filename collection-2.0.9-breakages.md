# ibm.cloudcollection 2.0.8 → 2.0.9 Breakage Report
# Affects: net-cloud.yml + fa-vars.yml
# Collection path: ~/.ansible/collections/ansible_collections/ibm/cloudcollection

---

## Summary Table

| # | Task (line)                                     | Module                          | Issue                                                                                             | Severity              |
|---|-------------------------------------------------|---------------------------------|---------------------------------------------------------------------------------------------------|-----------------------|
| 1 | net-cloud.yml:45                                | `ibm_is_vpc_info`               | `failed_when: not _vpc_info.found` crashes when module fails before setting `found` — base class never seeds `found` | 🔴 Hard failure       |
| 2 | net-cloud.yml:42–43                             | `ibm_is_vpc_info`               | `mutually_exclusive: [name, id]` now enforced — `omit` trick is only safe on Ansible ≥ 2.14      | 🟡 Latent risk        |
| 3 | net-cloud.yml:83                                | `ibm_is_subnet_info`            | Param renamed `vpc_id` → `vpc` (playbook already uses correct name for 2.0.9)                    | ℹ️  2.0.8 back-compat |
| 4 | net-cloud.yml:154                               | `ibm_is_subnet_reserved_ip`     | Param renamed `subnet` → `subnet_id` (playbook already uses correct name for 2.0.9)              | ℹ️  2.0.8 back-compat |
| 5 | net-cloud.yml:162                               | `ibm_is_subnet_reserved_ip`     | List mode returns `resources` (plural), no `found` key — playbook correct but no safety guard     | 🟡 Latent risk        |
| 6 | net-cloud.yml:26 (`module_defaults`)            | group/ibm.cloudcollection.ibm   | Group name confirmed correct in `meta/runtime.yml` — no change needed                            | ✅ No change needed   |

---

## Break 1 — `ibm_is_vpc_info`: `failed_when` crashes on missing `found` key  🔴 Hard failure

**File to fix:** `plugins/modules/ibm_is_vpc_info.py`
**Also affects playbook:** `net-cloud.yml:45`

### What changed
The base class `IBMCloudSDKModule.__init__` (in `plugins/module_utils/ibm_cloud_sdk.py`)
seeds `self.result` with only:
```python
self.result = {
    'changed': False,
    'resource': {},
    'msg': ''
}
```
`found` is **not** seeded. In 2.0.8 it was either seeded in the base class or always set
before any `fail_json` path. In 2.0.9, if the module crashes during `__init__` (e.g. missing
`IC_API_KEY` raises `ValueError` → `fail_json`) `found` is never added to `self.result`, and
the playbook's `failed_when: not _vpc_info.found` blows up with:

> `object of type 'dict' has no attribute 'found'`

### Fix option A — fix the base class (recommended, fixes all info modules at once)
**File:** `plugins/module_utils/ibm_cloud_sdk.py`
```python
# Change the result seed in IBMCloudSDKModule.__init__:
self.result = {
    'changed': False,
    'resource': {},
    'msg':     '',
    'found':   False,   # ← add this line
}
```

### Fix option B — fix the playbook (quicker workaround)
**File:** `net-cloud.yml:45`
```yaml
# Before
failed_when: not _vpc_info.found

# After
failed_when: not (_vpc_info.found | default(false))
```

---

## Break 2 — `ibm_is_vpc_info`: `mutually_exclusive` now enforced on `name`/`id`  🟡 Latent risk

**File to fix:** `plugins/modules/ibm_is_vpc_info.py`

### What changed
2.0.9 adds:
```python
module = AnsibleModule(
    argument_spec=argument_spec,
    supports_check_mode=True,
    mutually_exclusive=[['name', 'id']]   # ← new in 2.0.9
)
```
The playbook passes both `name:` and `id:` with one set to `omit`. On Ansible ≥ 2.14 the
`omit` sentinel is stripped before the module sees params, so this is safe. On older Ansible
the sentinel string `__omit_place_holder__...` is passed as the value and both keys appear
non-null, triggering the mutual-exclusion error.

### Fix
No code change needed if `requires_ansible: ">=2.14"` (already declared in `meta/runtime.yml`).
If you need to support older Ansible, remove the `mutually_exclusive` constraint and guard
inside `run()` instead:
```python
if self.resource_id and self.resource_name:
    self.fail_json(msg="Parameters 'id' and 'name' are mutually exclusive")
```

---

## Break 3 — `ibm_is_subnet_info`: param renamed `vpc_id` → `vpc`  ℹ️ 2.0.8 back-compat

**File fixed in 2.0.9:** `plugins/modules/ibm_is_subnet_info.py`
**Playbook:** `net-cloud.yml:83–86` — already uses `vpc:` (correct for 2.0.9)

### What changed
```python
# 2.0.8 argument_spec
'vpc_id': {'type': 'str', 'required': False}

# 2.0.9 argument_spec
'vpc':    {'type': 'str', 'required': False}
```
The internal variable is `self.vpc_filter = self.params.get('vpc')`.
The playbook was already updated and is correct. No further action needed.
Note this as a **breaking rename** for any other playbooks that used `vpc_id:`.

---

## Break 4 — `ibm_is_subnet_reserved_ip`: param renamed `subnet` → `subnet_id`  ℹ️ 2.0.8 back-compat

**File fixed in 2.0.9:** `plugins/modules/ibm_is_subnet_reserved_ip.py`
**Playbook:** `net-cloud.yml:142,155` — already uses `subnet_id:` (correct for 2.0.9)

### What changed
```python
# 2.0.8 argument_spec
'subnet': {'type': 'str', 'required': True}

# 2.0.9 argument_spec
'subnet_id': {'type': 'str', 'required': True}
```
Note this as a **breaking rename** for any other playbooks that used `subnet:`.

---

## Break 5 — `ibm_is_subnet_reserved_ip` list mode: no `found` key in result  🟡 Latent risk

**File:** `plugins/modules/ibm_is_subnet_reserved_ip.py`

### What changed
In list mode (name and id both omitted) the module sets:
```python
self.result['resources'] = all_rips   # plural — correct
self.result['msg'] = ...
# 'found' is never set in list mode
```
The playbook accesses `item.resources` which is correct. However there is no `found` guard,
so if a subnet returns zero reserved IPs the `zip`+`dict` in the build-map task will produce
an empty dict silently rather than failing loudly.

### Fix (defensive guard in playbook net-cloud.yml:162–176)
```yaml
- name: Build reserved IP name-to-id map
  ansible.builtin.set_fact:
    rip_id_map: >-
      {{
        rip_id_map | default({}) |
        combine(
          dict(
            item.resources | map(attribute='name') | list
            | zip(item.resources | map(attribute='id') | list)
          )
        )
      }}
  loop: "{{ _all_rips_raw.results }}"
  loop_control:
    label: "{{ item.item }}"
  when: (item.resources | default([]) | length) > 0   # ← add this guard
```

---

## Immediate Action Required

Only **Break 1** is a hard blocker that prevents the playbook from running at all.
Apply **either** Fix A (base class seed) or Fix B (playbook `| default(false)`) to unblock.

Breaks 3 and 4 are already handled in the current playbook.
Breaks 2 and 5 are latent risks worth addressing before production use.

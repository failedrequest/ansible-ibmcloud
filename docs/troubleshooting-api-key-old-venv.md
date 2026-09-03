# Troubleshooting: Running Against test.cloud.ibm.com (Staging / Non-Production)

## Background

IBM Cloud operates a staging environment at `test.cloud.ibm.com`. Its endpoints,
API keys, and IAM tokens are completely separate from the production environment at
`cloud.ibm.com`. Mixing endpoints from different environments produces authentication
errors.

From **version 2.0.17** the collection reads the same environment variables that the
IBM Cloud CLI sets, so no code or playbook changes are needed — only the correct env
vars must be present on the host.

---

## Required Environment Variables

The IBM Cloud CLI sets these automatically when configured for a non-production
target. Set them manually if not using the CLI:

| Variable | Purpose | Example value |
|---|---|---|
| `IBMCLOUD_IAM_API_ENDPOINT` | IAM token endpoint | `https://iam.test.cloud.ibm.com` |
| `IBMCLOUD_IS_NG_API_ENDPOINT` | VPC (IS) API endpoint | `https://us-south-stage01.iaasdev.cloud.ibm.com/v1` |
| `IC_API_KEY` or `IBMCLOUD_API_KEY` | API key for the target environment | *(your test-env key)* |

```bash
export IBMCLOUD_IAM_API_ENDPOINT=https://iam.test.cloud.ibm.com
export IBMCLOUD_IS_NG_API_ENDPOINT=https://us-south-stage01.iaasdev.cloud.ibm.com/v1
export IC_API_KEY="<your-test-environment-api-key>"
ansible-playbook -e@vars.yml playbook.yml
```

> **Note:** `IBMCLOUD_IS_NG_API_ENDPOINT` is a single URL that already includes
> the `/v1` path. It covers the entire region — there is no per-region substitution.
> If you work across multiple regions in one play, set this to the primary region
> endpoint; region-specific tasks in staging typically share one endpoint.

---

## How the Collection Uses These Variables

### IAM authentication — `IBMCloudAuth`

[`IBMCloudAuth.__init__()`](../plugins/module_utils/ibm_cloud_sdk.py) calls
`_get_iam_url_from_env()` which checks (in order):

1. `IBMCLOUD_IAM_API_ENDPOINT` — the IBM Cloud CLI standard
2. `IC_IAM_TOKEN_URL` — alternate name accepted by this collection

The result is passed as `url=` to `IAMAuthenticator`:

```python
iam_url = self._get_iam_url_from_env()
if iam_url:
    self.authenticator = IAMAuthenticator(self.api_key, url=iam_url)
else:
    self.authenticator = IAMAuthenticator(self.api_key)  # → iam.cloud.ibm.com
```

### VPC service URL — `IBMCloudSDKModule`

[`_get_vpc_url()`](../plugins/module_utils/ibm_cloud_sdk.py) checks (in order):

1. `IBMCLOUD_IS_NG_API_ENDPOINT` — IBM Cloud CLI standard for the VPC/IS endpoint
2. `IBMCLOUD_VPC_URL` / `IC_VPC_URL` — explicit override accepted by this collection
3. `https://{region}.iaas.cloud.ibm.com/v1` — production default

The result is stored as `self.vpc_url` on the module base class and every IS module
calls `self.vpc_service.set_service_url(self.vpc_url)` — no hardcoded production
URLs remain in any module.

---

## Error Reference

### HTTP 400 — "Provided API key could not be found"

The API key was sent to the wrong IAM endpoint. The key exists in the test
environment but the request went to production IAM (`iam.cloud.ibm.com`).

**Fix:** set `IBMCLOUD_IAM_API_ENDPOINT=https://iam.test.cloud.ibm.com`

Verify the key directly against the correct endpoint:

```bash
curl -s -X POST 'https://iam.test.cloud.ibm.com/identity/token' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d "grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey=$IC_API_KEY" \
  | python3 -m json.tool
```

A working key returns a JSON body containing `access_token`.

---

### HTTP 401 — "provided token is invalid or expired"

A token was issued (IAM endpoint was correct) but the VPC service rejected it.
The token is scoped to the test environment and was sent to production VPC.

**Fix:** set `IBMCLOUD_IS_NG_API_ENDPOINT` to the correct staging VPC URL.

---

### DNS failure — "Failed to resolve 'us-south.iaas.test.cloud.ibm.com'"

An earlier version of this collection tried to derive the VPC hostname from the
IAM hostname by string manipulation. The staging VPC hostname
(`us-south-stage01.iaasdev.cloud.ibm.com`) bears no resemblance to the IAM
hostname (`iam.test.cloud.ibm.com`), so the derived URL was invalid.

This is fixed in **2.0.17** — the collection reads `IBMCLOUD_IS_NG_API_ENDPOINT`
directly and uses it unchanged.

---

### `TypeError: __init__() got an unexpected keyword argument 'iam_url'`

The `IAMAuthenticator` constructor parameter is `url=`, not `iam_url=`. Fixed in
**2.0.15**.

---

### Wrong virtual environment

If the traceback paths show a different venv than the one you activated (e.g.
`/home/vpcuser/old-venv/...`), Ansible is not using the expected Python interpreter.

**Fix:** activate the correct venv before running, or set `ansible_python_interpreter`
in your inventory or vars file:

```yaml
ansible_python_interpreter: /home/vpcuser/new-venv39/bin/python3
```

Verify which interpreter Ansible will use:

```bash
ansible -m debug -a "msg={{ ansible_python_version }}" localhost
```

---

## Full Known-Good Setup (test.cloud.ibm.com)

```bash
source ~/new-venv39/bin/activate

export IC_API_KEY="<test-environment-api-key>"
export IBMCLOUD_IAM_API_ENDPOINT=https://iam.test.cloud.ibm.com
export IBMCLOUD_IS_NG_API_ENDPOINT=https://us-south-stage01.iaasdev.cloud.ibm.com/v1

ansible-galaxy collection install ibm-cloudcollection-2.0.17.tar.gz --force
ansible-playbook -e@vars.yml playbook.yml
```

---

## Version History of This Fix

| Version | Change |
|---|---|
| 2.0.14 | Initial attempt: read `IBMCLOUD_IAM_API_ENDPOINT` and `IBMCLOUD_VPC_URL`; VPC URL required manual override |
| 2.0.15 | Fixed `iam_url=` → `url=` in `IAMAuthenticator` constructor |
| 2.0.16 | Attempted auto-derivation of VPC URL from IAM hostname — **incorrect**, staging VPC hostnames are unrelated to IAM hostnames |
| 2.0.17 | **Correct fix:** read `IBMCLOUD_IS_NG_API_ENDPOINT` directly (IBM Cloud CLI standard); removed hostname-derivation logic |

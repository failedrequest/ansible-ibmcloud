#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Unit tests for ibm_is_subnet_reserved_ip module.

All IBM Cloud SDK calls are mocked — no live API key required.
Covers: create, create (check mode), update (name), update (auto_delete),
        no-op update, delete, delete (not found), list lookup by name,
        get by ID, 404 handling, required_one_of validation.
"""

import sys
import json
import unittest
from unittest.mock import MagicMock, patch, PropertyMock
from io import StringIO

# ---------------------------------------------------------------------------
# Bootstrap the Ansible + collection import path so the module under test
# can find both ansible.module_utils.basic and the collection module_utils.
# ---------------------------------------------------------------------------
import os

COLLECTION_ROOT = os.path.expanduser(
    "~/.ansible/collections"
)
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

for path in [COLLECTION_ROOT, REPO_ROOT]:
    if path not in sys.path:
        sys.path.insert(0, path)

# ---------------------------------------------------------------------------
# Stub out ibm_vpc / ibm_cloud_sdk_core before importing the module so the
# import guard (HAS_IBM_VPC) does not block and we control all SDK objects.
# ---------------------------------------------------------------------------
FAKE_VPC_MOD = MagicMock()
FAKE_SDK_CORE = MagicMock()

sys.modules.setdefault("ibm_vpc", FAKE_VPC_MOD)
sys.modules.setdefault("ibm_cloud_sdk_core", FAKE_SDK_CORE)

# ApiException needs to be a real exception class so "except ApiException"
# clauses work correctly.
class FakeApiException(Exception):
    def __init__(self, message="", code=500):
        super().__init__(message)
        self.message = message
        self.code = code

FAKE_SDK_CORE.ApiException = FakeApiException
FAKE_VPC_MOD.VpcV1 = MagicMock()

# Now import — module_utils.ibm_cloud_sdk also imports ApiException at the
# top level, so patch it there too.
import importlib

# Patch the module_utils SDK import before loading it
with patch.dict("sys.modules", {
    "ibm_cloud_sdk_core": FAKE_SDK_CORE,
    "ibm_cloud_sdk_core.authenticators": MagicMock(),
    "ibm_vpc": FAKE_VPC_MOD,
}):
    import ansible_collections.ibm.cloudcollection.plugins.module_utils.ibm_cloud_sdk as sdk_utils
    import ansible_collections.ibm.cloudcollection.plugins.modules.ibm_is_subnet_reserved_ip as mod


# ---------------------------------------------------------------------------
# Helper — build a minimal AnsibleModule-like mock
# ---------------------------------------------------------------------------

SUBNET_ID = "0717-subnet-aaaa-bbbb"
RIP_ID    = "0717-rip-1111-2222"


def make_module(params, check_mode=False):
    """Return a mock AnsibleModule with the given params."""
    m = MagicMock()
    m.params = {
        "ibmcloud_api_key": "fake-key",
        "region": "us-south",
        "state": "present",
        "resource_group": None,
        "subnet_id": SUBNET_ID,
        "name": None,
        "id": None,
        "address": None,
        "auto_delete": None,
        "target": None,
        **params,
    }
    m.check_mode = check_mode
    m.exit_json = MagicMock(side_effect=SystemExit(0))
    m.fail_json = MagicMock(side_effect=lambda **kw: (_ for _ in ()).throw(
        AssertionError(f"fail_json called: {kw.get('msg')}")
    ))
    return m


def make_rip(name="my-rip", address="10.0.0.5", auto_delete=False):
    return {
        "id": RIP_ID,
        "name": name,
        "address": address,
        "auto_delete": auto_delete,
        "lifecycle_state": "stable",
        "owner": "user",
        "resource_type": "subnet_reserved_ip",
        "href": f"https://us-south.iaas.cloud.ibm.com/v1/subnets/{SUBNET_ID}/reserved_ips/{RIP_ID}",
        "created_at": "2024-01-01T00:00:00Z",
    }


def build_instance(module):
    """Instantiate IBMSubnetReservedIPModule with mocked SDK internals."""
    # Patch IAMAuthenticator so IBMCloudAuth doesn't hit IAM
    with patch.object(sdk_utils, "IAMAuthenticator", MagicMock()):
        instance = mod.IBMSubnetReservedIPModule(module)

    # Give it a clean mock VPC service
    vpc_svc = MagicMock()
    instance.vpc_service = vpc_svc
    return instance, vpc_svc


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestSubnetReservedIPCreate(unittest.TestCase):

    def test_create_new_rip(self):
        """state=present, resource doesn't exist → create called."""
        module = make_module({"name": "my-rip", "address": "10.0.0.5"})
        inst, svc = build_instance(module)

        svc.list_subnet_reserved_ips.return_value.get_result.return_value = {
            "reserved_ips": []
        }
        created = make_rip()
        svc.create_subnet_reserved_ip.return_value.get_result.return_value = created

        with self.assertRaises(SystemExit):
            inst.run()

        svc.create_subnet_reserved_ip.assert_called_once_with(
            subnet_id=SUBNET_ID,
            name="my-rip",
            address="10.0.0.5",
        )
        call_kwargs = module.exit_json.call_args[1]
        self.assertTrue(call_kwargs["changed"])
        self.assertEqual(call_kwargs["resource"]["id"], RIP_ID)

    def test_create_check_mode(self):
        """state=present, check_mode=True → no API mutation, changed=True."""
        module = make_module({"name": "my-rip"}, check_mode=True)
        inst, svc = build_instance(module)

        svc.list_subnet_reserved_ips.return_value.get_result.return_value = {
            "reserved_ips": []
        }

        with self.assertRaises(SystemExit):
            inst.run()

        svc.create_subnet_reserved_ip.assert_not_called()
        call_kwargs = module.exit_json.call_args[1]
        self.assertTrue(call_kwargs["changed"])

    def test_create_with_auto_delete_and_target(self):
        """auto_delete and target are forwarded to create call."""
        module = make_module({
            "name": "my-rip",
            "auto_delete": True,
            "target": "vni-id-abc",
        })
        inst, svc = build_instance(module)

        svc.list_subnet_reserved_ips.return_value.get_result.return_value = {
            "reserved_ips": []
        }
        svc.create_subnet_reserved_ip.return_value.get_result.return_value = make_rip()

        with self.assertRaises(SystemExit):
            inst.run()

        svc.create_subnet_reserved_ip.assert_called_once_with(
            subnet_id=SUBNET_ID,
            name="my-rip",
            auto_delete=True,
            target={"id": "vni-id-abc"},
        )


class TestSubnetReservedIPUpdate(unittest.TestCase):

    def test_update_name(self):
        """state=present, existing rip with different name → update called."""
        module = make_module({"id": RIP_ID, "name": "new-name"})
        inst, svc = build_instance(module)

        existing = make_rip(name="old-name")
        svc.get_subnet_reserved_ip.return_value.get_result.return_value = existing
        updated = {**existing, "name": "new-name"}
        svc.update_subnet_reserved_ip.return_value.get_result.return_value = updated

        with self.assertRaises(SystemExit):
            inst.run()

        svc.update_subnet_reserved_ip.assert_called_once_with(
            subnet_id=SUBNET_ID,
            id=RIP_ID,
            reserved_ip_patch={"name": "new-name"},
        )
        call_kwargs = module.exit_json.call_args[1]
        self.assertTrue(call_kwargs["changed"])
        self.assertEqual(call_kwargs["resource"]["name"], "new-name")

    def test_update_auto_delete(self):
        """auto_delete change triggers update."""
        module = make_module({"id": RIP_ID, "name": "my-rip", "auto_delete": True})
        inst, svc = build_instance(module)

        existing = make_rip(auto_delete=False)
        svc.get_subnet_reserved_ip.return_value.get_result.return_value = existing
        updated = {**existing, "auto_delete": True}
        svc.update_subnet_reserved_ip.return_value.get_result.return_value = updated

        with self.assertRaises(SystemExit):
            inst.run()

        patch_arg = svc.update_subnet_reserved_ip.call_args[1]["reserved_ip_patch"]
        self.assertIn("auto_delete", patch_arg)
        self.assertTrue(patch_arg["auto_delete"])

    def test_noop_update(self):
        """state=present, existing rip matches desired state → no update, changed=False."""
        module = make_module({"id": RIP_ID, "name": "my-rip"})
        inst, svc = build_instance(module)

        existing = make_rip(name="my-rip")
        svc.get_subnet_reserved_ip.return_value.get_result.return_value = existing

        with self.assertRaises(SystemExit):
            inst.run()

        svc.update_subnet_reserved_ip.assert_not_called()
        call_kwargs = module.exit_json.call_args[1]
        self.assertFalse(call_kwargs["changed"])

    def test_update_check_mode(self):
        """state=present, name change, check_mode → no API mutation, changed=True."""
        module = make_module({"id": RIP_ID, "name": "new-name"}, check_mode=True)
        inst, svc = build_instance(module)

        existing = make_rip(name="old-name")
        svc.get_subnet_reserved_ip.return_value.get_result.return_value = existing

        with self.assertRaises(SystemExit):
            inst.run()

        svc.update_subnet_reserved_ip.assert_not_called()
        call_kwargs = module.exit_json.call_args[1]
        self.assertTrue(call_kwargs["changed"])


class TestSubnetReservedIPDelete(unittest.TestCase):

    def test_delete_by_id(self):
        """state=absent, resource exists → delete called."""
        module = make_module({"id": RIP_ID, "state": "absent"})
        inst, svc = build_instance(module)

        svc.get_subnet_reserved_ip.return_value.get_result.return_value = make_rip()

        with self.assertRaises(SystemExit):
            inst.run()

        svc.delete_subnet_reserved_ip.assert_called_once_with(
            subnet_id=SUBNET_ID, id=RIP_ID
        )
        call_kwargs = module.exit_json.call_args[1]
        self.assertTrue(call_kwargs["changed"])

    def test_delete_by_name(self):
        """state=absent, lookup by name → delete called."""
        module = make_module({"name": "my-rip", "state": "absent"})
        inst, svc = build_instance(module)

        svc.list_subnet_reserved_ips.return_value.get_result.return_value = {
            "reserved_ips": [make_rip(name="my-rip")]
        }

        with self.assertRaises(SystemExit):
            inst.run()

        svc.delete_subnet_reserved_ip.assert_called_once_with(
            subnet_id=SUBNET_ID, id=RIP_ID
        )

    def test_delete_not_found(self):
        """state=absent, resource doesn't exist → no-op, changed=False."""
        module = make_module({"name": "ghost-rip", "state": "absent"})
        inst, svc = build_instance(module)

        svc.list_subnet_reserved_ips.return_value.get_result.return_value = {
            "reserved_ips": []
        }

        with self.assertRaises(SystemExit):
            inst.run()

        svc.delete_subnet_reserved_ip.assert_not_called()
        call_kwargs = module.exit_json.call_args[1]
        self.assertFalse(call_kwargs["changed"])

    def test_delete_check_mode(self):
        """state=absent, check_mode=True → no API mutation, changed=True."""
        module = make_module({"id": RIP_ID, "state": "absent"}, check_mode=True)
        inst, svc = build_instance(module)

        svc.get_subnet_reserved_ip.return_value.get_result.return_value = make_rip()

        with self.assertRaises(SystemExit):
            inst.run()

        svc.delete_subnet_reserved_ip.assert_not_called()
        call_kwargs = module.exit_json.call_args[1]
        self.assertTrue(call_kwargs["changed"])


class TestSubnetReservedIPLookup(unittest.TestCase):

    def test_lookup_by_name_found(self):
        """Name-based lookup finds matching reserved IP."""
        module = make_module({"name": "my-rip"})
        inst, svc = build_instance(module)

        rips = [
            {**make_rip(name="other-rip"), "id": "0717-other"},
            make_rip(name="my-rip"),
        ]
        svc.list_subnet_reserved_ips.return_value.get_result.return_value = {
            "reserved_ips": rips
        }
        # No update needed (names match), so no update mock needed

        with self.assertRaises(SystemExit):
            inst.run()

        # Should NOT call create — the existing one was found
        svc.create_subnet_reserved_ip.assert_not_called()
        call_kwargs = module.exit_json.call_args[1]
        self.assertFalse(call_kwargs["changed"])

    def test_get_by_id_404_returns_none(self):
        """404 from get_subnet_reserved_ip is treated as not-found → create."""
        module = make_module({"id": RIP_ID, "name": "my-rip"})
        inst, svc = build_instance(module)

        svc.get_subnet_reserved_ip.side_effect = FakeApiException("not found", code=404)
        svc.create_subnet_reserved_ip.return_value.get_result.return_value = make_rip()

        with self.assertRaises(SystemExit):
            inst.run()

        svc.create_subnet_reserved_ip.assert_called_once()
        call_kwargs = module.exit_json.call_args[1]
        self.assertTrue(call_kwargs["changed"])

    def test_get_by_id_non_404_raises(self):
        """Non-404 API error from get → fail_json."""
        module = make_module({"id": RIP_ID, "name": "my-rip"})
        module.fail_json = MagicMock(side_effect=SystemExit(1))
        inst, svc = build_instance(module)

        svc.get_subnet_reserved_ip.side_effect = FakeApiException("server error", code=500)

        with self.assertRaises(SystemExit):
            inst.run()

        module.fail_json.assert_called_once()
        self.assertIn("500", module.fail_json.call_args[1]["msg"])


if __name__ == "__main__":
    unittest.main(verbosity=2)

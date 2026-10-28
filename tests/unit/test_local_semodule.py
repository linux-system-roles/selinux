# -*- coding: utf-8 -*-

# Copyright: (c) 2026, Red Hat, Inc.
# SPDX-License-Identifier: MIT
"""Unit tests for check mode handling in the local_semodule module."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import unittest

import local_semodule


class _FakeSemanage(object):
    """Minimal stand-in for the libsemanage python bindings.

    It records the calls that would change the module store, so that the
    tests can check that nothing is changed or committed in check mode.
    """

    def __init__(self, enabled=1, installed=True, checksum="sha256:old"):
        self.enabled = enabled
        self.installed = installed
        self.checksum = checksum
        self.changes = []

    def semanage_module_key_create(self, sh):
        return 0, "key"

    def semanage_module_key_set_name(self, sh, modkey, name):
        return 0

    def semanage_module_key_set_priority(self, sh, modkey, priority):
        return 0

    def semanage_module_compute_checksum(self, sh, modkey, cil):
        return 0, self.checksum, len(self.checksum)

    def semanage_set_default_priority(self, sh, priority):
        return 0

    def semanage_set_ignore_module_cache(self, sh, value):
        return 0

    def semanage_module_get_enabled(self, sh, modkey):
        return 0, self.enabled

    def semanage_module_list_all(self, sh):
        return 0, "modinfo", 1 if self.installed else 0

    def semanage_module_list_nth(self, modinfo, n):
        return "module"

    def semanage_module_info_get_name(self, sh, m):
        return 0, "foo-selinux"

    def semanage_module_info_get_priority(self, sh, m):
        return 0, 400

    def semanage_module_install_file(self, sh, path):
        self.changes.append("install")
        return 0

    def semanage_module_set_enabled(self, sh, modkey, enabled):
        self.changes.append("set_enabled")
        return 0

    def semanage_module_remove(self, sh, name):
        self.changes.append("remove")
        return 0

    def semanage_commit(self, sh):
        self.changes.append("commit")
        return 0


class _FakeModule(object):
    def __init__(self, check_mode=False, checksum="new"):
        self.check_mode = check_mode
        self._checksum = checksum

    def sha256(self, path):
        return self._checksum

    def fail_json(self, **kwargs):
        raise AssertionError(kwargs)


class TestLocalSemoduleCheckMode(unittest.TestCase):
    def _run(self, func, fake, check_mode, *args):
        local_semodule.semanage = fake
        module = _FakeModule(check_mode=check_mode)
        return func(module, *args)

    def test_install_check_mode_reports_change_without_commit(self):
        fake = _FakeSemanage(checksum="sha256:old")
        result = self._run(
            local_semodule.semodule_install,
            fake,
            True,
            "/tmp/foo-selinux.cil",
            400,
            False,
            "sh",
        )
        self.assertTrue(result["changed"])
        self.assertEqual(fake.changes, [])

    def test_install_check_mode_no_change_when_checksum_matches(self):
        fake = _FakeSemanage(checksum="sha256:new")
        result = self._run(
            local_semodule.semodule_install,
            fake,
            True,
            "/tmp/foo-selinux.cil",
            400,
            False,
            "sh",
        )
        self.assertFalse(result["changed"])
        self.assertEqual(fake.changes, [])

    def test_install_normal_mode_commits(self):
        fake = _FakeSemanage(checksum="sha256:old")
        result = self._run(
            local_semodule.semodule_install,
            fake,
            False,
            "/tmp/foo-selinux.cil",
            400,
            False,
            "sh",
        )
        self.assertTrue(result["changed"])
        self.assertEqual(fake.changes, ["install", "commit"])

    def test_disable_check_mode_reports_change_without_commit(self):
        fake = _FakeSemanage(enabled=1)
        result = self._run(
            local_semodule.semodule_enable, fake, True, "foo-selinux", 0, "sh"
        )
        self.assertTrue(result["changed"])
        self.assertEqual(fake.changes, [])

    def test_enable_check_mode_no_change_when_already_enabled(self):
        fake = _FakeSemanage(enabled=1)
        result = self._run(
            local_semodule.semodule_enable, fake, True, "foo-selinux", 1, "sh"
        )
        self.assertFalse(result["changed"])
        self.assertEqual(fake.changes, [])

    def test_disable_normal_mode_commits(self):
        fake = _FakeSemanage(enabled=1)
        result = self._run(
            local_semodule.semodule_enable, fake, False, "foo-selinux", 0, "sh"
        )
        self.assertTrue(result["changed"])
        self.assertEqual(fake.changes, ["set_enabled", "commit"])

    def test_remove_check_mode_reports_change_without_commit(self):
        fake = _FakeSemanage(installed=True)
        result = self._run(
            local_semodule.semodule_remove, fake, True, "foo-selinux", 0, "sh"
        )
        self.assertTrue(result["changed"])
        self.assertEqual(fake.changes, [])

    def test_remove_check_mode_no_change_when_absent(self):
        fake = _FakeSemanage(installed=False)
        result = self._run(
            local_semodule.semodule_remove, fake, True, "foo-selinux", 0, "sh"
        )
        self.assertFalse(result["changed"])
        self.assertEqual(fake.changes, [])

    def test_remove_normal_mode_commits(self):
        fake = _FakeSemanage(installed=True)
        result = self._run(
            local_semodule.semodule_remove, fake, False, "foo-selinux", 0, "sh"
        )
        self.assertTrue(result["changed"])
        self.assertEqual(fake.changes, ["remove", "commit"])


if __name__ == "__main__":
    unittest.main()

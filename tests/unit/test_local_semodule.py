# -*- coding: utf-8 -*-

# SPDX-License-Identifier: MIT
"""Unit tests for local_semodule module helpers."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import unittest

import local_semodule


class _FailJsonException(Exception):
    """Capture arguments passed to a fake module's fail_json method."""

    def __init__(self, kwargs):
        """Store the fail_json keyword arguments for assertions."""
        self.kwargs = kwargs


class _FakeModule(object):
    """Provide the AnsibleModule methods used by semodule_install."""

    def sha256(self, _path):
        """Return a stable checksum for the test module."""
        return "module-checksum"

    def fail_json(self, **kwargs):
        """Raise an inspectable exception in place of exiting Ansible."""
        raise _FailJsonException(kwargs)


class _FakeSemanage(object):
    """Record libsemanage calls, including module-cache control."""

    def __init__(self):
        """Initialize the ordered call log."""
        self.calls = []

    def semanage_module_key_create(self, _sh):
        """Select the legacy installation path used by this focused test."""
        raise AttributeError

    def semanage_set_ignore_module_cache(self, _sh, value):
        """Record requests to bypass the module cache."""
        self.calls.append(("set_ignore_module_cache", value))

    def semanage_module_install_file(self, _sh, path):
        """Record module installation requests."""
        self.calls.append(("install_file", path))

    def semanage_commit(self, _sh):
        """Record SELinux store commits."""
        self.calls.append(("commit", None))


class _FakeSemanageWithoutIgnoreModuleCache(object):
    """Represent a libsemanage binding without cache-control support."""

    def __init__(self):
        """Initialize the ordered call log."""
        self.calls = []

    def semanage_module_key_create(self, _sh):
        """Select the legacy installation path used by this focused test."""
        raise AttributeError

    def semanage_module_install_file(self, _sh, path):
        """Record unexpected module installation requests."""
        self.calls.append(("install_file", path))

    def semanage_commit(self, _sh):
        """Record unexpected SELinux store commits."""
        self.calls.append(("commit", None))


class TestSemoduleInstall(unittest.TestCase):
    """Verify module-cache behavior during SELinux module installation."""

    def setUp(self):
        """Preserve the imported module's libsemanage binding."""
        self._had_semanage = hasattr(local_semodule, "semanage")
        self._semanage = getattr(local_semodule, "semanage", None)

    def tearDown(self):
        """Restore the imported module's libsemanage binding."""
        if self._had_semanage:
            local_semodule.semanage = self._semanage
        else:
            del local_semodule.semanage

    def test_ignore_module_cache_calls_libsemanage_api(self):
        """Request cache bypass before installing and committing a module."""
        fake_semanage = _FakeSemanage()
        local_semodule.semanage = fake_semanage

        result = local_semodule.semodule_install(
            _FakeModule(), "test.pp", 400, True, object()
        )

        self.assertTrue(result["changed"])
        self.assertEqual(
            fake_semanage.calls,
            [
                ("set_ignore_module_cache", 1),
                ("install_file", "test.pp"),
                ("commit", None),
            ],
        )

    def test_ignore_module_cache_fails_when_api_is_unavailable(self):
        """Fail cleanly when libsemanage lacks module-cache control."""
        fake_semanage = _FakeSemanageWithoutIgnoreModuleCache()
        local_semodule.semanage = fake_semanage

        with self.assertRaises(_FailJsonException) as context:
            local_semodule.semodule_install(
                _FakeModule(), "test.pp", 400, True, object()
            )

        self.assertEqual(
            context.exception.kwargs["msg"],
            "Installed python3-libsemanage does not support ignore_module_cache",
        )
        self.assertEqual(fake_semanage.calls, [])

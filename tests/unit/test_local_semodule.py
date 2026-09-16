# -*- coding: utf-8 -*-

# SPDX-License-Identifier: MIT
"""Unit tests for local_semodule module helpers."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import unittest

import local_semodule


class _FailJsonException(Exception):
    def __init__(self, kwargs):
        self.kwargs = kwargs


class _FakeModule(object):
    def sha256(self, _path):
        return "module-checksum"

    def fail_json(self, **kwargs):
        raise _FailJsonException(kwargs)


class _FakeSemanage(object):
    def __init__(self):
        self.calls = []

    def semanage_module_key_create(self, _sh):
        raise AttributeError

    def semanage_set_ignore_module_cache(self, _sh, value):
        self.calls.append(("set_ignore_module_cache", value))

    def semanage_module_install_file(self, _sh, path):
        self.calls.append(("install_file", path))

    def semanage_commit(self, _sh):
        self.calls.append(("commit", None))


class _FakeSemanageWithoutIgnoreModuleCache(object):
    def __init__(self):
        self.calls = []

    def semanage_module_key_create(self, _sh):
        raise AttributeError

    def semanage_module_install_file(self, _sh, path):
        self.calls.append(("install_file", path))

    def semanage_commit(self, _sh):
        self.calls.append(("commit", None))


class TestSemoduleInstall(unittest.TestCase):
    def setUp(self):
        self._had_semanage = hasattr(local_semodule, "semanage")
        self._semanage = getattr(local_semodule, "semanage", None)

    def tearDown(self):
        if self._had_semanage:
            local_semodule.semanage = self._semanage
        else:
            del local_semodule.semanage

    def test_ignore_module_cache_calls_libsemanage_api(self):
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

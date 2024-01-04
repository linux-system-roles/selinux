#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2023, Petr Lautrbach <lautrbach@redhat.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: local_semodule
short_description: Manages SELinux modules
description:
    - Manages SELinux modules
options:
  name:
    description:
      - A module name, used with "enabled" to enabled disabled module
    type: str
  path:
    description:
      - A local module filename, used with "enabled" to install a module
    type: str
  priority:
    description:
      - SELinux module priority, 0 means SELinux store default (400) with "path" and "enabled", otherwise all priorities
    type: int
    default: 0
  state:
    description:
      - Desired module state
      - enabled - install a module file with `path`, enable a module with `name`
      - disabled - disable module
      - absent - remove module
    type: str
    choices: [ enabled, disabled, absent ]
    default: enabled
  store:
    description:
      - Use other than current SELinux module store, e.g. mls, minimum, refpolicy ...
    type: str
    default: ""
notes:
   - The changes are persistent across reboots.
   - Not tested on any debian based system.
requirements:
- python3-libselinux
- python3-libsemanage
author:
- Petr Lautrbach (@bachradsusi)
"""

EXAMPLES = r"""
- name: Install mymodule.pp with default priority (400)
  local_semodule:
    path: mymodule.pp
    state: enabled

- name: Install mymodule.pp with default priority (300)
  local_semodule:
    path: mymodule.pp
    priority: 300
    state: enabled

- name: Disable mymodule
  local_semodule:
    name: mymodule
    state: disabled

- name: Enable mymodule
  local_semodule:
    name: mymodule
    state: enabled

- name: Remove mymodule with priority 300
  local_semodule:
    name: mymodule
    priority: 300
    state: absent

- name: Remove mymodule - all priorities
  local_semodule:
    name: mymodule
    state: absent
"""

import traceback

SELINUX_IMP_ERR = None
try:
    import selinux

    HAVE_SELINUX = True
except ImportError:
    SELINUX_IMP_ERR = traceback.format_exc()
    HAVE_SELINUX = False

SEMANAGE_IMP_ERR = None
try:
    import semanage

    HAVE_SEMANAGE = True
except ImportError:
    SEMANAGE_IMP_ERR = traceback.format_exc()
    HAVE_SEMANAGE = False

from ansible.module_utils.basic import AnsibleModule, missing_required_lib

import os.path


def get_runtime_status(ignore_selinux_state=False):
    return ignore_selinux_state or selinux.is_selinux_enabled()


def init_libsemanage(store=""):
    sh = semanage.semanage_handle_create()
    if not sh:
        raise ValueError("Could not create semanage handle")

    if store != "":
        semanage.semanage_select_store(sh, store, semanage.SEMANAGE_CON_DIRECT)
    semanage.semanage_connect(sh)
    semanage.semanage_set_reload(sh, 0)
    return sh


def semodule_install(module, path, priority, sh):
    """Install a local policy module

    :type module: AnsibleModule
    :param module: Ansible module

    :type path: str
    :param name: a local module file (either .cil or .pp) to be installed on a node

    :type priority: int
    :param priority: SELinux module priority, 0 - use SELinux module store default (400)
    """

    path_checksum = "sha256:" + module.sha256(path)

    filename = os.path.split(path)[1]
    (name, ext) = os.path.splitext(filename)

    if ext == ".cil":
        cil = 1
    elif ext == ".pp":
        cil = 0
    else:
        raise Exception("Only .cil and .pp files are supported")

    result = {
        "changed": False,
        "name": name,
        "priority": priority,
        "state": "enabled",
    }

    try:
        r, modkey = semanage.semanage_module_key_create(sh)
    except AttributeError:
        # fallback to old libsemanage api
        modkey = None

    if modkey is not None and r != 0:
        raise Exception(r)

    if modkey:
        r = semanage.semanage_module_key_set_name(sh, modkey, name)
        if r != 0:
            raise Exception(r)

        if priority == 0:
            r, modinfo, num_modules = semanage.semanage_module_list(sh)
            for n in range(num_modules):
                m = semanage.semanage_module_list_nth(modinfo, n)

                r, m_name = semanage.semanage_module_info_get_name(sh, m)
                if name == m_name:
                    r, m_prio = semanage.semanage_module_info_get_priority(sh, m)
                    priority = m_prio
                    break
        if priority != 0:
            r = semanage.semanage_module_key_set_priority(sh, modkey, priority)
            if r != 0:
                raise Exception(r)

        try:
            r, module_checksum, _len = semanage.semanage_module_compute_checksum(
                sh, modkey, cil
            )

        except Exception:
            r = 0
            module_checksum = ""

        if r != 0:
            raise Exception(r)

        if path_checksum == module_checksum:
            return result

        if priority != 0:
            semanage.semanage_set_default_priority(sh, priority)

    semanage.semanage_module_install_file(sh, path)
    semanage.semanage_commit(sh)

    result["changed"] = True

    return result


def semodule_enable(module, name, enabled, sh):
    """Enable or install a local policy module

    :type module: AnsibleModule
    :param module: Ansible module

    :type name: str
    :param name: module name, used for enabling disabled modules, disabling enabled modules, removing modules

    :type enabled: int
    :param enabled: 0 - disable, 1 - enable
    """
    result = {
        "changed": False,
        "name": name,
        "state": "enabled" if enabled else "disabled",
    }

    try:
        r, modkey = semanage.semanage_module_key_create(sh)
    except AttributeError:
        # fallback to old libsemanage api
        modkey = None

    if modkey is not None:
        if r != 0:
            raise Exception(r)

        r = semanage.semanage_module_key_set_name(sh, modkey, name)
        if r != 0:
            raise Exception(r)

        try:
            r, m_enabled = semanage.semanage_module_get_enabled(sh, modkey)
        except Exception:
            raise ValueError("Could not find module {name}".format(name=name))

        if enabled == m_enabled:
            return result

        r = semanage.semanage_module_set_enabled(sh, modkey, enabled)
        if r < 0:
            raise ValueError("Could not enable/disable module {name}".format(name=name))
    else:
        if enabled:
            r = semanage.semanage_module_enable(sh, name)
        else:
            r = semanage.semanage_module_disable(sh, name)
        if r < 0:
            raise ValueError("Could not enable/disable module {name}".format(name=name))

    semanage.semanage_commit(sh)

    result["changed"] = True
    return result


def semodule_remove(module, name, priority, sh):
    """Enable or install a local policy module

    :type module: AnsibleModule
    :param module: Ansible module

    :type name: str
    :param name: module name, used for enabling disabled modules, disabling enabled modules, removing modules

    :type priority: int
    :param priority: SELinux module priority, 0 - remove all priorities
    """
    result = {
        "changed": False,
        "name": name,
        "priority": priority,
        "state": "absent",
    }

    try:
        r, modinfo, num_modules = semanage.semanage_module_list_all(sh)
    except AttributeError:
        modinfo = None

    if modinfo is not None:
        for n in range(num_modules):
            m = semanage.semanage_module_list_nth(modinfo, n)

            r, m_name = semanage.semanage_module_info_get_name(sh, m)
            if name == m_name:
                r, m_prio = semanage.semanage_module_info_get_priority(sh, m)
                if priority == 0 or priority == m_prio:
                    semanage.semanage_set_default_priority(sh, m_prio)
                    r = semanage.semanage_module_remove(sh, name)
                    if r < 0:
                        if r != -2:
                            raise ValueError(
                                "Could not remove module {name} (remove failed)".format(
                                    name=name
                                )
                            )
                    else:
                        result["changed"] = True
    else:
        r = semanage.semanage_module_remove(sh, name)
        if r < 0:
            if r != -2:
                raise ValueError(
                    "Could not remove module {name} (remove failed)".format(name=name)
                )
        else:
            result["changed"] = True

    if result["changed"]:
        semanage.semanage_commit(sh)

    return result


def main():
    module = AnsibleModule(
        argument_spec=dict(
            path=dict(type="str"),
            name=dict(type="str"),
            priority=dict(type="int", default=0),
            state=dict(
                type="str", default="enabled", choices=["absent", "disabled", "enabled"]
            ),
            store=dict(type="str", default=""),
        ),
        supports_check_mode=True,
    )

    if not HAVE_SELINUX:
        module.fail_json(
            msg=missing_required_lib("python3-libselinux"), exception=SELINUX_IMP_ERR
        )

    if not HAVE_SEMANAGE:
        module.fail_json(
            msg=missing_required_lib("python3-libsemanage"),
            exception=SEMANAGE_IMP_ERR,
        )

    if not get_runtime_status():
        module.fail_json(msg="SELinux is disabled on this host.")

    path = module.params["path"]
    name = module.params["name"]
    priority = module.params["priority"]
    state = module.params["state"]
    store = module.params["store"]

    result = {
        "path": path,
        "name": name,
        "priority": priority,
        "state": state,
    }

    try:
        sh = init_libsemanage(store)
    except Exception:
        module.fail_json(
            msg="Could not connect to SELinux module store",
            exception=traceback.format_exc(),
        )

    if state == "enabled":
        if path is not None:
            result = semodule_install(module, path, priority, sh)
        elif name is not None:
            result = semodule_enable(module, name, 1, sh)
        else:
            module.fail_json(msg="`name` or `path` must be specified")
    elif state == "disabled":
        result = semodule_enable(module, name, 0, sh)
    elif state == "absent":
        if name is None:
            module.fail_json(msg="`name` is required")
        result = semodule_remove(module, name, priority, sh)
    else:
        module.fail_json(msg='Invalid value of argument "state": {0}'.format(state))

    module.exit_json(**result)


if __name__ == "__main__":
    main()

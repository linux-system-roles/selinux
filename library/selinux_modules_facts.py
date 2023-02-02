#!/usr/bin/python

# Copyright: (c) 2020, Petr Lautrbach <plautrba@redhat.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: selinux_modules_facts

short_description: Gather state of SELinux modules

version_added: '0.0.1'

description:
    - "WARNING: Do not use this module directly! It is only for role internal use."
    - Gather state of SELinux modules

author:
    - Petr Lautrbach (@bachradsusi)
"""

# placeholder - ansible-test requires EXAMPLES
EXAMPLES = r"""
"""

import traceback

SEMANAGE_IMP_ERR = None
try:
    import semanage

    HAVE_SEMANAGE = True
except ImportError:
    SEMANAGE_IMP_ERR = traceback.format_exc()
    HAVE_SEMANAGE = False

# https://docs.ansible.com/ansible/latest/dev_guide/developing_modules_general.html#creating-an-info-or-a-facts-module
from ansible.module_utils.basic import AnsibleModule, missing_required_lib


def init_libsemanage(store=""):
    sh = semanage.semanage_handle_create()
    if not sh:
        raise ValueError("Could not create semanage handle")

    if store != "":
        semanage.semanage_select_store(sh, store, semanage.SEMANAGE_CON_DIRECT)
    semanage.semanage_connect(sh)
    semanage.semanage_set_reload(sh, 0)
    return sh


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict()

    # seed the result dict in the object
    # we primarily care about changed and state
    # changed is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
        ansible_facts=dict(),
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    if not HAVE_SEMANAGE:
        module.fail_json(
            msg=missing_required_lib("python3-libsemanage"), exception=SEMANAGE_IMP_ERR
        )

    try:
        sh = init_libsemanage()
    except Exception:
        module.fail_json(
            msg="Could not connect to SELinux module store",
            exception=traceback.format_exc(),
        )

    priorities = True
    checksums = True
    try:
        r, modinfo, num_modules = semanage.semanage_module_list_all(sh)
    except AttributeError:
        r, modinfo, num_modules = semanage.semanage_module_list(sh)
        priorities = False
        checksums = False

    result["ansible_facts"] = {"selinux_installed_modules": {}}
    selinux_modules = {}
    if priorities:
        for n in range(num_modules):
            r, modkey = semanage.semanage_module_key_create(sh)

            m = semanage.semanage_module_list_nth(modinfo, n)

            rc, m_name = semanage.semanage_module_info_get_name(sh, m)
            if rc < 0:
                raise ValueError("Could not get module name")
            r = semanage.semanage_module_key_set_name(sh, modkey, m_name)
            if r != 0:
                raise Exception(r)

            rc, m_enabled = semanage.semanage_module_info_get_enabled(sh, m)
            if rc < 0:
                raise ValueError("Could not get module enabled")

            rc, m_priority = semanage.semanage_module_info_get_priority(sh, m)
            if rc < 0:
                raise ValueError("Could not get module priority")
            r = semanage.semanage_module_key_set_priority(sh, modkey, m_priority)
            if r != 0:
                raise Exception(r)

            rc, m_lang_ext = semanage.semanage_module_info_get_lang_ext(sh, m)
            if rc < 0:
                raise ValueError("Could not get module lang_ext")

            if m_lang_ext == "cil":
                cil = 1
            else:
                cil = 0

            try:
                r, m_checksum, _len = semanage.semanage_module_compute_checksum(
                    sh, modkey, cil
                )
            except AttributeError:
                r = 0
                m_checksum = ""
                checksums = False

            if m_name not in selinux_modules:
                selinux_modules[m_name] = {}
            selinux_modules[m_name][m_priority] = {
                "enabled": m_enabled,
                "checksum": m_checksum,
            }
    else:
        for n in range(num_modules):
            m = semanage.semanage_module_list_nth(modinfo, n)
            m_name = semanage.semanage_module_get_name(m)
            m_enabled = semanage.semanage_module_get_enabled(m)
            selinux_modules[m_name] = {}
            selinux_modules[m_name][0] = {
                "enabled": m_enabled,
                "checksum": "",
            }

    result["ansible_facts"] = {
        "selinux_installed_modules": selinux_modules,
        "selinux_priorities": priorities,
        "selinux_checksums": checksums,
    }

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)


if __name__ == "__main__":
    run_module()

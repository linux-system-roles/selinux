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

from subprocess import PIPE, Popen

# https://docs.ansible.com/ansible/latest/dev_guide/developing_modules_general.html#creating-an-info-or-a-facts-module
from ansible.module_utils.basic import AnsibleModule


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

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        module.exit_json(**result)
    # manipulate or modify the state as needed (this is going to be the
    # part where your module will do what it needs to do)

    priorities = True
    semodule_l = Popen(
        ["/usr/sbin/semodule", "-lfull"],
        stdin=None,
        stdout=PIPE,
        stderr=PIPE,
        universal_newlines=True,
    ).communicate()
    # most likely RHEL 6 with old SELinux userspace - no priorities
    if "invalid option" in semodule_l[1]:
        semodule_l = Popen(
            ["/usr/sbin/semodule", "-l"],
            stdin=None,
            stdout=PIPE,
            stderr=PIPE,
            universal_newlines=True,
        ).communicate()
        priorities = False

    result["ansible_facts"] = {"selinux_installed_modules": {}}
    selinux_modules = {}
    for line in semodule_l[0].splitlines():
        module_data = line.split()
        if priorities:
            # 100 zosremote         pp disabled
            if module_data[1] not in selinux_modules:
                selinux_modules[module_data[1]] = {}

            selinux_modules[module_data[1]][module_data[0]] = (
                module_data[3] if len(module_data) > 3 else "enabled"
            )
        else:
            # zosremote       1.1.0   Disabled
            if module_data[0] not in selinux_modules:
                selinux_modules[module_data[0]] = {}
                selinux_modules[module_data[0]]["0"] = (
                    "disabled" if len(module_data) > 2 else "enabled"
                )

    result["ansible_facts"] = {
        "selinux_installed_modules": selinux_modules,
        "selinux_priorities": priorities,
    }

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)


def main():
    run_module()


if __name__ == "__main__":
    main()

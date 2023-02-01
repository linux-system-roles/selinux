# SELinux
![CI Testing](https://github.com/linux-system-roles/selinux/workflows/tox/badge.svg)

## Expected functionality

Essentially provide mechanisms to manage local customizations:

* Set enforcing/permissive
* restorecon portions of filesystem tree
* Set/Get Booleans
* Set/Get file contexts
* Manage logins
* Manage ports

## Available modules in Ansible

[selinux](https://docs.ansible.com/ansible/latest/collections/ansible/posix/selinux_module.html#ansible-collections-ansible-posix-selinux-module): Configures the
SELinux mode and policy.

[seboolean](https://docs.ansible.com/ansible/latest/collections/ansible/posix/seboolean_module.html#ansible-collections-ansible-posix-seboolean-module): Toggles SELinux booleans.

[sefcontext](https://docs.ansible.com/ansible/latest/collections/community/general/sefcontext_module.html#ansible-collections-community-general-sefcontext-module): Manages
SELinux file context mapping definitions similar to the `semanage fcontext`
command.

[seport](https://docs.ansible.com/ansible/latest/collections/community/general/seport_module.html#ansible-collections-community-general-seport-module): Manages SELinux
network port type definitions.

## Requirements

The role requires some SELinux modules.  If you are using `ansible-core`, you must
get these from the `ansible.posix` and `community.general` collections.  Use the
file `meta/collection-requirements.yml` to install these:
```
ansible-galaxy collection install -vv -r meta/collection-requirements.yml
```
If you are using Ansible Engine 2.9, or are using an Ansible bundle which
includes these collections/modules, you should have to do nothing.

### Modules provided by this repository

* `selinux_modules_facts`: Gather state of SELinux modules

## Usage

The general usage is demonstrated in [selinux-playbook.yml](examples/selinux-playbook.yml) playbook.

### selinux role

This role can be configured using variables as it is described below.

```yaml
vars:
  [ see below ]
roles:
  - role: linux-system-roles.selinux
```

#### purge local modifications

By default, the modifications specified in `selinux_booleans`, `selinux_fcontexts`,
`selinux_ports` and `selinux_logins` are applied on top of pre-existing modifications.
To purge local modifications prior to setting new ones, set following variables to true:

- SELinux booleans: `selinux_booleans_purge`
- SELinux file contexts: `selinux_fcontexts_purge`
- SELinux ports: `selinux_ports_purge`
- SELinux user mapping: `selinux_logins_purge`

You can purge all modifications by using shorthand:

```yaml
selinux_all_purge: true
```

#### set SELinux policy type and mode

```yaml
selinux_policy: targeted
selinux_state: enforcing
```
Allowed values for `selinux_state` are `disabled`, `enforcing` and `permissive`.

If `selinux_state` is not set, the SELinux state is not changed.
If `selinux_policy` is not set and SELinux is to be enabled, it defaults to `targeted`. 
If SELinux is already enabled, the policy is not changed.

#### set SELinux booleans

```yaml
selinux_booleans:
  - { name: 'samba_enable_home_dirs', state: 'on' }
  - { name: 'ssh_sysadm_login', state: 'on', persistent: 'yes' }
```

#### Set SELinux file contexts

```yaml
selinux_fcontexts:
  - { target: '/tmp/test_dir(/.*)?', setype: 'user_home_dir_t', ftype: 'd', state: 'present' }
```
Users may also pass the following optional parameters:
- `seuser`: to set the SELinux user
- `selevel`: to set the MLS/MCS Security Range (MLS/MCS Systems only) SELinux Range for SELinux login mapping defaults to the SELinux user record range.

Individual modifications can be dropped by setting `state` to `absent`.

#### Set SELinux ports

```yaml
selinux_ports:
  - { ports: '22100', proto: 'tcp', setype: 'ssh_port_t', state: 'present', local: true }
```

#### run restorecon on filesystem trees

```yaml
selinux_restore_dirs:
  - /tmp/test_dir
```

#### Set linux user to SELinux user mapping

```yaml
    selinux_logins:
      - { login: 'plautrba', seuser: 'staff_u', state: 'absent' }
      - { login: '__default__', seuser: 'staff_u', serange: 's0-s0:c0.c1023', state: 'present' }
```

#### Manage SELinux modules

It is possible to maintain SELinux modules using `selinux_modules` variable which would contain a list of dictionaries, e.g.:

```yaml
    selinux_modules:
      - { path: 'localmodule.pp', state: 'enabled' }
      - { path: 'localmodule.cil', priority: '350', state: 'enabled' }
      - { name: 'unconfineduser', state: 'disabled' }
      - { name: 'localmodule', priority: '350', state: 'absent' }
```

  - `path`: a local module file (either .cil or .pp) to be installed on a node, used for installing new modules
  - `name`: module name, used for enabling disabled modules, disabling enabled modules, removing modules
  - `priority`: SELinux module priority, default is *"400"*. *"100"* is used for modules installed from *selinux-policy* packages, *"200"* for other modules installed from 3rd party rpms, *"300"* is used by SETroubleshoot
  - `state`:
  * `enabled`: install or enable module
  * `disabled`: disable module
  * `absent`: remove module

**Note:** Building modules from source on nodes is not supported.
However, in many cases a binary *pp* or *cil* module could be used on different systems if all systems support
types, classes and permissions used in the module.
In case of *pp* module it also needs to be built with the lowest supported policydb module version on target systems,
i.e. on the oldest system.

**Note:** Module priorities are ignored in Red Hat Enterprise Linux 6

**Note:** Managing modules is idempotent only on Fedora, and EL 8.6 and later. You can manage modules on older releases, but it will not be idempotent.

## Ansible Facts

### selinux\_reboot\_required

This custom fact is set to `true` if system reboot is necessary when SELinux is set from `disabled` to `enabled` or vice versa.  Otherwise the fact is set to `false`.  In the case that system reboot is needed, it will be indicated by returning failure from the role which needs to be handled using a `block:`...`rescue:` construct. The reboot needs to be performed in the playbook, the role itself never reboots the managed host. After the reboot the role needs to be reapplied to finish the changes.

### selinux\_installed\_modules

This custom fact represents SELinux module store structure

``` json
selinux_installed_modules = {
  <module name>: {
    <module priority>: ("enabled"|"disabled"),
    ...
  },
  ...
}
```

e.g.

``` json
"ansible_facts": {
  "selinux_installed_modules": {
    "abrt": {
      "100": "enabled",
      "400": "disabled"
    },
    "accountsd": {
      "100": "enabled"
    },
    "acct": {
      "100": "enabled"
    }
  }
}
```

**NOTE:** Module priority is set to "0" when priorities are not supported, e.g. on Red Hat Enterprise Linux 6

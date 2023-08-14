# Confined users

By default linux users are mapped to SELinux user `unconfined_u`, which is subject to minimal restrictions. You can greatly improve security of your systems by confining users, that is by mapping them to SELinux users with less privilege.
`confined_users-playbook.yml` contains an example configuration for confining existing users and creating new ones with varying levels of access.

## Expected functionality

* Set default user mapping
* Confine existing users accounts
* Set booleans to customize access

## Variables

### selinux_booleans

SELinux policy provides several booleans for customizing access of confined users.

`selinux_booleans` is expected to hold a list of booleans together with their intended value and persistence setting.
Formally it is a `list` of `dict`, where each `dict` is in the same format as used by the
[seboolean](https://docs.ansible.com/ansible/latest/collections/ansible/posix/seboolean_module.html#ansible-collections-ansible-posix-seboolean-module)
module.

```yaml
selinux_booleans:
  - {name: 'ssh_sysadm_login', state: 'on', persistent: 'yes'}
  - {name: 'user_exec_content', state: 'off', persistent: 'yes'}
```

See
[confined users documentation](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/9/html-single/using_selinux/index#managing-confined-and-unconfined-users_using-selinux)
 for a list of relevant booleans.

### existing_privileged_users

Specify a list of existing users to be mapped to `staff_u` and allowed to use `sudo` to perform administrative tasks.

```yaml
existing_privileged_users:
  - "Mark"
  - "Roger"
```

### selinux_logins

Manage the linux user to SELinux user mapping. This is a `list` of `dict`,
where each `dict` is in the same format as used by the
[selogin](https://docs.ansible.com/ansible/latest/collections/community/general/selogin_module.html)
module.

```yaml
selinux_logins:
  - {login: 'plautrba', seuser: 'staff_u', state: 'absent'}
  - {login: '__default__', seuser: 'staff_u', serange: 's0-s0:c0.c1023', state: 'present'}
```

`__default__` is the value assigned to a new user when no login mapping is specified for them. All other lines must correspond to existing user accounts. Note that changing a login mapping changes the file context definitions of the user's home directory. This change is applied using `restorecon` at the end of the playbook.

## Examples

Confining users is demonstrated in
[confined_users-playbook.yml](examples/confined_users-playbook.yml) playbook.

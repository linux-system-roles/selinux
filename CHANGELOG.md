Changelog
=========

[1.4.0] - 2022-07-28
--------------------

### New Features

- Added setting of seuser and selevel for completeness (#108)

Added setting of seuser and selevel for completeness
See Issue #106 "RFE: Support for setting seuser in selinux_fcontexts"
https://github.com/linux-system-roles/selinux/issues/106

Added explanation of seuser and selevel parameters

Added -F flag to restorecon to force reset
See "man restorecon" for more detail on -F flag

Authored-by: Benjamin Blasco <bblasco@redhat.com>

### Bug Fixes

- none

### Other Changes

- changelog_to_tag action - support other than "master" for the main branch name, as well (#117)

- Use GITHUB_REF_NAME as name of push branch; fix error in branch detection [citest skip] (#118)

We need to get the name of the branch to which CHANGELOG.md was pushed.
For now, it looks as though `GITHUB_REF_NAME` is that name.  But don't
trust it - first, check that it is `main` or `master`.  If not, then use
a couple of other methods to determine what is the push branch.

Signed-off-by: Rich Megginson <rmeggins@redhat.com>

[1.3.7] - 2022-07-19
--------------------

### New Features

- none

### Bug Fixes

- none

### Other Changes

- make all tests work with gather_facts: false (#111)

Ensure all tests work if using ANSIBLE_GATHERING=explicit

- make min_ansible_version a string in meta/main.yml (#112)

The Ansible developers say that `min_ansible_version` in meta/main.yml
must be a `string` value like `"2.9"`, not a `float` value like `2.9`.

- Add CHANGELOG.md (#113)

[1.3.6] - 2022-05-06
--------------------

### New Features

- none

### Bug Fixes

- none

### Other Changes

- Use meta/collection-requirements.yml for collection dependencies
- bump tox-lsr version to 2.11.0; remove py37; add py310

[1.3.5] - 2022-04-14
--------------------

### New Features

- support gather\_facts: false; support setup-snapshot.yml

### Bug Fixes

- none

### Other Changes

- bump tox-lsr version to 2.10.1

[1.3.4] - 2022-01-10
--------------------

### New Features

- none

### Bug Fixes

- none

### Other Changes

- bump tox-lsr version to 2.8.3
- change recursive role symlink to individual role dir symlinks

[1.3.3] - 2021-11-08
--------------------

### New Features

- support python 39, ansible-core 2.12, ansible-plugin-scan

### Bug Fixes

- fix ansible-lint issues

### Other Changes

- update tox-lsr version to 2.7.1
- Add meta/requirements.yml; support ansible-core 2.11

[1.3.2] - 2021-10-05
--------------------

### New Features

- none

### Bug Fixes

- Fix version comparisons for ansible\_distribution\_major\_version

### Other Changes

- none

[1.3.1] - 2021-10-04
--------------------

### New Features

- Improve README
- Add support for Rocky Linux 8

### Bug Fixes

- none

### Other Changes

- use tox-lsr version 2.5.1
- use apt-get install -y

[1.3.0] - 2021-08-10
--------------------

### New Features

- Drop support for Ansible 2.8 by bumping the Ansible version to 2.9

### Bug Fixes

- none

### Other Changes

- Clean up Ansible 2.8 CI configuration entries

[1.2.3] - 2021-06-01
--------------------

### New Features

- Update semanage task to not specify Fedora since it also runs on RHEL/CentOS 8

### Bug Fixes

- none

### Other Changes

- none

[1.2.2] - 2021-05-06
--------------------

### New Features

- use lazy unmount to fix umount: target is busy
- move example playbook to examples/ directory
- use reboot module; ansible 2.8
- Drop selogin module

### Bug Fixes

- tag problematic tests; fix wording; fix formatting
- Fix issues found by - linters - enable all tests on all repos - remove suppressions
- Fix ansible-test errors

### Other Changes

- Remove python-26 environment from tox testing
- update to tox-lsr 2.4.0 - add support for ansible-test sanity with docker
- Add a note to each module Doc to indicate it is private
- use tox-lsr 2.2.1
- CI: Add support for RHEL-9

[1.2.1] - 2021-02-11
--------------------

### New Features

- none

### Bug Fixes

- fix incorrect default value \(there is no variable named "present"\)
- Fix centos6 repos; use standard centos images; add centos8

### Other Changes

- use tox-lsr 2.2.0
- use molecule v3, drop v2 - use tox-lsr 2.1.2
- remove ansible 2.7 support from molecule
- Add explaining comments to selinux-playbook.yml
- use tox for ansible-lint instead of molecule
- use new tox-lsr plugin
- use github actions instead of travis

[1.2.0] - 2020-11-20
--------------------

### New Features

- Add ability to manage SELinux modules on multiple machines

### Bug Fixes

- none

### Other Changes

- none

[1.1.1] - 2020-10-14
--------------------

### New Features

- none

### Bug Fixes

- none

### Other Changes

- lock ansible-lint version at 4.3.5; suppress role name lint warning
- sync collections related changes from template to selinux role
- collections prep - use FQRN

[1.1.0] - 2020-08-12
--------------------

### New Features

- none

### Bug Fixes

- Fix yamllint errors
- Fix typo, older ansible did not care, but 2.7 does.

### Other Changes

- Synchronize files from linux-system-roles/template
- sync with latest template including shellcheck
- use molecule v2
- List all variables in defaults.
- Configure Molecule and Travis CI
- Add test running the role with default parameters
- Move defaults to defaults/main.yml

[1.0.0] - 2018-08-21
--------------------

### Initial Release

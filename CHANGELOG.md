Changelog
=========

[1.6.2] - 2023-09-07
--------------------

### Other Changes

- ci: Add markdownlint, test_converting_readme, and build_docs workflows (#182)

  - markdownlint runs against README.md to avoid any issues with
    converting it to HTML
  - test_converting_readme converts README.md > HTML and uploads this test
    artifact to ensure that conversion works fine
  - build_docs converts README.md > HTML and pushes the result to the
    docs branch to publish dosc to GitHub pages site.
  - Fix markdown issues in README.md
  
  Signed-off-by: Sergei Petrosian <spetrosi@redhat.com>

- docs: Fix highlighting for code blocks to look nice (#183)

  For given code blocks yaml looks nicer, json marks some parts as errors.

- docs: Make badges consistent, run markdownlint on all .md files (#185)

  - Consistently generate badges for GH workflows in README RHELPLAN-146921
  - Run markdownlint on all .md files
  - Add custom-woke-action if not used already
  - Rename woke action to Woke for a pretty badge
  
  Signed-off-by: Sergei Petrosian <spetrosi@redhat.com>

- ci: Remove badges from README.md prior to converting to HTML (#186)

  - Remove thematic break after badges
  - Remove badges from README.md prior to converting to HTML
  
  Signed-off-by: Sergei Petrosian <spetrosi@redhat.com>


[1.6.1] - 2023-07-19
--------------------

### Bug Fixes

- fix: facts being gathered unnecessarily (#180)

### Other Changes

- ci: Add pull request template and run commitlint on PR title only (#175)
- ci: Rename commitlint to PR title Lint, echo PR titles from env var (#176)
- ci: fix python 2.7 CI tests by manually installing python2.7 package (#177)
- ci: ansible-lint - ignore var-naming[no-role-prefix] (#178)
- refactor: ansible-lint - vars cannot be reserved names (#179)

[1.6.0] - 2023-05-26
--------------------

### New Features

- feat: Use `restorecon -T 0` on Fedora and RHEL > 8

### Other Changes

- docs: Consistent contributing.md for all roles - allow role specific contributing.md section
- docs: add Collection requirements section to README
- test: Add basic selinux_restore_dirs test

[1.5.9] - 2023-04-27
--------------------

### Other Changes

- test: ensure the test works with ANSIBLE_GATHERING=explicit
- ci: Add commitlint GitHub action to ensure conventional commits with feedback

[1.5.8] - 2023-04-13
--------------------

### Other Changes

- ansible-lint - use changed_when for conditional tasks (#163)

[1.5.7] - 2023-04-06
--------------------

### Other Changes

- s/restoreconf/restorecon/ (#160)
- Add README-ansible.md to refer Ansible intro page on linux-system-roles.github.io (#161)

[1.5.6] - 2023-02-09
--------------------

### New Features

- none

### Bug Fixes

- use fileglob to lookup selinux module file - idempotency support (#155)

### Other Changes

- none

[1.5.5] - 2023-02-08
--------------------

### New Features

- none

### Bug Fixes

- Use stat on localhost with become: false for module idempotency (#152)

### Other Changes

- none

[1.5.4] - 2023-02-03
--------------------

### New Features

- none

### Bug Fixes

- Fix idempotency - Use lookup file + sha256 to get hash of local policy file

### Other Changes

- none

[1.5.3] - 2023-02-02
--------------------

### New Features

- none

### Bug Fixes

- Use selinux facts to compare module checksums before copying to a node (#144)

### Other Changes

- do not use 'become' in tests, examples (#145)

[1.5.2] - 2023-01-26
--------------------

### New Features

- none

### Bug Fixes

- Rewrite selinux_load_module.yml to use local_semodule  (#135)

This makes module management idempotent on Fedora, and EL 8.6
and later.

### Other Changes

- none

[1.5.1] - 2023-01-24
--------------------

### New Features

- none

### Bug Fixes

- ansible-lint 6.x fixes (#132)

### Other Changes

- Add check for non-inclusive language (#131)
- cleanup non-inclusive words.
- ensure semanage present on EL7 tests; fix jinja spacing, quoting (#139)

[1.5.0] - 2022-09-19
--------------------

### New Features

- add 'local' parameter to seport (#124)

`community.general.seport` has recently added the `local` parameter
which is now supported by the role.

- `local: true`:
  * `state: present` enforces change to be made even though the
    port mapping could already exists in built in policy
  * `state: absent` would remove only local modification and would not
    try to remove builtin mapping.

The role vendors-in the seport module as `local_seport`, because otherwise
it is too difficult to support both Ansible 2.9 and ansible-core.  We will
revisit this when Ansible 2.9 is EOL.

### Bug Fixes

- none

### Other Changes

- add test for fcontext seuser and selevel (#120)

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

- changelog_to_tag action - github action ansible test improvements

- Use GITHUB_REF_NAME as name of push branch; fix error in branch detection [citest skip] (#118)

We need to get the name of the branch to which CHANGELOG.md was pushed.

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
- update to tox-lsr 2.4.0 - add support for ansible-test with docker
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

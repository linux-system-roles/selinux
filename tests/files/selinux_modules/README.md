# Information

Only the *.pp files are used in the actual tests.

The other files are provided in case you need to regenerate the test-d.pp file.

You must rebuild on the oldest supported OS. Right now that means EL7.  You can
use a container:

```bash
cd tests/files/selinux_modules
podman run --rm --privileged -v `pwd`:/root -it centos:7 bash
sed -i '/^mirror/d;s/#\(baseurl=http:\/\/\)mirror/\1vault/' /etc/yum.repos.d/*.repo
cd /root
yum install -y setools setools-devel selinux-policy-devel
make -f /usr/share/selinux/devel/Makefile linux-system-roles-selinux-test-d.pp
```

# Overview

Find the unstable and stable RPMs at the following locations.

* [Unstable RPMs][1] (e.g. main/develop/feature/bugfix branches, anything that is not a git-tag)
* [Stable RPMs][2] (e.g. git-tags)

To install the latest RPM, use the following `zypper` command:

```bash
zypper --plus-repo=https://artifactory.algol60.net/artifactory/csm-rpms/hpe/stable/sle-15sp3 --no-gpg-checks -n in canu -y
```

## Installing/Upgrading

* Get the rpm to the system directly (curl/wget) or scp depending.
* For systems without rpm signing install via `rpm -Uvh <rpm file name>`
* Likely best to install on both a worker and a master.

[1]: https://artifactory.algol60.net/artifactory/csm-rpms/hpe/unstable/sle-15sp3/canu/
[2]: https://artifactory.algol60.net/artifactory/csm-rpms/hpe/stable/sle-15sp3/canu/

# Installing The CANU RPM

Find the unstable and stable RPMs at the following locations.

* [Unstable RPMs][1] (e.g. main/develop/feature/bugfix branches, anything that is not a git-tag)
* [Stable RPMs][2] (e.g. git-tags)

To install the latest RPM, use `zypper` or `rpm`:

```bash
zypper --plus-repo=https://artifactory.algol60.net/artifactory/csm-rpms/hpe/stable/sle-15sp3 --no-gpg-checks -n in canu -y
rpm -ivh https://artifactory.algol60.net/ui/native/csm-rpms/hpe/stable/sle-15sp3/canu/x86_64/canu-<version>.rpm
```

[1]: https://artifactory.algol60.net/artifactory/csm-rpms/hpe/unstable/sle-15sp3/canu/
[2]: https://artifactory.algol60.net/artifactory/csm-rpms/hpe/stable/sle-15sp3/canu/

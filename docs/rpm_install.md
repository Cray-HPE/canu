# Overview
* To view all CANU RPM builds: https://artifactory.algol60.net/ui/native/csm-rpms/hpe/
  * Unstable for develop branch
  * Stable for the main branch
* For CSM 1.2 `sle-15sp2/canu/x86_64`
* Pick the build desired.  For development builds pick the most recent dated build for the branch.  PR builds for a branch are after branch builds if a PR build is desired.

# Example:
To use the last PR build (before merge) of the 1.1.6 develop branch the broser should point to:
https://artifactory.algol60.net/ui/native/csm-rpms/hpe/unstable/sle-15sp2/canu/x86_64/canu-1.1.6~develop-1~pr_84~20220201235020.6a90219.x86_64.rpm

To download the file via curl or wget the URL is slightly different:
https://artifactory.algol60.net/artifactory/csm-rpms/hpe/unstable/sle-15sp2/canu/x86_64/canu-1.1.6~develop-1~pr_84~20220201235020.6a90219.x86_64.rpm

# Installing/Upgrading
* Get the rpm to the system directly (curl/wget) or scp depending.
* For systems without rpm signing install via `rpm -Uvh <rpm file name>`
* Likely best to install on both a worker and a master.
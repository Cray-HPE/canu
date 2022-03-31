# Procedure

1. `git checkout develop`
2. `git pull`
3. `git checkout main`
4. `git pull`
5. `git checkout -b release-<x.y.z>`
6. `git merge develop`
7. Resolve conflicts - generally accept all incoming (CAREFUL use: `git merge develop --strategy-option theirs`).
8. Modify readme.md by moving ~develop from the main title header
9. Modify `canu/.version` to remove `~develop`
10. Run `nox` locally and ensure testing passes.
11. Commit the readme.md, .version and any nox resolutions..
12. Put up a PR merging the release branch to *main* (not develop).  See template below. 
13. Use the usual review process to get the PR merged.
14. Navigate to github releases: `https://github.com/Cray-HPE/canu/releases`
15. Select "Draft a new release"
16. "Choose a tag" - enter the new x.y.z release number (not `vx.y.z`)
17. Select `main` as the target
18. Write a short, quippy title for the release.
19. In the main text write "Overview", a few short bullet points pulled from the changelog outlining major changes.
20. In the main text write "Detailed Changelog" and paste in the changelog from readme.md
21. Click "Publish release"
21. Make sure the canu binary RPM exists in artifactory:  (https://artifactory.algol60.net/ui/native/csm-rpms/hpe/stable/sle-15sp3/canu/x86_64) and should probably test it physically.
22. Create a CASMNET Jira for the release.  Annotate appropriately for Component: CANU, Label: NET, RELEASE_CRITICAL, Fix Version: v1.X
23. Clone the `csm` and `csm-rpms` repos.
24. Create branches off each release/x.y you need to go to and edit the following files.
To release CANU into CSM:
* https://github.com/Cray-HPE/csm/blob/main/rpm/cray/csm/sle-15sp2/index.yaml#L49
* https://github.com/Cray-HPE/csm/blob/main/rpm/cray/csm/sle-15sp3/index.yaml#L49
* https://github.com/Cray-HPE/csm-rpms/blob/main/packages/cray-pre-install-toolkit/base.packages#L3
* https://github.com/Cray-HPE/csm-rpms/blob/main/packages/node-image-non-compute-common/base.packages#L3


# PR Template
```
Title: "Release <x.y.z>"

Summary:
* <List any new features as individual points>
* <List any call out bugfixes (one or two lines only)>

Detailed Changelog since last official release:
<paste in all changes from readme.md between last release and current, removing [x.y.z~develop] headers>

```
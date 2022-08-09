1. `git checkout develop`
2. `git pull`
3. `git checkout main`
4. `git pull`
5. `git checkout -b release-<x.y.z>`
6. `git merge develop`
7. Resolve conflicts - generally accept all incoming.
8. Modify changelog by moving develop header
9. Modify `canu/.version` to remove `~develop`
10. Put up a PR.
11. Once the PR is merged 
12. Navigate to github releases: `https://github.com/Cray-HPE/canu/releases`
13. Select "Draft a new release"
14. "Choose a tag" - enter the new x.y.z release number (not `vx.y.z`)
15. Select `main` as the target
16. Write a short, quippy title for the release.
17. In the main text write "Overview", a few short bullet points pulled from the changelog outlining major changes.
18. In the main text write "Detailed Changelog" and paste in the changelog from readme.md
19. Click "Publish release"

20. Make sure the canu binary RPM exists in artifactory:  URL.... and should probably test it physically.

To release CANU into CSM:
* https://github.com/Cray-HPE/csm/blob/main/rpm/cray/csm/sle-15sp3/index.yaml#L26
* https://github.com/Cray-HPE/csm-rpms/blob/main/packages/cray-pre-install-toolkit/base.packages#L3
* https://github.com/Cray-HPE/csm-rpms/blob/main/packages/node-image-non-compute-common/base.packages#L6
* https://github.com/Cray-HPE/csm/blob/main/docker/index.yaml#L33

21. Once new canu RPM is created. Navigate to: 'https://github.com/Cray-HPE/canu/releases' edit release and upload the new RPM can also be downloaded from Github.


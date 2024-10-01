<p align="center">
  <br>
  <h1><strong>🛶 CANU (CSM Automatic Network Utility)</strong></h1>
  <i>will float through a Shasta network and make switch setup and validation a breeze.</i>
</p>

CANU can be used to:

- Check if switches (Aruba, Dell, or Mellanox) on a Shasta network meet the firmware version requirements
- Check network cabling status using LLDP
- Validate BGP status
- Validate that SHCD spreadsheets are configured correctly and pass a number of checks
- Validate an SHCD against actual network cabling status to check for mis-cabling
- Generate switch configuration for an entire network
- Convert SHCD to CCJ (CSM Cabling JSON)
- Use CCJ / Paddle to validate the network and generate network config
- Run tests against the mgmt network to check for faults/inconsistencies.
- Backup switch configs.

# Documentation

There are several ways to view the CANU documentation:

- [https://cray-hpe.github.io/canu](https://cray-hpe.github.io/canu)
- from a virtualenv in the root of this repo: `nox -e docs && mkdocs serve --config mkdocs.yml` (local web server via `mkdocs`)
- from a virtualenv in the root of this repo: `nox -e docs && make docs` (local web server via `mkdocs`)

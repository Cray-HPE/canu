# CANU

**(CSM Automatic Network Utility)** _floats through a Shasta network and makes setup and config breeze._

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

.. module:: canu

.. toctree::
    :hidden:
    :maxdepth: 2

    backup
    cache
    canu_inventory
    container_install
    examples_output
    generate
    index
    init
    lags
    nox_testing
    paddle
    quickstart
    releasing
    report
    rpm_install
    send_command
    test_network
    uninstallation
    validate
    versioning

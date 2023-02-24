## Changelog

### [1.6.36]

- Add better LLDP data error handling for `canu report network cabling` and `canu validate network cabling`.
- Refine error messaging for failed logins.
- Detect and respond to a rare condition where LLDP queries to Mellanox switches succeed, but the return data is not JSON.

### [1.6.35]

- Bump netmiko version
- Bump nornir_netmiko version
- Fix canu test and canu validate bgp

### [1.6.34]

- Add viz node to v2 TDS architecture.

### [1.6.33]

- Modify ansible playbook to work with aruba 6300s.

### [1.6.32]

- Updated Aruba ansible playbook and documentation.
- Added ansible play to retain mgmt interface configuration.  This will help avoid lockouts.
- Added ansible play utilize the aruba checkpoint feature.  This will revert the switch config after 1 minute if the switch becomes unresponsive. 

### [1.6.31]

- Modify nmn-hmn ACL to block traffic between the NMNLB and HMNLB networks.

### [1.6.30]

- Add the ability to generate NMN configs for application nodes (v1 architecture).

### [1.6.29]

- Added dynamic ansible inventory script, installed as `canu-inventory`.
- Added a playbook to validate/upload a config.
- Add viz node to v1 architecture

### [1.6.28]

- Fix a bug where `bmc` slots were allowed non-existent port `3`.
- Remove confusing references to "bi-directional" in warnings and errors.
- Change versioning of flake8-commas to break dependency loop.
- Add logging to `validate paddle`.
- Begin refactoring the model to better validate and pick slot/port/speed requests.
- Enhance node connection exception messaging in the model.

### [1.6.27]

- Fix login node shasta name for v1 architecture

### [1.6.26]

- Added gpu and kvm node definitions to v1 architecture.
- Added logging to `canu generate switch/network config` to clean up output.
- Provided better messaging about next-step handling of missing configs in generated files.

### [1.6.25]

- Fix the CANU model to allow "cable swapping" while using LLDP data.
- Add gpu node definitiions to v2 TDS architecture.
- Provide better guidance during SHCD validation if port re-use/change is attempted.
- Update generated docs from template changes.

### [1.6.24]

- Fix sls_utils so that it works correctly when using a SLS.json file.

### [1.6.23]

- Shutdown UAN CAN port when CHN is enabled.

### [1.6.22]

- Remove Control Plane ACL for CSM 1.2 previousl missed.

### [1.6.21]

- Update Arista BGP templates
- Add feature flag for CHN BGP control plane
- Fix ordering of switch configuration when using custom switch configs or `--reorder`

### [1.6.20]

- Change UAN port config to be a trunk port on mellanox (prevously hybrid port).

### [1.6.19]

- Remove Control Plane ACL for CSM 1.3.

### [1.6.18]

- Add BGP multipath to mellanox default VRF.

### [1.6.17]

- Add Arista ISL to the Model
- Update MTN VLAN descriptions on CDU switches
- Update Arista configs to match slingshot docs
- Add datamover to canu model
- Add LNET, datamover to config generation

### [1.6.16]

- Fix a bug where destination port reuse was incorrectly allowed for `validate shcd` and `validate paddle`

### [1.6.15]

- Fix switch firmware version for 1.2 and 1.3
- Fix JSON output with canu test
- Add canu test --ping
- Add additional tests for dellanox
- Remove CPU and memory, and ip helper test from aruba
- Add the ability to have multiple CSM versions for tests
- Add sls_utils

### [1.6.14]

- Support  SLS query in CANU container  that works both in and out of Kubernetes

### [1.6.13]

- Fix CSM 1.2 UAN template when CHN is used - do not produce None VLAN.
- Bump docs generated from code.
- Change exception-handling in `canu validate shcd` and from `network_modeling`.
- Provide better next steps from errors reported while validating SHCDs.

### [1.6.12]

- canu test add ping test for KEA

### [1.6.11]

- Update to release process

### [1.6.10]

- Enabling 1.3 configuration templates.

### [1.6.9]

- Ensure location rack and elevation strings are lower case.

### [1.6.8]

- Add 4 port OCP to templates.
- Add GPU node to model.
- Use Scrapli instead of Netmiko to SSH to Aruba switches when using Nornir.
- Add additional tests to the aruba test suite.
- Add dell CDUs to test suite.
- Add CSM version flag to `canu test`

### [1.6.7]

- Fix 1.3 template links.
- Fix VLAN ordering of CMM ports.
- Add Customer ACLs back to 1.3 templates.
- Add SSH ACLs to dellanox.
- Fix Dell CMN-CAN ACL.
- Remove CMN from UAN 1.3 template.
- Add KVM to HPE model.

### [1.6.6]

- Create initial CSM 1.3 configuration framework.

### [1.6.5]

- Remove Metallb IP ranges from ACLs.
- Remove CAN-CMN ACLs from VLAN interfaces.
- Add CMN VLAN to UAN template for Mellanox & Aruba.

### [1.6.4]

- Use full `show run` commands to retrieve running config from `canu network backup`
- UAN CAN ports are now shutdown if CHN is enabled.
- Mellanox UAN CAN ports now only allow the CAN vlan.
- Added CMC subrack port configuration.

### [1.6.3]

- Documentation updates to docs/network_configuration_and_upgrade

### [1.6.2]

- Correct the 'slot warning' to specify more accurate options

### [1.6.1]

- Disable load balacing configuration for Dell CDU/Leaf.

### [1.6.0]

- Add `canu report network version` feature.
- Fix Errors in the output of `canu test`

### [1.5.14]

- Add route-map and prefixes to allow connection to UAI's from CAN network.

### [1.5.13]

- Fix Dell4148 template to include correct port count 

### [1.5.12]

- Add netutils pyinstaller hook file.

### [1.5.11]

- Create unique VSX system macs for each VSX cluster.
- Fixed Mellanox Customer ACL.
- Add VLAN 7 to Dellanox UAN for 1.0

### [1.5.10]

- Fix canu paddle-file.json schema

### [1.5.9]

- Change Rosetta/Columbia switch naming to be sw-hsn-<rack>-<####> (as with PDU and CMM/CEC).
- Change switch port/interface descriptions to `dst:slot:port==>src` to avoid truncation.
- Change gateway nodes to 4 port 1G OCP card definitions.
- Add dvs and ssn nodes as 4 port 1G OCP card definitions.
- Change large memory node common name from `lm` to `lmem`.
- Beta release of `--reorder` for switch/network config generation where custom-config is not used.

### [1.5.8]

- Added shellcheck GitHub action
- Bump ipython to 7.16.3 to remediate CVE
- Clean up Jenkins build

### [1.5.7]

- Add ACL to block CHN <> traffic for CSM 1.2
- Add Route-Map to CMN BGP peers to restrict routes to only CMN IPs

### [1.5.6]

- More verbose instructions for generating switch configs

### [1.5.5]

- Add the ability to generate BGP config for Arista edge switches.

### [1.5.4]

- `canu backup network` and `canu test` now checks for connectivity before running commands against the switch.
- Refactored canu `test.py`.
- Fixed mellanox backup config.  It requires `show running-config expanded` vs `show run`
- Add test for out of sync LAG on aruba.
- Fixed mellanox ping test.

### [1.5.3]

- Update base packages required by Canu to function and fix known CVE from paramiko

### [1.5.2]

- Fixed aruba and dell 1.2 templates so CAN config is only generated when it's detected in SLS.
- Fix `canu generate --custom` and `canu generate --preserve` usage with RPM, this requried a new pyinstaller hook file.
- Remove MTU from mellanox templates
- Add negate commands to templates to remove switch defaults.
- Fix a couple `canu validate` issues
- Bump ttp version

### [1.5.1]

- Add DNS test to canu/test. remove folder "network configuration and upgrade"

### [1.5.0]

- Add `canu send command` feature.

### [1.4.1]

- Added new guide for network install

### [1.4.0]

- Add the ability to preserve LAG #s when generating switch configs.
- Fix hard coded LAG numbers in templates.
- Fix hard coded VLAN IDs in templates.
- Remove unused Dellanox TDS templates.

### [1.3.5]

- Fix BGP output of canu validate
- Ignore `user admin` and `snmpv3` config during canu validate

### [1.3.4]

- fixed PDU and sw-hsn ports being generated for sw-leaf-bmc switches

### [1.3.3]

- Define warnings variable as defaultdict(list) to handle invalid key errors

### [1.3.2]

- Fix aruba banner output during canu validate

### [1.3.1]

- shutdown unused ports by default on aruba 6300+dell+mellanox

### [1.3.0]

- Removed the override feature
- Add feature to inject custom configs into generated switch configs

### [1.2.10]

- Change Aruba banner from motd to exec

### [1.2.9]

- Reordered the configuration output so that vlans are defined before being applied to ports.

### [1.2.8]

- Fix Leaf-bmc naming corner case: leaf-bmc-bmc to leaf-bmc
- Fix OSPF CAN vlan for 1.2 in full/tds

### [1.2.7]

- Fixed bug to allow canu to exit gracefully with sys.exit(1)

### [1.2.6]

- Add network test cases
- Add network test cases for DNS and site connectivity
- Fixed missing DNS from Aruba switches

### [1.2.5]

- Add NMN network for 1.0 to ssh allowed into switches because of BGP DOCS in 1.0 allowing it.
- Remove router ospfv3 from 1.0/1.2
- Fixed ACL, OSPF, BGP config files
- Fixed test templates for ACL, OSPF, BGP
- Change Aruba banner to match running config.
- Fix Canu test --network

### [1.2.4]

- Add OSPF to vlan 1.
- Add 'ip ospf passive' to vlan 1,4.
- Fix test cases: test_generate_switch_config_aruba_csm_1_2.py | test_generate_switch_config_dellanox_csm_1_2.py.
- Fix missing OSPF configuration from VLAN 7 in /network_modeling/configs/templates/dellmellanox/1.2/*.
- Fix descriptions for MTL

### [1.2.3]

- Config backup create /running.

### [1.2.2]

- Add SHCD filename to paddle/ccj JSON to obtain originating SHCD version.

### [1.2.1]

- Remove `canu config bgp`, there is no need for this as it's configured during `canu generated switch/network config`
- Move Aruba CMN ospf instance from 1 to 2.
- `canu validate` output enahncements & bug fixes.
- Template fixes/enhancements.

### [1.2.0]

- Add `canu backup network`

### [1.1.11]

- `canu validate BGP` now has an option to choose what network to run against.
- Remove `'lacp-individual` from mellanox spine02.
- Generate unique MAC address for each Mellanox magp virtual router.

### [1.1.10]

- Update canu validate to user heir config diff and cleaner output.
- Add --remediate option for canu validate
- bump heir config version

### [1.1.9]

- Fix Mellanox web interface command
- Remove hard coded BGP ASN #
- Add CMN to CAN ACL
- Level set CSM 1.0 templates with CSM 1.2 minus CMN, VRF, etc..

### [1.1.8]

- Add banner motd to all switch configs with CSM and CANU versions.
- Add documentation to install from RPM (for SLES).

### [1.1.7]

- Remove CMN ip helper on mellanox.
- Remove broken tests.
- Fix Aruba OSPF process.
- Mellanox dns command fix.
- Mellanox loopback command fix.
- Mellanox NTP command fix.

### [1.1.5]

- Add ACLs to VLAN interfaces.
- Add maximum paths to mellanox BGP template for customer VRF.
- Fix Mellanox ISL speed setting.
- Fix PDU node recognition and naming: `pdu<#>, <cabinet>pdu<#>, <cabinet>p<#> all map to a name pdu-<cabinet>-<####>`
- Add large memory UAN node definitions: `lm-<####> maps to lm-<####>`
- Add gateway: `gateway<#>, gw<#> map to gateway-<####>`

### [1.1.4]

- fix sls url

### [1.1.3]

- validate BGP now reads IPs from the SLS API
- Added a feature to run tests against a live network. (Aruba only)

### [1.1.2]

- Enabled webui for mellanox.
- Added speed commands to dell/mellanox templates.

### [1.1.1] 2022-12-07

- Updated pull_request_template.md
- Adjusted the STP timeout to 4 seconds from the default of 15.
- Changed setup.py file glob to follow previously updated Jinja2 template locations.
- Command line option --csi-folder has changed to --sls-file. Any SLS JSON file can be used.
- Installation via pip now supports non-developer modes. Pyinstaller binary and RPM now work as advertised.
- The directory of canu_cache.yaml is now dynamically configured in the user's home directory (preferred), or the system temporary directory depending on filesystem permissions.
- Added `canu cache location` print the folder where your cache is located
- Added `canu cache print` to print a colored version of your cache to the screen
- Added `canu cache delete` to delete the cache file, the file will be created again on the next canu command
- Added Dell and Mellanox support to the `canu validate switch config` command
- Added Dell and Mellanox support to the `canu validate network config` command
- Added ability to compare two config files with `canu validate switch config`
- Added ability to compare two config folders with `canu validate network config`
- Added an `--override` option to `canu generate switch config` and `canu generate network config`, this allows users to ignore custom configuration so CANU does not overwrite it.
- Changed the `-s --shasta` flag to `--csm`
- Added Mellanox support to the `canu config bgp` command
- Added Dell/Mellanox support to the `canu generate network config` & `canu generate switch config` commands
- Updated `canu validate shcd-cabling` to show port by port differences.
- Updated the docs in the `/docs` folder to build automatically with nox
- Added support for CMN (Customer Management Network) on Aruba and Dellanox.
- Added mgmt plane ACL on Aruba Switches
- Added Metallb networks to ACLs
- Removed the hardcoded VLAN variables, these are now being pulled in from SLS.
- Added 1.2 Aruba templates
- Added CANU validate switch config support for dellanox.
- BGP is now generated during `canu generate` switch/network config. (aruba &Mellanox)
- Computes/HSN-bmcs/VizNodes/LoginNodes/pdus now have their switch config generated.
- Added SubRack support for reading in all variations from the SHCD, and added **sub_location** and **parent** to the JSON output
- Added Paddle / CCJ (CSM Cabling JSON) support. Commands `canu validate paddle` and `canu validate paddle-cabling` can validate the CCJ. Config can be generated using CCJ.
- Added the `jq` command to the Docker image.
- Added `canu test` to run tests against the network (aruba only).

### [0.0.6] - 2021-9-23

- Added alpha version of schema-checked JSON output in `validate shcd` as a machine-readable exchange for SHCD data.
- Add ability to run CANU in a container, and update Python virtual environment documentation.
- Added `canu generate switch config` to generate switch configuration for Aruba systems.
- Added `canu generate network config` to generate network configuration for Aruba systems.
- Added `canu validate switch config` to compare running switch config to a file for Aruba systems.
- Added `canu validate network config` to compare running network config to files for Aruba systems.
- Updated naming conventions to `canu <verb> switch/network <noun>`
- Added the ability to fully track device slot and port assignments.
- Mountain hardware (CMM, CEC) is now being generated in the switch configurations.
- Fixed multiple templates to match what is on the Aruba switch, these include, UANs, Loopbacks, VLAN interfaces, ACLs.
- Known Limitations:
  - PDUs are not yet properly handled in the generated switch configurations.
  - Switch and SNMP passwords have been removed from generated configurations until the handling code is secure.

### [0.0.5] - 2021-5-14

- Updated license
- Updated the plan-of-record firmware for the 8360 in Shasta 1.4 and 1.5
- Added `config bgp` command to update bgp configuration for a pair of switches.

### [0.0.4] - 2021-05-07

- Added `verify shcd` command to allow verification of SHCD spreadsheets
- Added `verify cabling` command to run verifications on network IPs
- Added additional documentation for each command, added docstring checks to lint tests, and updated testing feedback
- Added `verify shcd-cabling` command to run verifications of SHCD spreadsheets against network IPs
- Added `validate bgp` command to validate spine switch neighbors

### [0.0.3] - 2021-04-16

#### Added

- Cache firmware API calls to canu_cache.yaml file.
- Able to check cabling with LLDP on a switch using the `canu switch cabling` command.
- Cache cabling information to canu_cache.yaml file.
- For the `canu init` command the CSI input now comes from the `sls_input_file.json` instead of the `NMN.yaml` file.
- Able to check cabling with LLDP on the whole network using the `canu network cabling` command.

### [0.0.2] - 2021-03-29

#### Added

- Added ability to initialize CANU by reading IP addresses from the CSI output folder, or from the Shasta SLS API by running `canu init`. The initialization will output the IP addresses to an output file.
- Added ability for the network firmware command to read IPv4 address from a file using the --ips-file flag
- Added the --out flag to the switch firmware and network firmware commands to output to a file.
- Added the --json output to the network firmware command
- Full coverage testing
- Added --version flag
- Docstring checks and improvements

### [0.0.1] - 2021-03-19

#### Added

- Initial release!
- Ability for CANU to get the firmware of a single or multiple Aruba switches
- Standardized the canu.yaml file to show currently supported switch firmware versions.

[unreleased]: https://github.com/Cray-HPE/canu/tree/main 
[1.6.32]: https://github.com/Cray-HPE/canu/tree/1.6.32
[1.6.31]: https://github.com/Cray-HPE/canu/tree/1.6.31
[1.6.30]: https://github.com/Cray-HPE/canu/tree/1.6.30
[1.6.29]: https://github.com/Cray-HPE/canu/tree/1.6.29
[1.6.28]: https://github.com/Cray-HPE/canu/tree/1.6.28
[1.6.27]: https://github.com/Cray-HPE/canu/tree/1.6.27
[1.6.26]: https://github.com/Cray-HPE/canu/tree/1.6.26
[1.6.25]: https://github.com/Cray-HPE/canu/tree/1.6.25
[1.6.24]: https://github.com/Cray-HPE/canu/tree/1.6.24
[1.6.23]: https://github.com/Cray-HPE/canu/tree/1.6.23
[1.6.22]: https://github.com/Cray-HPE/canu/tree/1.6.22
[1.6.21]: https://github.com/Cray-HPE/canu/tree/1.6.21
[1.6.20]: https://github.com/Cray-HPE/canu/tree/1.6.20
[1.6.19]: https://github.com/Cray-HPE/canu/tree/1.6.19
[1.6.18]: https://github.com/Cray-HPE/canu/tree/1.6.18
[1.6.17]: https://github.com/Cray-HPE/canu/tree/1.6.17
[1.6.16]: https://github.com/Cray-HPE/canu/tree/1.6.16
[1.6.15]: https://github.com/Cray-HPE/canu/tree/1.6.15
[1.6.14]: https://github.com/Cray-HPE/canu/tree/1.6.14
[1.6.13]: https://github.com/Cray-HPE/canu/tree/1.6.13
[1.6.12]: https://github.com/Cray-HPE/canu/tree/1.6.12
[1.6.11]: https://github.com/Cray-HPE/canu/tree/1.6.11
[1.6.10]: https://github.com/Cray-HPE/canu/tree/1.6.10
[1.6.9]: https://github.com/Cray-HPE/canu/tree/1.6.9
[1.6.8]: https://github.com/Cray-HPE/canu/tree/1.6.8
[1.6.7]: https://github.com/Cray-HPE/canu/tree/1.6.7
[1.6.6]: https://github.com/Cray-HPE/canu/tree/1.6.6
[1.6.5]: https://github.com/Cray-HPE/canu/tree/1.6.5
[1.6.4]: https://github.com/Cray-HPE/canu/tree/1.6.4
[1.6.3]: https://github.com/Cray-HPE/canu/tree/1.6.3
[1.6.2]: https://github.com/Cray-HPE/canu/tree/1.6.2
[1.6.1]: https://github.com/Cray-HPE/canu/tree/1.6.1
[1.6.0]: https://github.com/Cray-HPE/canu/tree/1.6.0
[1.5.14]: https://github.com/Cray-HPE/canu/tree/1.5.14
[1.5.13]: https://github.com/Cray-HPE/canu/tree/1.5.13
[1.5.12]: https://github.com/Cray-HPE/canu/tree/1.5.12
[1.5.11]: https://github.com/Cray-HPE/canu/tree/1.5.11
[1.5.10]: https://github.com/Cray-HPE/canu/tree/1.5.10
[1.5.9]: https://github.com/Cray-HPE/canu/tree/1.5.9
[1.5.8]: https://github.com/Cray-HPE/canu/tree/1.5.8
[1.5.7]: https://github.com/Cray-HPE/canu/tree/1.5.7
[1.5.6]: https://github.com/Cray-HPE/canu/tree/1.5.6
[1.5.5]: https://github.com/Cray-HPE/canu/tree/1.5.5
[1.5.4]: https://github.com/Cray-HPE/canu/tree/1.5.4
[1.5.3]: https://github.com/Cray-HPE/canu/tree/1.5.3
[1.5.2]: https://github.com/Cray-HPE/canu/tree/1.5.2
[1.5.1]: https://github.com/Cray-HPE/canu/tree/1.5.1
[1.5.0]: https://github.com/Cray-HPE/canu/tree/1.5.0
[1.4.1]: https://github.com/Cray-HPE/canu/tree/1.4.1
[1.4.0]: https://github.com/Cray-HPE/canu/tree/1.4.0
[1.3.5]: https://github.com/Cray-HPE/canu/tree/1.3.5
[1.3.4]: https://github.com/Cray-HPE/canu/tree/1.3.4
[1.3.3]: https://github.com/Cray-HPE/canu/tree/1.3.3
[1.3.2]: https://github.com/Cray-HPE/canu/tree/1.3.2
[1.3.1]: https://github.com/Cray-HPE/canu/tree/1.3.1
[1.3.0]: https://github.com/Cray-HPE/canu/tree/1.3.0
[1.2.10]: https://github.com/Cray-HPE/canu/tree/1.2.10
[1.2.9]: https://github.com/Cray-HPE/canu/tree/1.2.9
[1.2.8]: https://github.com/Cray-HPE/canu/tree/1.2.8
[1.2.7]: https://github.com/Cray-HPE/canu/tree/1.2.7
[1.2.6]: https://github.com/Cray-HPE/canu/tree/1.2.6
[1.2.5]: https://github.com/Cray-HPE/canu/tree/1.2.5
[1.2.4]: https://github.com/Cray-HPE/canu/tree/1.2.4
[1.2.3]: https://github.com/Cray-HPE/canu/tree/1.2.3
[1.2.2]: https://github.com/Cray-HPE/canu/tree/1.2.2
[1.2.1]: https://github.com/Cray-HPE/canu/tree/1.2.1
[1.2.0]: https://github.com/Cray-HPE/canu/tree/1.2.0
[1.1.11]: https://github.com/Cray-HPE/canu/tree/1.1.11
[1.1.10]: https://github.com/Cray-HPE/canu/tree/1.1.10
[1.1.9]: https://github.com/Cray-HPE/canu/tree/1.1.9
[1.1.8]: https://github.com/Cray-HPE/canu/tree/1.1.8
[1.1.7]: https://github.com/Cray-HPE/canu/tree/1.1.7
[1.1.5]: https://github.com/Cray-HPE/canu/tree/1.1.5
[1.1.4]: https://github.com/Cray-HPE/canu/tree/1.1.4
[1.1.3]: https://github.com/Cray-HPE/canu/tree/1.1.3
[1.1.2]: https://github.com/Cray-HPE/canu/tree/1.1.2
[1.1.1]: https://github.com/Cray-HPE/canu/tree/1.1.1
[0.0.6]: https://github.com/Cray-HPE/canu/tree/0.0.6
[0.0.5]: https://github.com/Cray-HPE/canu/tree/0.0.5
[0.0.4]: https://github.com/Cray-HPE/canu/tree/0.0.4
[0.0.3]: https://github.com/Cray-HPE/canu/tree/0.0.3
[0.0.2]: https://github.com/Cray-HPE/canu/tree/0.0.2
[0.0.1]: https://github.com/Cray-HPE/canu/tree/0.0.1
[0.0.6]: https://github.com/Cray-HPE/canu/tree/0.0.6
[0.0.5]: https://github.com/Cray-HPE/canu/tree/0.0.5
[0.0.4]: https://github.com/Cray-HPE/canu/tree/0.0.4
[0.0.3]: https://github.com/Cray-HPE/canu/tree/0.0.3
[0.0.2]: https://github.com/Cray-HPE/canu/tree/0.0.2
[0.0.1]: https://github.com/Cray-HPE/canu/tree/0.0.1

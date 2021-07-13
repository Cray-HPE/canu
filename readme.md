# 🛶 CANU v0.0.5~alpha

CANU (CSM Automatic Network Utility) will float through a new Shasta network and make setup a breeze. Use CANU to check if Aruba switches on a Shasta network meet the firmware version requirements and check their cabling status using LLDP.

CANU reads switch version information from the _canu.yaml_ file in the root directory. This file still needs testing to ensure that switches and firmware versions are labeled properly. Please let us know if something is broken or needs to be updated.

# Table of Contents

**[Installation](#installation)**<br>
**[CANU Initialization](#initialization)**<br>
**[Check Single Switch Firmware](#check-single-switch-firmware)**<br>
**[Check Firmware of Multiple Switches](#check-firmware-of-multiple-switches)**<br>
**[Check Single Switch Cabling](#check-single-switch-cabling)**<br>
**[Check Cabling of Multiple Switches](#check-cabling-of-multiple-switches)**<br>
**[Validate SHCD](#validate-shcd)**<br>
**[Validate Cabling](#validate-cabling)**<br>
**[Validate SHCD and Cabling](#validate-shcd-and-cabling)**<br>
**[Validate BGP](#validate-bgp)**<br>
**[Config BGP](#config-bgp)**<br>
**[Generate Switch Config](#generate-switch-config)**<br>
**[Generate Network Config](#generate-network-config)**<br>
**[Uninstallation](#uninstallation)**<br>
**[Road Map](#road-map)**<br>
**[Testing](#testing)**<br>
**[Changelog](#changelog)**<br>

# Installation and Usage

## Prerequisites

In order to run CANU, both python3 and pip3 need to be installed.

## Installation

To install the development build of CANU type:

```bash
python3 setup.py develop --user
```

If that doesn't work, try:

```bash
pip3 install --editable .
```

## Usage

To run, just type `canu`, it should run and display help. To see a list of commands and arguments, just append `--help`.

When running CANU, the Shasta version is required, you can pass it in with either `-s` or `--shasta` like `canu -s 1.4`.

### Initialization

**[Details](docs/init.md)**<br>

To help make switch setup a breeze. CANU can automatically parse CSI output or the Shasta SLS API for switch IPv4 addresses.

#### CSI Input

- In order to parse CSI output, use the `--csi-folder FOLDER` flag to pass in the folder where the _sls_input_file.json_ file is located.

The _sls_input_file.json_ file is generally stored in one of two places depending on how far the system is in the install process.

- Early in the install process, when running off of the LiveCD the _sls_input_file.json_ file is normally found in the the directory `/var/www/ephemeral/prep/config/SYSTEMNAME/`
- Later in the install process, the _sls_input_file.json_ file is generally in `/mnt/pitdata/prep/SYSTEMNAME/`

To get the switch IP addresses from CSI output, run the command:

```bash
$ canu -s 1.4 init --csi-folder /CSI/OUTPUT/FOLDER/ADDRESS --out output.txt
8 IP addresses saved to output.txt
```

#### SLS API Input

- To parse the Shasta SLS API for IP addresses, ensure that you have a valid token. The token file can either be passed in with the `--auth-token TOKEN_FILE` flag, or it can be automatically read if the environmental variable **SLS_TOKEN** is set. The SLS address is default set to _api-gw-service-nmn.local_, if you are operating on a system with a different address, you can set it with the `--sls-address SLS_ADDRESS` flag.

To get the switch IP addresses from the Shasta SLS API, run the command:

```bash
$ canu -s 1.4 init --auth-token ~./config/cray/tokens/ --sls-address 1.2.3.4 --out output.txt
8 IP addresses saved to output.txt
```

The output file for the `canu init` command is set with the `--out FILENAME` flag.

### Check Single Switch Firmware

**[Details](docs/switch_firmware.md)**<br>

To check the firmware of a single switch run: `canu --shasta 1.4 switch firmware --ip 192.168.1.1 --username USERNAME --password PASSWORD`

```bash
$ canu --shasta 1.4 switch firmware --ip 192.168.1.1 --username USERNAME --password PASSWORD
🛶 - Pass - IP: 192.168.1.1 Hostname:test-switch-spine01 Firmware: GL.10.06.0001
```

### Check Firmware of Multiple Switches

**[Details](docs/network_firmware.md)**<br>

Multiple Aruba switches on a network can be checked for their firmware versions. The IPv4 addresses of the switches can either be entered comma separated, or be read from a file. To enter a comma separated list of IP addresses to the `---ips` flag. To read the IP addresses from a file, make sure the file has one IP address per line, and use the flag like `--ips-file FILENAME` to input the file.

An example of checking the firmware of multiple switches: `canu --shasta 1.4 network firmware --ips 192.168.1.1,192.168.1.2 --username USERNAME --password PASSWORD`

```bash
$ canu --shasta 1.4 network firmware --ips 192.168.1.1,192.168.1.2,192.168.1.3,192.168.1.4 --username USERNAME --password PASSWORD

------------------------------------------------------------------
    STATUS  IP              HOSTNAME            FIRMWARE
------------------------------------------------------------------
 🛶 Pass    192.168.1.1     test-switch-spine01 GL.10.06.0010
 🛶 Pass    192.168.1.2     test-switch-leaf01  FL.10.06.0010
 ❌ Fail    192.168.1.3     test-wrong-version  FL.10.05.0001   Firmware should be in range ['FL.10.06.0001']
 🔺 Error   192.168.1.4


Errors
------------------------------------------------------------------
192.168.1.4     - HTTP Error. Check that this IP is an Aruba switch, or check the username and password

Summary
------------------------------------------------------------------
🛶 Pass - 2 switches
❌ Fail - 1 switches
🔺 Error - 1 switches
GL.10.06.0010 - 1 switches
FL.10.06.0010 - 1 switches
FL.10.05.0010 - 1 switches
```

When using the _network firmware_ commands, the table will show either: 🛶 Pass, ❌ Fail, or 🔺 Error. The switch will **pass** or **fail** based on if the switch firmware matches the _canu.yaml_

### Output to a File

To output the results of the switch firmware or network firmware commands to a file, append the `--out FILENAME` flag

### JSON

To get the JSON output from a single switch, or from multiple switches, make sure to use the `--json` flag. An example json output is below.

```bash
$ canu --shasta 1.4 network firmware --ips 192.168.1.1,192.168.1.2 --username USERNAME --password PASSWORD --json

{
    "192.168.1.1": {
        "status": "Pass",
        "hostname": "test-switch-spine01",
        "platform_name": "8325",
        "firmware": {
            "current_version": "GL.10.06.0010",
            "primary_version": "GL.10.06.0010",
            "secondary_version": "GL.10.05.0020",
            "default_image": "primary",
            "booted_image": "primary",
        },
    },
    "192.168.1.2": {
        "status": "Pass",
        "hostname": "test-switch-leaf01",
        "platform_name": "6300",
        "firmware": {
            "current_version": "FL.10.06.0010",
            "primary_version": "FL.10.06.0010",
            "secondary_version": "FL.10.05.0020",
            "default_image": "primary",
            "booted_image": "primary",
        },
    },
}


```

### Check Single Switch Cabling

**[Details](docs/switch_cabling.md)**<br>
CANU can also use LLDP to check the cabling status of a switch. To check the cabling of a single switch run: `canu --shasta 1.4 switch cabling --ip 192.168.1.1 --username USERNAME --password PASSWORD`

```bash
$ canu --shasta 1.4 switch cabling --ip 192.168.1.1 --username USERNAME --password PASSWORD

Switch: test-switch-spine01 (192.168.1.1)
Aruba 8325
------------------------------------------------------------------------------------------------------------------------------------------
PORT        NEIGHBOR       NEIGHBOR PORT      PORT DESCRIPTION                                      DESCRIPTION
------------------------------------------------------------------------------------------------------------------------------------------
1/1/1   ==>                00:00:00:00:00:01  No LLDP data, check ARP vlan info.                    192.168.1.20:vlan1, 192.168.2.12:vlan2
1/1/3   ==> ncn-test2      00:00:00:00:00:02  mgmt0                                                 Linux ncn-test2
1/1/5   ==> ncn-test3      00:00:00:00:00:03  mgmt0                                                 Linux ncn-test3
1/1/7   ==>                00:00:00:00:00:04  No LLDP data, check ARP vlan info.                    192.168.1.10:vlan1, 192.168.2.9:vlan2
1/1/51  ==> test-spine02   1/1/51                                                                   Aruba JL635A  GL.10.06.0010
1/1/52  ==> test-spine02   1/1/52                                                                   Aruba JL635A  GL.10.06.0010
```

Sometimes when checking cabling using LLDP, the neighbor does not return any information except a MAC address. When that is the case, CANU looks up the MAC in the ARP table and displays the IP addresses and vlan information associated with the MAC.

Entries in the table will be colored based on what they are. Neighbors that have _ncn_ in their name will be colored blue. Neighbors that have a port labeled (not a MAC address), are generally switches and are labeled green. Ports that are duplicated, will be bright white.

### Check Cabling of Multiple Switches

**[Details](docs/network_cabling.md)**<br>

The cabling of multiple Aruba switches on a network can be checked at the same time using LLDP. The IPv4 addresses of the switches can either be entered comma separated, or be read from a file. To enter a comma separated list of IP addresses to the `---ips` flag. To read the IP addresses from a file, make sure the file has one IP address per line, and use the flag like `--ips-file FILENAME` to input the file.

An example of checking the cabling of multiple switches: `canu --shasta 1.4 network cabling --ips 192.168.1.1,192.168.1.2 --username USERNAME --password PASSWORD`

There are two different `--view` options, **switch** and **equipment**.

1. The `--view switch` option displays a table for every switch IP address passed in showing connections. This is the same view as shown in the above example of checking single switch cabling.

2. The `--view equipment` option displays a table for each mac address connection. This means that servers and switches will both display incoming and outgoing connections.

An example of checking the cabling of multiple switches and displaying with the equipment view: `canu --shasta 1.4 network cabling --ips 192.168.1.1,192.168.1.2 --username USERNAME --password PASSWORD --view equipment`

```bash
$ canu --shasta 1.4 network cabling --ips 192.168.1.1,192.168.1.2 --username USERNAME --password PASSWORD --view equipment

sw-spine01 Aruba JL635A  GL.10.06.0010
aa:aa:aa:aa:aa:aa
----------------------------------------------------------------------------------------------------
1/1/1                     <==> sw-spine02      1/1/1  Aruba JL635A  GL.10.06.0010
1/1/3                     ===>                 00:00:00:00:00:00 mgmt1
1/1/4                     ===> ncn-test        bb:bb:bb:bb:bb:bb mgmt1 Linux ncn-test


sw-spine02 Aruba JL635A  GL.10.06.0010
bb:bb:bb:bb:bb:bb
----------------------------------------------------------------------------------------------------
1/1/1                     <==> sw-spine01      1/1/1  Aruba JL635A  GL.10.06.0010


00:00:00:00:00:00
192.168.2.2:vlan3, 192.168.1.2:vlan1
----------------------------------------------------------------------------------------------------
00:00:00:00:00:00 mgmt1   <=== sw-spine01      1/1/3


ncn-test Linux ncn-test2
bb:bb:bb:bb:bb:bb
----------------------------------------------------------------------------------------------------
bb:bb:bb:bb:bb:bb mgmt1   <=== sw-spine01      1/1/4
```

### Validate SHCD

**[Details](docs/validate_shcd.md)**<br>

CANU can be used to validate that an SHCD (SHasta Cabling Diagram) passes basic validation checks.

- The `--architecture / -a` flag is used to set the architecture of the system, either **TDS**, or **Full**.
- Use the `--tabs` flag to select which tabs on the spreadsheet will be included.
- The `--corners` flag is used to input the upper left and lower right corners of the table on each tab of the worksheet. The table should contain the 11 headers: **Source, Rack, Location, Slot, (Blank), Port, Destination, Rack, Location, (Blank), Port**. If the corners are not specified, you will be prompted to enter them for each tab.

To check an SHCD run: `canu -s 1.4 validate shcd -a tds --shcd FILENAME.xlsx --tabs 25G_10G,NMN,HMN --corners I14,S25,I16,S22,J20,T39`

```bash
$ canu -s 1.4 validate shcd -a tds --shcd FILENAME.xlsx --tabs 25G_10G,NMN,HMN --corners I14,S25,I16,S22,J20,T39

SHCD Node Connections
------------------------------------------------------------
0: sw-spine-001 connects to 6 nodes: [1, 2, 3, 4, 5, 6]
1: sw-spine-002 connects to 6 nodes: [0, 2, 3, 4, 5, 6]
2: sw-leaf-bmc-001 connects to 2 nodes: [0, 1]
3: uan001 connects to 2 nodes: [0, 1]
4: ncn-s001 connects to 2 nodes: [0, 1]
5: ncn-w001 connects to 2 nodes: [0, 1]
6: ncn-m001 connects to 2 nodes: [0, 1]

Warnings

Node type could not be determined for the following
------------------------------------------------------------
CAN switch
```

### Validate Cabling

**[Details](docs/validate_cabling.md)**<br>

CANU can be used to validate that network cabling passes basic validation checks.

- The `--architecture / -a` flag is used to set the architecture of the system, either **TDS**, or **Full**.
- To enter a comma separated list of IP addresses to the `---ips` flag. To read the IP addresses from a file, make sure the file has one IP address per line, and use the flag like `--ips-file FILENAME` to input the file.

To validate the cabling run: `canu -s 1.4 validate cabling -a tds --ips 192.168.1.1,192.168.1.2 --username USERNAME --password PASSWORD`

```bash
$ canu -s 1.4 validate cabling -a tds --ips 192.168.1.1,192.168.1.2 --username USERNAME --password PASSWORD

Cabling Node Connections
------------------------------------------------------------
0: sw-spine-001 connects to 10 nodes: [1, 2, 3, 4]
1: ncn-m001 connects to 2 nodes: [0, 4]
2: ncn-w001 connects to 2 nodes: [0, 4]
3: ncn-s001 connects to 2 nodes: [0, 4]
4: sw-spine-002 connects to 10 nodes: [0, 1, 2, 3 ]

Warnings

Node type could not be determined for the following
------------------------------------------------------------
sw-leaf-001
sw-spine-001     1/1/1     ===> aa:aa:aa:aa:aa:aa
sw-spine-001     1/1/2     ===> 1/1/1 CFCANB4S1 Aruba JL479A  TL.10.03.0081
sw-spine-001     1/1/3     ===> 1/1/3 sw-leaf-001 Aruba JL663A  FL.10.06.0010
sw-spine-002     1/1/4     ===> bb:bb:bb:bb:bb:bb
sw-spine-002     1/1/5     ===> 1/1/2 CFCANB4S1 Aruba JL479A  TL.10.03.0081
sw-spine-002     1/1/6     ===> 1/1/6 sw-leaf-001 Aruba JL663A  FL.10.06.0010
Nodes that show up as MAC addresses might need to have LLDP enabled.

The following nodes should be renamed
------------------------------------------------------------
sw-leaf01 should be renamed (could not identify node)
sw-spine01 should be renamed sw-spine-001
sw-spine02 should be renamed sw-spine-002
```

If there are any nodes that cannot be determined or should be renamed, there will be warning tables that show the details.

### Validate SHCD and Cabling

**[Details](docs/validate_shcd_cabling.md)**<br>

CANU can be used to validate an SHCD against the current network cabling.

- The `--architecture / -a` flag is used to set the architecture of the system, either **TDS**, or **Full**.
- Use the `--tabs` flag to select which tabs on the spreadsheet will be included.
- The `--corners` flag is used to input the upper left and lower right corners of the table on each tab of the worksheet. The table should contain the 11 headers: **Source, Rack, Location, Slot, (Blank), Port, Destination, Rack, Location, (Blank), Port**. If the corners are not specified, you will be prompted to enter them for each tab.
- To enter a comma separated list of IP addresses to the `---ips` flag. To read the IP addresses from a file, make sure the file has one IP address per line, and use the flag like `--ips-file FILENAME` to input the file.

To validate an SHCD against the cabling run: `canu -s 1.4 validate shcd-cabling -a tds --shcd FILENAME.xlsx --tabs 25G_10G,NMN --corners I14,S49,I16,S22 --ips 192.168.1.1,192.168.1.2 --username USERNAME --password PASSWORD`

```bash
$ canu -s 1.4 validate shcd-cabling -a tds --shcd FILENAME.xlsx --tabs 25G_10G,NMN --corners I14,S49,I16,S22 --ips 192.168.1.1,192.168.1.2 --username USERNAME --password PASSWORD

====================================================================================================
SHCD
====================================================================================================

SHCD Node Connections
------------------------------------------------------------
0: sw-spine-001 connects to 6 nodes: [1, 2, 3, 4, 5, 6]
1: sw-spine-002 connects to 6 nodes: [0, 2, 3, 4, 5, 6]
2: sw-leaf-bmc-001 connects to 2 nodes: [0, 1]
3: uan001 connects to 2 nodes: [0, 1]
4: ncn-s001 connects to 2 nodes: [0, 1]
5: ncn-w001 connects to 2 nodes: [0, 1]
6: ncn-m001 connects to 2 nodes: [0, 1]

Warnings

Node type could not be determined for the following
------------------------------------------------------------
CAN switch

====================================================================================================
Cabling
====================================================================================================

Cabling Node Connections
------------------------------------------------------------
0: sw-spine-001 connects to 10 nodes: [1, 2, 3, 4]
1: ncn-m001 connects to 2 nodes: [0, 4]
2: ncn-w001 connects to 2 nodes: [0, 4]
3: ncn-s001 connects to 2 nodes: [0, 4]
4: sw-spine-002 connects to 10 nodes: [0, 1, 2, 3 ]

Warnings

Node type could not be determined for the following
------------------------------------------------------------
sw-leaf-001
sw-spine-001     1/1/1     ===> aa:aa:aa:aa:aa:aa
sw-spine-001     1/1/2     ===> 1/1/1 CFCANB4S1 Aruba JL479A  TL.10.03.0081
sw-spine-001     1/1/3     ===> 1/1/3 sw-leaf-001 Aruba JL663A  FL.10.06.0010
sw-spine-002     1/1/4     ===> bb:bb:bb:bb:bb:bb
sw-spine-002     1/1/5     ===> 1/1/2 CFCANB4S1 Aruba JL479A  TL.10.03.0081
sw-spine-002     1/1/6     ===> 1/1/6 sw-leaf-001 Aruba JL663A  FL.10.06.0010
Nodes that show up as MAC addresses might need to have LLDP enabled.

The following nodes should be renamed
------------------------------------------------------------
sw-leaf01 should be renamed (could not identify node)
sw-spine01 should be renamed sw-spine-001
sw-spine02 should be renamed sw-spine-002

====================================================================================================
SHCD vs Cabling
====================================================================================================

SHCD / Cabling Comparison
------------------------------------------------------------
sw-spine-001    : Found in SHCD and on the network, but missing the following connections on the network that were found in the SHCD:
                ['sw-leaf-bmc-001', 'uan001']
sw-spine-002    : Found in SHCD and on the network, but missing the following connections on the network that were found in the SHCD:
                ['sw-leaf-bmc-001', 'uan001']
sw-leaf-bmc-001 : Found in SHCD but not found on the network.
uan001          : Found in SHCD but not found on the network.
```

The output of the `validate shcd-cabling` command will show the results for `validate shcd`, `validate cabling`, and then a comparison of the two results. If there are nodes found on the SHCD, or on the network that are not found in the other one, it will be displayed in _blue_. If a node is found on both the network and in the SHCD, but the connections are not the same, it will be shown in _green_, and the missing connections will be shown.

### Validate BGP

**[Details](docs/validate_bgp.md)**<br>

CANU can be used to validate BGP neighbors. All neighbors of a switch must return status **Established** or the verification will fail.

- To enter a comma separated list of IP addresses to the `---ips` flag. To read the IP addresses from a file, make sure the file has one IP address per line, and use the flag like `--ips-file FILENAME` to input the file.
- The default **asn** is set to _65533_ if it needs to be changed, use the flag `--asn NEW_ASN_NUMBER` to set the new number

If you want to see the individual status of all the neighbors of a switch, use the `--verbose` flag.

To validate BGP run: `canu -s 1.4 validate bgp --ips 192.168.1.1,192.168.1.2 --username USERNAME --password PASSWORD`

```bash
$ canu -s 1.4 validate bgp --ips 192.168.1.1,192.168.1.2 --username USERNAME --password PASSWORD

BGP Neighbors Established
--------------------------------------------------
PASS - IP: 192.168.1.1 Hostname: sw-spine01 
PASS - IP: 192.168.1.2 Hostname: sw-spine01 
```

If any of the spine switch neighbors for a connection other than **Established**, the switch will **FAIL** validation.

If a switch that is not a **spine** switch is tested, it will show in the results table as **SKIP**.

### Config BGP

**[Details](docs/config_bgp.md)**<br>

CANU can be used to configure BGP for a pair of switches.

This command will remove previous configuration (BGP, Prefix Lists, Route Maps), then add prefix lists, create
route maps, and update BGP neighbors, then write it all to the switch memory.

The network and NCN data can be read from one of two sources, the SLS API, or using CSI.

To access SLS, a token must be passed in using the `--auth-token` flag.
Tokens are typically stored in ~./config/cray/tokens/
Instead of passing in a token file, the environmental variable SLS_TOKEN can be used.

To get the network data using CSI, pass in the CSI folder containing the sls_input_file.json file using the `--csi-folder` flag

The sls_input_file.json file is generally stored in one of two places depending on how far the system is in the install process.

- Early in the install process, when running off of the LiveCD the sls_input_file.json file is normally found in the the directory `/var/www/ephemeral/prep/config/SYSTEMNAME/`

- Later in the install process, the sls_input_file.json file is generally in `/mnt/pitdata/prep/SYSTEMNAME/`

To configure BGP run: `canu -s 1.4 config bgp --ips 192.168.1.1,192.168.1.2 --username USERNAME --password PASSWORD`

```bash
$ canu -s 1.4 config bgp --ips 192.168.1.1,192.168.1.2 --username USERNAME --password PASSWORD

BGP Updated
--------------------------------------------------
192.168.1.1
192.168.1.2

```

To print extra details (prefixes, NCN names, IPs), add the `--verbose` flag

### Generate Switch Config

**[Details](docs/switch_config.md)**<br>

CANU can be used to generate switch config.

In order to generate switch config, a valid SHCD must be passed in and system variables must be read in from either CSI output or the SLS API.

#### CSI Input

- In order to parse CSI output, use the `--csi-folder FOLDER` flag to pass in the folder where the _sls_input_file.json_ file is located.

The sls_input_file.json file is generally stored in one of two places depending on how far the system is in the install process.

- Early in the install process, when running off of the LiveCD the sls_input_file.json file is normally found in the the directory `/var/www/ephemeral/prep/config/SYSTEMNAME/`

- Later in the install process, the sls_input_file.json file is generally in `/mnt/pitdata/prep/SYSTEMNAME/`

#### SLS API Input

- To parse the Shasta SLS API for IP addresses, ensure that you have a valid token. The token file can either be passed in with the `--auth-token TOKEN_FILE` flag, or it can be automatically read if the environmental variable **SLS_TOKEN** is set. The SLS address is default set to _api-gw-service-nmn.local_, if you are operating on a system with a different address, you can set it with the `--sls-address SLS_ADDRESS` flag.

#### SHCD Input

- The `--architecture / -a` flag is used to set the architecture of the system, either **TDS**, or **Full**.
- Use the `--tabs` flag to select which tabs on the spreadsheet will be included.
- The `--corners` flag is used to input the upper left and lower right corners of the table on each tab of the worksheet. The table should contain the 11 headers: **Source, Rack, Location, Slot, (Blank), Port, Destination, Rack, Location, (Blank), Port**. If the corners are not specified, you will be prompted to enter them for each tab.

To generate config for a specific switch, a hostname must also be passed in using the `--name HOSTNAME` flag. To output the config to a file, append the `--out FILENAME` flag.

To generate switch config run: `canu -s 1.5 switch config -a full --shcd FILENAME.xlsx --tabs 'INTER_SWITCH_LINKS,NON_COMPUTE_NODES,HARDWARE_MANAGEMENT,COMPUTE_NODES' --corners 'J14,T44,J14,T48,J14,T24,J14,T23' --csi-folder /CSI/OUTPUT/FOLDER/ADDRESS --name SWITCH_HOSTNAME --out FILENAME`

```bash
$ canu -s 1.5 switch config -a full --shcd FILENAME.xlsx --tabs INTER_SWITCH_LINKS,NON_COMPUTE_NODES,HARDWARE_MANAGEMENT,COMPUTE_NODES --corners J14,T44,J14,T48,J14,T24,J14,T23 --csi-folder /CSI/OUTPUT/FOLDER/ADDRESS --name sw-spine-001

hostname sw-spine-001
user admin group administrators password plaintext
bfd
no ip icmp redirect
vrf CAN
vrf keepalive
...

```

### Generate Network Config

**[Details](docs/network_config.md)**<br>

CANU can also generate switch config for all the switches on a network.

In order to generate network config, a valid SHCD must be passed in and system variables must be read in from either CSI output or the SLS API. The instructions are exactly the same as the above **[Generate Switch Config](#generate-switch-config)** except there will not be a hostname and a folder must be specified for config output using the `--folder FOLDERNAME` flag.

To generate switch config run: `canu -s 1.5 network config -a full --shcd FILENAME.xlsx --tabs 'INTER_SWITCH_LINKS,NON_COMPUTE_NODES,HARDWARE_MANAGEMENT,COMPUTE_NODES' --corners 'J14,T44,J14,T48,J14,T24,J14,T23' --csi-folder /CSI/OUTPUT/FOLDER/ADDRESS --folder FOLDERNAME`

```bash
$ canu -s 1.5 network config -a full --shcd FILENAME.xlsx --tabs INTER_SWITCH_LINKS,NON_COMPUTE_NODES,HARDWARE_MANAGEMENT,COMPUTE_NODES --corners J14,T44,J14,T48,J14,T24,J14,T23 --csi-folder /CSI/OUTPUT/FOLDER/ADDRESS --folder switch_config

sw-spine-001 Config Generated
sw-spine-002 Config Generated
sw-leaf-001 Config Generated
sw-leaf-002 Config Generated
sw-leaf-003 Config Generated
sw-leaf-004 Config Generated
sw-cdu-001 Config Generated
sw-cdu-002 Config Generated
sw-leaf-bmc-001 Config Generated

```

## Uninstallation

`pip3 uninstall canu`

# Road Map

CANU is under active development, therefore things are changing on a daily basis. Expect commands to change and tests to fail while CANU trends towards stability.

Currently CANU can check the firmware version of a single Aruba switch, or the firmware version of multiple Aruba switches on the network. CANU can also check the cabling of a single switch using LLDP.

Future versions will allow CANU to check switch configurations and network wiring.

# Testing

To run the full set of tests, linting, and coverage map run:

```bash
$ nox
```

To run just tests run `nox -s tests` or to just run linting use `nox -s lint`. To rerun a session without reinstalling all testing dependencies use the `-rs` flag instead of `-s`.

# Changelog

## [0.0.5~alpha] - 2021-5-14

- Updated license
- Updated the plan-of-record firmware for the 8360 in Shasta 1.4 and 1.5
- Added `config bgp` command to update bgp configuration for a pair of switches.

## [0.0.4] - 2021-05-07

- Added `verify shcd` command to allow verification of SHCD spreadsheets
- Added `verify cabling` command to run verifications on network IPs
- Added additional documentation for each command, added docstring checks to lint tests, and updated testing feedback
- Added `verify shcd-cabling` command to run verifications of SHCD spreadsheets against network IPs
- Added `validate bgp` command to validate spine switch neighbors

## [0.0.3] - 2021-04-16

### Added

- Cache firmware API calls to canu_cache.yaml file.
- Able to check cabling with LLDP on a switch using the `canu switch cabling` command.
- Cache cabling information to canu_cache.yaml file.
- For the `canu init` command the CSI input now comes from the _sls_input_file.json_ instead of the _NMN.yaml_ file.
- Able to check cabling with LLDP on the whole network using the `canu network cabling` command.

## [0.0.2] - 2021-03-29

### Added

- Added ability to initialize CANU by reading IP addresses from the CSI output folder, or from the Shasta SLS API by running `canu init`. The initialization will output the IP addresses to an output file.
- Added ability for the network firmware command to read IPv4 address from a file using the --ips-file flag
- Added the --out flag to the switch firmware and network firmware commands to output to a file.
- Added the --json output to the network firmware command
- Full coverage testing
- Added --version flag
- Docstring checks and improvements

## [0.0.1] - 2021-03-19

### Added

- Initial release!
- Ability for CANU to get the firmware of a single or multiple Aruba switches
- Standardized the canu.yaml file to show currently supported switch firmware versions.

[unreleased]: https://stash.us.cray.com/projects/CSM/repos/canu/compare/commits?targetBranch=refs%2Ftags%2F0.0.4&sourceBranch=refs%2Fheads%2Fmaster&targetRepoId=12732
[0.0.4]: https://stash.us.cray.com/projects/CSM/repos/canu/browse?at=refs%2Ftags%2F0.0.4
[0.0.3]: https://stash.us.cray.com/projects/CSM/repos/canu/browse?at=refs%2Ftags%2F0.0.3
[0.0.2]: https://stash.us.cray.com/projects/CSM/repos/canu/browse?at=refs%2Ftags%2F0.0.2
[0.0.1]: https://stash.us.cray.com/projects/CSM/repos/canu/browse?at=refs%2Ftags%2F0.0.1

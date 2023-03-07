# Initialization

To help make switch setup a breeze. CANU can automatically parse SLS JSON data - including CSI sls_input_file.json output or the Shasta SLS API for switch IPv4 addresses.

## CSI Input

- In order to parse CSI output, use the `--sls-file FILE` flag to pass in the folder where an SLS JSON file is located.

The CSI `sls_input_file.json` file is generally stored in one of two places depending on how far the system is in the install process.

- Early in the install process, when running off of the LiveCD the CSI `sls_input_file.json` file is normally found in the the directory `/var/www/ephemeral/prep/SYSTEMNAME/`
- Later in the install process, the CSI `sls_input_file.json` file is generally in `/mnt/pitdata/prep/SYSTEMNAME/`
- The SLS file can also be obtained from an NCN that's in the k8s cluster by running `cray sls dumpstate list  --format json`
- The switch IPs will be read from the 'NMN' network, if a different network is desired, use the `--network` flag to choose a different one e.g. (CAN, MTL, NMN).

To get the switch IP addresses from CSI output, run the command:

```bash
canu init --sls-file SLS_FILE --out output.txt
```

Potential output:

```text
8 IP addresses saved to output.txt
```

## SLS API Input

- To parse the Shasta SLS API for IP addresses, ensure that you have a valid token. The token file can either be passed in with the `--auth-token TOKEN_FILE` flag, or it can be automatically read if the environmental variable **`SLS_TOKEN`** is set. The SLS address is default set to `api-gw-service-nmn.local`, if you are operating on a system with a different address, you can set it with the `--sls-address SLS_ADDRESS` flag.

To get the switch IP addresses from the Shasta SLS API, run the command:

```bash
canu init --auth-token ~./config/cray/tokens/ --sls-address 1.2.3.4 --out output.txt
```

Potential output:

```text
8 IP addresses saved to output.txt
```

The output file for the `canu init` command is set with the `--out FILENAME` flag.

#  Report Switch Firmware

CANU checks the switch firmware version against the standard in the `canu.yaml` file found in the root directory.

The CSM version is required to determine the firmware to validate against, you can pass it in with `--csm` like `--csm 1.2`.

To check the firmware of a single switch run: `canu report switch firmware --csm 1.2 --ip 192.168.1.1 --username USERNAME --password PASSWORD`

```bash
$ canu report switch firmware --csm 1.2 --ip 192.168.1.1 --username USERNAME --password PASSWORD
🛶 - Pass - IP: 192.168.1.1 Hostname:sw-spine-001 Firmware: GL.10.06.0010
```

# Report Network Firmware

Multiple switches on a network (Aruba, Dell, or Mellanox) can be checked for their firmware versions. The IPv4 addresses of the switches can either be entered comma separated, or be read from a file. To enter a comma separated list of IP addresses to the `---ips` flag. To read the IP addresses from a file, make sure the file has one IP address per line, and use the flag like `--ips-file FILENAME` to input the file.

The CSM version is required to determine the firmware to validate against, you can pass it in with `--csm` like `--csm 1.2`.

An example of checking the firmware of multiple switches: `canu report network firmware --csm 1.2 --ips 192.168.1.1,192.168.1.2 --username USERNAME --password PASSWORD`

```bash
canu report network firmware --csm 1.2 --ips 192.168.1.1,192.168.1.2,192.168.1.3,192.168.1.4 --username USERNAME --password PASSWORD
```

Potential output:

```text
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

When using the _network firmware_ commands, the table will show either: 🛶 Pass, ❌ Fail, or 🔺 Error. The switch will **pass** or **fail** based on if the switch firmware matches the `canu.yaml`.

## Output to a File

To output the results of the switch firmware or network firmware commands to a file, append the `--out FILENAME` flag

## Output to JSON

To get the JSON output from a single switch, or from multiple switches, make sure to use the `--json` flag. An example json output is below.

```bash
canu network firmware --csm 1.2 --ips 192.168.1.1,192.168.1.2 --username USERNAME --password PASSWORD --json
```
           
Potential output:

```json
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

# Report Switch Cabling

CANU can also use LLDP to check the cabling status of a switch. To check the cabling of a single switch run: `canu report switch cabling --ip 192.168.1.1 --username USERNAME --password PASSWORD`

```bash
canu report switch cabling --ip 192.168.1.1 --username USERNAME --password PASSWORD
```

Potential output:

```text
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

# Report Network Cabling

The cabling of multiple switches (Aruba, Dell, or Mellanox) on a network can be checked at the same time using LLDP. The IPv4 addresses of the switches can either be entered comma separated, or be read from a file. To enter a comma separated list of IP addresses to the `---ips` flag. To read the IP addresses from a file, make sure the file has one IP address per line, and use the flag like `--ips-file FILENAME` to input the file.

An example of checking the cabling of multiple switches: `canu report network cabling --ips 192.168.1.1,192.168.1.2 --username USERNAME --password PASSWORD`

There are two different `--view` options, **switch** and **equipment**.

1. The `--view switch` option displays a table for every switch IP address passed in showing connections. This is the same view as shown in the above example of checking single switch cabling.
1. The `--view equipment` option displays a table for each mac address connection. This means that servers and switches will both display incoming and outgoing connections.

An example of checking the cabling of multiple switches and displaying with the equipment view: `canu network cabling --ips 192.168.1.1,192.168.1.2 --username USERNAME --password PASSWORD --view equipment`

```bash
canu report network cabling --ips 192.168.1.1,192.168.1.2 --username USERNAME --password PASSWORD --view equipment
```

Potential output:

```text
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

# Validate SHCD

CANU can be used to validate that an SHCD (SHasta Cabling Diagram) passes basic validation checks.

- The `--architecture / -a` flag is used to set the architecture of the system, either **TDS**, **Full**, or **V1**..
- Use the `--tabs` flag to select which tabs on the spreadsheet will be included.
- The `--corners` flag is used to input the upper left and lower right corners of the table on each tab of the worksheet. The table should contain the 11 headers: **Source, Rack, Location, Slot, (Blank), Port, Destination, Rack, Location, (Blank), Port**. If the corners are not specified, you will be prompted to enter them for each tab.

To check an SHCD run: `canu validate shcd -a tds --shcd FILENAME.xlsx --tabs 25G_10G,NMN,HMN --corners I14,S25,I16,S22,J20,T39`

```bash
canu validate shcd -a tds --shcd FILENAME.xlsx --tabs 25G_10G,NMN,HMN --corners I14,S25,I16,S22,J20,T39
```

Potential output:

```text
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

The SHCD can easily be converted into CCJ by using by using the `--json` flag and outputting to a file by `canu validate shcd --shcd SHCD.xlsx --json --out paddle.json`

# Validate Paddle

CANU can be used to validate that a CCJ (CSM Cabling JSON) passes basic validation checks.

To validate a paddle CCJ run: `canu validate paddle --ccj paddle.json`

```bash
canu validate paddle --ccj paddle.json
```

Potential output:

```text
CCJ Node Connections
------------------------------------------------------------
0: sw-spine-001 connects to 6 nodes: [1, 2, 3, 4, 5, 6]
1: sw-spine-002 connects to 6 nodes: [0, 2, 3, 4, 5, 6]
2: sw-leaf-bmc-001 connects to 2 nodes: [0, 1]
3: uan001 connects to 2 nodes: [0, 1]
4: ncn-s001 connects to 2 nodes: [0, 1]
5: ncn-w001 connects to 2 nodes: [0, 1]
6: ncn-m001 connects to 2 nodes: [0, 1]
```

# Validate Network Cabling

CANU can be used to validate that network cabling passes basic validation checks.

- The `--architecture / -a` flag is used to set the architecture of the system, either **TDS**, **Full**, or **V1**.
- To enter a comma separated list of IP addresses to the `---ips` flag. To read the IP addresses from a file, make sure the file has one IP address per line, and use the flag like `--ips-file FILENAME` to input the file.

To validate the cabling run: `canu validate network cabling -a tds --ips 192.168.1.1,192.168.1.2 --username USERNAME --password PASSWORD`

```bash
canu validate network cabling -a tds --ips 192.168.1.1,192.168.1.2 --username USERNAME --password PASSWORD
```

Potential output:

```text
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

# Validate SHCD and Cabling

CANU can be used to validate an SHCD against the current network cabling.

- The `--csm` flag is used to set the CSM version of the system.
- The `--architecture / -a` flag is used to set the architecture of the system, either **TDS**, **Full**, or **V1**.
- Use the `--tabs` flag to select which tabs on the spreadsheet will be included.
- The `--corners` flag is used to input the upper left and lower right corners of the table on each tab of the worksheet. The table should contain the 11 headers: **Source, Rack, Location, Slot, (Blank), Port, Destination, Rack, Location, (Blank), Port**. If the corners are not specified, you will be prompted to enter them for each tab.
- To enter a comma separated list of IP addresses to the `---ips` flag. To read the IP addresses from a file, make sure the file has one IP address per line, and use the flag like `--ips-file FILENAME` to input the file.

To validate an SHCD against the cabling run: `canu validate shcd-cabling --csm 1.2 -a tds --shcd FILENAME.xlsx --tabs 25G_10G,NMN --corners I14,S49,I16,S22 --ips 192.168.1.1,192.168.1.2 --username USERNAME --password PASSWORD`

```bash
canu validate shcd-cabling --csm 1.2 -a tds --shcd FILENAME.xlsx --tabs 25G_10G,NMN --corners I14,S49,I16,S22 --ips 192.168.1.1,192.168.1.2 --username USERNAME --password PASSWORD
```

Potential output:

```text
====================================================================================================
SHCD vs Cabling
====================================================================================================

ncn-m001
Rack: x3000    Elevation: u14
--------------------------------------------------------------------------------
Port   SHCD                     Cabling
--------------------------------------------------------------------------------
1      sw-spine-001:5           sw-spine-001:5
2      sw-spine-002:5           sw-spine-002:5

ncn-s001
Rack: x3000    Elevation: u15
--------------------------------------------------------------------------------
Port   SHCD                     Cabling
--------------------------------------------------------------------------------
1      sw-spine-001:6           None
2      sw-spine-002:6           None

ncn-w001
Rack: x3000    Elevation: u16
--------------------------------------------------------------------------------
Port   SHCD                     Cabling
--------------------------------------------------------------------------------
1      sw-spine-001:7           sw-spine-001:7
2      sw-spine-002:7           sw-spine-002:7

sw-spine-001
Rack: x3000    Elevation: u17
--------------------------------------------------------------------------------
Port   SHCD                     Cabling
--------------------------------------------------------------------------------
1      sw-spine-002:1           sw-spine-002:1
2      sw-spine-002:2           sw-spine-002:2
3      uan001:pcie-slot1:1      aa:aa:aa:aa:aa:aa Cray, Inc.
5      ncn-m001:pcie-slot1:1    ncn-m001:pcie-slot1:1
6      ncn-s001:pcie-slot1:1    b4:2e:99:aa:bb:cc GIGA-BYTE TECHNOLOGY CO.,LTD.
7      ncn-w001:pcie-slot1:1    ncn-w001:pcie-slot1:1

sw-spine-002
Rack: x3000    Elevation: u18
--------------------------------------------------------------------------------
Port   SHCD                     Cabling
--------------------------------------------------------------------------------
1      sw-spine-001:1           sw-spine-001:1
2      sw-spine-001:2           sw-spine-001:2
3      uan001:pcie-slot1:2      bb:bb:bb:bb:bb:bb Cray, Inc.
5      ncn-m001:pcie-slot1:2    ncn-m001:pcie-slot1:2
6      ncn-s001:pcie-slot1:2    b8:59:9f:aa:bb:cc Mellanox Technologies, Inc.
7      ncn-w001:pcie-slot1:2    ncn-w001:pcie-slot1:2

uan001
Rack: x3000    Elevation: u19
--------------------------------------------------------------------------------
Port   SHCD                     Cabling
--------------------------------------------------------------------------------
1      sw-spine-001:3           None
2      sw-spine-002:3           None


====================================================================================================
SHCD Warnings
====================================================================================================

Warnings

Node type could not be determined for the following
------------------------------------------------------------
Sheet: HMN
Cell: R21      Name: SITE


====================================================================================================
Cabling Warnings
====================================================================================================

Node type could not be determined for the following
------------------------------------------------------------
sw-spine-001     1/1/3     ===> aa:aa:aa:aa:aa:aa Cray, Inc.
sw-spine-002     1/1/3     ===> bb:bb:bb:bb:bb:bb Cray, Inc.
Nodes that show up as MAC addresses might need to have LLDP enabled.
```

The output of the `validate shcd-cabling` command will show a port by port comparison between the devices found in the SHCD and devices found on the network. If there is a difference in what is found connected to a devices port in SHCD and Cabling, the line will be highlighted in red.

# Validate Paddle and Cabling

CANU can be used to validate aCCJ paddle against the current network cabling.

- The `--csm` flag is used to set the CSM version of the system.
- The `--ccj` flag is used to input the CCJ file.
- To enter a comma separated list of IP addresses to the `---ips` flag. To read the IP addresses from a file, make sure the file has one IP address per line, and use the flag like `--ips-file FILENAME` to input the file.

To validate an SHCD against the cabling run: `canu validate paddle-cabling --csm 1.2 --ccj paddle.json --ips 192.168.1.1,192.168.1.2 --username USERNAME --password PASSWORD`

```bash
canu validate paddle-cabling --csm 1.2 --ccj paddle.json --ips 192.168.1.1,192.168.1.2 --username USERNAME --password PASSWORD
```

Potential output:

```text
====================================================================================================
CCJ vs Cabling
====================================================================================================

ncn-m001
Rack: x3000    Elevation: u14
--------------------------------------------------------------------------------
Port   CCJ                      Cabling
--------------------------------------------------------------------------------
1      sw-spine-001:5           sw-spine-001:5
2      sw-spine-002:5           sw-spine-002:5

ncn-s001
Rack: x3000    Elevation: u15
--------------------------------------------------------------------------------
Port   CCJ                      Cabling
--------------------------------------------------------------------------------
1      sw-spine-001:6           None
2      sw-spine-002:6           None

ncn-w001
Rack: x3000    Elevation: u16
--------------------------------------------------------------------------------
Port   CCJ                      Cabling
--------------------------------------------------------------------------------
1      sw-spine-001:7           sw-spine-001:7
2      sw-spine-002:7           sw-spine-002:7

sw-spine-001
Rack: x3000    Elevation: u17
--------------------------------------------------------------------------------
Port   CCJ                      Cabling
--------------------------------------------------------------------------------
1      sw-spine-002:1           sw-spine-002:1
2      sw-spine-002:2           sw-spine-002:2
3      uan001:pcie-slot1:1      aa:aa:aa:aa:aa:aa Cray, Inc.
5      ncn-m001:pcie-slot1:1    ncn-m001:pcie-slot1:1
6      ncn-s001:pcie-slot1:1    b4:2e:99:aa:bb:cc GIGA-BYTE TECHNOLOGY CO.,LTD.
7      ncn-w001:pcie-slot1:1    ncn-w001:pcie-slot1:1

sw-spine-002
Rack: x3000    Elevation: u18
--------------------------------------------------------------------------------
Port   CCJ                      Cabling
--------------------------------------------------------------------------------
1      sw-spine-001:1           sw-spine-001:1
2      sw-spine-001:2           sw-spine-001:2
3      uan001:pcie-slot1:2      bb:bb:bb:bb:bb:bb Cray, Inc.
5      ncn-m001:pcie-slot1:2    ncn-m001:pcie-slot1:2
6      ncn-s001:pcie-slot1:2    b8:59:9f:aa:bb:cc Mellanox Technologies, Inc.
7      ncn-w001:pcie-slot1:2    ncn-w001:pcie-slot1:2

uan001
Rack: x3000    Elevation: u19
--------------------------------------------------------------------------------
Port   CCJ                      Cabling
--------------------------------------------------------------------------------
1      sw-spine-001:3           None
2      sw-spine-002:3           None


====================================================================================================
CCJ  Warnings
====================================================================================================

====================================================================================================
Cabling Warnings
====================================================================================================

Node type could not be determined for the following
------------------------------------------------------------
sw-spine-001     1/1/3     ===> aa:aa:aa:aa:aa:aa Cray, Inc.
sw-spine-002     1/1/3     ===> bb:bb:bb:bb:bb:bb Cray, Inc.
Nodes that show up as MAC addresses might need to have LLDP enabled.
```

The output of the `validate paddle-cabling` command will show a port by port comparison between the devices found in the CCJ and devices found on the network. If there is a difference in what is found connected to a devices port in CCJ and Cabling, the line will be highlighted in red.

# Validate Network BGP

CANU can be used to validate BGP neighbors. All neighbors of a switch must return status **Established** or the verification will fail.

- The default **asn** is set to _65533_ if it needs to be changed, use the flag `--asn NEW_ASN_NUMBER` to set the new number

If you want to see the individual status of all the neighbors of a switch, use the `--verbose` flag.

To validate BGP run: `canu validate network bgp --ips 192.168.1.1,192.168.1.2 --username USERNAME --password PASSWORD`

```bash
canu validate network bgp --username USERNAME --password PASSWORD
```

Potential output:

```text
BGP Neighbors Established
--------------------------------------------------
PASS - IP: 192.168.1.1 Hostname: sw-spine01
PASS - IP: 192.168.1.2 Hostname: sw-spine01
```

If any of the spine switch neighbors for a connection other than **Established**, the switch will **FAIL** validation.

# Generate Switch Config

To see all the lags that are generated, see {doc}`lags <lags>`

CANU can be used to generate switch config.

In order to generate switch config, a valid SHCD or CCJ must be passed in and system variables must be read in from any SLS data, including CSI output or the SLS API.

## CSI Input

- In order to parse CSI output, use the `--sls-file FILE` flag to pass in the folder where the `sls_file.json` file is located.

The sls_input_file.json file is generally stored in one of two places depending on how far the system is in the install process.

- Early in the install process, when running off of the LiveCD the sls_input_file.json file is normally found in the the directory `/var/www/ephemeral/prep/SYSTEMNAME/`

- Later in the install process, the sls_input_file.json file is generally in `/mnt/pitdata/prep/SYSTEMNAME/`

## SLS API Input

- To parse the Shasta SLS API for IP addresses, ensure that you have a valid token. The token file can either be passed in with the `--auth-token TOKEN_FILE` flag, or it can be automatically read if the environmental variable **SLS_TOKEN** is set. The SLS address is default set to _api-gw-service-nmn.local_, if you are operating on a system with a different address, you can set it with the `--sls-address SLS_ADDRESS` flag.

## Paddle / CCJ Input

- The `--csm` flag is used to set the CSM version of the system.
- The `--ccj` flag is used to input the CCJ file.

To generate switch config run: `canu generate switch config --csm 1.2 --ccj paddle.json --sls-file SLS_FILE --name SWITCH_HOSTNAME --out FILENAME`

## SHCD Input

- The `--csm` flag is used to set the CSM version of the system.
- The `--architecture / -a` flag is used to set the architecture of the system, either **TDS**, **Full**, or **V1**..
- Use the `--tabs` flag to select which tabs on the spreadsheet will be included.
- The `--corners` flag is used to input the upper left and lower right corners of the table on each tab of the worksheet. The table should contain the 11 headers: **Source, Rack, Location, Slot, (Blank), Port, Destination, Rack, Location, (Blank), Port**. If the corners are not specified, you will be prompted to enter them for each tab.

To generate config for a specific switch, a hostname must also be passed in using the `--name HOSTNAME` flag. To output the config to a file, append the `--out FILENAME` flag.

To generate switch config run: `canu generate switch config --csm 1.2 -a full --shcd FILENAME.xlsx --tabs 'INTER_SWITCH_LINKS,NON_COMPUTE_NODES,HARDWARE_MANAGEMENT,COMPUTE_NODES' --corners 'J14,T44,J14,T48,J14,T24,J14,T23' --sls-file SLS_FILE --name SWITCH_HOSTNAME --out FILENAME`

```bash
canu generate switch config --csm 1.2 -a full --shcd FILENAME.xlsx --tabs INTER_SWITCH_LINKS,NON_COMPUTE_NODES,HARDWARE_MANAGEMENT,COMPUTE_NODES --corners J14,T44,J14,T48,J14,T24,J14,T23 --sls-file SLS_FILE --name sw-spine-001
```

Potential output:

```text
hostname sw-spine-001
user admin group administrators password plaintext
bfd
no ip icmp redirect
vrf CAN
vrf keepalive
...
```

## Generate Switch Configs Including Custom Configurations

Pass in a switch config file that CANU will inject into the generated config. A use case would be to add custom site connections.
This config file will overwrite previously generate config.

The `custom-config` file type is YAML and a single file can be used for multiple switches. You will need to specify the switch name and what config inject.  The `custom-config` feature is using the hierarchical configuration library, documentation can be found here <https://netdevops.io/hier_config/>.

custom config file examples

Aruba

```yaml
sw-spine-001:  |
    ip route 0.0.0.0/0 10.103.15.185
    interface 1/1/36
        no shutdown
        ip address 10.103.15.186/30
        exit
    system interface-group 3 speed 10g
    interface 1/1/2
        no shutdown
        mtu 9198
        description sw-spine-001:16==>ion-node
        no routing
        vlan access 7
        spanning-tree bpdu-guard
        spanning-tree port-type admin-edge
sw-spine-002:  |
    ip route 0.0.0.0/0 10.103.15.189
    interface 1/1/36
        no shutdown
        ip address 10.103.15.190/30
        exit
    system interface-group 3 speed 10g
sw-leaf-bmc-001:  |
    interface 1/1/20
        no routing
        vlan access 4
        spanning-tree bpdu-guard
        spanning-tree port-type admin-edge
```

Mellanox/Dell

```yaml
sw-spine-001:  |
    interface ethernet 1/1 speed 10G force
    interface ethernet 1/1 description "sw-spine02-1/16"
    interface ethernet 1/1 no switchport force
    interface ethernet 1/1 ip address 10.102.255.14/30 primary
    interface ethernet 1/1 dcb priority-flow-control mode on force
    ip route vrf default 0.0.0.0/0 10.102.255.13
sw-spine-002:  |
    interface ethernet 1/16 speed 10G force
    interface ethernet 1/16 description "sw-spine01-1/16"
    interface ethernet 1/16 no switchport force
    interface ethernet 1/16 ip address 10.102.255.34/30 primary
    interface ethernet 1/16 dcb priority-flow-control mode on force
    ip route vrf default 0.0.0.0/0 10.102.255.33
sw-leaf-bmc-001:  |
    interface ethernet1/1/12
      description sw-leaf-bmc-001:12==>cn003:2
      no shutdown
      switchport access vlan 4
      mtu 9216
      flowcontrol receive off
      flowcontrol transmit off
      spanning-tree bpduguard enable
      spanning-tree port type edge
    interface vlan7
        description CMN
        no shutdown
        ip vrf forwarding Customer
        mtu 9216
        ip address 10.102.4.100/25
        ip access-group cmn-can in
        ip access-group cmn-can out
        ip ospf 2 area 0.0.0.0
```

To generate switch configuration with custom config injection.

```bash
canu generate switch config --csm 1.2 -a full --shcd FILENAME.xlsx --tabs INTER_SWITCH_LINKS,NON_COMPUTE_NODES,HARDWARE_MANAGEMENT,COMPUTE_NODES --corners J14,T44,J14,T48,J14,T24,J14,T23 --sls-file SLS_FILE --name sw-spine-001 --custom-config CUSTOM_CONFIG_FILE.yaml
```

## Generate Switch Config while preserving LAG #s

This option allows you to generate swtich configs while preserving the lag #s of the previous running config.

The use case for this is if you have a running system and you don't want to take an outage to renumber the LAGs.

It requires a folder with the config/s backed up.

The recommended way to back these configs up is with `canu backup`

```
canu generate switch config -a v1 --csm 1.0 --ccj ccj.json --sls-file sls_input_file.json --name sw-spine-001 --preserve ../backup_configs/
```

# Generate Network Config

To see all the lags that are generated, see {doc}`lags <lags>`

CANU can also generate switch config for all the switches on a network.

In order to generate network config, a valid SHCD or CCJ must be passed in and system variables must be read in from either CSI output or the SLS API. The instructions are exactly the same as the above except there will not be a hostname and a folder must be specified for config output using the `--folder FOLDERNAME` flag.

To generate switch config from a CCJ paddle run: `canu generate network config --csm 1.2 --ccj paddle.json --sls-file SLS_FILE --folder FOLDERNAME`

To generate switch config from SHCD run: `canu generate network config --csm 1.2 -a full --shcd FILENAME.xlsx --tabs 'INTER_SWITCH_LINKS,NON_COMPUTE_NODES,HARDWARE_MANAGEMENT,COMPUTE_NODES' --corners 'J14,T44,J14,T48,J14,T24,J14,T23' --sls-file SLS_FILE --folder FOLDERNAME`

```bash
canu generate network config --csm 1.2 -a full --shcd FILENAME.xlsx --tabs INTER_SWITCH_LINKS,NON_COMPUTE_NODES,HARDWARE_MANAGEMENT,COMPUTE_NODES --corners J14,T44,J14,T48,J14,T24,J14,T23 --sls-file SLS_FILE --folder switch_config
```

Potential output:

```text
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

## Generate Network Config With Custom Config Injection

This option allows extension and maintenance of switch configurations beyond plan-of-record. A YAML file expresses custom configurations across the network and these configurations are merged with the plan-of-record configurations.

WARNING: Extreme diligence should be used applying custom configurations which override plan-of-record generated configurations. Custom configurations will overwrite generated configurations! Override/overwrite is by design to support and document cases where site-interconnects demand "nonstandard" configurations or a bug must be worked around.

To generate network configuration with custom config injection run

```bash
canu generate network config --csm 1.2 -a full --shcd FILENAME.xlsx --tabs INTER_SWITCH_LINKS,NON_COMPUTE_NODES,HARDWARE_MANAGEMENT,COMPUTE_NODES --corners J14,T44,J14,T48,J14,T24,J14,T23 --sls-file SLS_FILE --folder switch_config --custom-config CUSTOM_CONFIG_FILE.yaml
```

## Generate Network Config while preserving LAG #s

This option allows you to generate swtich configs while preserving the lag #s of the previous running config.

The use case for this is if you have a running system and you don't want to take an outage to renumber the LAGs.

It requires a folder with the config/s backed up.

The recommended way to back these configs up is with `backup network`

```bash
canu generate network config --csm 1.0 -a full --shcd FILENAME.xlsx --tabs INTER_SWITCH_LINKS,NON_COMPUTE_NODES,HARDWARE_MANAGEMENT,COMPUTE_NODES --corners J14,T44,J14,T48,J14,T24,J14,T23 --sls-file SLS_FILE --folder switch_config --preserve FOLDER_WITH_SWITCH_CONFIGS
```

# Validate Switch Config

After config has been generated, CANU can validate the generated config against running switch config. The running config can be from either an IP address, or a config file.

- To get running config from an IP address, use the flags `--ip 192.168.1.1 --username USERNAME --password PASSWORD`.
- To get running config from a file, use the flag `--running RUNNING_CONFIG.cfg` instead.

After running the `validate switch config` command, you will be shown a line by line comparison of the currently running switch config against the config file that was passed in. You will also be given a list of remediation commands that can be typed into the switch to get the running config to match the config file. There will be a summary table at the end highlighting the most important differences between the configs.

- Lines that are red and start with a `-` are in the running config, but not in the config file
- Lines that are green and start with a `+` are not in the running config, but are in the config file
- Lines that are blue and start with a `?` are attempting to point out specific line differences

To validate switch config run: `canu validate switch config --ip 192.168.1.1 --username USERNAME --password PASSWORD --generated SWITCH_CONFIG.cfg`

```bash
canu validate switch config --ip 192.168.1.1 --generated sw-spine-001.cfg
```

Potential output:

```text
hostname sw-spine-001
- ntp server 192.168.1.10
?                       ^
+ ntp server 192.168.1.16
?                       ^
  vlan 1
  vlan 2
-     name RVR_NMN
?          ----
+     name NMN
      apply access-list ip nmn-hmn in
      apply access-list ip nmn-hmn out
...

Switch: sw-leaf-001 (192.168.1.1)
Differences
-------------------------------------------------------------------------
In Generated Not In Running (+)     |  In Running Not In Generated (-)
-------------------------------------------------------------------------
Total Additions:                 7  |  Total Deletions:                 7
Hostname:                        1  |  Hostname:                        1
Interface:                       2  |  Interface:                       1
Interface Lag:                   1  |  Interface Lag:                   2
Spanning Tree:                   2  |  Spanning Tree:                   3
Router:                          1  |
```

# Validate Network Config

Aruba support only.

The `validate network config` command works almost the same as the above `validate switch config` command. There are three options for passing in the running config:

- A comma separated list of ips using `--ips 192.168.1.1,192.168.1.`
- A file of ip addresses, one per line using the flag `--ips-file ips.txt`
- A directory containing the running configuration `--running RUNNING/CONFIG/DIRECTORY`

A directory of generated config files will also need to be passed in using `--generated GENERATED/CONFIG/DIRECTORY`. There will be a summary table for each switch highlighting the most important differences between the running switch config and the generated config files.

To validate switch config run: `canu validate network config --ips-file ips.txt --username USERNAME --password PASSWORD --generated /CONFIG/FOLDER`

```bash
canu validate network config --csm 1.2 --ips-file ips.txt --generated /CONFIG/FOLDER
```

Potential output:

```text
Switch: sw-leaf-001 (192.168.1.1)
Differences
-------------------------------------------------------------------------
In Generated Not In Running (+)     |  In Running Not In Generated (-)
-------------------------------------------------------------------------
Total Additions:                 7  |  Total Deletions:                 7
Hostname:                        1  |  Hostname:                        1
Interface:                       2  |  Interface:                       1
Interface Lag:                   1  |  Interface Lag:                   2
Spanning Tree:                   2  |  Spanning Tree:                   3
Router:                          1  |

Switch: sw-spine-001 (192.168.1.2)
Differences
-------------------------------------------------------------------------
In Generated Not In Running (+)     |  In Running Not In Generated (-)
-------------------------------------------------------------------------
Total Additions:                 3  |  Total Deletions:                 2
Interface:                       2  |  Interface:                       1
Interface Lag:                   1  |

...

Errors
----------------------------------------------------------------------------------------------------
192.168.1.3      - Timeout error connecting to switch 192.168.1.3, check the entered username, IP address and password.
```

## File Output and JSON

To output the results of the config validation command to a file, append the `--out FILENAME` flag. To get the results as JSON, use the `--json` flag.

# Cache

There are several commands to help with the canu cache:

- `canu cache location` will tell you the folder where your cache is located
- `canu cache print` will print a colored version of your cache to the screen
- `canu cache delete` will delete your cache file, the file will be created again on the next canu command

# Test The Network

CANU has the ability to run a set of tests against all of the switches in the management network.
It is utilizing the nornir automation framework and additional nornir plugins to do this.

More info can be found at

- <https://nornir.tech/2021/08/06/testing-your-network-with-nornir-testsprocessor/>
- <https://github.com/nornir-automation/nornir>
- <https://github.com/dmulyalin/salt-nornir>

Required Input
You can either use an SLS file or pull the SLS file from the API-Gateway using a token.

- `--sls-file`
- `--auth-token`

Options

- `--log` outputs the nornir debug logs
- `--network [HMN|CMN]` This gives the user the ability to connect to the switches over the CMN.  This allows the use of this tool from outside the Mgmt Network.  The default network used is the HMN.
- `--json` outputs the results in json format.
- `--password` prompts if password is not entered
- `--username` defaults to admin

## Adding tests

Additional tests can be easily added by updating the .yaml file at `canu/test/*/test_suite.yaml`
More information on tests and how to write them can be found at <https://nornir.tech/2021/08/06/testing-your-network-with-nornir-testsprocessor/>

Example test

```yaml
- name: Software version test
  task: show version
  test: contains
  pattern: "10.08.1021"
  err_msg: Software version is wrong
  device:
    - cdu
    - leaf
    - leaf-bmc
    - spine
```

This test logs into the cdu, leaf, leaf-bmc, and spine switches and runs the command `show version` and checks that `10.09.0010` is in the output.  If it's not the test fails.

# Backup Network

Canu can backup the running configurations for switches in the management network.
It backs up the entire switch inventory from SLS by defualt, if you want to backup just one switch use the `--name` flag.

Required Input
You can either use an SLS file or pull the SLS file from the API-Gateway using a token.

- `--sls-file`
- `--folder` "Folder to store running config files"

Options

- `--log` outputs the nornir debug logs
- `--network [HMN|CMN]` This gives the user the ability to connect to the switches over the CMN.  This allows the use of this tool from outside the Mgmt Network.  The default network used is the HMN.
- `--password` prompts if password is not entered
- `--username` defaults to admin
- `--unsanitized` Retains sensitive data such as passwords and SNMP credentials.  The default is to sanitize the config.
- `--name` The name of the switch that you want to back up. e.g. 'sw-spine-001'

Example

```bash
canu backup network --sls-file ./sls_input_file.json --network CMN --folder ./ --unsanitized
```

Potential output:

```text
Running Configs Saved
---------------------
sw-spine-001.cfg
sw-spine-002.cfg
sw-leaf-001.cfg
sw-leaf-002.cfg
sw-leaf-003.cfg
sw-leaf-004.cfg
sw-leaf-bmc-001.cfg
sw-leaf-bmc-002.cfg
sw-cdu-001.cfg
sw-cdu-002.cfg
```

# Send Command

Canu can send commands to the switches via the CLI.
This is primarily used for `show` commands since we do not elevate to configuration mode.


You can either use an SLS file or pull the SLS file from the API-Gateway using a token.
- `--sls-file`
- `--log` outputs the nornir debug logs
- `--network [HMN|CMN]` This gives the user the ability to connect to the switches over the CMN.  This allows the use of this tool from outside the Mgmt Network.  The default network used is the HMN.
- `--command` command to send to the switch/switches.
- `--password` prompts if password is not entered
- `--username` defaults to admin
- `--name` The name of the switch that you want to back up. e.g. 'sw-spine-001'

Examples

  ```bash
  canu send command --sls-file ./sls_input_file.json --network cmn --command "show banner exec" --name sw-spine-001
  -netmiko_send_command************************************************************
  * sw-spine-001 ** changed : False **********************************************
  vvvv netmiko_send_command ** changed : False vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv INFO
  ###############################################################################
  # CSM version:  1.2
  # CANU version: 1.3.2
  ###############################################################################

  ^^^^ END netmiko_send_command ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  ```

  ```bash
  canu send command --command 'show version | include "Version      :"'
  \netmiko_send_command************************************************************
  * sw-leaf-bmc-001 ** changed : False *******************************************
  vvvv netmiko_send_command ** changed : False vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv INFO
  Version      : FL.10.09.0010                                                 
  ^^^^ END netmiko_send_command ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  * sw-spine-001 ** changed : False **********************************************
  vvvv netmiko_send_command ** changed : False vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv INFO
  Version      : GL.10.09.0010                                                 
  ^^^^ END netmiko_send_command ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  * sw-spine-002 ** changed : False **********************************************
  vvvv netmiko_send_command ** changed : False vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv INFO
  Version      : GL.10.09.0010                                                 
  ^^^^ END netmiko_send_command ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  ```

# Report Network Version

Canu reports the version of configuration on the switch.  It reads the exec baner of all the switches and outputs to the screen.

Options

- `--sls-file`
- `--network [HMN|CMN]` This gives the user the ability to connect to the switches over the CMN.  This allows the use of this tool from outside the Mgmt Network.  The default network used is the HMN.
- `--password` prompts if password is not entered
- `--username` defaults to admin

Example

  ```console
  canu report network version --sls-file ../sls_input_file.json --network cmn
  Password: 
  SWITCH            CANU VERSION      CSM VERSION
  sw-spine-001      1.5.12            1.2  
  sw-spine-002      1.5.12            1.2  
  sw-leaf-bmc-001   1.5.12            1.2
  ```

```bash
canu send command --command 'show version | include "Version      :"'
\netmiko_send_command************************************************************
* sw-leaf-bmc-001 ** changed : False *******************************************
vvvv netmiko_send_command ** changed : False vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv INFO
Version      : FL.10.09.0010
^^^^ END netmiko_send_command ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
* sw-spine-001 ** changed : False **********************************************
vvvv netmiko_send_command ** changed : False vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv INFO
Version      : GL.10.09.0010
^^^^ END netmiko_send_command ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
* sw-spine-002 ** changed : False **********************************************
vvvv netmiko_send_command ** changed : False vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv INFO
Version      : GL.10.09.0010
^^^^ END netmiko_send_command ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
```

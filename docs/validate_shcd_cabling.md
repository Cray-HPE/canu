# Validate SHCD and Cabling

CANU can be used to validate an SHCD against the current network cabling.

- The `--architecture / -a` flag is used to set the architecture of the system, either **TDS**, or **Full**.
- Use the `--tabs` flag to select which tabs on the spreadsheet will be included.
- The `--corners` flag is used to input the upper left and lower right corners of the table on each tab of the worksheet. The table should contain the 11 headers: **Source, Rack, Location, Slot, (Blank), Port, Destination, Rack, Location, (Blank), Port**. If the corners are not specified, you will be prompted to enter them for each tab.
- To enter a comma separated list of IP addresses to the `---ips` flag. To read the IP addresses from a file, make sure the file has one IP address per line, and use the flag like `--ips-file FILENAME` to input the file.

## Example

### Validate SHCD and Cabling

To validate an SHCD against the cabling run: `canu validate shcd-cabling -a tds --shcd FILENAME.xlsx --tabs 25G_10G,NMN --corners I14,S49,I16,S22 --ips 192.168.1.1,192.168.1.2 --username USERNAME --password PASSWORD`

```bash
$ canu validate shcd-cabling -a tds --shcd FILENAME.xlsx --tabs 25G_10G,NMN --corners I14,S49,I16,S22 --ips 192.168.1.1,192.168.1.2 --username USERNAME --password PASSWORD

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

![](images/canu_validate_shcd_cabling.png)

The output of the `validate shcd-cabling` command will show the results for `validate shcd`, `validate cabling`, and then a comparison of the two results. If there are nodes found on the SHCD, or on the network that are not found in the other one, it will be displayed in _blue_. If a node is found on both the network and in the SHCD, but the connections are not the same, it will be shown in _green_, and the missing connections will be shown.

## Flags

| Option                | Description                                                                |
| --------------------- | -------------------------------------------------------------------------- |
| `-a / --architecture` | Shasta architecture ("Full", or "TDS")                                     |
| `--shcd`              | SHCD File                                                                  |
| `--tabs`              | The tabs on the SHCD file to check, e.g. 10G_25G_40G_100G,NMN,HMN.         |
| `--corners`           | The corners on each tab, comma separated e.g. 'J37,U227,J15,T47,J20,U167'. |
| `--ips`               | Comma separated list of IPv4 addresses of switches                         |
| `--ips-file`          | File with one IPv4 address per line                                        |
| `--username`          | Switch username                                                            |
| `--password`          | Switch password                                                            |
| `--log`               | Level of logging. ("DEBUG", "INFO", "WARNING", "ERROR")                    |

---

**[Back To Readme](/readme.md)**<br>

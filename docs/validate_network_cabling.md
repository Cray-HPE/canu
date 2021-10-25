# Validate Network Cabling

CANU can be used to validate that network cabling passes basic validation checks.

- The `--architecture / -a` flag is used to set the architecture of the system, either **TDS**, or **Full**.
- To enter a comma separated list of IP addresses to the `---ips` flag. To read the IP addresses from a file, make sure the file has one IP address per line, and use the flag like `--ips-file FILENAME` to input the file.

## Example

### Validate Network Cabling

To validate the cabling run: `canu validate network cabling -a tds --ips 192.168.1.1,192.168.1.2 --username USERNAME --password PASSWORD`

```bash
$ canu validate network cabling -a tds --ips 192.168.1.1,192.168.1.2 --username USERNAME --password PASSWORD

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

## Flags

| Option                | Description                                             |
| --------------------- | ------------------------------------------------------- |
| `-a / --architecture` | CSM architecture ("Full", or "TDS")                     |
| `--ips`               | Comma separated list of IPv4 addresses of switches      |
| `--ips-file`          | File with one IPv4 address per line                     |
| `--username`          | Switch username                                         |
| `--password`          | Switch password                                         |
| `--log`               | Level of logging. ("DEBUG", "INFO", "WARNING", "ERROR") |

---

**[Back To Readme](/readme.md)**<br>

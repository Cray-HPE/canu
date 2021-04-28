# Network Cabling

Report the cabling of all Aruba switches (API v10.04) on the network by using LLDP.

To check out the LLDP neighbor status of switches and their neighboring devices on the network either pass in a comma separated list of IP addresses using the `--ips` option or pass in a file of IP addresses with one address per line using the `--ips-file` option.

There are three different connection types that will be shown in the results.

1. '===>' Outbound connections

2. '<===' Inbound connections

3. '<==>' Bi-directional connections

There are two different `--view` options, `switch` and `equipment`.

1. The `--view switch` option displays a table for every switch IP address passed in showing connections.

2. The `--view equipment` option displays a table for each mac address connection. This means that servers
   and switches will both display incoming and outgoing connections.

If the neighbor name is not in LLDP, the IP and vlan information are displayed by looking up the MAC address in the ARP table.

If there is a duplicate port, the duplicates will be highlighted in **bright white**.

Ports highlighted in **blue** contain the string "ncn" in the hostname.

Ports are highlighted in **green** when the port name is set with the interface name.

## Examples

### 1. Network Cabling `--view switch` (default view)

To check the cabling of multiple switches run: `canu --shasta 1.4 network cabling --ips 192.168.1.1,192.168.1.2 --username USERNAME --password PASSWORD`. Or to load IP addresses from a file run: `canu --shasta 1.4 network cabling --ips-file ip_file.txt --username USERNAME --password PASSWORD`

```bash
$ canu --shasta 1.4 network cabling --ips 192.168.1.1,192.168.1.2 --username USERNAME --password PASSWORD

Switch: sw-test01 (192.168.1.1)
Aruba X86-64
----------------------------------------------------------------------------------------------------------------------------------------
PORT        NEIGHBOR       NEIGHBOR PORT      PORT DESCRIPTION                                      DESCRIPTION
----------------------------------------------------------------------------------------------------------------------------------------
1/1/1   ==> sw-test02      1/1/1                                                                    Test switch description
1/1/2   ==> sw-test02      1/1/2                                                                    Test switch2 description
1/1/3   ==>                00:00:00:00:00:00  No LLDP data, check ARP vlan info.                    192.168.1.2:vlan1, 192.168.2.2:vlan3
1/1/4   ==> ncn-test       cc:cc:cc:cc:cc:cc  mgmt1                                                 NCN description


Switch: sw-test02 (192.168.1.2)
Aruba X86-64
----------------------------------------------------------------------------------------------------------------------------------------
PORT        NEIGHBOR       NEIGHBOR PORT      PORT DESCRIPTION                                      DESCRIPTION
----------------------------------------------------------------------------------------------------------------------------------------
1/1/1   ==> sw-test01      1/1/1                                                                    Test switch description
```

### 2. Network Cabling `--view equipment`

An example of checking the cabling of multiple switches and displaying with the equipment view: `canu --shasta 1.4 network cabling --ips 192.168.1.1,192.168.1.2 --username USERNAME --password PASSWORD --view equipment`

```bash
$ canu --shasta 1.4 network cabling --ips 192.168.1.1,192.168.1.2 --username USERNAME --password PASSWORD --view equipment

sw-test01 Test switch description
aa:aa:aa:aa:aa:aa
----------------------------------------------------------------------------------------------------
1/1/1                     ===> sw-test02       1/1/1  Test switch description
1/1/2                     ===> sw-test02       1/1/2  Test switch description
1/1/3                     ===>                 00:00:00:00:00:00
1/1/4                     ===> ncn-test        cc:cc:cc:cc:cc:cc mgmt1 NCN description


sw-test02 Test switch description
bb:bb:bb:bb:bb:bb
----------------------------------------------------------------------------------------------------
1/1/1                     <=== sw-test01       1/1/1
1/1/2                     <=== sw-test01       1/1/2


00:00:00:00:00:00
192.168.1.2:vlan1, 192.168.2.2:vlan3
----------------------------------------------------------------------------------------------------
00:00:00:00:00:00         <=== sw-test01       1/1/3


ncn-test NCN description
cc:cc:cc:cc:cc:cc
----------------------------------------------------------------------------------------------------
cc:cc:cc:cc:cc:cc mgmt1   <=== sw-test01       1/1/4
```

### File Out

The network cabling command can also be run with the `--out FILENAME` flag to output the results to a file.

## Flags

| Option       | Description                                          |
| ------------ | ---------------------------------------------------- |
| `--ips`      | Switch IPv4 address                                  |
| `--ips-file` | File with one IPv4 address per line                  |
| `--username` | Switch username                                      |
| `--password` | Switch password                                      |
| `--out`      | Name of the output file                              |
| `--view`     | View of the cabling results, `switch` or `equipment` |

---

**[Back To Readme](/readme.md)**<br>

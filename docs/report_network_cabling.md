# Report Network Cabling

## canu report network cabling

Report the cabling of all switches (Aruba, Dell, or Mellanox) on the network by using LLDP.

Pass in either a comma separated list of IP addresses using the –ips option

OR

Pass in a file of IP addresses with one address per line.

There are three different connection types that will be shown in the results.


1. ‘===>’ Outbound connections


2. ‘<===’ Inbound connections


3. ‘<==>’ Bi-directional connections

There are two different ‘–view’ options, ‘switch’ and ‘equipment’.


1. The ‘–view switch’ option displays a table for every switch IP address passed in showing connections.

2. The ‘–view equipment’ option displays a table for each mac address connection. This means that servers
and switches will both display incoming and outgoing connections.

If the neighbor name is not in LLDP, the IP and vlan information are displayed
by looking up the MAC address in the ARP table and mac address table.

If there is a duplicate port, the duplicates will be highlighted in ‘bright white’.

Ports highlighted in ‘blue’ contain the string “ncn” in the hostname.

Ports are highlighted in ‘green’ when the port name is set with the interface name.

```shell
canu report network cabling [OPTIONS]
```

### Options


### --ips( <ips>)
Comma separated list of IPv4 addresses of switches


### --ips-file( <ips_file>)
File with one IPv4 address per line


### --username( <username>)
Switch username


* **Default**

    `admin`



### --password( <password>)
Switch password


### --out( <out>)
Output results to a file


### --view( <view>)
View of the cabling results.


* **Default**

    `switch`



* **Options**

    switch | equipment



### --log( <log_>)
Level of logging.


* **Options**

    DEBUG | INFO | WARNING | ERROR


## Examples

### 1. Network Cabling `--view switch` (default view)

To check the cabling of multiple switches run: `canu report network cabling --ips 192.168.1.1,192.168.1.2 --username USERNAME --password PASSWORD`. Or to load IP addresses from a file run: `canu report network cabling --ips-file ip_file.txt --username USERNAME --password PASSWORD`

```bash
$ canu report network cabling --ips 192.168.1.1,192.168.1.2 --username USERNAME --password PASSWORD

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

An example of checking the cabling of multiple switches and displaying with the equipment view: `canu report network cabling --ips 192.168.1.1,192.168.1.2 --username USERNAME --password PASSWORD --view equipment`

```bash
$ canu report network cabling --ips 192.168.1.1,192.168.1.2 --username USERNAME --password PASSWORD --view equipment

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

The cabling of multiple switches (Aruba, Dell, or Mellanox) on a network can be checked at the same time using LLDP. The IPv4 addresses of the switches can either be entered comma separated, or be read from a file. To enter a comma separated list of IP addresses to the `---ips` flag. To read the IP addresses from a file, make sure the file has one IP address per line, and use the flag like `--ips-file FILENAME` to input the file.

An example of checking the cabling of multiple switches: `canu report network cabling --ips 192.168.1.1,192.168.1.2 --username USERNAME --password PASSWORD`

There are two different `--view` options, **switch** and **equipment**.


1. The `--view switch` option displays a table for every switch IP address passed in showing connections. This is the same view as shown in the above example of checking single switch cabling.


2. The `--view equipment` option displays a table for each mac address connection. This means that servers and switches will both display incoming and outgoing connections.

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

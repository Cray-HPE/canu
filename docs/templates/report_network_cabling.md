# Report Network Cabling

```{eval-rst}
.. click:: canu.report.network.cabling.cabling:cabling
   :prog: canu report network cabling
```

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

---

<a href="/readme.md">Back To Readme</a><br>

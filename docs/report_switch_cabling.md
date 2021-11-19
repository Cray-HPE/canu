# Report Switch Cabling

## canu report switch cabling

Report the cabling of a switch (Aruba, Dell, or Mellanox) on the network by using LLDP.

If the neighbor name is not in LLDP, the IP and vlan information are displayed
by looking up the MAC address in the ARP table or the mac address table.

If there is a duplicate port, the duplicates will be highlighted in ‘bright white’.

Ports highlighted in ‘blue’ contain the string “ncn” in the hostname.

Ports are highlighted in ‘green’ when the port name is set with the interface name.


---

```
canu report switch cabling [OPTIONS]
```

### Options


### --ip( <ip>)
**Required** The IP address of the switch


### --username( <username>)
Switch username


* **Default**

    admin



### --password( <password>)
Switch password


### --out( <out>)
Output results to a file

## Example

To check the cabling of a single switch run: `canu report switch cabling --ip 192.168.1.1 --username USERNAME --password PASSWORD`

```
$ canu report switch cabling --ip 192.168.1.1 --username USERNAME --password PASSWORD

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



![image](images/canu_report_switch_cabling.png)



---

<a href="/readme.md">Back To Readme</a><br>

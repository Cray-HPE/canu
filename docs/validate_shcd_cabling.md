# Validate SHCD and Cabling

## canu validate shcd-cabling

Validate a SHCD file against the current network cabling.

Pass in a SHCD file and a list of IP address to compair the connections.

The output of the validate shcd-cabling command will show a port by port comparison between the devices found in the SHCD and devices found on the network.
If there is a difference in what is found connected to a devices port in SHCD and Cabling, the line will be highlighted in ‘red’.


---

```shell
canu validate shcd-cabling [OPTIONS]
```

### Options


### --csm( <csm>)
**Required** CSM network version


* **Options**

    1.0 | 1.2 | 1.3



### -a(, --architecture( <architecture>)
**Required** CSM architecture


* **Options**

    Full | TDS | V1



### --shcd( <shcd>)
**Required** SHCD file


### --tabs( <tabs>)
The tabs on the SHCD file to check, e.g. 10G_25G_40G_100G,NMN,HMN.


### --corners( <corners>)
The corners on each tab, comma separated e.g. ‘J37,U227,J15,T47,J20,U167’.


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


### --log( <log_>)
Level of logging.


* **Options**

    DEBUG | INFO | WARNING | ERROR



### --out( <out>)
Output results to a file


### --macs()
Print NCN MAC addresses

## Example

### Validate SHCD and Cabling

To validate an SHCD against the cabling run: `canu validate shcd-cabling --csm 1.2 -a tds --shcd FILENAME.xlsx --tabs 25G_10G,NMN --corners I14,S49,I16,S22 --ips 192.168.1.1,192.168.1.2 --username USERNAME --password PASSWORD`

```bash
$ canu validate shcd-cabling --csm 1.2 -a tds --shcd FILENAME.xlsx --tabs 25G_10G,NMN --corners I14,S49,I16,S22 --ips 192.168.1.1,192.168.1.2 --username USERNAME --password PASSWORD

====================================================================================================
SHCD vs Cabling
====================================================================================================

sw-spine-001
Rack: x3000    Elevation: u12
--------------------------------------------------------------------------------
Port   SHCD                     Cabling
--------------------------------------------------------------------------------
1      sw-spine-002:1           sw-spine-002:1
2      sw-spine-002:2           sw-spine-002:2
3      uan001:pcie-slot1:1      aa:aa:aa:aa:aa:aa Cray, Inc.
5      ncn-m001:pcie-slot1:1    ncn-m001:pcie-slot1:1
6      ncn-s002:pcie-slot1:1    ncn-s002:pcie-slot1:1
7      ncn-w001:pcie-slot1:1    ncn-w001:pcie-slot1:1

sw-spine-002
Rack: x3000    Elevation: u13
--------------------------------------------------------------------------------
Port   SHCD                     Cabling
--------------------------------------------------------------------------------
1      sw-spine-001:1           sw-spine-001:1
2      sw-spine-001:2           sw-spine-001:2
3      uan001:pcie-slot1:2      bb:bb:bb:bb:bb:bb Cray, Inc.
5      ncn-m001:pcie-slot1:2    ncn-m001:pcie-slot1:2
6      ncn-s002:pcie-slot1:2    ncn-s002:pcie-slot1:2
7      ncn-w001:pcie-slot1:2    ncn-w001:pcie-slot1:2

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
1      sw-spine-001:6           sw-spine-001:6
2      sw-spine-002:6           sw-spine-002:6

ncn-w001
Rack: x3000    Elevation: u16
--------------------------------------------------------------------------------
Port   SHCD                     Cabling
--------------------------------------------------------------------------------
1      sw-spine-001:7           sw-spine-001:7
2      sw-spine-002:7           sw-spine-002:7


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



![image](images/canu_validate_shcd_cabling.png)



---

<a href="/readme.md">Back To Readme</a><br>

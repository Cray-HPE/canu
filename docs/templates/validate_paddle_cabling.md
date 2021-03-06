# Validate Paddle and Cabling

```{eval-rst}
.. click:: canu.validate.paddle_cabling.paddle_cabling:paddle_cabling
   :prog: canu validate paddle-cabling
```

## Example

### Validate Paddle and Cabling

To validate a CCJ Paddle against the cabling run: `canu validate paddle-cabling --csm 1.2 --ccj paddle.json --ips 192.168.1.1,192.168.1.2 --username USERNAME --password PASSWORD`

```bash
$ canu validate paddle-cabling --csm 1.2 --ccj paddle.json --ips 192.168.1.1,192.168.1.2 --username USERNAME --password PASSWORD

====================================================================================================
CCJ vs Cabling
====================================================================================================

sw-spine-001
Rack: x3000    Elevation: u12
--------------------------------------------------------------------------------
Port   CCJ                      Cabling
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
Port   CCJ                      Cabling
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
Port   CCJ                      Cabling
--------------------------------------------------------------------------------
1      sw-spine-001:5           sw-spine-001:5
2      sw-spine-002:5           sw-spine-002:5

ncn-s001
Rack: x3000    Elevation: u15
--------------------------------------------------------------------------------
Port   CCJ                      Cabling
--------------------------------------------------------------------------------
1      sw-spine-001:6           sw-spine-001:6
2      sw-spine-002:6           sw-spine-002:6

ncn-w001
Rack: x3000    Elevation: u16
--------------------------------------------------------------------------------
Port   CCJ                      Cabling
--------------------------------------------------------------------------------
1      sw-spine-001:7           sw-spine-001:7
2      sw-spine-002:7           sw-spine-002:7


====================================================================================================
CCJ Warnings
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

---

<a href="/readme.md">Back To Readme</a><br>

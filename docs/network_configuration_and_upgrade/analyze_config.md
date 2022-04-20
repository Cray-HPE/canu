# Analyze CSM configuration update

Configuration updates depending on the current version of network configuration may be as easy as adding few lines or be complete rip & replace operation which may lead you to choosing to wipe the existing configuration or just simply adding few lines in the configuration.  

Always before making configuration changes, analyze the changes shown in the above configuration diff section. 

For example:  

```text
Config differences between running config and generated config 
Safe Commands 
These commands should be safe to run while the system is running. 
------------------------------------------------------------------------- 
interface 1/1/mgmt0 
  no shutdown 
interface 1/1/30 
  mtu 9198 
  description vsx isl 
interface vlan 7 
  ip ospf 1 area 0.0.0.0 
router ospf 1 vrf Customer 
  router-id 10.2.0.2 
  default-information originate 
  area 0.0.0.0 

------------------------------------------------------------------------- 
Manual Commands 

These commands may cause disruption to the system and should be done only during a maintenance period. 

It is recommended to have an out of band connection while running these commands. 
------------------------------------------------------------------------- 
interface 1/1/mgmt0 
  vrf attach keepalive 
  ip address 192.168.255.0/31 
interface 1/1/30 
  no vrf attach keepalive 
  lag 256 
------------------------------------------------------------------------- 
Commands NOT classified as Safe or Manual 
These commands include authentication as well as unique commands for the system. 
These should be looked over carefully before keeping/applying. 
------------------------------------------------------------------------- 
no profile Leaf 
no debug ospfv2 all 
no snmp-server vrf default  
no route-map CMN permit seq 10 
no router ospf 2 vrf Customer 
router bgp 65533 
  vrf Customer 
    no exit-address-family 
------------------------------------------------------------------------- 
Switch: sw-spine-001 
Differences 
------------------------------------------------------------------------- 
In Generated Not In Running (+)     |  In Running Not In Generated (-)    
------------------------------------------------------------------------- 
Total Additions:                 6  |  Total Deletions:                33 
Interface:                       1  |  Interface:                       3 
Router:                          1  |  Router:                          2 
```

[Back to index](index.md)
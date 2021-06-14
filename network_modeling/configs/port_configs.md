# HPE Port configurations and standards - CSM v1.0

Hardware Type: HPE

Software Version: CSM v1.0

# NCN-Master port config
```
interface lag 1 multi-chassis
no shutdown
description ncn-m001 port mgmt0
no routing
vlan trunk native 1
vlan trunk allowed 1-2,4,7
lacp mode active
lacp fallback
spanning-tree port-type admin-edge

interface 1/1/1
no shutdown
mtu 9198
description ncn-m001 port mgmt0    
interface lag 1

```

# NCN-Worker port config
```
interface lag 2 multi-chassis
no shutdown
description ncn-w001 port mgmt0
no routing
vlan trunk native 1
vlan trunk allowed 1-2,4,7
lacp mode active
lacp fallback
spanning-tree port-type admin-edge

interface 1/1/2
no shutdown
mtu 9198
description ncn-w001 port mgmt0    
lag 2
```

# NCN-Storage port config
```
interface lag 3 multi-chassis
no shutdown
description ncn-s001 port mgmt0
no routing
vlan trunk native 1
vlan trunk allowed 1-2,4,7,10
lacp mode active
lacp fallback
spanning-tree port-type admin-edge

interface 1/1/3
no shutdown
mtu 9198
description ncn-s001 port mgmt0    
lag 3
```
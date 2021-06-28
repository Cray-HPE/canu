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

# UAN port config
```
interface lag 4 multi-chassis
no shutdown
description uan
no routing
vlan trunk native 1
vlan trunk allowed 1-2,4,7
lacp mode active
lacp fallback
spanning-tree port-type admin-edge

interface 1/1/4
no shutdown
mtu 9198
description uan    
interface lag 4

interface 1/1/5
no shutdown
mtu 9198
no routing
vlan access 2
description uan
spanning-tree bpdu-guard
spanning-tree port-type admin-edge
```

# Login node port config
```
interface lag 5 multi-chassis
no shutdown
description login node
no routing
vlan trunk native 1
vlan trunk allowed 1-2,4,7
lacp mode active
lacp fallback
spanning-tree port-type admin-edge

interface 1/1/6
no shutdown
mtu 9198
description login node    
interface lag 5
```

# CMM port config
```
interface lag 6 static
no shutdown
description cmm
no routing
vlan trunk native 2000
vlan trunk allowed 2000,3000,4091
spanning-tree root-guard

interface 1/1/8
no shutdown
mtu 9198
description cmm    
interface lag 6
```
# CEC port config
```
interface 1/1/7
no shutdown
mtu 9198
description cec    
no routing
vlan access 3000
spanning-tree bpdu-guard
spanning-tree port-type admin-edge
```
# BMC port config
```
```
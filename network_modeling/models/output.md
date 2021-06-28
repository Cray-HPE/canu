Port configurations - CSM 

#ncn master port config
```

interface lag 1 multi-chassis
no shutdown
description ncn-m001 port mgmt0
no routing
vlan trunk native 1
vlan trunk allowed 1-2,4,7,10
lacp mode active
lacp fallback
spanning-tree port-type admin-edge
interface 
no shutdown
mtu 9198
description ncn-m001 port mgmt0    
lag 1

interface lag 2 multi-chassis
no shutdown
description ncn-m002 port mgmt0
no routing
vlan trunk native 1
vlan trunk allowed 1-2,4,7,10
lacp mode active
lacp fallback
spanning-tree port-type admin-edge
interface 
no shutdown
mtu 9198
description ncn-m002 port mgmt0    
lag 2

interface lag 3 multi-chassis
no shutdown
description ncn-m003 port mgmt0
no routing
vlan trunk native 1
vlan trunk allowed 1-2,4,7,10
lacp mode active
lacp fallback
spanning-tree port-type admin-edge
interface 
no shutdown
mtu 9198
description ncn-m003 port mgmt0    
lag 3


```

#ncn worker port config
```

interface lag  multi-chassis
no shutdown
description 
no routing
vlan trunk native 1
vlan trunk allowed 1-2,4,7,10
lacp mode active
lacp fallback
spanning-tree port-type admin-edge
interface 
no shutdown
mtu 9198
description     
lag 
interface lag  multi-chassis
no shutdown
description 
no routing
vlan trunk native 1
vlan trunk allowed 1-2,4,7,10
lacp mode active
lacp fallback
spanning-tree port-type admin-edge
interface 
no shutdown
mtu 9198
description     
lag 
interface lag  multi-chassis
no shutdown
description 
no routing
vlan trunk native 1
vlan trunk allowed 1-2,4,7,10
lacp mode active
lacp fallback
spanning-tree port-type admin-edge
interface 
no shutdown
mtu 9198
description     
lag 

```

#ncn storage port config
```

interface lag  multi-chassis
no shutdown
description 
no routing
vlan trunk native 1
vlan trunk allowed 1-2,4,7,10
lacp mode active
lacp fallback
spanning-tree port-type admin-edge
interface 
no shutdown
mtu 9198
description     
lag 
interface lag  multi-chassis
no shutdown
description 
no routing
vlan trunk native 1
vlan trunk allowed 1-2,4,7,10
lacp mode active
lacp fallback
spanning-tree port-type admin-edge
interface 
no shutdown
mtu 9198
description     
lag 
interface lag  multi-chassis
no shutdown
description 
no routing
vlan trunk native 1
vlan trunk allowed 1-2,4,7,10
lacp mode active
lacp fallback
spanning-tree port-type admin-edge
interface 
no shutdown
mtu 9198
description     
lag 

```
Port configurations - CSM 

#ncn master port config
```

interface lag 1 multi-chassis
no shutdown
description ncn-m001 port mgmt0
no routing
vlan trunk native 1
vlan trunk allowed 1-2,4,7,10
lacp mode active
lacp fallback
spanning-tree port-type admin-edge
interface 
no shutdown
mtu 9198
description ncn-m001 port mgmt0    
lag 1


```

#ncn worker port config
```

interface lag  multi-chassis
no shutdown
description 
no routing
vlan trunk native 1
vlan trunk allowed 1-2,4,7,10
lacp mode active
lacp fallback
spanning-tree port-type admin-edge
interface 
no shutdown
mtu 9198
description     
lag 
interface lag  multi-chassis
no shutdown
description 
no routing
vlan trunk native 1
vlan trunk allowed 1-2,4,7,10
lacp mode active
lacp fallback
spanning-tree port-type admin-edge
interface 
no shutdown
mtu 9198
description     
lag 
interface lag  multi-chassis
no shutdown
description 
no routing
vlan trunk native 1
vlan trunk allowed 1-2,4,7,10
lacp mode active
lacp fallback
spanning-tree port-type admin-edge
interface 
no shutdown
mtu 9198
description     
lag 

```

#ncn storage port config
```

interface lag  multi-chassis
no shutdown
description 
no routing
vlan trunk native 1
vlan trunk allowed 1-2,4,7,10
lacp mode active
lacp fallback
spanning-tree port-type admin-edge
interface 
no shutdown
mtu 9198
description     
lag 
interface lag  multi-chassis
no shutdown
description 
no routing
vlan trunk native 1
vlan trunk allowed 1-2,4,7,10
lacp mode active
lacp fallback
spanning-tree port-type admin-edge
interface 
no shutdown
mtu 9198
description     
lag 
interface lag  multi-chassis
no shutdown
description 
no routing
vlan trunk native 1
vlan trunk allowed 1-2,4,7,10
lacp mode active
lacp fallback
spanning-tree port-type admin-edge
interface 
no shutdown
mtu 9198
description     
lag 

```
Port configurations - CSM 

#ncn master port config
```

interface lag 1 multi-chassis
no shutdown
description ncn-m001 port mgmt0
no routing
vlan trunk native 1
vlan trunk allowed 1-2,4,7,10
lacp mode active
lacp fallback
spanning-tree port-type admin-edge
interface 
no shutdown
mtu 9198
description ncn-m001 port mgmt0    
lag 1


```

#ncn worker port config
```

interface lag  multi-chassis
no shutdown
description 
no routing
vlan trunk native 1
vlan trunk allowed 1-2,4,7,10
lacp mode active
lacp fallback
spanning-tree port-type admin-edge
interface 
no shutdown
mtu 9198
description     
lag 
interface lag  multi-chassis
no shutdown
description 
no routing
vlan trunk native 1
vlan trunk allowed 1-2,4,7,10
lacp mode active
lacp fallback
spanning-tree port-type admin-edge
interface 
no shutdown
mtu 9198
description     
lag 
interface lag  multi-chassis
no shutdown
description 
no routing
vlan trunk native 1
vlan trunk allowed 1-2,4,7,10
lacp mode active
lacp fallback
spanning-tree port-type admin-edge
interface 
no shutdown
mtu 9198
description     
lag 

```

#ncn storage port config
```

interface lag  multi-chassis
no shutdown
description 
no routing
vlan trunk native 1
vlan trunk allowed 1-2,4,7,10
lacp mode active
lacp fallback
spanning-tree port-type admin-edge
interface 
no shutdown
mtu 9198
description     
lag 

interface lag  multi-chassis
no shutdown
description 
no routing
vlan trunk native 1
vlan trunk allowed 1-2,4,7,10
lacp mode active
lacp fallback
spanning-tree port-type admin-edge
interface 
no shutdown
mtu 9198
description     
lag 

interface lag  multi-chassis
no shutdown
description 
no routing
vlan trunk native 1
vlan trunk allowed 1-2,4,7,10
lacp mode active
lacp fallback
spanning-tree port-type admin-edge
interface 
no shutdown
mtu 9198
description     
lag 


```
Port configurations - CSM 

#ncn master port config
```

interface lag 1 multi-chassis
no shutdown
description ncn-m001 port mgmt0
no routing
vlan trunk native 1
vlan trunk allowed 1-2,4,7,10
lacp mode active
lacp fallback
spanning-tree port-type admin-edge
interface 
no shutdown
mtu 9198
description ncn-m001 port mgmt0    
lag 1


```

#ncn worker port config
```

interface lag 2 multi-chassis
no shutdown
description ncn-w001 port mgmt0
no routing
vlan trunk native 1
vlan trunk allowed 1-2,4,7,10
lacp mode active
lacp fallback
spanning-tree port-type admin-edge
interface 
no shutdown
mtu 9198
description ncn-w001 port mgmt0    
lag 2


```

#ncn storage port config
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
interface 
no shutdown
mtu 9198
description ncn-s001 port mgmt0    
lag 3


```
Port configurations - CSM 

#ncn master port config
```

interface lag 1 multi-chassis
no shutdown
description ncn-m001 port mgmt0
no routing
vlan trunk native 1
vlan trunk allowed 1-2,4,7,10
lacp mode active
lacp fallback
spanning-tree port-type admin-edge
interface 
no shutdown
mtu 9198
description ncn-m001 port mgmt0    
lag 1
```

#ncn worker port config
```

interface lag 2 multi-chassis
no shutdown
description ncn-w001 port mgmt0
no routing
vlan trunk native 1
vlan trunk allowed 1-2,4,7,10
lacp mode active
lacp fallback
spanning-tree port-type admin-edge
interface 
no shutdown
mtu 9198
description ncn-w001 port mgmt0    
lag 2
```

#ncn storage port config
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
interface 
no shutdown
mtu 9198
description ncn-s001 port mgmt0    
lag 3
```
Port configurations - CSM 

#ncn master port config
```

interface lag 1 multi-chassis
no shutdown
description ncn-m001 port mgmt0
no routing
vlan trunk native 1
vlan trunk allowed 1-2,4,7,10
lacp mode active
lacp fallback
spanning-tree port-type admin-edge
interface 
no shutdown
mtu 9198
description ncn-m001 port mgmt0    
lag 1
```

#ncn worker port config
```

interface lag 2 multi-chassis
no shutdown
description ncn-w001 port mgmt0
no routing
vlan trunk native 1
vlan trunk allowed 1-2,4,7,10
lacp mode active
lacp fallback
spanning-tree port-type admin-edge
interface 
no shutdown
mtu 9198
description ncn-w001 port mgmt0    
lag 2
```

#ncn storage port config
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
interface 
no shutdown
mtu 9198
description ncn-s001 port mgmt0    
lag 3
```

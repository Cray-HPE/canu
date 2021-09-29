# HPE Port configurations and standards - CSM v1.2

Hardware Type: HPE

Software Version: CSM v1.2

# NCN-Master port config
```
```

# NCN-Worker port config
```

interface lag  multi-chassis
    no shutdown
    description 
    no routing
    vlan trunk native 1
    vlan trunk allowed 1-2,4,7
    lacp mode active
    lacp fallback
    spanning-tree port-type admin-edge

interface 1/1/2
    no shutdown
    mtu 9198
    description 
    lag ```

# NCN-Storage port config
```

interface lag  multi-chassis
    no shutdown
    description 
    no routing
    vlan trunk native 1    vlan trunk allowed 10    lacp mode active
    lacp fallback
    spanning-tree port-type admin-edge

interface 1/1/3
    no shutdown
    mtu 9198
    description 
    lag ```

# UAN port config
```
```

# Login node port config
```
interface lag  multi-chassis
    no shutdown
    description 
    no routing
    vlan trunk native 1
    vlan trunk allowed 1-2,4,7
    lacp mode active
    lacp fallback
    spanning-tree port-type admin-edge

interface 1/1/6
    no shutdown
    mtu 9198
    description 
    no routing
    interface lag 
```

# CMM port config
```
interface lag  static
    no shutdown
    description 
    no routing
    vlan trunk native 
    vlan trunk allowed ,
    spanning-tree root-guard

interface 1/1/8
    no shutdown
    mtu 9198
    description 
    lag ```
# CEC port config
```
interface 
    no shutdown
    mtu 9198
    description 
    no routing
    vlan access 
    spanning-tree bpdu-guard
    spanning-tree port-type admin-edge```
# BMC port config
```
```
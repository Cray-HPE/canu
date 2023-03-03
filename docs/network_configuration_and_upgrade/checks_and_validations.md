# Checks and validations

A worksheet that runs "cleanly” will have checked that: 

* Nodes are “architecturally allowed” to connect to each other. 
* No overlapping ports specified. 
* Node connections can be made at the appropriate speeds. 

A clean run will have the following sections: 

* SHCD Node Connections – A high level list of all node connections on the system. 
* SHCD Port Usage – A Port-by-port detailed listing of all node connections on the system. 

Warnings 

* A list of nodes found that are not categorized on the system. NOTE this list is important as it could include misspellings of nodes that should be included! 
* A list of cell-by-cell warnings of misspellings and other nit-picking items that CANU has autocorrected on the system. 

Critically, the Warnings output will contain a section headed “Node type could not be determined for the following”.  This needs to be carefully reviewed because it may contain site uplinks that are not tracked by CANU but may also contain mis-spelled or mis-categorized nodes. As an example: 

 
```text
Node type or port number could not be determined for the following. 
These nodes are not currently included in the model. 
(This may be a missing architectural definition/lookup or a spelling error) 
---------------------------------------------------------------------------

Sheet: 10G_25G_40G_100G 
Cell: I96      Name: CAN switch 
Cell: I97      Name: CAN switch 
Cell: O87      Name: CAN switch 
Cell: O90      Name: CAN switch 
Cell: O93      Name: CAN switch 
Cell: O100     Name: CAN switch 
Cell: O103     Name: CAN switch 
Cell: I38      Name: sw-spinx-002 
Sheet: HMN 
Cell: R36      Name: SITE 
Sheet: NMN 
Cell: P16      Name: SITE 
```

From the above example two important observations can be made: 

* CAN and SITE uplinks are not in the “clean run” model. This means that these ports will not be configured. 
* Critically, in the example cell I38 has a name of “sw-spinx-002". This should be noted as a misspelling of “sw-spine-002" and corrected. 

 

Today CANU validates many things, but a future feature is full cable specification checking of nodes (e.g. what NCN ports go to which switches to properly form bonds).  There are several CANU roadmap items, but today a manual review of the “SHCD Port Usage” connections list is vital.  

Specifically, check: 

* K8S NCN cabling (manager, worker, storage) follows PoR cabling [Link to cable management](https://github.com/Cray-HPE/docs-csm/blob/main/install/cable_management_network_servers.md) 
* UAN NCN cabling (UAN, viz, and other Application Nodes) follow PoR cabling [Link to cable management](https://github.com/Cray-HPE/docs-csm/blob/main/install/cable_management_network_servers.md)
* Switch pair cabling is appropriate for VSX, MAGP etc. 
* Switch-to-switch cabling is appropriate for LAG formation. 
* “Other” nodes on the network seem correct. 

[Back to index](index.md)
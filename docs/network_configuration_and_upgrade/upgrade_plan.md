# Planning for CSM upgrade/install

Creating an upgrade plan is always going to be unique and dependent on the requirements of the upgrade path.  

Some release versions of the network configuration require coupled upgrade of software to enable new software functionality or bug fixes that may add time required to do the full upgrade.  

***For example:*** in CSM 1.0 to CSM 1.2 we will upgrade Aruba switches to newer code.  

In another words: n cases where configuration changes are extensive you may want to consider the extent of the generated configurations after review that maybe best option is to fully wipe the existing switch configuration and build from scratch

This will prevent human error, especially from the extensive changes like say modifying 10’s or 100’s of ports away and have you installed the generated configuration via the system without having to do the individual changes by hand.  

 In addition to firmware upgrade paths, the application of CANU-generated switch configurations should be carefully considered and detailed. The following are important considerations: 

* Critically analyze proposed changes to ensure the customer does not have an unexpected outage. 
* Provide a holistic upgrade plan which includes switch-by-switch ordered changes and minimizes system outages. Typically, this should begin on the periphery of the network (leaf-bmc's) and move centrally towards spines and site uplinks. 
*  Where system outages or interruptions are expected to occur, provide details on the change order of operations, expected timing of interruptions and guidance should the interruption be beyond expected timing. 


The resulting “plan” should provide a procedure which can be followed by the customer/installer to upgrade the system from current state.   

[Back to index](index.md)
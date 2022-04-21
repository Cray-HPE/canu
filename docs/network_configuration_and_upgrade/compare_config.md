# Compare CSM switch configs with running configs 

Next you would want to compare the current running configuration with the generated configuration.  

For the comparison, since we’ve pulled the configuration to our working directory we can compare the files locally. 

You can also have Canu pull the configuration from the switch by defining ip list and username &  password field.  

Example: 

```text
canu validate switch config --ip 192.168.1.1 --username USERNAME --password PASSWORD --generated ./generated/sw-spine-001.cfg 
```

Doing file comparisons on your local machine:  

* Comparing configuration file for single switch:  

```text
canu validate switch config --running ./running/sw-spine-001.cfg --generated sw-spine-001.cfg  
``` 

Comparing configuration files for full system:  

```text
canu validate network config --csm 1.2 --running ./running/ --generated ./generated/ 
```
 
CANU generated switch configurations will not include any ports or devices not defined in the model. These were previously discussed in the Validate the SHCD section but include edge uplinks (CAN/CMN) and custom configurations applied by the customer.  When looking at the generated configurations being applied against existing running configurations CANU will recommend removal of some critical configurations. It is vital that these devices and configurations be identified and protected. This can be accomplished in three ways: 

* Provide CANU validation of generated configurations against running configurations with an override or “blackout” configuration – a yaml file which tells CANU to ignore customer-specific configurations. The process of creating this file was previously described in the This file will be custom to every site and must be distributed with the analysis and configuration file bundle to be used in the future. See the section “Configuration Blackout”. 
* Based on experience and knowledge the network, manually reorder the proposed upgrade configurations. This may require manual exclusion of required configurations which the CANU analysis says to remove. 
* Some devices may be used by multiple sites and may not currently be in the CANU architecture and configuration. If a device type is more universally used on several sites, then it should be added to the architectural and configuration definitions via the CANU code and Pull Request (PR) process.

NOTE: site defined uplinks/custom configuration can be added to the configurations using canu config injection.

[Back to index](index.md)
# Generate CSM switch configs 

Generating configuration files can be done for singular switch or for the full system. For example; in a case where you suspect a configuration issue on single switch you can generate just that one file for easier debugging purposes.  

* Generating configuration file for single switch:  

```text
canu generate switch config --csm 1.2 -a full --ccj hela-ccj.json  --sls-file sls_file.json --name sw-spine-001 --folder generated 
```
 
* Generating configuration files for full system:  

```text
canu generate network config --csm 1.2 -a full --ccj hela-ccj.json  --sls-file sls_file.json  --folder generated 
```

NOTE: --csm xxx dictates the version of CSM you are generating the configs for. (1.0 vs 1.2)

Again, make sure that you select the correct (-a) architecture specific to your setup: 

* ***Tds*** – Aruba-based Test and Development System.  
* ***Full*** – Aruba-based Leaf-Spine systems, usually customer production systems. 
* ***V1*** – Dell and Mellanox based systems of either a TDS or Full layout. 

[Back to index](index.md)
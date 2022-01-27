# Validate SHCD

## canu validate shcd

Validate a SHCD file.

CANU can be used to validate that an SHCD (SHasta Cabling Diagram) passes basic validation checks.


* Use the ‘–tabs’ flag to select which tabs on the spreadsheet will be included.


* The ‘–corners’ flag is used to input the upper left and lower right corners of the table on each tab of the worksheet. If the corners are not specified, you will be prompted to enter them for each tab.


* The table should contain the 11 headers: Source, Rack, Location, Slot, (Blank), Port, Destination, Rack, Location, (Blank), Port.


---

# noqa: D301, B950

Args:

    ctx: CANU context settings
    architecture: CSM architecture
    shcd: SHCD file
    tabs: The tabs on the SHCD file to check, e.g. 10G_25G_40G_100G,NMN,HMN.
    corners: The corners on each tab, comma separated e.g. ‘J37,U227,J15,T47,J20,U167’.
    out: Filename for the JSON Topology if requested.


    ```
    json_
    ```

    : Bool indicating json output


    ```
    log_
    ```

    : Level of logging.

```shell
canu validate shcd [OPTIONS]
```

### Options


### -a(, --architecture( <architecture>)
**Required** CSM architecture


* **Options**

    Full | TDS | V1



### --shcd( <shcd>)
**Required** SHCD file


### --tabs( <tabs>)
The tabs on the SHCD file to check, e.g. 10G_25G_40G_100G,NMN,HMN.


### --corners( <corners>)
The corners on each tab, comma separated e.g. ‘J37,U227,J15,T47,J20,U167’.


### --out( <out>)
Output results to a file


### --json()
Output JSON model to a file


### --log( <log_>)
Level of logging.


* **Options**

    DEBUG | INFO | WARNING | ERROR


## Example

To check an SHCD run: `canu validate shcd -a tds --shcd FILENAME.xlsx --tabs 25G_10G,NMN,HMN --corners I14,S25,I16,S22,J20,T39`

```bash
$ canu validate shcd -a tds --shcd FILENAME.xlsx --tabs 25G_10G,NMN,HMN --corners I14,S25,I16,S22,J20,T39

SHCD Node Connections
------------------------------------------------------------
0: sw-spine-001 connects to 6 nodes: [1, 2, 3, 4, 5, 6]
1: sw-spine-002 connects to 6 nodes: [0, 2, 3, 4, 5, 6]
2: sw-leaf-bmc-001 connects to 2 nodes: [0, 1]
3: uan001 connects to 2 nodes: [0, 1]
4: ncn-s001 connects to 2 nodes: [0, 1]
5: ncn-w001 connects to 2 nodes: [0, 1]
6: ncn-m001 connects to 2 nodes: [0, 1]

Warnings

Node type could not be determined for the following
------------------------------------------------------------
CAN switch
```



![image](images/canu_validate_shcd.png)



---

<a href="/readme.md">Back To Readme</a><br>

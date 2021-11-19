# Generate Switch Config

## canu generate switch config

Generate switch config using the SHCD.

In order to generate switch config, a valid SHCD must be passed in and system variables must be read in from either
an SLS output file or the SLS API.

## CSI Input


* In order to parse network data using SLS, pass in the file containing SLS JSON data (normally sls_file.json) using the ‘–sls-file’ flag


* If used, CSI-generated sls_input_file.json file is generally stored in one of two places depending on how far the system is in the install process.


* Early in the install process, when running off of the LiveCD the sls_input_file.json file is normally found in the the directory ‘/var/www/ephemeral/prep/SYSTEMNAME/’


* Later in the install process, the sls_file.json file is generally in ‘/mnt/pitdata/prep/SYSTEMNAME/’

## SLS API Input


* To parse the Shasta SLS API for IP addresses, ensure that you have a valid token.


* The token file can either be passed in with the ‘–auth-token TOKEN_FILE’ flag, or it can be automatically read if the environmental variable ‘SLS_TOKEN’ is set.


* The SLS address is default set to ‘api-gw-service-nmn.local’.


* if you are operating on a system with a different address, you can set it with the ‘–sls-address SLS_ADDRESS’ flag.

## SHCD Input


* Use the ‘–tabs’ flag to select which tabs on the spreadsheet will be included.


* The ‘–corners’ flag is used to input the upper left and lower right corners of the table on each tab of the worksheet. If the corners are not specified, you will be prompted to enter them for each tab.


* The table should contain the 11 headers: Source, Rack, Location, Slot, (Blank), Port, Destination, Rack, Location, (Blank), Port.

Use the ‘–folder FOLDERNAME’ flag to output all the switch configs to a folder.


---

```
canu generate switch config [OPTIONS]
```

### Options


### --csm( <csm>)
**Required** CSM network version


* **Options**

    1.0 | 1.2



### -a(, --architecture( <architecture>)
**Required** CSM architecture


* **Options**

    Full | TDS | V1



### --ccj( <ccj>)
Paddle CCJ file


### --shcd( <shcd>)
SHCD file


### --tabs( <tabs>)
The tabs on the SHCD file to check, e.g. 10G_25G_40G_100G,NMN,HMN.


### --corners( <corners>)
The corners on each tab, comma separated e.g. ‘J37,U227,J15,T47,J20,U167’.


### --name( <switch_name>)
**Required** The name of the switch to generate config e.g. ‘sw-spine-001’


### --sls-file( <sls_file>)
File containing system SLS JSON data.


### --auth-token( <auth_token>)
Token for SLS authentication


### --sls-address( <sls_address>)

* **Default**

    api-gw-service-nmn.local



### --out( <out>)
Output results to a file


### --override( <override>)
Switch configuration override

### Environment variables


### SLS_TOKEN()
> Provide a default for `--auth-token`

## Examples

### 1. Generate switch config from SLS API for sw-spine-001

To generate switch config run: `canu generate switch config --csm 1.2 -a full --shcd FILENAME.xlsx --tabs 'INTER_SWITCH_LINKS,NON_COMPUTE_NODES,HARDWARE_MANAGEMENT,COMPUTE_NODES' --corners 'J14,T44,J14,T48,J14,T24,J14,T23' --auth_token TOKEN_FILE --name SWITCH_HOSTNAME --out FILENAME`

```
$ canu generate switch config --csm 1.2 -a full --shcd FILENAME.xlsx --tabs INTER_SWITCH_LINKS,NON_COMPUTE_NODES,HARDWARE_MANAGEMENT,COMPUTE_NODES --corners J14,T44,J14,T48,J14,T24,J14,T23 --auth_token TOKEN_FILE --name sw-spine-001

hostname sw-spine-001
user admin group administrators password plaintext
bfd
no ip icmp redirect
vrf CAN
vrf keepalive
...

```

### 2. Generate switch config from CSI for sw-leaf-bmc-001

To generate switch config run: `canu generate switch config --csm 1.2 -a full --shcd FILENAME.xlsx --tabs 'INTER_SWITCH_LINKS,NON_COMPUTE_NODES,HARDWARE_MANAGEMENT,COMPUTE_NODES' --corners 'J14,T44,J14,T48,J14,T24,J14,T23' --sls-file /CSI/OUTPUT/FOLDER/ADDRESS --name SWITCH_HOSTNAME --out FILENAME`

```
$ canu generate switch config --csm 1.2 -a full --shcd FILENAME.xlsx --tabs INTER_SWITCH_LINKS,NON_COMPUTE_NODES,HARDWARE_MANAGEMENT,COMPUTE_NODES --corners J14,T44,J14,T48,J14,T24,J14,T23 --sls-file /CSI/OUTPUT/FOLDER/ADDRESS --name sw-leaf-bmc-001

hostname sw-leaf-bmc-001
user admin group administrators password plaintext
no ip icmp redirect
ntp server 192.168.1.4
ntp server 192.168.1.5
ntp server 192.168.1.6
ntp enable
...

```


---

<a href="/readme.md">Back To Readme</a><br>

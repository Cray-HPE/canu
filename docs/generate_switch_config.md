# Generate Switch Config

CANU can be used to generate switch config.

To see all the lags that are generated, see [lags](docs/lags.md)

In order to generate switch config, a valid SHCD must be passed in and system variables must be read in from either CSI output or the SLS API.

#### CSI Input

- In order to parse network data using SLS, pass in the file containing SLS JSON data (sometimes sls_file.json) the --sls-file flag

- If used, CSI-generated sls_file.json file is generally stored in one of two places depending on how far the system is in the install process.

- Early in the install process, when running off of the LiveCD the sls_file.json file is normally found in the the directory `/var/www/ephemeral/prep/SYSTEMNAME/`

- Later in the install process, the sls_file.json file is generally in `/mnt/pitdata/prep/SYSTEMNAME/`

#### SLS API Input

- To parse the Shasta SLS API for IP addresses, ensure that you have a valid token. The token file can either be passed in with the `--auth-token TOKEN_FILE` flag, or it can be automatically read if the environmental variable **SLS_TOKEN** is set. The SLS address is default set to _api-gw-service-nmn.local_, if you are operating on a system with a different address, you can set it with the `--sls-address SLS_ADDRESS` flag.

#### SHCD Input

- The `--shasta / -s` flag is used to set the Shasta version of the system.
- The `--architecture / -a` flag is used to set the architecture of the system, either **TDS**, or **Full**.
- Use the `--tabs` flag to select which tabs on the spreadsheet will be included.
- The `--corners` flag is used to input the upper left and lower right corners of the table on each tab of the worksheet. The table should contain the 11 headers: **Source, Rack, Location, Slot, (Blank), Port, Destination, Rack, Location, (Blank), Port**. If the corners are not specified, you will be prompted to enter them for each tab.

To generate config for a specific switch, a hostname must also be passed in using the `--name HOSTNAME` flag. To output the config to a file, append the `--out FILENAME` flag.

## Examples

### 1. Generate switch config from SLS API for sw-spine-001

To generate switch config run: `canu generate switch config -s 1.5 -a full --shcd FILENAME.xlsx --tabs 'INTER_SWITCH_LINKS,NON_COMPUTE_NODES,HARDWARE_MANAGEMENT,COMPUTE_NODES' --corners 'J14,T44,J14,T48,J14,T24,J14,T23' --auth_token TOKEN_FILE --name SWITCH_HOSTNAME --out FILENAME`

```bash
$ canu generate switch config -s 1.5 -a full --shcd FILENAME.xlsx --tabs INTER_SWITCH_LINKS,NON_COMPUTE_NODES,HARDWARE_MANAGEMENT,COMPUTE_NODES --corners J14,T44,J14,T48,J14,T24,J14,T23 --auth_token TOKEN_FILE --name sw-spine-001

hostname sw-spine-001
user admin group administrators password plaintext
bfd
no ip icmp redirect
vrf CAN
vrf keepalive
...

```

### 2. Generate switch config from CSI for sw-leaf-bmc-001

To generate switch config run: `canu generate switch config -s 1.5 -a full --shcd FILENAME.xlsx --tabs 'INTER_SWITCH_LINKS,NON_COMPUTE_NODES,HARDWARE_MANAGEMENT,COMPUTE_NODES' --corners 'J14,T44,J14,T48,J14,T24,J14,T23' --sls-file /CSI/OUTPUT/FOLDER/ADDRESS --name SWITCH_HOSTNAME --out FILENAME`

```bash
$ canu generate switch config -s 1.5 -a full --shcd FILENAME.xlsx --tabs INTER_SWITCH_LINKS,NON_COMPUTE_NODES,HARDWARE_MANAGEMENT,COMPUTE_NODES --corners J14,T44,J14,T48,J14,T24,J14,T23 --sls-file /CSI/OUTPUT/FOLDER/ADDRESS --name sw-leaf-bmc-001

hostname sw-leaf-bmc-001
user admin group administrators password plaintext
no ip icmp redirect
ntp server 192.168.1.4
ntp server 192.168.1.5
ntp server 192.168.1.6
ntp enable
...

```

## Flags

| Option                | Description                                                                |
| --------------------- | -------------------------------------------------------------------------- |
| `-s / --shasta`       | Shasta version                                                             |
| `-a / --architecture` | Shasta architecture ("Full", or "TDS")                                     |
| `--shcd`              | SHCD File                                                                  |
| `--tabs`              | The tabs on the SHCD file to check, e.g. 10G_25G_40G_100G,NMN,HMN.         |
| `--corners`           | The corners on each tab, comma separated e.g. 'J37,U227,J15,T47,J20,U167'. |
| `--sls_file`          | File containing the CSI json                                               |
| `--auth_token`        | Token for SLS authentication                                               |
| `--sls_address`       | The address of SLS                                                         |
| `--name`              | Switch Name                                                                |
| `--out`               | Name of the output file                                                    |

---

**[Back To Readme](/readme.md)**<br>

# Config BGP

CANU can be used to configure BGP for a pair of switches.

This command will remove previous configuration (BGP, Prefix Lists, Route Maps), then add prefix lists, create
route maps, and update BGP neighbors, then write it all to the switch memory.

The network and NCN data can be read from one of two sources, the SLS API, or using CSI.

To access SLS, a token must be passed in using the `--auth-token` flag.
Tokens are typically stored in ~./config/cray/tokens/
Instead of passing in a token file, the environmental variable SLS_TOKEN can be used.

To get the network data using CSI, pass in the CSI folder containing the sls_input_file.json file using the `--csi-folder` flag

The sls_input_file.json file is generally stored in one of two places depending on how far the system is in the install process.

- Early in the install process, when running off of the LiveCD the sls_input_file.json file is normally found in the the directory `/var/www/ephemeral/prep/SYSTEMNAME/`

- Later in the install process, the sls_input_file.json file is generally in `/mnt/pitdata/prep/SYSTEMNAME/`

## Examples

### 1. Config BGP from SLS API

To configure BGP run: `canu config bgp --ips 192.168.1.1,192.168.1.2 --username USERNAME --password PASSWORD --auth_token token_file.token`

```bash
$ canu config bgp --ips 192.168.1.1,192.168.1.2 --username USERNAME --password PASSWORD --auth_token token_file.token

BGP Updated
--------------------------------------------------
192.168.1.1
192.168.1.2

```

### 2. Config BGP from CSI

To config BGP from CSI: `canu config bgp --ips 192.168.1.1,192.168.1.2 --username USERNAME --password PASSWORD --csi-folder /path/to/csi/folder`

```bash
$ canu config bgp --ips 192.168.1.1,192.168.1.2 --username USERNAME --password PASSWORD --csi-folder /path/to/csi/folder

BGP Updated
--------------------------------------------------
192.168.1.1
192.168.1.2
```

### 3. Config BGP Verbose

To print extra details (prefixes, NCN names, IPs), add the `--verbose` flag: `canu config bgp --ips 192.168.1.1,192.168.1.2 --username USERNAME --password PASSWORD --verbose`

```bash
$ canu config bgp --ips 192.168.1.1,192.168.1.2 --username USERNAME --password PASSWORD --verbose

BGP Updated
--------------------------------------------------
192.168.1.1
192.168.1.2


Details
--------------------------------------------------
CAN Prefix: 192.168.5.0/23
HMN Prefix: 192.168.6.0/24
NMN Prefix: 192.168.7.0/24
TFTP Prefix: 192.168.7.60/32
NCN Names: ['ncn-w001', 'ncn-w002', 'ncn-w003', 'ncn-w004', 'ncn-w005']
NCN CAN IPs: ['192.168.5.25', '192.168.5.26', '192.168.5.27', '192.168.5.28', '192.168.5.29']
NCN NMN IPs: ['192.168.10.24', '192.168.10.25', '192.168.10.26', '192.168.10.27', '192.168.10.28']
NCN HMN IPs: ['192.168.20.44', '192.168.20.45', '192.168.20.46', '192.168.20.47', '192.168.20.48']
```

## Flags

| Option          | Description                            |
| --------------- | -------------------------------------- |
| `--csi_folder`  | Directory containing the CSI json file |
| `--auth_token`  | Token for SLS authentication           |
| `--sls_address` | The address of SLS                     |
| `--ips`         | Switch IPv4 address                    |
| `--ips-file`    | File with one IPv4 address per line    |
| `--username`    | Switch username                        |
| `--password`    | Switch password                        |
| `--asn`         | Switch ASN (Default: 65533)            |
| `--verbose`     | Bool indicating verbose output         |

---

**[Back To Readme](/readme.md)**<br>

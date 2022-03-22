# Config BGP

## canu config bgp

Configure BGP for a pair of switches.

This command will remove previous configuration (BGP, Prefix Lists, Route Maps), then add prefix lists, create
route maps, and update BGP neighbors, then write it all to the switch memory.

The network and NCN data can be read from one of two sources, the SLS API, or using CSI.

To access SLS, a token must be passed in using the ‘–auth-token’ flag.
Tokens are typically stored in ~./config/cray/tokens/
Instead of passing in a token file, the environmental variable ‘SLS_TOKEN’ can be used.

To initialize using SLS data, pass in the file containing SLS JSON data (typically sls_input_file.json) using the ‘–sls-file’ flag

If used, CSI-generated sls_file.json file is generally stored in one of two places
depending on how far the system is in the install process.


* Early in the install process, when running off of the LiveCD the sls_input_file.json file is normally found in the the directory ‘/var/www/ephemeral/prep/SYSTEMNAME/’


* Later in the install process, the sls_input_file.json file is generally in ‘/mnt/pitdata/prep/SYSTEMNAME/’

To print extra details (prefixes, NCN names, IPs), add the ‘–verbose’ flag

```
canu config bgp [OPTIONS]
```

### Options


### --sls-file( <sls_file>)
File containing system SLS JSON data.


### --auth-token( <auth_token>)
Token for SLS authentication


### --sls-address( <sls_address>)

* **Default**

    api-gw-service-nmn.local



### --ips( <ips>)
Comma separated list of IPv4 addresses of switches


### --ips-file( <ips_file>)
File with one IPv4 address per line


### --username( <username>)
Switch username


* **Default**

    admin



### --password( <password>)
Switch password


### --asn( <asn>)
ASN


* **Default**

    65533



### --verbose()
Verbose mode

### Environment variables


### SLS_TOKEN()
> Provide a default for `--auth-token`

## Examples

### 1. Config BGP from SLS API

To configure BGP run: `canu config bgp --ips 192.168.1.1,192.168.1.2 --username USERNAME --password PASSWORD --auth_token token_file.token`

```
$ canu config bgp --ips 192.168.1.1,192.168.1.2 --username USERNAME --password PASSWORD --auth_token token_file.token

BGP Updated
--------------------------------------------------
192.168.1.1
192.168.1.2

```

### 2. Config BGP from CSI

To config BGP from CSI: `canu config bgp --ips 192.168.1.1,192.168.1.2 --username USERNAME --password PASSWORD --sls-file SLS_FILE`

```
$ canu config bgp --ips 192.168.1.1,192.168.1.2 --username USERNAME --password PASSWORD --sls-file SLS_FILE

BGP Updated
--------------------------------------------------
192.168.1.1
192.168.1.2
```

### 3. Config BGP Verbose

To print extra details (prefixes, NCN names, IPs), add the `--verbose` flag: `canu config bgp --ips 192.168.1.1,192.168.1.2 --username USERNAME --password PASSWORD --verbose`

```
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


---

<a href="/readme.md">Back To Readme</a><br>

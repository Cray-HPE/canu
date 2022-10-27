# Config BGP

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

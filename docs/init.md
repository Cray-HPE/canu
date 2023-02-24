# Initialization

To help make switch setup a breeze. CANU can automatically parse SLS JSON data - including CSI sls_input_file.json output or the Shasta SLS API for switch IPv4 addresses.

## canu init

Initialize CANU by extracting all the switch IPs from CSI generated json, or by getting IPs from SLS.

To access the SLS API, a token must be passed in using the ‘–auth-token’ flag.
- Tokens are typically stored in ‘~./config/cray/tokens/’
- Instead of passing in a token file, the environmental variable SLS_TOKEN can be used.

To initialize using JSON instead of the SLS API, pass in the file containing SLS JSON data (normally sls_input_file.json) using the ‘–sls-file’ flag

If used, CSI-generated sls_input_file.json file is generally stored in one of two places depending on how far the system is in the install process.
- Early in the install process, when running off of the LiveCD the CSI sls_input_file.json file is normally found in the the directory ‘/var/www/ephemeral/prep/SYSTEMNAME/’
- Later in the install process, the CSI sls_input_file.json file is generally in ‘/mnt/pitdata/prep/SYSTEMNAME/’

The output file for the canu init command is set with the –out FILENAME flag.

```shell
canu init [OPTIONS]
```

### Options


### --sls-file( <sls_file>)
File containing system SLS JSON data.


### --auth-token( <auth_token>)
Token for SLS authentication


### --sls-address( <sls_address>)

* **Default**

    `api-gw-service-nmn.local`



### --network( <network>)
Switch network e.g. (CAN, MTL, NMN)


* **Default**

    `NMN`



### --out( <out>)
**Required** Output file with CSI IP addresses

### Environment variables


### SLS_TOKEN()
> Provide a default for `--auth-token`

## Examples

### 1. CSI

To get the switch IP addresses from CSI output, run the command:

```bash
$ canu init --sls-file SLS_FILE --out output.txt
8 IP addresses saved to output.txt
```



![image](_static/images/canu_init.png)

### 2. SLS Shasta API

To get the switch IP addresses from the Shasta SLS API, run the command:

```bash
$ canu init --auth-token ~./config/cray/tokens/ --sls-address 1.2.3.4 --out output.txt
8 IP addresses saved to output.txt
```

#### CSI Input


* In order to parse CSI output, use the `--sls-file FILE` flag to pass in the folder where an SLS JSON file is located.

The CSI `sls_input_file.json` file is generally stored in one of two places depending on how far the system is in the install process.


* Early in the install process, when running off of the LiveCD the CSI `sls_input_file.json` file is normally found in the the directory `/var/www/ephemeral/prep/SYSTEMNAME/`


* Later in the install process, the CSI `sls_input_file.json` file is generally in `/mnt/pitdata/prep/SYSTEMNAME/`


* The SLS file can also be obtained from an NCN that’s in the k8s cluster by running `cray sls dumpstate list  --format json`


* The switch IPs will be read from the ‘NMN’ network, if a different network is desired, use the `--network` flag to choose a different one e.g. (CAN, MTL, NMN).

To get the switch IP addresses from CSI output, run the command:

```bash
canu init --sls-file SLS_FILE --out output.txt
```

Potential output:

```text
8 IP addresses saved to output.txt
```

#### SLS API Input


* To parse the Shasta SLS API for IP addresses, ensure that you have a valid token. The token file can either be passed in with the `--auth-token TOKEN_FILE` flag, or it can be automatically read if the environmental variable **`SLS_TOKEN`** is set. The SLS address is default set to `api-gw-service-nmn.local`, if you are operating on a system with a different address, you can set it with the `--sls-address SLS_ADDRESS` flag.

To get the switch IP addresses from the Shasta SLS API, run the command:

```bash
canu init --auth-token ~./config/cray/tokens/ --sls-address 1.2.3.4 --out output.txt
```

Potential output:

```text
8 IP addresses saved to output.txt
```



![image](_static/images/canu_init.png)

The output file for the `canu init` command is set with the `--out FILENAME` flag.

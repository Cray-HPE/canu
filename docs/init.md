# Initialization

To help make switch setup a breeze. CANU can automatically parse CSI output or the Shasta SLS API for switch IPv4 addresses. In order to parse CSI output, use the `--csi-folder FOLDER` flag to pass in the folder where the _sls_input_file.json_ file is located. To parse the Shasta SLS API for IP addresses, ensure that you have a valid token. The token file can either be passed in with the `--auth-token TOKEN_FILE` flag, or it can be automatically read if the environmental variable **SLS_TOKEN** is set. The SLS address is default set to _api-gw-service-nmn.local_, if you are operating on a system with a different address, you can set it with the `--sls-address SLS_ADDRESS` flag.

The _sls_input_file.json_ file is generally stored in one of two places depending on how far the system is in the install process.

- Early in the install process, when running off of the LiveCD the _sls_input_file.json_ file is normally found in the the directory `/var/www/ephemeral/prep/SYSTEMNAME/`
- Later in the install process, the _sls_input_file.json_ file is generally in `/mnt/pitdata/prep/SYSTEMNAME/`

The output file for the `canu init` command is set with the `--out FILENAME` flag.

## Examples

### 1. CSI

To get the switch IP addresses from CSI output, run the command:

```bash
$ canu init --csi-folder /CSI/OUTPUT/FOLDER/ADDRESS --out output.txt
8 IP addresses saved to output.txt
```

### 2. SLS Shasta API

To get the switch IP addresses from the Shasta SLS API, run the command:

```bash
$ canu init --auth-token ~./config/cray/tokens/ --sls-address 1.2.3.4 --out output.txt
8 IP addresses saved to output.txt
```

## Flags

| Option          | Description                            |
| --------------- | -------------------------------------- |
| `--csi_folder`  | Directory containing the CSI json file |
| `--auth_token`  | Token for SLS authentication           |
| `--sls_address` | The address of SLS                     |
| `--out`         | Name of the output file                |

---

**[Back To Readme](/readme.md)**<br>

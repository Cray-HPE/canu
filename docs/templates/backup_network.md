# Backup Network

```{eval-rst}
.. click:: canu.backup.network.network:network
  :prog: canu backup network
  :show-nested:
```

Canu can backup the running configurations for switches in the management network.
It backs up the entire switch inventory from SLS by defualt, if you want to backup just one switch use the `--name` flag.

Required Input
You can either use an SLS file or pull the SLS file from the API-Gateway using a token.

- `--sls-file`
- `--folder` "Folder to store running config files"

Options

- `--log` outputs the nornir debug logs
- `--network [HMN|CMN]` This gives the user the ability to connect to the switches over the CMN.  This allows the use of this tool from outside the Mgmt Network.  The default network used is the HMN.
- `--password` prompts if password is not entered
- `--username` defaults to admin
- `--unsanitized` Retains sensitive data such as passwords and SNMP credentials.  The default is to sanitize the config.
- `--name` The name of the switch that you want to back up. e.g. 'sw-spine-001'

Example

```bash
canu backup network --sls-file ./sls_input_file.json --network CMN --folder ./ --unsanitized
```

Potential output:

```text
Running Configs Saved
---------------------
sw-spine-001.cfg
sw-spine-002.cfg
sw-leaf-001.cfg
sw-leaf-002.cfg
sw-leaf-003.cfg
sw-leaf-004.cfg
sw-leaf-bmc-001.cfg
sw-leaf-bmc-002.cfg
sw-cdu-001.cfg
sw-cdu-002.cfg
```

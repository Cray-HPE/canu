# Send Command

## canu send command

Canu send command.

```shell
canu send command [OPTIONS]
```

### Options


### --sls-file( <sls_file>)
File containing system SLS JSON data.


### --network( <network>)
The network that is used to connect to the switches.


* **Default**

    `HMN`



* **Options**

    HMN | CMN



### --log()
enable logging.


### --command( <command>)
**Required** command to send to the switches e.g. show version


### --name( <name>)
The name of the switch to run the command on, the default for this is all switches e.g. sw-leaf-bmc-001


### --sls-address( <sls_address>)

* **Default**

    `api-gw-service-nmn.local`



### --password( <password>)
Switch password


### --username( <username>)
Switch username


* **Default**

    `admin`


Canu can send commands to the switches via the CLI.
This is primarily used for `show` commands since we do not elevate to configuration mode.

You can either use an SLS file or pull the SLS file from the API-Gateway using a token.


* `--sls-file`


* `--log` outputs the nornir debug logs


* `--network [HMN|CMN]` This gives the user the ability to connect to the switches over the CMN.  This allows the use of this tool from outside the Mgmt Network.  The default network used is the HMN.


* `--command` command to send to the switch/switches.


* `--password` prompts if password is not entered


* `--username` defaults to admin


* `--name` The name of the switch that you want to back up. e.g. ‘sw-spine-001’

Examples

```bash
canu send command --sls-file ./sls_input_file.json --network cmn --command "show banner exec" --name sw-spine-001
-netmiko_send_command************************************************************
* sw-spine-001 ** changed : False **********************************************
vvvv netmiko_send_command ** changed : False vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv INFO
###############################################################################
# CSM version:  1.2
# CANU version: 1.3.2
###############################################################################

^^^^ END netmiko_send_command ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
```

```bash
canu send command --command 'show version | include "Version      :"'
\netmiko_send_command************************************************************
* sw-leaf-bmc-001 ** changed : False *******************************************
vvvv netmiko_send_command ** changed : False vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv INFO
Version      : FL.10.09.0010                                                 
^^^^ END netmiko_send_command ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
* sw-spine-001 ** changed : False **********************************************
vvvv netmiko_send_command ** changed : False vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv INFO
Version      : GL.10.09.0010                                                 
^^^^ END netmiko_send_command ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
* sw-spine-002 ** changed : False **********************************************
vvvv netmiko_send_command ** changed : False vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv INFO
Version      : GL.10.09.0010                                                 
^^^^ END netmiko_send_command ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
```

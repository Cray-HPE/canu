# Report Network Version

## canu report network version

Report Switch Version.

Args:

    ctx: CANU context settings
    username: Switch username
    password: Switch password
    sls_file: JSON file containing SLS data
    sls_address: The address of SLS
    network: The network that is used to connect to the switches.


    ```
    log_
    ```

    : enable logging

```shell
canu report network version [OPTIONS]
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


### --username( <username>)
Switch username


* **Default**

    `admin`



### --password( <password>)
Switch password


### --sls-address( <sls_address>)

* **Default**

    `api-gw-service-nmn.local`


# Details

Canu reports the version of configuration on the switch.  It reads the exec baner of all the switches and outputs to the screen.

Options


* `--sls-file`


* `--network [HMN|CMN]` This gives the user the ability to connect to the switches over the CMN.  This allows the use of this tool from outside the Mgmt Network.  The default network used is the HMN.


* `--password` prompts if password is not entered


* `--username` defaults to admin

Example

```console
canu report network version --sls-file ../sls_input_file.json --network cmn
Password: 
SWITCH            CANU VERSION      CSM VERSION
sw-spine-001      1.5.12            1.2  
sw-spine-002      1.5.12            1.2  
sw-leaf-bmc-001   1.5.12            1.2
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

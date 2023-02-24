# Report Network Version

```{eval-rst}
.. click:: canu.report.network.version.version:version
   :prog: canu report network version
```
# Details 

Canu reports the version of configuration on the switch.  It reads the exec baner of all the switches and outputs to the screen.

Options

- `--sls-file`
- `--network [HMN|CMN]` This gives the user the ability to connect to the switches over the CMN.  This allows the use of this tool from outside the Mgmt Network.  The default network used is the HMN.
- `--password` prompts if password is not entered
- `--username` defaults to admin

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

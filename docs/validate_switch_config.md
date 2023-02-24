# Validate Switch Config

## canu validate switch config

Validate switch config.

After config has been generated, CANU can validate the generated config against running switch config. The running config can be from either an IP address, or a config file.


* To get running config from an IP address, use the flags ‘–ip 192.168.1.1 –username USERNAME –password PASSWORD’.


* To get running config from a file, use the flag ‘–running RUNNING_CONFIG.cfg’ instead.

After running the ‘validate switch config’ command, you will be shown a line by line comparison of the currently running switch config against the config file that was passed in. You will also be given a list of remediation commands that can be typed into the switch to get the running config to match the config file. There will be a summary table at the end highlighting the most important differences between the configs.


* Lines that are red and start with a ‘-’ are in the running config, but not in the config file


* Lines that are green and start with a ‘+’ are not in the running config, but are in the config file


* Lines that are blue and start with a ‘?’ are attempting to point out specific line differences


---

```shell
canu validate switch config [OPTIONS]
```

### Options


### --ip( <ip>)
The IP address of the switch with running config


### --running( <running>)
The running switch config file


### --vendor( <vendor>)
The vendor is needed if passing in the running config from a file


* **Options**

    Aruba | Dell | Mellanox



### --username( <username>)
Switch username


* **Default**

    `admin`



### --password( <password>)
Switch password


### --generated( <generated_config>)
Generated config file


### --out( <out>)
Output results to a file


### --remediation()
Outputs commands to get from the running-config to generated config

## Example

To validate switch config run: `canu validate switch config --ip 192.168.1.1 --username USERNAME --password PASSWORD --generated SWITCH_CONFIG.cfg`

```bash
$ canu validate switch config --ip 192.168.1.1 --generated sw-spine-001.cfg

hostname sw-spine-001
- ntp server 192.168.1.10
?                       ^
+ ntp server 192.168.1.16
?                       ^
  vlan 1
  vlan 2
-     name RVR_NMN
?          ----
+     name NMN
      apply access-list ip nmn-hmn in
      apply access-list ip nmn-hmn out
...

Switch: sw-leaf-001 (192.168.1.1)
Differences
-------------------------------------------------------------------------
In Generated Not In Running (+)     |  In Running Not In Generated (-)
-------------------------------------------------------------------------
Total Additions:                 7  |  Total Deletions:                 7
Hostname:                        1  |  Hostname:                        1
Interface:                       2  |  Interface:                       1
Interface Lag:                   1  |  Interface Lag:                   2
Spanning Tree:                   2  |  Spanning Tree:                   3
Router:                          1  |

```



![image](_static/images/canu_validate_switch_config.png)

After config has been generated, CANU can validate the generated config against running switch config. The running config can be from either an IP address, or a config file.


* To get running config from an IP address, use the flags `--ip 192.168.1.1 --username USERNAME --password PASSWORD`.


* To get running config from a file, use the flag `--running RUNNING_CONFIG.cfg` instead.

After running the `validate switch config` command, you will be shown a line by line comparison of the currently running switch config against the config file that was passed in. You will also be given a list of remediation commands that can be typed into the switch to get the running config to match the config file. There will be a summary table at the end highlighting the most important differences between the configs.


* Lines that are red and start with a `-` are in the running config, but not in the config file


* Lines that are green and start with a `+` are not in the running config, but are in the config file


* Lines that are blue and start with a `?` are attempting to point out specific line differences

To validate switch config run: `canu validate switch config --ip 192.168.1.1 --username USERNAME --password PASSWORD --generated SWITCH_CONFIG.cfg`

```bash
canu validate switch config --ip 192.168.1.1 --generated sw-spine-001.cfg
```

Potential output:

```text
hostname sw-spine-001
- ntp server 192.168.1.10
?                       ^
+ ntp server 192.168.1.16
?                       ^
  vlan 1
  vlan 2
-     name RVR_NMN
?          ----
+     name NMN
      apply access-list ip nmn-hmn in
      apply access-list ip nmn-hmn out
...

Switch: sw-leaf-001 (192.168.1.1)
Differences
-------------------------------------------------------------------------
In Generated Not In Running (+)     |  In Running Not In Generated (-)
-------------------------------------------------------------------------
Total Additions:                 7  |  Total Deletions:                 7
Hostname:                        1  |  Hostname:                        1
Interface:                       2  |  Interface:                       1
Interface Lag:                   1  |  Interface Lag:                   2
Spanning Tree:                   2  |  Spanning Tree:                   3
Router:                          1  |
```



![image](_static/images/canu_validate_switch_config.png)

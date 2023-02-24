# Validate Network Config

```{eval-rst}
.. click:: canu.validate.network.config.config:config
   :prog: canu validate network config
```

## Example

To validate switch config run: `canu validate network config --ips-file ips.txt --username USERNAME --password PASSWORD --generated /CONFIG/FOLDER`

```bash
$ canu validate network config --csm 1.2 --ips-file ips.txt --generated /CONFIG/FOLDER

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

Switch: sw-spine-001 (192.168.1.2)
Differences
-------------------------------------------------------------------------
In Generated Not In Running (+)     |  In Running Not In Generated (-)
-------------------------------------------------------------------------
Total Additions:                 3  |  Total Deletions:                 2
Interface:                       2  |  Interface:                       1
Interface Lag:                   1  |

...

Errors
----------------------------------------------------------------------------------------------------
192.168.1.3      - Timeout error connecting to switch 192.168.1.3, check the entered username, IP address and password.
```

```{eval-rst}
.. image:: _static/images/canu_validate_switch_config.png
  :alt: canu validate switch config
```


Aruba support only.

The `validate network config` command works almost the same as the above `validate switch config` command. There are three options for passing in the running config:

- A comma separated list of ips using `--ips 192.168.1.1,192.168.1.`
- A file of ip addresses, one per line using the flag `--ips-file ips.txt`
- A directory containing the running configuration `--running RUNNING/CONFIG/DIRECTORY`

A directory of generated config files will also need to be passed in using `--generated GENERATED/CONFIG/DIRECTORY`. There will be a summary table for each switch highlighting the most important differences between the running switch config and the generated config files.

To validate switch config run: `canu validate network config --ips-file ips.txt --username USERNAME --password PASSWORD --generated /CONFIG/FOLDER`

```bash
canu validate network config --csm 1.2 --ips-file ips.txt --generated /CONFIG/FOLDER
```

Potential output:

```text
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

Switch: sw-spine-001 (192.168.1.2)
Differences
-------------------------------------------------------------------------
In Generated Not In Running (+)     |  In Running Not In Generated (-)
-------------------------------------------------------------------------
Total Additions:                 3  |  Total Deletions:                 2
Interface:                       2  |  Interface:                       1
Interface Lag:                   1  |

...

Errors
----------------------------------------------------------------------------------------------------
192.168.1.3      - Timeout error connecting to switch 192.168.1.3, check the entered username, IP address and password.
```

### File Output and JSON

To output the results of the config validation command to a file, append the `--out FILENAME` flag. To get the results as JSON, use the `--json` flag.

### Cache

There are several commands to help with the canu cache:

- `canu cache location` will tell you the folder where your cache is located
- `canu cache print` will print a colored version of your cache to the screen
- `canu cache delete` will delete your cache file, the file will be created again on the next canu command

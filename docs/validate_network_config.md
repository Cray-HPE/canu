# Validate Network Config

The `validate network config` command works almost the same as the above `validate switch config` command. There are three options for passing in the running config:

- A comma separated list of ips using `--ips 192.168.1.1,192.168.1.`
- A file of ip addresses, one per line using the flag `--ips-file ips.txt`
- A directory containing the running configuration `--running RUNNING/CONFIG/DIRECTORY`

A directory of generated config files will also need to be passed in using `--generated GENERATED/CONFIG/DIRECTORY`. There will be a summary table for each switch highlighting the most important differences between the running switch config and the generated config files.

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
192.168.1.3      - Timeout error connecting to switch 192.168.1.3, check the IP address and try again.
```

![](images/canu_validate_switch_config.png)

## Flags

| Option        | Description                                        |
| ------------- | -------------------------------------------------- |
| `--csm`       | CSM version                                        |
| `--ips`       | Comma separated list of IPv4 addresses of switches |
| `--ips-file`  | File with one IPv4 address per line                |
| `--running`   | Directory containing running config files          |
| `--username`  | Switch username                                    |
| `--password`  | Switch password                                    |
| `--generated` | Folder containing generated config files           |
| `--json`      | Bool indicating json output                        |
| `--out`       | Name of the output file                            |

---

**[Back To Readme](/readme.md)**<br>

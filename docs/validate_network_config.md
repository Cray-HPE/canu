# Validate Network Config

The `validate network config` command works almost the same as thh above `validate switch config` command. Pass in a list of ips, or a file of ip addresses and a directory of generated config files and there will be a summary table for each switch highlighting the most important differences between the runnig switch config and the config files.

## Example

To validate switch config run: `canu validate network config --ips-file ips.txt --username USERNAME --password PASSWORD --config /CONFIG/FOLDER`

```bash
$ canu validate network config -s 1.5 --ips-file ips.txt --config /CONFIG/FOLDER

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

## Flags

| Option          | Description                                        |
| --------------- | -------------------------------------------------- |
| `-s / --shasta` | Shasta version                                     |
| `--ips`         | Comma separated list of IPv4 addresses of switches |
| `--ips-file`    | File with one IPv4 address per line                |
| `--username`    | Switch username                                    |
| `--password`    | Switch password                                    |
| `--config`      | Config folder                                      |

---

**[Back To Readme](/readme.md)**<br>

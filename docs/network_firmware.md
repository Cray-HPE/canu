# Network Firmware

Multiple Aruba switches on a network can be checked for their firmware versions. The IPv4 addresses of the switches can either be entered comma separated, or be read from a file. To enter a comma separated list of IP addresses to the `---ips` flag. To read the IP addresses from a file, make sure the file has one IP address per line, and use the flag like `--ips-file FILENAME` to input the file.

There are three different statuses found in the report.

- 🛶 Pass: Indicates that the switch passed the firmware verification.

- ❌ Fail: Indicates that the switch failed the firmware verification, in the generated table, a
  list of expected firmware versions for that switch is displayed.

- 🔺 Error: Indicates that there was an error connecting to the switch, check the Errors table for the specific error.

## Examples

### 1. Network Firmware

An example of checking the firmware of multiple switches: `canu --shasta 1.4 network firmware --ips 192.168.1.1,192.168.1.2 --username USERNAME --password PASSWORD` Or to load IP addresses from a file run: `canu --shasta 1.4 network firmware --ips-file ip_file.txt --username USERNAME --password PASSWORD`

```bash
$ canu --shasta 1.4 network firmware --ips 192.168.1.1,192.168.1.2,192.168.1.3,192.168.1.4 --username USERNAME --password PASSWORD

------------------------------------------------------------------
    STATUS  IP              HOSTNAME            FIRMWARE
------------------------------------------------------------------
 🛶 Pass    192.168.1.1     test-switch-spine01 GL.10.06.0010
 🛶 Pass    192.168.1.2     test-switch-leaf01  FL.10.06.0010
 ❌ Fail    192.168.1.3     test-wrong-version  FL.10.05.0001   Firmware should be in range ['FL.10.06.0001']
 🔺 Error   192.168.1.4


Errors
------------------------------------------------------------------
192.168.1.4     - HTTP Error. Check that this IP is an Aruba switch, or check the username and password

Summary
------------------------------------------------------------------
🛶 Pass - 2 switches
❌ Fail - 1 switches
🔺 Error - 1 switches
GL.10.06.0010 - 1 switches
FL.10.06.0010 - 1 switches
FL.10.05.0010 - 1 switches
```

When using the _network firmware_ commands, the table will show either: 🛶 Pass, ❌ Fail, or 🔺 Error. The switch will **pass** or **fail** based on if the switch firmware matches the _canu.yaml_

### 1. Network Firmware JSON

To get the JSON output from multiple switches, make sure to use the `--json` flag. An example json output is below.

```bash
$ canu --shasta 1.4 network firmware --ips 192.168.1.1,192.168.1.2 --username USERNAME --password PASSWORD --json

{
    "192.168.1.1": {
        "status": "Pass",
        "hostname": "test-switch-spine01",
        "platform_name": "8325",
        "firmware": {
            "current_version": "GL.10.06.0010",
            "primary_version": "GL.10.06.0010",
            "secondary_version": "GL.10.05.0020",
            "default_image": "primary",
            "booted_image": "primary",
        },
    },
    "192.168.1.2": {
        "status": "Pass",
        "hostname": "test-switch-leaf01",
        "platform_name": "6300",
        "firmware": {
            "current_version": "FL.10.06.0010",
            "primary_version": "FL.10.06.0010",
            "secondary_version": "FL.10.05.0020",
            "default_image": "primary",
            "booted_image": "primary",
        },
    },
}
```

### File Out

To output the results of the network firmware commands to a file, append the `--out FILENAME` flag

## Flags

| Option       | Description                         |
| ------------ | ----------------------------------- |
| `--ips`      | Switch IPv4 address                 |
| `--ips-file` | File with one IPv4 address per line |
| `--username` | Switch username                     |
| `--password` | Switch password                     |
| `--json`     | Bool indicating json output         |
| `--out`      | Name of the output file             |

---

**[Back To Readme](/readme.md)**<br>

# Report Network Firmware

## canu report network firmware

Report the firmware versions of all switches (Aruba, Dell, or Mellanox) on the network.

Pass in either a comma separated list of IP addresses using the ‘–ips’ option

OR

Pass in a file of IP addresses with one address per line using the ‘–ips-file’ option

There are three different statuses found in the report.


* 🛶 Pass: Indicates that the switch passed the firmware verification.


* ❌ Fail: Indicates that the switch failed the firmware verification, in the generated table, a list of expected firmware versions for that switch is displayed.


* 🔺 Error: Indicates that there was an error connecting to the switch, check the Errors table for the specific error.


---

# noqa: D301, B950

Args:

    ctx: CANU context settings
    csm: CSM version
    ips: Comma separated list of IPv4 addresses of switches
    ips_file: File with one IPv4 address per line
    username: Switch username
    password: Switch password


    ```
    json_
    ```

    : Bool indicating json output
    out: Name of the output file

Returns:

    json_formatted: If JSON is selected, returns output

```shell
canu report network firmware [OPTIONS]
```

### Options


### --csm( <csm>)
**Required** CSM network version


* **Options**

    1.0 | 1.2



### --ips( <ips>)
Comma separated list of IPv4 addresses of switches


### --ips-file( <ips_file>)
File with one IPv4 address per line


### --username( <username>)
Switch username


* **Default**

    admin



### --password( <password>)
Switch password


### --json()
Output JSON


### --out( <out>)
Output results to a file

## Examples

### 1. Network Firmware

An example of checking the firmware of multiple switches: `canu report network firmware --csm 1.2 --ips 192.168.1.1,192.168.1.2 --username USERNAME --password PASSWORD` Or to load IP addresses from a file run: `canu report network firmware --csm 1.2 --ips-file ip_file.txt --username USERNAME --password PASSWORD`

```bash
$ canu report network firmware --csm 1.2 --ips 192.168.1.1,192.168.1.2,192.168.1.3,192.168.1.4 --username USERNAME --password PASSWORD

------------------------------------------------------------------
    STATUS  IP              HOSTNAME            FIRMWARE
------------------------------------------------------------------
 🛶 Pass    192.168.1.1     test-switch-spine01 GL.10.06.0010
 🛶 Pass    192.168.1.2     test-switch-leaf01  FL.10.06.0010
 ❌ Fail    192.168.1.3     test-wrong-version  FL.10.05.0001   Firmware should be in range ['FL.10.06.0001']
 🔺 Error   192.168.1.4


Errors
------------------------------------------------------------------
192.168.1.4     - HTTP Error. Check that the IP, username, or password

Summary
------------------------------------------------------------------
🛶 Pass - 2 switches
❌ Fail - 1 switches
🔺 Error - 1 switches
GL.10.06.0010 - 1 switches
FL.10.06.0010 - 1 switches
FL.10.05.0010 - 1 switches
```



![image](images/canu_report_network_firmware.png)


### 2. Network Firmware JSON

To get the JSON output from multiple switches, make sure to use the `--json` flag. An example json output is below.

```bash
$ canu report network firmware --csm 1.2 --ips 192.168.1.1,192.168.1.2 --username USERNAME --password PASSWORD --json

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


---

<a href="/readme.md">Back To Readme</a><br>

# Validate BGP

CANU can be used to validate BGP neighbors. All neighbors of a switch must return status **Established** or the verification will fail.

- To enter a comma separated list of IP addresses to the `---ips` flag. To read the IP addresses from a file, make sure the file has one IP address per line, and use the flag like `--ips-file FILENAME` to input the file.
- The default **asn** is set to _65533_ if it needs to be changed, use the flag `--asn NEW_ASN_NUMBER` to set the new number

If you want to see the individual status of all the neighbors of a switch, use the `--verbose` flag.

## Examples

### 1. Validate BGP

To validate BGP run: `canu validate bgp --ips 192.168.1.1,192.168.1.2 --username USERNAME --password PASSWORD`

```bash
$ canu validate bgp --ips 192.168.1.1,192.168.1.2 --username USERNAME --password PASSWORD

BGP Neighbors Established
--------------------------------------------------
PASS - IP: 192.168.1.1 Hostname: sw-spine01
PASS - IP: 192.168.1.2 Hostname: sw-spine02

```

### 2. Validate BGP Verbose

To get verbose BGP neighbor details: `canu validate bgp --ips 192.168.1.1,192.168.1.3,192.168.1.2 --username USERNAME --password PASSWORD --verbose`

```bash
$ canu validate bgp --ips 192.168.1.1,192.168.1.3,192.168.1.2 --username USERNAME --password PASSWORD --verbose

--------------------------------------------------
sw-spine01
--------------------------------------------------
sw-spine01 ===> 192.168.1.2: Established
sw-spine01 ===> 192.168.1.3: Established
sw-spine01 ===> 192.168.1.4: Established
sw-spine01 ===> 192.168.1.5: Established
--------------------------------------------------
sw-leaf01
--------------------------------------------------
--------------------------------------------------
sw-spine02
--------------------------------------------------
sw-spine02 ===> 192.168.1.1: Established
sw-spine02 ===> 192.168.1.3: Idle
sw-spine02 ===> 192.168.1.4: Idle
sw-spine02 ===> 192.168.1.5: Idle


BGP Neighbors Established
--------------------------------------------------
PASS - IP: 192.168.1.1 Hostname: sw-spine01
SKIP - IP: 192.168.1.3 Hostname: sw-leaf01 is not a spine switch.
FAIL - IP: 192.168.1.2 Hostname: sw-spine02


Errors
--------------------------------------------------
192.168.1.3     - sw-leaf01 not a spine switch
```

If any of the spine switch neighbors for a connection other than **Established**, the switch will **FAIL** validation.

If a switch that is not a **spine** switch is tested, it will show in the results table as **SKIP**.

## Flags

| Option       | Description                         |
| ------------ | ----------------------------------- |
| `--ips`      | Switch IPv4 address                 |
| `--ips-file` | File with one IPv4 address per line |
| `--username` | Switch username                     |
| `--password` | Switch password                     |
| `--asn`      | Switch ASN (Default: 65533)         |

---

**[Back To Readme](/readme.md)**<br>

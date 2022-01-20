# Validate Network BGP

## canu validate network bgp

Validate BGP neighbors.

This command will check the BGP neighbors for the switch IP addresses entered. All of the neighbors of a switch
must be ‘Established’, or the verification will fail.

If a switch that is not a spine switch is tested, it will show in the results table as ‘SKIP’.


* Enter a comma separated list of IP addresses with the ‘—ips’ flag.


* Or read the IP addresses from a file, one IP address per line, using ‘–ips-file FILENAME’ flag.


* The default ‘asn’ is set to 65533 if it needs to be changed, use the ‘–asn NEW_ASN_NUMBER’ flag.

If you want to see the individual status of all the neighbors of a switch, use the ‘–verbose’ flag.


---

```
canu validate network bgp [OPTIONS]
```

### Options


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


### --asn( <asn>)
ASN


* **Default**

    65533



### -a(, --architecture( <architecture>)
**Required** CSM architecture


* **Options**

    Full | TDS | V1



### --verbose()
Verbose mode

## Examples

### 1. Validate BGP

To validate BGP run: `canu validate network bgp --ips 192.168.1.1,192.168.1.2 --username USERNAME --password PASSWORD`

```
$ canu validate network bgp --ips 192.168.1.1,192.168.1.2 --username USERNAME --password PASSWORD

BGP Neighbors Established
--------------------------------------------------
PASS - IP: 192.168.1.1 Hostname: sw-spine01
PASS - IP: 192.168.1.2 Hostname: sw-spine02

```

### 2. Validate BGP Verbose

To get verbose BGP neighbor details: `canu validate network bgp --ips 192.168.1.1,192.168.1.3,192.168.1.2 --username USERNAME --password PASSWORD --verbose`

```
$ canu validate network bgp --ips 192.168.1.1,192.168.1.3,192.168.1.2 --username USERNAME --password PASSWORD --verbose

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


---

<a href="/readme.md">Back To Readme</a><br>

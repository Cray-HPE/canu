# Validate Network BGP

```{eval-rst}
.. click:: canu.validate.network.bgp.bgp:bgp
   :prog: canu validate network bgp
```

## Examples

### 1. Validate BGP

To validate BGP run: `canu validate network bgp --ips 192.168.1.1,192.168.1.2 --username USERNAME --password PASSWORD`

```bash
$ canu validate network bgp --ips 192.168.1.1,192.168.1.2 --username USERNAME --password PASSWORD

BGP Neighbors Established
--------------------------------------------------
PASS - IP: 192.168.1.1 Hostname: sw-spine01
PASS - IP: 192.168.1.2 Hostname: sw-spine02

```

### 2. Validate BGP Verbose

To get verbose BGP neighbor details: `canu validate network bgp --ips 192.168.1.1,192.168.1.3,192.168.1.2 --username USERNAME --password PASSWORD --verbose`

```bash
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

# Generate Switch Config

## Examples

### 1. Generate switch config from SLS API for sw-spine-001

To generate switch config run: `canu generate switch config --csm 1.2 -a full --shcd FILENAME.xlsx --tabs 'INTER_SWITCH_LINKS,NON_COMPUTE_NODES,HARDWARE_MANAGEMENT,COMPUTE_NODES' --corners 'J14,T44,J14,T48,J14,T24,J14,T23' --auth_token TOKEN_FILE --name SWITCH_HOSTNAME --out FILENAME`

```bash
$ canu generate switch config --csm 1.2 -a full --shcd FILENAME.xlsx --tabs INTER_SWITCH_LINKS,NON_COMPUTE_NODES,HARDWARE_MANAGEMENT,COMPUTE_NODES --corners J14,T44,J14,T48,J14,T24,J14,T23 --auth_token TOKEN_FILE --name sw-spine-001

hostname sw-spine-001
user admin group administrators password plaintext
bfd
no ip icmp redirect
vrf CAN
vrf keepalive
...

```

### 2. Generate switch config from CSI for sw-leaf-bmc-001

To generate switch config run: `canu generate switch config --csm 1.2 -a full --shcd FILENAME.xlsx --tabs 'INTER_SWITCH_LINKS,NON_COMPUTE_NODES,HARDWARE_MANAGEMENT,COMPUTE_NODES' --corners 'J14,T44,J14,T48,J14,T24,J14,T23' --sls-file /CSI/OUTPUT/FOLDER/ADDRESS --name SWITCH_HOSTNAME --out FILENAME`

```bash
$ canu generate switch config --csm 1.2 -a full --shcd FILENAME.xlsx --tabs INTER_SWITCH_LINKS,NON_COMPUTE_NODES,HARDWARE_MANAGEMENT,COMPUTE_NODES --corners J14,T44,J14,T48,J14,T24,J14,T23 --sls-file /CSI/OUTPUT/FOLDER/ADDRESS --name sw-leaf-bmc-001

hostname sw-leaf-bmc-001
user admin group administrators password plaintext
no ip icmp redirect
ntp server 192.168.1.4
ntp server 192.168.1.5
ntp server 192.168.1.6
ntp enable
...

```


---

<a href="/readme.md">Back To Readme</a><br>

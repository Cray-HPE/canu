# Generate Switch Config

```{eval-rst}
.. click:: canu.generate.switch.config.config:config
   :prog: canu generate switch config
```

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

To see all the lags that are generated, see {doc}`lags <lags>`

CANU can be used to generate switch config.

In order to generate switch config, a valid SHCD or CCJ must be passed in and system variables must be read in from any SLS data, including CSI output or the SLS API.

#### CSI Input

- In order to parse CSI output, use the `--sls-file FILE` flag to pass in the folder where the `sls_file.json` file is located.

The sls_input_file.json file is generally stored in one of two places depending on how far the system is in the install process.

- Early in the install process, when running off of the LiveCD the sls_input_file.json file is normally found in the the directory `/var/www/ephemeral/prep/SYSTEMNAME/`

- Later in the install process, the sls_input_file.json file is generally in `/mnt/pitdata/prep/SYSTEMNAME/`

#### SLS API Input

- To parse the Shasta SLS API for IP addresses, ensure that you have a valid token. The token file can either be passed in with the `--auth-token TOKEN_FILE` flag, or it can be automatically read if the environmental variable **SLS_TOKEN** is set. The SLS address is default set to _api-gw-service-nmn.local_, if you are operating on a system with a different address, you can set it with the `--sls-address SLS_ADDRESS` flag.

#### Paddle / CCJ Input

- The `--csm` flag is used to set the CSM version of the system.
- The `--ccj` flag is used to input the CCJ file.

To generate switch config run: `canu generate switch config --csm 1.2 --ccj paddle.json --sls-file SLS_FILE --name SWITCH_HOSTNAME --out FILENAME`

#### SHCD Input

- The `--csm` flag is used to set the CSM version of the system.
- The `--architecture / -a` flag is used to set the architecture of the system, either **TDS**, **Full**, or **V1**..
- Use the `--tabs` flag to select which tabs on the spreadsheet will be included.
- The `--corners` flag is used to input the upper left and lower right corners of the table on each tab of the worksheet. The table should contain the 11 headers: **Source, Rack, Location, Slot, (Blank), Port, Destination, Rack, Location, (Blank), Port**. If the corners are not specified, you will be prompted to enter them for each tab.

To generate config for a specific switch, a hostname must also be passed in using the `--name HOSTNAME` flag. To output the config to a file, append the `--out FILENAME` flag.

To generate switch config run: `canu generate switch config --csm 1.2 -a full --shcd FILENAME.xlsx --tabs 'INTER_SWITCH_LINKS,NON_COMPUTE_NODES,HARDWARE_MANAGEMENT,COMPUTE_NODES' --corners 'J14,T44,J14,T48,J14,T24,J14,T23' --sls-file SLS_FILE --name SWITCH_HOSTNAME --out FILENAME`

```bash
canu generate switch config --csm 1.2 -a full --shcd FILENAME.xlsx --tabs INTER_SWITCH_LINKS,NON_COMPUTE_NODES,HARDWARE_MANAGEMENT,COMPUTE_NODES --corners J14,T44,J14,T48,J14,T24,J14,T23 --sls-file SLS_FILE --name sw-spine-001
```

Potential output:

```text
hostname sw-spine-001
user admin group administrators password plaintext
bfd
no ip icmp redirect
vrf CAN
vrf keepalive
...
```

#### Generate Switch Configs Including Custom Configurations

Pass in a switch config file that CANU will inject into the generated config. A use case would be to add custom site connections.
This config file will overwrite previously generate config.

The `custom-config` file type is YAML and a single file can be used for multiple switches. You will need to specify the switch name and what config inject.  The `custom-config` feature is using the hierarchical configuration library, documentation can be found here <https://netdevops.io/hier_config/>.

custom config file examples

Aruba

```yaml
sw-spine-001:  |
    ip route 0.0.0.0/0 10.103.15.185
    interface 1/1/36
        no shutdown
        ip address 10.103.15.186/30
        exit
    system interface-group 3 speed 10g
    interface 1/1/2
        no shutdown
        mtu 9198
        description sw-spine-001:16==>ion-node
        no routing
        vlan access 7
        spanning-tree bpdu-guard
        spanning-tree port-type admin-edge
sw-spine-002:  |
    ip route 0.0.0.0/0 10.103.15.189
    interface 1/1/36
        no shutdown
        ip address 10.103.15.190/30
        exit
    system interface-group 3 speed 10g
sw-leaf-bmc-001:  |
    interface 1/1/20
        no routing
        vlan access 4
        spanning-tree bpdu-guard
        spanning-tree port-type admin-edge
```

Mellanox/Dell

```yaml
sw-spine-001:  |
    interface ethernet 1/1 speed 10G force
    interface ethernet 1/1 description "sw-spine02-1/16"
    interface ethernet 1/1 no switchport force
    interface ethernet 1/1 ip address 10.102.255.14/30 primary
    interface ethernet 1/1 dcb priority-flow-control mode on force
    ip route vrf default 0.0.0.0/0 10.102.255.13
sw-spine-002:  |
    interface ethernet 1/16 speed 10G force
    interface ethernet 1/16 description "sw-spine01-1/16"
    interface ethernet 1/16 no switchport force
    interface ethernet 1/16 ip address 10.102.255.34/30 primary
    interface ethernet 1/16 dcb priority-flow-control mode on force
    ip route vrf default 0.0.0.0/0 10.102.255.33
sw-leaf-bmc-001:  |
    interface ethernet1/1/12
      description sw-leaf-bmc-001:12==>cn003:2
      no shutdown
      switchport access vlan 4
      mtu 9216
      flowcontrol receive off
      flowcontrol transmit off
      spanning-tree bpduguard enable
      spanning-tree port type edge
    interface vlan7
        description CMN
        no shutdown
        ip vrf forwarding Customer
        mtu 9216
        ip address 10.102.4.100/25
        ip access-group cmn-can in
        ip access-group cmn-can out
        ip ospf 2 area 0.0.0.0
```

To generate switch configuration with custom config injection.

```bash
canu generate switch config --csm 1.2 -a full --shcd FILENAME.xlsx --tabs INTER_SWITCH_LINKS,NON_COMPUTE_NODES,HARDWARE_MANAGEMENT,COMPUTE_NODES --corners J14,T44,J14,T48,J14,T24,J14,T23 --sls-file SLS_FILE --name sw-spine-001 --custom-config CUSTOM_CONFIG_FILE.yaml
```

#### Generate Switch Config while preserving LAG \#s

This option allows you to generate swtich configs while preserving the lag #s of the previous running config.

The use case for this is if you have a running system and you don't want to take an outage to renumber the LAGs.

It requires a folder with the config/s backed up.

The recommended way to back these configs up is with {doc}`Backup Network <backup_network>`

```
canu generate switch config -a v1 --csm 1.0 --ccj ccj.json --sls-file sls_input_file.json --name sw-spine-001 --preserve ../backup_configs/
```

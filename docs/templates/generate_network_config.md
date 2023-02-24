# Generate Network Config

```{eval-rst}
.. click:: canu.generate.network.config.config:config
   :prog: canu generate network config
```

## Examples

### 1. Generate network config from SLS API

To generate network config run: `canu generate network config --csm 1.2 -a full --shcd FILENAME.xlsx --tabs 'INTER_SWITCH_LINKS,NON_COMPUTE_NODES,HARDWARE_MANAGEMENT,COMPUTE_NODES' --corners 'J14,T44,J14,T48,J14,T24,J14,T23' --auth_token TOKEN_FILE --folder SWITCH_CONFIG`

```bash
$ canu generate network config --csm 1.2 -a full --shcd FILENAME.xlsx --tabs INTER_SWITCH_LINKS,NON_COMPUTE_NODES,HARDWARE_MANAGEMENT,COMPUTE_NODES --corners J14,T44,J14,T48,J14,T24,J14,T23 --auth_token TOKEN_FILE --folder SWITCH_CONFIG

sw-spine-001 Config Generated
sw-spine-002 Config Generated
sw-leaf-001 Config Generated
sw-leaf-002 Config Generated
sw-leaf-003 Config Generated
sw-leaf-004 Config Generated
sw-cdu-001 Config Generated
sw-cdu-002 Config Generated
sw-leaf-bmc-001 Config Generated

```

### 2. Generate network config from CSI

To generate network config run: `canu generate network config --csm 1.2 -a full --shcd FILENAME.xlsx --tabs 'INTER_SWITCH_LINKS,NON_COMPUTE_NODES,HARDWARE_MANAGEMENT,COMPUTE_NODES' --corners 'J14,T44,J14,T48,J14,T24,J14,T23' --sls-file SLS_FILE --folder SWITCH_CONFIG`

```bash
$ canu generate network config --csm 1.2 -a full --shcd FILENAME.xlsx --tabs INTER_SWITCH_LINKS,NON_COMPUTE_NODES,HARDWARE_MANAGEMENT,COMPUTE_NODES --corners J14,T44,J14,T48,J14,T24,J14,T23 --sls-file SLS_FILE --folder SWITCH_CONFIG

sw-spine-001 Config Generated
sw-spine-002 Config Generated
sw-leaf-001 Config Generated
sw-leaf-002 Config Generated
sw-leaf-003 Config Generated
sw-leaf-004 Config Generated
sw-cdu-001 Config Generated
sw-cdu-002 Config Generated
sw-leaf-bmc-001 Config Generated

```


To see all the lags that are generated, see {doc}`lags <lags>`

CANU can also generate switch config for all the switches on a network.

In order to generate network config, a valid SHCD or CCJ must be passed in and system variables must be read in from either CSI output or the SLS API. The instructions are exactly the same as the above Generate Switch Config except there will not be a hostname and a folder must be specified for config output using the `--folder FOLDERNAME` flag.

To generate switch config from a CCJ paddle run: `canu generate network config --csm 1.2 --ccj paddle.json --sls-file SLS_FILE --folder FOLDERNAME`

To generate switch config from SHCD run: `canu generate network config --csm 1.2 -a full --shcd FILENAME.xlsx --tabs 'INTER_SWITCH_LINKS,NON_COMPUTE_NODES,HARDWARE_MANAGEMENT,COMPUTE_NODES' --corners 'J14,T44,J14,T48,J14,T24,J14,T23' --sls-file SLS_FILE --folder FOLDERNAME`

```bash
canu generate network config --csm 1.2 -a full --shcd FILENAME.xlsx --tabs INTER_SWITCH_LINKS,NON_COMPUTE_NODES,HARDWARE_MANAGEMENT,COMPUTE_NODES --corners J14,T44,J14,T48,J14,T24,J14,T23 --sls-file SLS_FILE --folder switch_config
```

Potential output:

```text
sw-spine-001 Config Generated
sw-spine-002 Config Generated
sw-leaf-001 Config Generated
sw-leaf-002 Config Generated
sw-leaf-003 Config Generated
sw-leaf-004 Config Generated
sw-cdu-001 Config Generated
sw-cdu-002 Config Generated
sw-leaf-bmc-001 Config Generated

```

#### Generate Network Config With Custom Config Injection

This option allows extension and maintenance of switch configurations beyond plan-of-record. A YAML file expresses custom configurations across the network and these configurations are merged with the plan-of-record configurations.

WARNING: Extreme diligence should be used applying custom configurations which override plan-of-record generated configurations. Custom configurations will overwrite generated configurations! Override/overwrite is by design to support and document cases where site-interconnects demand "nonstandard" configurations or a bug must be worked around.

The instructions are exactly the same as Generate Switch Config with Custom Config Injection.

To generate network configuration with custom config injection run

```bash
canu generate network config --csm 1.2 -a full --shcd FILENAME.xlsx --tabs INTER_SWITCH_LINKS,NON_COMPUTE_NODES,HARDWARE_MANAGEMENT,COMPUTE_NODES --corners J14,T44,J14,T48,J14,T24,J14,T23 --sls-file SLS_FILE --folder switch_config --custom-config CUSTOM_CONFIG_FILE.yaml
```

#### Generate Network Config while preserving LAG #s

This option allows you to generate swtich configs while preserving the lag #s of the previous running config.

The use case for this is if you have a running system and you don't want to take an outage to renumber the LAGs.

It requires a folder with the config/s backed up.

The recommended way to back these configs up is with {doc}`Backup Network <backup_network>`.

```bash
canu generate network config --csm 1.0 -a full --shcd FILENAME.xlsx --tabs INTER_SWITCH_LINKS,NON_COMPUTE_NODES,HARDWARE_MANAGEMENT,COMPUTE_NODES --corners J14,T44,J14,T48,J14,T24,J14,T23 --sls-file SLS_FILE --folder switch_config --preserve FOLDER_WITH_SWITCH_CONFIGS
```

# Generate Switch Configs

Generating configuration files can be done for singular switch or for the full system.

For example, if there is a suspected configuration issue on single switch, a configuration file can be generated for just that switch to make it easier to debug problems.

## Generate Configuration Files

Ensure the correct architecture (`-a` parameter) is selected for the setup in use.

The following are the different architectures that can be specified:

* ***Tds*** – Aruba-based Test and Development System. These are small systems characterized by Kubernetes NCNs cabling directly to the spine.
* ***Full*** – Aruba-based Leaf-Spine systems, usually customer production systems.
* ***V1*** – Dell and Mellanox based systems of either a TDS or Full layout.

Generating a configuration file can be done for a single switch, or for the full system. Below are example commands for both scenarios:

***Important***

Modify the following items in your command:

* `--csm` : Which CSM version configuration do you want to use? For example, 1.2 or 1.0
* `--a`   : What is the system architecture? (See above)
* `--ccj` : Match the `ccj.json` file to the one you created for your system.
* `--sls` : Match the `sls_file.json` to the one you created for your system.

* Generate a configuration file for single switch:

  ```bash
  ncn# canu generate switch config --csm 1.2 -a full --ccj system-ccj.json  --sls-file sls_file.json --name sw-spine-001
  ```

* Generate a configuration files for full system:

  ```bash
  ncn# canu generate network config --csm 1.2 -a full --ccj system-ccj.json  --sls-file sls_file.json --folder generated
  ```

[Back to index](index.md)
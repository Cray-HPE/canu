# Quickstart Guide

To checkout a fresh system using CSI:

1. Make a new directory to save switch IP addresses

  ```bash
  mkdir ips_folder
  cd ips_folder
  ```

1. Parse CSI files and save switch IP addresses
   
    ```bash
    canu init --sls-file sls_input_file.json --out ips.txt`
    ```

1. Check network firmware

    ```bash
    canu report network firmware --csm 1.2 --ips-file ips.txt
    ```

1. Check network cabling

    ```bash
    canu report network cabling --ips-file ips.txt
    ```

1. Validate BGP status

    ```bash
    canu validate network bgp --ips-file ips.txt --verbose
    ```

1. Validate cabling

    ```bash
    canu validate network cabling --ips-file ips.txt
    ```

If you have the system's **SHCD**, there are even more commands that can be run

1. Validate the SHCD

    ```bash
    canu validate shcd --shcd SHCD.xlsx
    ```

1. Validate the SHCD against network cabling

    ```bash
    canu validate shcd-cabling --shcd SHCD.xlsx --ips-file ips.txt
    ```

1. Generate switch config for the network

    ```bash
    canu generate network config --shcd SHCD.xlsx --sls-file sls_input_file.json --folder configs
    ```

1. Convert the SHCD to CCJ

    ```bash
    canu validate shcd --shcd SHCD.xlsx --json --out paddle.json
    ```


If you have the system's **CCJ**

1. Validate the Paddle / CCJ

    ```bash
    canu validate paddle --ccj paddle.json
    ```

1. Validate the CCJ against network cabling

    ```bash
    canu validate paddle-cabling --ccj paddle.json --ips-file ips.txt
    ```
1. Generate switch config for the network

    ```bash
    canu generate network config --ccj paddle.json --sls-file sls_input_file.json --folder configs
    ```

## Paddle / CCJ

The **paddle** or **CCJ** (CSM Cabling JSON) is a JSON representation of the network. There are many benefits of using the CCJ:

- The CCJ schema has been validated using `paddle-schema.json`
- The paddle has been architecturally validated to ensure all connections between devices are approved
- All port connections between devices have been checked using the CANU model to ensure speed, slot choice, and port availability has been confirmed
- The CCJ is machine-readable and therefore easy to build additional tooling around
- Less flags need to be used when reading the CCJ vs the SHCD

The SHCD can easily be converted into CCJ by using

  ```bash
  canu validate shcd --shcd SHCD.xlsx --json --out paddle.json
  ```

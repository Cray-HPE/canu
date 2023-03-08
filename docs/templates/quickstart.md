# Quickstart Guide

After installing [the container](container_install.md) or [the RPM](rpm_install.md), or in a [virtualenv](venv.md), there are several ways to invoke CANU, including:

- `docker run` (or other runtime)
- `docker exec` (or other runtime)
- `canuctl`
- `canu` (direct execution of the binary, which will be deprecated in upcoming versions)
- `canu` (running the Python code)

For consistency and simplification, the invocations of CANU throughout the documentation will simply be show as

```shell
canu <command> --flags
```

even though you may be invoking CANU via a different method.

## Checkout A Fresh System

This procedure requires [`csi`](https://github.com/Cray-HPE/cray-site-init)

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

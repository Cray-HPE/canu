# 🛶 CANU v0.0.2

CANU (CSM Automatic Network Utility) will float through a new Shasta network and make setup a breeze. Use CANU to check if Aruba switches on a Shasta network meet the version requirements.

CANU reads switch version information from the _canu.yaml_ file in the root directory. This file still needs testing to ensure that switches and firmware versions are labeled properly. Please let us know if something is broken or needs to be updated. You can currently use CANU to check the firmware versions of Aruba switches on the network.

# Installation and Usage

## Installation

To install the development build of CANU type:

```bash
python3 setup.py develop --user
```

If that doesn't work, try:

```bash
pip3 install --editable .
```

## Usage

To run, just type `canu`, it should run and display help. To see a list of commands and arguments, just append `--help`.

When running CANU, the Shasta version is required, you can pass it in with either `-s` or `--shasta` like `canu -s 1.4`.

### Initialization

To help make switch setup a breeze. CANU can automatically parse CSI output or the Shasta SLS API for switch IPv4 addresses. In order to parse CSI output, use the `--csi-folder FOLDER` flag to pass in the folder where the _NMN.yaml_ file is located. To parse the Shasta SLS API for IP addresses, ensure that you have a valid token. The token file can either be passed in with the `--auth-token TOKEN_FILE` flag, or it can be automatically read if the environmental variable **SLS_TOKEN** is set. The SLS address is default set to _api-gw-service-nmn.local_, if you are operating on a system with a different address, you can set it with the `--sls-address SLS_ADDRESS` flag.

The output file fir the canu input command is et with the `--out FILENAME` flag.

To get the switch IP addresses from CSI output, run the command:

```bash
$ canu -s 1.4 init --csi-folder /CSI/OUTPUT/FOLDER/ADDRESS --out output.txt
8 IP addresses saved to output.txt
```

To get the switch IP addresses from the Shasta SLS API, run the command:

```bash
$ canu -s 1.4 init --auth-token ~./config/cray/tokens/ --sls-address 1.2.3.4 --out output.txt
8 IP addresses saved to output.txt
```

### Check Single Switch Firmware

To check the firmware of a single switch run: `canu --shasta 1.4 switch firmware --ip 192.168.1.1 --username USERNAME --password PASSWORD`

```bash
$ canu --shasta 1.4 switch firmware --ip 192.168.1.1 --username USERNAME --password PASSWORD
🛶 - Pass - IP: 192.168.1.1 Hostname:test-switch-spine01 Firmware: GL.10.06.0001
```

### Check Firmware of Multiple Switches

Multiple Aruba switches on a network can be checked for their firmware versions. The IPv4 addresses of the switches can either be entered comma separated, or be read from a file. To enter a comma separated list of IP addresses to the `---ips` flag. To read the IP addresses from a file, make sure the file has one IP address per line, and use the flag like `--ips-file FILENAME` to input the file.

An example of checking the firmware of multiple switches: `canu --shasta 1.4 network firmware --ips 192.168.1.1,192.168.1.2 --username USERNAME --password PASSWORD`

```bash
$ canu --shasta 1.4 network firmware --ips 192.168.1.1,192.168.1.2,192.168.1.3,192.168.1.4 --username USERNAME --password PASSWORD

------------------------------------------------------------------
    STATUS  IP              HOSTNAME            FIRMWARE
------------------------------------------------------------------
 🛶 Pass    192.168.1.1     test-switch-spine01 GL.10.06.0010
 🛶 Pass    192.168.1.2     test-switch-leaf01  FL.10.06.0010
 ❌ Fail    192.168.1.3     test-wrong-version  FL.10.05.0001   Firmware should be in range ['FL.10.06.0001']
 🔺 Error   192.168.1.4


Errors
------------------------------------------------------------------
192.168.1.4     - HTTP Error. Check that this IP is an Aruba switch, or check the username and password

Summary
------------------------------------------------------------------
🛶 Pass - 2 switches
❌ Fail - 1 switches
🔺 Error - 1 switches
GL.10.06.0010 - 1 switches
FL.10.06.0010 - 1 switches
FL.10.05.0010 - 1 switches
```

When using the _network firmware_ commands, the table will show either: 🛶 Pass, ❌ Fail, or 🔺 Error. The switch will **pass** or **fail** based on if the switch firmware matches the _canu.yaml_

### Output to a File

To output the results of the switch firmware or network firmware commands to a file, append the `--out FILENAME` flag

### JSON

To get the JSON output from a single switch, or from multiple switches, make sure to use the --json flag. An example json output is below.

```bash
$ canu --shasta 1.4 network firmware --ips 192.168.1.1,192.168.1.2 --username USERNAME --password PASSWORD --json

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

### File Output

## To Uninstall

`pip3 uninstall canu`

# Road Map

CANU is under active development, therefore things are changing on a daily basis. Expect commands to change and tests to fail while CANU trends towards stability.

Currently CANU can check the firmware version of a single Aruba switch, or the firmware version of multiple Aruba switches on the network.

Future versions will allow CANU to check switch configurations and network wiring.

# Testing

To test CANU run:

```bash
$ nox
```

# Changelog

## [unreleased]

### Added

- Cache firmware API calls to canu_cache.yaml file.

## [0.0.2] - 2021-03-29

### Added

- Added ability to initialize CANU by reading IP addresses from the CSI output folder, or from the Shasta SLS API by running `canu init`. The initialization will output the IP addresses to an output file.
- Added ability for the network firmware command to read IPv4 address from a file using the --ips-file flag
- Added the --out flag to the switch firmware and network firmware commands to output to a file.
- Added the --json output to the network firmware command
- Full coverage testing
- Added --version flag
- Docstring checks and improvements

## [0.0.1] - 2021-03-19

### Added

- Initial release!
- Ability for CANU to get the firmware of a single or multiple Aruba switches
- Standardized the canu.yaml file to show currently supported switch firmware versions.

[unreleased]: https://stash.us.cray.com/projects/CSM/repos/canu/compare/commits?targetBranch=refs%2Ftags%2F0.0.2&sourceBranch=refs%2Fheads%2Fmaster&targetRepoId=12732
[0.0.2]: https://stash.us.cray.com/projects/CSM/repos/canu/browse?at=refs%2Ftags%2F0.0.2
[0.0.1]: https://stash.us.cray.com/projects/CSM/repos/canu/browse?at=refs%2Ftags%2F0.0.1

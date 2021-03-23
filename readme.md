# 🛶 CANU v0.0.1

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

### Check Single Switch Firmware

To check the firmware of a single switch run: `canu --shasta 1.4 switch firmware --ip 192.168.1.1 --username username --password password`

```bash
$ canu --shasta 1.4 switch firmware --ip 192.168.1.1 --username username --password password
🛶 - Pass - IP: 192.168.1.1 Hostname:test-switch-spine01 Firmware: GL.10.06.0001
```

### Check Firmware of Multiple Switches

To check the firmware of multiple switches run: `canu --shasta 1.4 network firmware --ips 192.168.1.1,192.168.1.2 --username username --password password`

```bash
$ canu --shasta 1.4 network firmware --ips 192.168.1.1,192.168.1.2,192.168.1.3,192.168.1.4 --username username --password password

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

## [Unreleased]

### Added

- Full coverage testing
- Added the --out flag to the switch firmware and network firmware commands to output to a file.
- Added ability for the network firmware command to read IPv4 address from a file using the --ips-file flag
- Added --version flag
- Added the --json output to the network firmware command

## [0.0.1] - 2021-03-19

### Added

- Initial release!
- Ability for CANU to get the firmware of a single or multiple Aruba switches
- Standardized the canu.yaml file to show currently supported switch firmware versions.

[0.0.1]: https://stash.us.cray.com/projects/CSM/repos/canu/browse?at=refs%2Ftags%2F0.0.1

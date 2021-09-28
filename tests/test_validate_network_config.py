# MIT License
#
# (C) Copyright [2021] Hewlett Packard Enterprise Development LP
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
"""Test CANU validate network config commands."""
import json
from os import urandom
from unittest.mock import patch

from click import testing
from netmiko import ssh_exception

from canu.cli import cli
from .test_validate_switch_config import switch_config


username = "admin"
password = "admin"
ips = "192.168.1.1"
credentials = {"username": username, "password": password}
cache_minutes = 0
running_config_file = "running_switch.cfg"
shasta = "1.4"
runner = testing.CliRunner()


@patch("canu.validate.switch.config.config.switch_vendor")
@patch("canu.validate.switch.config.config.netmiko_command")
def test_validate_network_config(netmiko_command, switch_vendor):
    """Test that the `canu validate network config` command runs."""
    switch_config_edit = switch_config[:-15] + "router add\n"
    with runner.isolated_filesystem():
        switch_vendor.return_value = "aruba"
        netmiko_command.return_value = "sw-spine-001"
        netmiko_command.return_value = switch_config
        with open("sw-spine-001.cfg", "w") as f:
            f.writelines(switch_config_edit)

        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "validate",
                "network",
                "config",
                "--ips",
                ips,
                "--username",
                username,
                "--password",
                password,
                "--generated",
                ".",
                "-s",
                shasta,
            ],
        )
        assert result.exit_code == 0
        assert (
            "Switch: sw-spine-001 (192.168.1.1)\n"
            + "Differences\n"
            + "-------------------------------------------------------------------------\n"
            + "In Generated Not In Running (+)     |  In Running Not In Generated (-)   \n"
            + "-------------------------------------------------------------------------\n"
            + "Total Additions:                 1  |  Total Deletions:                 1\n"
            + "                                    |  Script:                          1\n"
            + "Router:                          1  |                                    \n"
        ) in str(result.output)


def test_validate_network_config_running_file():
    """Test that the `canu validate network config` command runs."""
    switch_config_edit = switch_config[:-15] + "router add\n"
    with runner.isolated_filesystem():
        with open("running_switch.cfg", "w") as f:
            f.writelines(switch_config)
        with open("sw-spine-001.cfg", "w") as f:
            f.writelines(switch_config_edit)

        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "validate",
                "network",
                "config",
                "--running",
                ".",
                "--generated",
                ".",
                "-s",
                shasta,
            ],
        )
        assert result.exit_code == 0
        assert (
            "Switch: sw-spine-001\n"
            + "Differences\n"
            + "-------------------------------------------------------------------------\n"
            + "In Generated Not In Running (+)     |  In Running Not In Generated (-)   \n"
            + "-------------------------------------------------------------------------\n"
            + "Total Additions:                 1  |  Total Deletions:                 1\n"
            + "                                    |  Script:                          1\n"
            + "Router:                          1  |                                    \n"
        ) in str(result.output)


@patch("canu.validate.switch.config.config.switch_vendor")
@patch("canu.validate.switch.config.config.netmiko_command")
def test_validate_network_config_json(netmiko_command, switch_vendor):
    """Test that the `canu validate network config` command runs."""
    switch_config_edit = switch_config[:-15] + "router add\n"
    with runner.isolated_filesystem():
        switch_vendor.return_value = "aruba"
        netmiko_command.return_value = "sw-spine-001"
        netmiko_command.return_value = switch_config
        with open("sw-spine-001.cfg", "w") as f:
            f.writelines(switch_config_edit)

        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "validate",
                "network",
                "config",
                "--ips",
                ips,
                "--username",
                username,
                "--password",
                password,
                "--generated",
                ".",
                "-s",
                shasta,
                "--json",
            ],
        )
        result_json = json.loads(result.output)

        assert result.exit_code == 0
        assert result_json == {
            "sw-spine-001": {
                "additions": 1,
                "deletions": 1,
                "hostname_additions": 0,
                "hostname_deletions": 0,
                "interface_additions": 0,
                "interface_deletions": 0,
                "interface_lag_additions": 0,
                "interface_lag_deletions": 0,
                "spanning_tree_additions": 0,
                "spanning_tree_deletions": 0,
                "script_additions": 0,
                "script_deletions": 1,
                "router_additions": 1,
                "router_deletions": 0,
                "system_mac_additions": 0,
                "system_mac_deletions": 0,
                "isl_additions": 0,
                "isl_deletions": 0,
                "role_additions": 0,
                "role_deletions": 0,
                "keepalive_additions": 0,
                "keepalive_deletions": 0,
            },
        }


def test_validate_network_config_json_file():
    """Test that the `canu validate network config` command runs and outputs JSON from files."""
    switch_config_edit = switch_config[:-15] + "router add\n"
    with runner.isolated_filesystem():
        with open("running_switch.cfg", "w") as f:
            f.writelines(switch_config)
        with open("sw-spine-001.cfg", "w") as f:
            f.writelines(switch_config_edit)

        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "validate",
                "network",
                "config",
                "--running",
                ".",
                "--generated",
                ".",
                "-s",
                shasta,
                "--json",
            ],
        )
        result_json = json.loads(result.output)
        print(result_json)
        assert result.exit_code == 0
        assert result_json == {
            "sw-spine-001": {
                "additions": 1,
                "deletions": 1,
                "hostname_additions": 0,
                "hostname_deletions": 0,
                "interface_additions": 0,
                "interface_deletions": 0,
                "interface_lag_additions": 0,
                "interface_lag_deletions": 0,
                "spanning_tree_additions": 0,
                "spanning_tree_deletions": 0,
                "script_additions": 0,
                "script_deletions": 1,
                "router_additions": 1,
                "router_deletions": 0,
                "system_mac_additions": 0,
                "system_mac_deletions": 0,
                "isl_additions": 0,
                "isl_deletions": 0,
                "role_additions": 0,
                "role_deletions": 0,
                "keepalive_additions": 0,
                "keepalive_deletions": 0,
            },
        }


@patch("canu.validate.switch.config.config.switch_vendor")
@patch("canu.validate.switch.config.config.netmiko_command")
def test_validate_network_config_file(netmiko_command, switch_vendor):
    """Test that the `canu validate network config` command runs from a file."""
    switch_config_edit = switch_config[:-15] + "router add\n"
    with runner.isolated_filesystem():
        switch_vendor.return_value = "aruba"
        netmiko_command.return_value = "sw-spine-001"
        netmiko_command.return_value = switch_config
        with open("test.txt", "w") as f:
            f.write("192.168.1.1")

        with open("sw-spine-001.cfg", "w") as f:
            f.writelines(switch_config_edit)

        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "validate",
                "network",
                "config",
                "--ips-file",
                "test.txt",
                "--username",
                username,
                "--password",
                password,
                "--generated",
                ".",
                "-s",
                shasta,
            ],
        )
        assert result.exit_code == 0
        assert (
            "Switch: sw-spine-001 (192.168.1.1)\n"
            + "Differences\n"
            + "-------------------------------------------------------------------------\n"
            + "In Generated Not In Running (+)     |  In Running Not In Generated (-)   \n"
            + "-------------------------------------------------------------------------\n"
            + "Total Additions:                 1  |  Total Deletions:                 1\n"
            + "                                    |  Script:                          1\n"
            + "Router:                          1  |                                    \n"
        ) in str(result.output)


@patch("canu.validate.switch.config.config.switch_vendor")
@patch("canu.validate.switch.config.config.netmiko_command")
def test_validate_network_config_password_prompt(netmiko_command, switch_vendor):
    """Test that the `canu validate network config` command runs and prompts for password."""
    switch_config_edit = switch_config[:-15] + "router add\n"
    with runner.isolated_filesystem():
        switch_vendor.return_value = "aruba"
        netmiko_command.return_value = "sw-spine-001"
        netmiko_command.return_value = switch_config
        with open("sw-spine-001.cfg", "w") as f:
            f.writelines(switch_config_edit)

        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "validate",
                "network",
                "config",
                "--ips",
                ips,
                "--username",
                username,
                "--generated",
                ".",
                "-s",
                shasta,
            ],
            input=password,
        )
        assert result.exit_code == 0
        assert (
            "Switch: sw-spine-001 (192.168.1.1)\n"
            + "Differences\n"
            + "-------------------------------------------------------------------------\n"
            + "In Generated Not In Running (+)     |  In Running Not In Generated (-)   \n"
            + "-------------------------------------------------------------------------\n"
            + "Total Additions:                 1  |  Total Deletions:                 1\n"
            + "                                    |  Script:                          1\n"
            + "Router:                          1  |                                    \n"
        ) in str(result.output)


@patch("canu.validate.switch.config.config.switch_vendor")
@patch("canu.validate.switch.config.config.netmiko_command")
def test_validate_network_config_timeout(netmiko_command, switch_vendor):
    """Test that the `canu validate network config` command errors on timeout."""
    switch_config_edit = switch_config[:-15] + "router add\n"
    with runner.isolated_filesystem():
        switch_vendor.return_value = "aruba"
        netmiko_command.side_effect = ssh_exception.NetmikoTimeoutException
        with open("sw-spine-001.cfg", "w") as f:
            f.writelines(switch_config_edit)

        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "validate",
                "network",
                "config",
                "--ips",
                ips,
                "--username",
                username,
                "--password",
                password,
                "--generated",
                ".",
                "-s",
                shasta,
            ],
        )
        assert result.exit_code == 0
        assert (
            "Errors\n"
            + "----------------------------------------------------------------------------------------------------\n"
            + "192.168.1.1     - Timeout error. Check the IP address and try again.\n"
        ) in str(result.output)


@patch("canu.validate.switch.config.config.switch_vendor")
@patch("canu.validate.switch.config.config.netmiko_command")
def test_validate_network_config_authentication(netmiko_command, switch_vendor):
    """Test that the `canu validate network config` command errors on authentication."""
    switch_config_edit = switch_config[:-15] + "router add\n"
    with runner.isolated_filesystem():
        switch_vendor.return_value = "aruba"
        netmiko_command.side_effect = ssh_exception.NetmikoAuthenticationException
        with open("sw-spine-001.cfg", "w") as f:
            f.writelines(switch_config_edit)

        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "validate",
                "network",
                "config",
                "--ips",
                ips,
                "--username",
                username,
                "--password",
                password,
                "--generated",
                ".",
                "-s",
                shasta,
            ],
        )
        assert result.exit_code == 0
        assert (
            "Errors\n"
            + "----------------------------------------------------------------------------------------------------\n"
            + "192.168.1.1     - Authentication error. Check the credentials or IP address and try again"
        ) in str(result.output)


def test_validate_network_config_bad_config_file():
    """Test that the `canu validate network config` command fails on bad file."""
    switch_config_edit = switch_config[:-15] + "router add\n"
    with runner.isolated_filesystem():
        # Generate random binary file
        with open("bad.file", "wb") as f:
            f.write(urandom(128))

        with open("bad_config.cfg", "w") as f:
            f.write("bad")

        with open("switch.cfg", "w") as f:
            f.writelines(switch_config_edit)
        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "validate",
                "network",
                "config",
                "--running",
                ".",
                "--generated",
                ".",
                "-s",
                shasta,
            ],
        )
        print(result.output)
        assert result.exit_code == 0
        assert (
            "Errors\n"
            + "----------------------------------------------------------------------------------------------------\n"
            + "./bad_config.cfg - The file ./bad_config.cfg is not a valid config file.\n"
            + "sw-spine-001    - Could not find generated config file ./sw-spine-001.cfg\n"
            + "./bad.file      - The file ./bad.file is not a valid config file.\n"
        ) in str(result.output)


def test_validate_network_config_bad_config_file_json():
    """Test that the `canu validate network config` command errors on bad file JSON."""
    with runner.isolated_filesystem():
        # Generate random binary file
        with open("bad.file", "wb") as f:
            f.write(urandom(128))

        with open("bad_config.cfg", "w") as f:
            f.write("bad")

        with open("switch.cfg", "w") as f:
            f.writelines(switch_config)
        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "validate",
                "network",
                "config",
                "--running",
                ".",
                "--generated",
                ".",
                "-s",
                shasta,
                "--json",
            ],
        )
        result_json = json.loads(result.output)

        assert result.exit_code == 0
        assert result_json == {
            "sw-spine-001": {
                "additions": 0,
                "deletions": 161,
                "hostname_additions": 0,
                "hostname_deletions": 1,
                "interface_additions": 0,
                "interface_deletions": 9,
                "interface_lag_additions": 0,
                "interface_lag_deletions": 4,
                "spanning_tree_additions": 0,
                "spanning_tree_deletions": 4,
                "script_additions": 0,
                "script_deletions": 1,
                "router_additions": 0,
                "router_deletions": 2,
                "system_mac_additions": 0,
                "system_mac_deletions": 1,
                "isl_additions": 0,
                "isl_deletions": 1,
                "role_additions": 0,
                "role_deletions": 1,
                "keepalive_additions": 0,
                "keepalive_deletions": 1,
            },
            "errors": {
                "./bad_config.cfg": "The file ./bad_config.cfg is not a valid config file.",
                "sw-spine-001": "Could not find generated config file ./sw-spine-001.cfg",
                "./bad.file": "The file ./bad.file is not a valid config file.",
            },
        }

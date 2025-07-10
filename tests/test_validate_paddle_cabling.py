# MIT License
#
# (C) Copyright 2022-2025 Hewlett Packard Enterprise Development LP
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
"""Test CANU validate shcd commands."""
import json
from os import path
from pathlib import Path
from unittest.mock import patch

import requests
import responses
from click import testing

from canu.cli import cli

from .test_validate_paddle import bad_ccj
from .test_validate_shcd_cabling import arp_neighbors_json1, lldp_neighbors_json1, mac_address_table, switch_info1

test_file_directory = Path(__file__).resolve().parent
test_file_name = "Full_Architecture_Golden_Config_1.1.5.json"
test_file = path.join(test_file_directory, "data", test_file_name)
csm = "1.2"
username = "admin"
password = "admin"
ip = "192.168.1.1"
ips = "192.168.1.1"
credentials = {"username": username, "password": password}
ccj_file = "test_file.json"
runner = testing.CliRunner()


@patch("canu.report.switch.cabling.cabling.switch_vendor")
@patch("canu.report.switch.cabling.cabling.netmiko_command")
@responses.activate
def test_validate_paddle_cabling(netmiko_command, switch_vendor):
    """Test that the `canu validate paddle-cabling` command runs and returns valid cabling."""
    with runner.isolated_filesystem():
        with open(ccj_file, "w") as f:
            json.dump(ccj, f)
        switch_vendor.return_value = "aruba"
        netmiko_command.return_value = mac_address_table

        responses.add(
            responses.POST,
            f"https://{ip}/rest/v10.04/login",
        )
        responses.add(
            responses.GET,
            f"https://{ip}/rest/v10.04/system?attributes=platform_name,hostname,system_mac",
            json=switch_info1,
        )
        responses.add(
            responses.GET,
            f"https://{ip}/rest/v10.04/system/interfaces/*/lldp_neighbors?depth=2",
            json=lldp_neighbors_json1,
        )
        responses.add(
            responses.GET,
            f"https://{ip}/rest/v10.04/system/vrfs/default/neighbors?depth=2",
            json=arp_neighbors_json1,
        )

        responses.add(
            responses.POST,
            f"https://{ip}/rest/v10.04/logout",
        )
        result = runner.invoke(
            cli,
            [
                "validate",
                "paddle-cabling",
                "--csm",
                csm,
                "--ccj",
                ccj_file,
                "--ips",
                ips,
                "--username",
                username,
                "--password",
                password,
            ],
        )
        assert result.exit_code == 0
        assert (
            "sw-spine-001\n"
            + "Rack: x3000    Elevation: u12\n"
            + "--------------------------------------------------------------------------------\n"
            + "Port   CCJ                      Cabling\n"
            + "--------------------------------------------------------------------------------\n"
            + "1      sw-spine-002:1           sw-spine-002:1\n"
            + "2      sw-spine-002:2           sw-spine-002:2\n"
            + "4      sw-leaf-bmc-099:2        ncn-m88:ocp:2\n"
            + "9      ncn-w003:ocp:1           None\n"
            + "15     ncn-s003:ocp:1           None\n"
            + "16     uan001:ocp:1             None\n"
            + "17     uan001:ocp:2             None\n"
            + "47     sw-spine-002:47          None\n"
            + "48     sw-leaf-bmc-001:49       None\n"
            + "5      None                     sw-leaf-bmc-099:5\n"
            + "\n"
            + "sw-spine-002\n"
            + "Rack: x3000    Elevation: u13\n"
            + "--------------------------------------------------------------------------------\n"
            + "Port   CCJ                      Cabling\n"
            + "--------------------------------------------------------------------------------\n"
            + "1      sw-spine-001:1           sw-spine-001:1\n"
            + "2      sw-spine-001:2           sw-spine-001:2\n"
            + "9      ncn-w003:ocp:2           None\n"
            + "16     uan001:pcie-slot1:1      None\n"
            + "17     uan001:pcie-slot1:2      None\n"
            + "47     sw-spine-001:47          None\n"
            + "48     sw-leaf-bmc-001:50       None\n"
        ) in str(result.output)


def test_validate_paddle_cabling_no_architecture():
    """Test that the `canu validate paddle-cabling` command errors on bad architecture."""
    bad_ccj_file = "bad.json"
    with runner.isolated_filesystem():
        with open(bad_ccj_file, "w") as f:
            json.dump(bad_ccj, f)

        result = runner.invoke(
            cli,
            [
                "validate",
                "paddle-cabling",
                "--ccj",
                bad_ccj_file,
                "--csm",
                csm,
                "--ips",
                ips,
                "--username",
                username,
                "--password",
                password,
            ],
        )
        assert result.exit_code == 0
        assert "The key 'architecture' is missing from the CCJ. Ensure that you are using a validated CCJ." in str(
            result.output,
        )


@patch("canu.report.switch.cabling.cabling.switch_vendor")
@patch("canu.report.switch.cabling.cabling.netmiko_command")
@responses.activate
def test_validate_paddle_cabling_file(netmiko_command, switch_vendor):
    """Test that the `canu validate paddle-cabling` command runs and returns valid cabling from file."""
    ccj_file = "test_file.json"
    with runner.isolated_filesystem():
        with open(ccj_file, "w") as f:
            json.dump(ccj, f)
        with open("test.txt", "w") as f:
            f.write("192.168.1.1")
        switch_vendor.return_value = "aruba"
        netmiko_command.return_value = mac_address_table

        responses.add(
            responses.POST,
            f"https://{ip}/rest/v10.04/login",
        )
        responses.add(
            responses.GET,
            f"https://{ip}/rest/v10.04/system?attributes=platform_name,hostname,system_mac",
            json=switch_info1,
        )
        responses.add(
            responses.GET,
            f"https://{ip}/rest/v10.04/system/interfaces/*/lldp_neighbors?depth=2",
            json=lldp_neighbors_json1,
        )
        responses.add(
            responses.GET,
            f"https://{ip}/rest/v10.04/system/vrfs/default/neighbors?depth=2",
            json=arp_neighbors_json1,
        )

        responses.add(
            responses.POST,
            f"https://{ip}/rest/v10.04/logout",
        )
        result = runner.invoke(
            cli,
            [
                "validate",
                "paddle-cabling",
                "--csm",
                csm,
                "--ccj",
                ccj_file,
                "--ips-file",
                "test.txt",
                "--username",
                username,
                "--password",
                password,
            ],
        )
        assert result.exit_code == 0

        assert (
            "sw-spine-001\n"
            + "Rack: x3000    Elevation: u12\n"
            + "--------------------------------------------------------------------------------\n"
            + "Port   CCJ                      Cabling\n"
            + "--------------------------------------------------------------------------------\n"
            + "1      sw-spine-002:1           sw-spine-002:1\n"
            + "2      sw-spine-002:2           sw-spine-002:2\n"
            + "4      sw-leaf-bmc-099:2        ncn-m88:ocp:2\n"
            + "9      ncn-w003:ocp:1           None\n"
            + "15     ncn-s003:ocp:1           None\n"
            + "16     uan001:ocp:1             None\n"
            + "17     uan001:ocp:2             None\n"
            + "47     sw-spine-002:47          None\n"
            + "48     sw-leaf-bmc-001:49       None\n"
            + "5      None                     sw-leaf-bmc-099:5\n"
            + "\n"
            + "sw-spine-002\n"
            + "Rack: x3000    Elevation: u13\n"
            + "--------------------------------------------------------------------------------\n"
            + "Port   CCJ                      Cabling\n"
            + "--------------------------------------------------------------------------------\n"
            + "1      sw-spine-001:1           sw-spine-001:1\n"
            + "2      sw-spine-001:2           sw-spine-001:2\n"
            + "9      ncn-w003:ocp:2           None\n"
            + "16     uan001:pcie-slot1:1      None\n"
            + "17     uan001:pcie-slot1:2      None\n"
            + "47     sw-spine-001:47          None\n"
            + "48     sw-leaf-bmc-001:50       None\n"
        ) in str(result.output)


def test_validate_paddle_cabling_missing_ips():
    """Test that the `canu validate paddle-cabling` command errors on missing IP address."""
    with runner.isolated_filesystem():
        with open(ccj_file, "w") as f:
            json.dump(ccj, f)

        result = runner.invoke(
            cli,
            [
                "validate",
                "paddle-cabling",
                "--csm",
                csm,
                "--ccj",
                test_file,
                "--username",
                username,
                "--password",
                password,
            ],
        )
        assert result.exit_code == 2
        assert (
            "Error: Missing one of the required mutually exclusive options from 'Network cabling IPv4 input sources' option group"
            in str(result.output)
        )


def test_validate_paddle_cabling_mutually_exclusive_ips_and_file():
    """Test that the `canu validate paddle-cabling` command only accepts IPs from command line OR file input, not both."""
    with runner.isolated_filesystem():
        with open(ccj_file, "w") as f:
            json.dump(ccj, f)
        result = runner.invoke(
            cli,
            [
                "validate",
                "paddle-cabling",
                "--csm",
                csm,
                "--ccj",
                test_file,
                "--username",
                username,
                "--password",
                password,
                "--ips",
                ips,
                "--ips-file",
                "file.txt",
            ],
        )
        assert result.exit_code == 2
        assert "Error: Mutually exclusive options from 'Network cabling IPv4 input sources'" in str(result.output)


def test_validate_paddle_cabling_invalid_ip():
    """Test that the `canu validate paddle-cabling` command errors on invalid IP address."""
    invalid_ip = "999.999.999.999"

    with runner.isolated_filesystem():
        with open(ccj_file, "w") as f:
            json.dump(ccj, f)
        result = runner.invoke(
            cli,
            [
                "validate",
                "paddle-cabling",
                "--csm",
                csm,
                "--ccj",
                test_file,
                "--ips",
                invalid_ip,
                "--username",
                username,
                "--password",
                password,
            ],
        )
        assert result.exit_code == 2
        assert "Error: Invalid value for '--ips': These items are not ipv4 addresses: ['999.999.999.999']" in str(
            result.output,
        )


def test_validate_paddle_cabling_invalid_ip_file():
    """Test that the `canu validate paddle-cabling` command errors on invalid IPs from a file."""
    invalid_ip = "999.999.999.999"

    with runner.isolated_filesystem():
        with open("test.txt", "w") as f:
            f.write(invalid_ip)

        with open(ccj_file, "w") as f:
            json.dump(ccj, f)
        result = runner.invoke(
            cli,
            [
                "validate",
                "paddle-cabling",
                "--csm",
                csm,
                "--ccj",
                test_file,
                "--ips-file",
                "test.txt",
                "--username",
                username,
                "--password",
                password,
            ],
        )
        assert result.exit_code == 2
        assert "Error: Invalid value:" in str(result.output)


@patch("canu.report.switch.cabling.cabling.switch_vendor")
@patch("canu.report.switch.cabling.cabling.netmiko_command")
@responses.activate
def test_validate_paddle_cabling_bad_ip(netmiko_command, switch_vendor):
    """Test that the `canu validate paddle-cabling` command errors on bad IP address."""
    bad_ip = "192.168.1.99"

    with runner.isolated_filesystem():
        switch_vendor.return_value = "aruba"
        netmiko_command.return_value = mac_address_table
        responses.add(
            responses.POST,
            f"https://{bad_ip}/rest/v10.04/login",
            body=requests.exceptions.ConnectionError(
                "Failed to establish a new connection: [Errno 60] Operation timed out'))",
            ),
        )
        with open(ccj_file, "w") as f:
            json.dump(ccj, f)
        result = runner.invoke(
            cli,
            [
                "validate",
                "paddle-cabling",
                "--csm",
                csm,
                "--ccj",
                test_file,
                "--ips",
                bad_ip,
                "--username",
                username,
                "--password",
                password,
            ],
        )
        assert result.exit_code == 0
        assert "check the entered username, IP address and password" in str(result.output)


@patch("canu.report.switch.cabling.cabling.switch_vendor")
@patch("canu.report.switch.cabling.cabling.netmiko_command")
@responses.activate
def test_validate_paddle_cabling_bad_ip_file(netmiko_command, switch_vendor):
    """Test that the `canu validate paddle-cabling` command errors on a bad IP from a file."""
    bad_ip = "192.168.1.99"

    with runner.isolated_filesystem():
        switch_vendor.return_value = "aruba"
        netmiko_command.return_value = mac_address_table
        with open("test.txt", "w") as f:
            f.write(bad_ip)

        responses.add(
            responses.POST,
            f"https://{bad_ip}/rest/v10.04/login",
            body=requests.exceptions.ConnectionError(
                "Failed to establish a new connection: [Errno 60] Operation timed out'))",
            ),
        )
        with open(ccj_file, "w") as f:
            json.dump(ccj, f)
        result = runner.invoke(
            cli,
            [
                "validate",
                "paddle-cabling",
                "--csm",
                csm,
                "--ccj",
                test_file,
                "--ips-file",
                "test.txt",
                "--username",
                username,
                "--password",
                password,
            ],
        )
        assert result.exit_code == 0
        assert "check the entered username, IP address and password" in str(result.output)


@patch("canu.report.switch.cabling.cabling.switch_vendor")
@patch("canu.report.switch.cabling.cabling.netmiko_command")
@responses.activate
def test_validate_paddle_cabling_bad_password(netmiko_command, switch_vendor):
    """Test that the `canu validate paddle-cabling` command errors on bad credentials."""
    bad_password = "foo"

    with runner.isolated_filesystem():
        switch_vendor.return_value = "aruba"
        netmiko_command.return_value = mac_address_table
        responses.add(
            responses.POST,
            f"https://{ip}/rest/v10.04/login",
            body=requests.exceptions.HTTPError("Client Error: Unauthorized for url"),
        )
        with open(ccj_file, "w") as f:
            json.dump(ccj, f)
        result = runner.invoke(
            cli,
            [
                "validate",
                "paddle-cabling",
                "--csm",
                csm,
                "--ccj",
                test_file,
                "--ips",
                ip,
                "--username",
                username,
                "--password",
                bad_password,
            ],
        )
        assert result.exit_code == 0
        assert "IP, username, or password" in str(result.output)


def test_validate_paddle_cabling_missing_file():
    """Test that the `canu validate paddle-cabling` command fails on missing file."""
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
                "validate",
                "paddle-cabling",
                "--csm",
                csm,
                "--ips",
                ips,
                "--username",
                username,
                "--password",
                password,
            ],
        )
        assert result.exit_code == 2
        assert "Error: Missing option '--ccj'." in str(result.output)


def test_validate_paddle_cabling_bad_file():
    """Test that the `canu validate paddle-cabling` command fails on bad file."""
    bad_file = "does_not_exist.json"
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
                "validate",
                "paddle-cabling",
                "--csm",
                csm,
                "--ccj",
                bad_file,
                "--ips",
                ips,
                "--username",
                username,
                "--password",
                password,
            ],
        )
        assert result.exit_code == 2
        assert "Error: Invalid value for '--ccj':" in str(result.output)


ccj = {
    "canu_version": "0.0.6",
    "architecture": "network_v2_tds",
    "shcd_file": "ccj",
    "topology": [
        {
            "common_name": "sw-spine-001",
            "id": 0,
            "architecture": "spine",
            "model": "8325_JL625A",
            "type": "switch",
            "vendor": "aruba",
            "ports": [
                {
                    "port": 1,
                    "speed": 25,
                    "slot": None,
                    "destination_node_id": 1,
                    "destination_port": 1,
                    "destination_slot": None,
                },
                {
                    "port": 2,
                    "speed": 25,
                    "slot": None,
                    "destination_node_id": 1,
                    "destination_port": 2,
                    "destination_slot": None,
                },
                {
                    "port": 4,
                    "speed": 10,
                    "slot": None,
                    "destination_node_id": 2,
                    "destination_port": 2,
                    "destination_slot": None,
                },
                {
                    "port": 9,
                    "speed": 25,
                    "slot": None,
                    "destination_node_id": 6,
                    "destination_port": 1,
                    "destination_slot": "ocp",
                },
                {
                    "port": 15,
                    "speed": 25,
                    "slot": None,
                    "destination_node_id": 5,
                    "destination_port": 1,
                    "destination_slot": "ocp",
                },
                {
                    "port": 16,
                    "speed": 25,
                    "slot": None,
                    "destination_node_id": 4,
                    "destination_port": 1,
                    "destination_slot": "ocp",
                },
                {
                    "port": 17,
                    "speed": 25,
                    "slot": None,
                    "destination_node_id": 4,
                    "destination_port": 2,
                    "destination_slot": "ocp",
                },
                {
                    "port": 47,
                    "speed": 25,
                    "slot": None,
                    "destination_node_id": 1,
                    "destination_port": 47,
                    "destination_slot": None,
                },
                {
                    "port": 48,
                    "speed": 10,
                    "slot": None,
                    "destination_node_id": 3,
                    "destination_port": 49,
                    "destination_slot": None,
                },
            ],
            "location": {"rack": "x3000", "elevation": "u12"},
        },
        {
            "common_name": "sw-spine-002",
            "id": 1,
            "architecture": "spine",
            "model": "8325_JL625A",
            "type": "switch",
            "vendor": "aruba",
            "ports": [
                {
                    "port": 1,
                    "speed": 25,
                    "slot": None,
                    "destination_node_id": 0,
                    "destination_port": 1,
                    "destination_slot": None,
                },
                {
                    "port": 2,
                    "speed": 25,
                    "slot": None,
                    "destination_node_id": 0,
                    "destination_port": 2,
                    "destination_slot": None,
                },
                {
                    "port": 9,
                    "speed": 25,
                    "slot": None,
                    "destination_node_id": 6,
                    "destination_port": 2,
                    "destination_slot": "ocp",
                },
                {
                    "port": 16,
                    "speed": 25,
                    "slot": None,
                    "destination_node_id": 4,
                    "destination_port": 1,
                    "destination_slot": "pcie-slot1",
                },
                {
                    "port": 17,
                    "speed": 25,
                    "slot": None,
                    "destination_node_id": 4,
                    "destination_port": 2,
                    "destination_slot": "pcie-slot1",
                },
                {
                    "port": 47,
                    "speed": 25,
                    "slot": None,
                    "destination_node_id": 0,
                    "destination_port": 47,
                    "destination_slot": None,
                },
                {
                    "port": 48,
                    "speed": 10,
                    "slot": None,
                    "destination_node_id": 3,
                    "destination_port": 50,
                    "destination_slot": None,
                },
            ],
            "location": {"rack": "x3000", "elevation": "u13"},
        },
        {
            "common_name": "sw-leaf-bmc-099",
            "id": 2,
            "architecture": "river_bmc_leaf",
            "model": "6300M_JL762A",
            "type": "switch",
            "vendor": "aruba",
            "ports": [
                {
                    "port": 2,
                    "speed": 10,
                    "slot": None,
                    "destination_node_id": 0,
                    "destination_port": 4,
                    "destination_slot": None,
                },
            ],
            "location": {"rack": "x3000", "elevation": "u13"},
        },
        {
            "common_name": "sw-leaf-bmc-001",
            "id": 3,
            "architecture": "river_bmc_leaf",
            "model": "6300M_JL762A",
            "type": "switch",
            "vendor": "aruba",
            "ports": [
                {
                    "port": 49,
                    "speed": 10,
                    "slot": None,
                    "destination_node_id": 0,
                    "destination_port": 48,
                    "destination_slot": None,
                },
                {
                    "port": 50,
                    "speed": 10,
                    "slot": None,
                    "destination_node_id": 1,
                    "destination_port": 48,
                    "destination_slot": None,
                },
            ],
            "location": {"rack": "x3000", "elevation": "U14"},
        },
        {
            "common_name": "uan001",
            "id": 4,
            "architecture": "river_ncn_node_4_port",
            "model": "river_ncn_node_4_port",
            "type": "server",
            "vendor": "hpe",
            "ports": [
                {
                    "port": 1,
                    "speed": 25,
                    "slot": "ocp",
                    "destination_node_id": 0,
                    "destination_port": 16,
                    "destination_slot": None,
                },
                {
                    "port": 2,
                    "speed": 25,
                    "slot": "ocp",
                    "destination_node_id": 0,
                    "destination_port": 17,
                    "destination_slot": None,
                },
                {
                    "port": 1,
                    "speed": 25,
                    "slot": "pcie-slot1",
                    "destination_node_id": 1,
                    "destination_port": 16,
                    "destination_slot": None,
                },
                {
                    "port": 2,
                    "speed": 25,
                    "slot": "pcie-slot1",
                    "destination_node_id": 1,
                    "destination_port": 17,
                    "destination_slot": None,
                },
            ],
            "location": {"rack": "x3000", "elevation": "u19"},
        },
        {
            "common_name": "ncn-s003",
            "id": 5,
            "architecture": "river_ncn_node_4_port",
            "model": "river_ncn_node_4_port",
            "type": "server",
            "vendor": "hpe",
            "ports": [
                {
                    "port": 1,
                    "speed": 25,
                    "slot": "ocp",
                    "destination_node_id": 0,
                    "destination_port": 15,
                    "destination_slot": None,
                },
            ],
            "location": {"rack": "x3000", "elevation": "u09"},
        },
        {
            "common_name": "ncn-w003",
            "id": 6,
            "architecture": "river_ncn_node_2_port",
            "model": "river_ncn_node_2_port",
            "type": "server",
            "vendor": "hpe",
            "ports": [
                {
                    "port": 1,
                    "speed": 25,
                    "slot": "ocp",
                    "destination_node_id": 0,
                    "destination_port": 9,
                    "destination_slot": None,
                },
                {
                    "port": 2,
                    "speed": 25,
                    "slot": "ocp",
                    "destination_node_id": 1,
                    "destination_port": 9,
                    "destination_slot": None,
                },
            ],
            "location": {"rack": "x3000", "elevation": "u06"},
        },
    ],
}

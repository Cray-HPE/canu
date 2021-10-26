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
"""Test CANU validate network cabling commands."""
from unittest.mock import patch

from click import testing
import requests
import responses

from canu.cli import cli
from canu.utils.cache import remove_switch_from_cache


architecture = "tds"
username = "admin"
password = "admin"
ip = "192.168.1.1"
ips = "192.168.1.1"
ip_dell = "192.168.1.2"
ip_mellanox = "192.168.1.3"
credentials = {"username": username, "password": password}
cache_minutes = 0
runner = testing.CliRunner()


@patch("canu.report.switch.cabling.cabling.switch_vendor")
@patch("canu.report.switch.cabling.cabling.netmiko_command")
@responses.activate
def test_validate_cabling(netmiko_command, switch_vendor):
    """Test that the `canu validate network cabling` command runs and returns valid cabling."""
    with runner.isolated_filesystem():
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
                "--cache",
                cache_minutes,
                "validate",
                "network",
                "cabling",
                "--architecture",
                architecture,
                "--ips",
                ips,
                "--username",
                username,
                "--password",
                password,
                "--log",
                "DEBUG",
            ],
        )
        assert result.exit_code == 0
        assert "sw-spine-001 connects to 4 nodes:" in str(result.output)
        remove_switch_from_cache(ip)


@patch("canu.report.switch.cabling.cabling.switch_vendor")
@patch("canu.report.switch.cabling.cabling.netmiko_command")
@responses.activate
def test_validate_cabling_full_architecture(netmiko_command, switch_vendor):
    """Test that the `canu validate network cabling` command runs and returns valid cabling with full architecture."""
    full_architecture = "full"
    with runner.isolated_filesystem():
        switch_vendor.return_value = "aruba"
        netmiko_command.return_value = mac_address_table
        responses.add(
            responses.POST,
            f"https://{ip}/rest/v10.04/login",
        )
        responses.add(
            responses.GET,
            f"https://{ip}/rest/v10.04/system?attributes=platform_name,hostname,system_mac",
            json=switch_info2,
        )
        responses.add(
            responses.GET,
            f"https://{ip}/rest/v10.04/system/interfaces/*/lldp_neighbors?depth=2",
            json=lldp_neighbors_json2,
        )
        responses.add(
            responses.GET,
            f"https://{ip}/rest/v10.04/system/vrfs/default/neighbors?depth=2",
            json=arp_neighbors_json2,
        )

        responses.add(
            responses.POST,
            f"https://{ip}/rest/v10.04/logout",
        )

        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "validate",
                "network",
                "cabling",
                "--architecture",
                full_architecture,
                "--ips",
                ips,
                "--username",
                username,
                "--password",
                password,
            ],
        )
        assert result.exit_code == 0
        assert "sw-spine-001 connects to 1 nodes:" in str(result.output)
        remove_switch_from_cache(ip)


@patch("canu.report.switch.cabling.cabling.switch_vendor")
@patch("canu.report.switch.cabling.cabling.netmiko_command")
@responses.activate
def test_validate_cabling_v1_architecture(netmiko_command, switch_vendor):
    """Test that the `canu validate network cabling` command runs and returns valid cabling with v1 architecture."""
    v1_architecture = "v1"
    with runner.isolated_filesystem():
        switch_vendor.return_value = "aruba"
        netmiko_command.return_value = mac_address_table
        responses.add(
            responses.POST,
            f"https://{ip}/rest/v10.04/login",
        )
        responses.add(
            responses.GET,
            f"https://{ip}/rest/v10.04/system?attributes=platform_name,hostname,system_mac",
            json=switch_info2,
        )
        responses.add(
            responses.GET,
            f"https://{ip}/rest/v10.04/system/interfaces/*/lldp_neighbors?depth=2",
            json=lldp_neighbors_json2,
        )
        responses.add(
            responses.GET,
            f"https://{ip}/rest/v10.04/system/vrfs/default/neighbors?depth=2",
            json=arp_neighbors_json2,
        )

        responses.add(
            responses.POST,
            f"https://{ip}/rest/v10.04/logout",
        )

        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "validate",
                "network",
                "cabling",
                "--architecture",
                v1_architecture,
                "--ips",
                ips,
                "--username",
                username,
                "--password",
                password,
            ],
        )
        assert result.exit_code == 0
        assert "sw-spine-001 connects to 1 nodes:" in str(result.output)
        remove_switch_from_cache(ip)


@patch("canu.report.switch.cabling.cabling.switch_vendor")
@patch("canu.report.switch.cabling.cabling.netmiko_command")
@responses.activate
def test_validate_cabling_file(netmiko_command, switch_vendor):
    """Test that the `canu validate network cabling` command runs and returns valid cabling with IPs from file."""
    with runner.isolated_filesystem():
        switch_vendor.return_value = "aruba"
        netmiko_command.return_value = mac_address_table
        with open("test.txt", "w") as f:
            f.write("192.168.1.1")

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
                "--cache",
                cache_minutes,
                "validate",
                "network",
                "cabling",
                "--architecture",
                architecture,
                "--ips-file",
                "test.txt",
                "--username",
                username,
                "--password",
                password,
            ],
        )
        assert result.exit_code == 0
        assert "sw-spine-001 connects to 4 nodes:" in str(result.output)
        remove_switch_from_cache(ip)


def test_validate_cabling_missing_ips():
    """Test that the `canu validate network cabling` command errors on missing IP address."""
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "validate",
                "network",
                "cabling",
                "--architecture",
                architecture,
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


def test_validate_cabling_mutually_exclusive_ips_and_file():
    """Test that the `canu validate network cabling` command only accepts IPs from command line OR file input, not both."""
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "validate",
                "network",
                "cabling",
                "--architecture",
                architecture,
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
        assert (
            "Error: Mutually exclusive options from 'Network cabling IPv4 input sources'"
            in str(result.output)
        )


def test_validate_cabling_invalid_ip():
    """Test that the `canu validate network cabling` command errors on invalid IP address."""
    invalid_ip = "999.999.999.999"

    with runner.isolated_filesystem():
        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "validate",
                "network",
                "cabling",
                "--architecture",
                architecture,
                "--ips",
                invalid_ip,
                "--username",
                username,
                "--password",
                password,
            ],
        )
        assert result.exit_code == 2
        assert (
            "Error: Invalid value for '--ips': These items are not ipv4 addresses: ['999.999.999.999']"
            in str(result.output)
        )


def test_validate_cabling_invalid_ip_file():
    """Test that the `canu validate network cabling` command errors on invalid IPs from a file."""
    invalid_ip = "999.999.999.999"

    with runner.isolated_filesystem():
        with open("test.txt", "w") as f:
            f.write(invalid_ip)

        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "validate",
                "network",
                "cabling",
                "--architecture",
                architecture,
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
@responses.activate
def test_validate_cabling_bad_ip(switch_vendor):
    """Test that the `canu validate network cabling` command errors on bad IP address."""
    bad_ip = "192.168.1.99"

    with runner.isolated_filesystem():
        switch_vendor.return_value = "aruba"
        responses.add(
            responses.POST,
            f"https://{bad_ip}/rest/v10.04/login",
            body=requests.exceptions.ConnectionError(
                "Failed to establish a new connection: [Errno 60] Operation timed out'))",
            ),
        )

        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "validate",
                "network",
                "cabling",
                "--architecture",
                architecture,
                "--ips",
                bad_ip,
                "--username",
                username,
                "--password",
                password,
            ],
        )
        assert result.exit_code == 0
        assert "check the IP address and try again" in str(result.output)


@patch("canu.report.switch.cabling.cabling.switch_vendor")
@responses.activate
def test_validate_cabling_bad_ip_file(switch_vendor):
    """Test that the `canu validate network cabling` command errors on a bad IP from a file."""
    bad_ip = "192.168.1.99"

    with runner.isolated_filesystem():
        switch_vendor.return_value = "aruba"
        with open("test.txt", "w") as f:
            f.write(bad_ip)

        responses.add(
            responses.POST,
            f"https://{bad_ip}/rest/v10.04/login",
            body=requests.exceptions.ConnectionError(
                "Failed to establish a new connection: [Errno 60] Operation timed out'))",
            ),
        )

        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "validate",
                "network",
                "cabling",
                "--architecture",
                architecture,
                "--ips-file",
                "test.txt",
                "--username",
                username,
                "--password",
                password,
            ],
        )
        assert result.exit_code == 0
        assert "check the IP address and try again" in str(result.output)


@patch("canu.report.switch.cabling.cabling.switch_vendor")
@responses.activate
def test_validate_cabling_bad_password(switch_vendor):
    """Test that the `canu validate network cabling` command errors on bad credentials on an Aruba switch."""
    bad_password = "foo"

    with runner.isolated_filesystem():
        switch_vendor.return_value = "aruba"
        responses.add(
            responses.POST,
            f"https://{ip}/rest/v10.04/login",
            body=requests.exceptions.HTTPError("Client Error: Unauthorized for url"),
        )

        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "validate",
                "network",
                "cabling",
                "--architecture",
                architecture,
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


@patch("canu.report.switch.cabling.cabling.switch_vendor")
@patch("canu.report.switch.cabling.cabling.netmiko_command")
@responses.activate
def test_validate_cabling_rename(netmiko_command, switch_vendor):
    """Test that the `canu validate network cabling` command runs and finds bad naming."""
    with runner.isolated_filesystem():
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
                "--cache",
                cache_minutes,
                "validate",
                "network",
                "cabling",
                "--architecture",
                architecture,
                "--ips",
                ips,
                "--username",
                username,
                "--password",
                password,
            ],
        )
        assert result.exit_code == 0
        assert "sw-leaf-bmc99 should be renamed sw-leaf-bmc-099" in str(result.output)
        assert "sw-spine01 should be renamed sw-spine-001" in str(result.output)
        remove_switch_from_cache(ip)


# Dell
@patch("canu.report.switch.cabling.cabling.switch_vendor")
@patch("canu.report.switch.cabling.cabling.netmiko_commands")
def test_switch_cabling_dell(netmiko_commands, switch_vendor):
    """Test that the `canu validate network cabling` command runs and returns valid Dell cabling."""
    full_architecture = "full"

    with runner.isolated_filesystem():
        switch_vendor.return_value = "dell"
        netmiko_commands.return_value = netmiko_commands_dell

        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "validate",
                "network",
                "cabling",
                "--architecture",
                full_architecture,
                "--ips",
                ip_dell,
                "--username",
                username,
                "--password",
                password,
            ],
        )
        assert result.exit_code == 0
        assert (
            "Cabling Node Connections\n"
            + "------------------------------------------------------------\n"
            + "0: sw-spine-003 connects to 2 nodes: [1, 2]\n"
            + "1: sw-leaf-001 connects to 1 nodes: [0]\n"
            + "2: sw-leaf-002 connects to 1 nodes: [0]\n"
        ) in str(result.output)
        remove_switch_from_cache(ip_dell)


# Mellanox
@patch("canu.report.switch.cabling.cabling.switch_vendor")
@responses.activate
def test_switch_cabling_mellanox(switch_vendor):
    """Test that the `canu validate network cabling` command runs and returns valid Mellanox cabling."""
    full_architecture = "full"

    with runner.isolated_filesystem():
        switch_vendor.return_value = "mellanox"
        responses.add(
            responses.POST,
            f"https://{ip_mellanox}/admin/launch?script=rh&template=json-request&action=json-login",
            json={"status": "OK", "status_msg": "Successfully logged-in"},
        )
        responses.add(
            responses.POST,
            f"https://{ip_mellanox}/admin/launch?script=rh&template=json-request&action=json-login",
            json=lldp_json_mellanox,
        )
        responses.add(
            responses.POST,
            f"https://{ip_mellanox}/admin/launch?script=rh&template=json-request&action=json-login",
            json=mlag_mellanox,
        )
        responses.add(
            responses.POST,
            f"https://{ip_mellanox}/admin/launch?script=rh&template=json-request&action=json-login",
            json=mac_address_table_mellanox,
        )
        responses.add(
            responses.POST,
            f"https://{ip_mellanox}/admin/launch?script=rh&template=json-request&action=json-login",
            json={"data": [{"Hostname": "sw-spine04"}]},
        )
        responses.add(
            responses.POST,
            f"https://{ip_mellanox}/admin/launch?script=rh&template=json-request&action=json-login",
            json={"data": {"value": ["MSN2100"]}},
        )
        responses.add(
            responses.POST,
            f"https://{ip_mellanox}/admin/launch?script=rh&template=json-request&action=json-login",
            json=arp_neighbors_mellanox,
        )
        responses.add(
            responses.POST,
            f"https://{ip_mellanox}/admin/launch?script=rh&template=json-request&action=json-logout",
        )

        result = runner.invoke(
            cli,
            [
                "--cache",
                cache_minutes,
                "validate",
                "network",
                "cabling",
                "--architecture",
                full_architecture,
                "--ips",
                ip_mellanox,
                "--username",
                username,
                "--password",
                password,
            ],
        )
        assert result.exit_code == 0
        assert (
            "Cabling Node Connections\n"
            + "------------------------------------------------------------\n"
            + "0: sw-spine-004 connects to 2 nodes: [1, 2]\n"
            + "1: sw-leaf-003 connects to 1 nodes: [0]\n"
            + "2: sw-leaf-004 connects to 1 nodes: [0]\n"
            + "\n"
            + "\n"
            + "Cabling Port Usage\n"
            + "------------------------------------------------------------\n"
            + "0: sw-spine-004 has the following port usage:\n"
            + "        01==>sw-leaf-003:11\n"
            + "        02==>sw-leaf-004:12\n"
            + "1: sw-leaf-003 has the following port usage:\n"
            + "        01-10==>UNUSED\n"
            + "        11==>sw-spine-004:1\n"
            + "2: sw-leaf-004 has the following port usage:\n"
            + "        01-11==>UNUSED\n"
            + "        12==>sw-spine-004:2\n"
        ) in str(result.output)
        remove_switch_from_cache(ip_mellanox)


# Switch 1
switch_info1 = {
    "hostname": "sw-spine01",
    "platform_name": "X86-64",
    "system_mac": "aa:aa:aa:aa:aa:aa",
}

lldp_neighbors_json1 = {
    "1%2F1%2F1": {
        "bb:bb:bb:bb:bb:bb,1/1/1": {
            "chassis_id": "bb:bb:bb:bb:bb:bb",
            "mac_addr": "bb:bb:bb:bb:bb:cc",
            "neighbor_info": {
                "chassis_description": "Test switch description",
                "chassis_name": "sw-spine02",
                "port_description": "",
                "port_id_subtype": "if_name",
            },
            "port_id": "1/1/1",
        },
    },
    "1%2F1%2F2": {
        "aa:bb:cc:88:00:00,1/1/2": {
            "chassis_id": "aa:bb:cc:88:00:00",
            "mac_addr": "aa:bb:cc:88:00:03",
            "neighbor_info": {
                "chassis_description": "Test switch2 description",
                "chassis_name": "sw-spine02",
                "port_description": "1/1/2",
                "port_id_subtype": "if_name",
            },
            "port_id": "1/1/2",
        },
    },
    "1%2F1%2F3": {
        "00:00:00:00:00:00,00:00:00:00:00:00": {
            "chassis_id": "00:00:00:00:00:00",
            "mac_addr": "00:00:00:00:00:00",
            "neighbor_info": {
                "chassis_description": "",
                "chassis_name": "",
                "port_description": "",
                "port_id_subtype": "link_local_addr",
            },
            "port_id": "00:00:00:00:00:00",
        },
        "11:11:11:11:11:11,11:11:11:11:11:11": {
            "chassis_id": "11:11:11:11:11:11",
            "mac_addr": "11:11:11:11:11:11",
            "neighbor_info": {
                "chassis_description": "",
                "chassis_name": "",
                "port_description": "",
                "port_id_subtype": "link_local_addr",
            },
            "port_id": "11:11:11:11:11:11",
        },
    },
    "1%2F1%2F4": {
        "aa:aa:aa:aa:aa:aa,1/1/4": {
            "chassis_id": "aa:aa:aa:aa:aa:aa",
            "mac_addr": "aa:aa:aa:aa:aa:aa",
            "neighbor_info": {
                "chassis_description": "sw-leaf-bmc99",
                "chassis_name": "sw-leaf-bmc99",
                "port_description": "1/1/4",
                "port_id_subtype": "if_name",
            },
            "port_id": "1/1/4",
        },
    },
    "1%2F1%2F5": {
        "99:99:99:99:99:99,99:99:99:99:99:99": {
            "chassis_id": "99:99:99:99:99:99",
            "mac_addr": "99:99:99:99:99:99",
            "neighbor_info": {
                "chassis_description": "junk",
                "chassis_name": "junk",
                "port_description": "",
                "port_id_subtype": "link_local_addr",
            },
            "port_id": "99:99:99:99:99:99",
        },
    },
    "1%2F1%2F6": {
        "aa:aa:aa:aa:aa:aa,1/1/6": {
            "chassis_id": "aa:aa:aa:aa:aa:aa",
            "mac_addr": "aa:aa:aa:aa:aa:aa",
            "neighbor_info": {
                "chassis_description": "cdu0sw1",
                "chassis_name": "cdu0sw1",
                "port_description": "1/1/6",
                "port_id_subtype": "if_name",
            },
            "port_id": "1/1/6",
        },
    },
}

arp_neighbors_json1 = {
    "192.168.1.2,vlan1": {
        "mac": "00:00:00:00:00:00",
        "ip_address": "192.168.1.2",
        "port": {"vlan1": "/rest/v10.04/system/interfaces/vlan1"},
    },
    "192.168.1.3,vlan2": {
        "mac": "11:11:11:11:11:11",
        "ip_address": "192.168.1.3",
        "port": {"vlan2": "/rest/v10.04/system/interfaces/vlan2"},
    },
    "192.168.2.2,vlan3": {
        "mac": "00:00:00:00:00:00",
        "ip_address": "192.168.2.2",
        "port": {"vlan3": "/rest/v10.04/system/interfaces/vlan3"},
    },
}

# Switch 2
switch_info2 = {
    "hostname": "sw-spine02",
    "platform_name": "X86-64",
    "system_mac": "bb:bb:bb:bb:bb:bb",
}

lldp_neighbors_json2 = {
    "1%2F1%2F1": {
        "aa:aa:aa:aa:aa:aa,1/1/1": {
            "chassis_id": "aa:aa:aa:aa:aa:aa",
            "mac_addr": "aa:aa:aa:aa:aa:bb",
            "neighbor_info": {
                "chassis_description": "Test switch description",
                "chassis_name": "sw-spine01",
                "port_description": "",
                "port_id_subtype": "if_name",
            },
            "port_id": "1/1/1",
        },
    },
}

arp_neighbors_json2 = {
    "192.168.1.2,vlan1": {
        "mac": "00:00:00:00:00:00",
        "ip_address": "192.168.1.2",
        "port": {"vlan1": "/rest/v10.04/system/interfaces/vlan1"},
    },
    "192.168.1.3,vlan2": {
        "mac": "11:11:11:11:11:11",
        "ip_address": "192.168.1.3",
        "port": {"vlan2": "/rest/v10.04/system/interfaces/vlan2"},
    },
    "192.168.2.2,vlan3": {
        "mac": "00:00:00:00:00:00",
        "ip_address": "192.168.2.2",
        "port": {"vlan3": "/rest/v10.04/system/interfaces/vlan3"},
    },
}


netmiko_commands_dell = [
    "",
    " \n"
    + "Remote Chassis ID: aa:bb:cc:dd:ee:ff\n"
    + "Remote Port ID: Eth1/15\n"
    + "Remote Port Description: sw-leaf01\n"
    + "Local Port ID: ethernet1/1/1\n"
    + "Remote System Name: sw-leaf01\n"
    + "Remote System Desc: Test Switch 1\n"
    + "--------------------------------------------------------------------------- \n"
    + "Remote Chassis ID: 00:40:a6:00:00:00\n"
    + "Remote Port ID: ethernet1/1/15\n"
    + "Remote Port Description: sw-leaf02\n"
    + "Local Port ID: ethernet1/1/2\n"
    + "Remote System Name: sw-leaf02\n"
    + "Remote System Desc: Test Switch 2\n"
    + "--------------------------------------------------------------------------- \n"
    + "Remote Chassis ID: 00:40:a6:00:00:02\n"
    + "Remote Port ID: 00:40:a6:00:00:02\n"
    + "Remote Port Description: Not Advertised\n"
    + "Local Port ID: mgmt1/1/3\n"
    + "Remote System Name: Not Advertised\n"
    + "Remote System Desc: Not Advertised\n"
    + "--------------------------------------------------------------------------- \n"
    + "Remote Chassis ID: 00:40:a6:00:00:01\n"
    + "Remote Port ID: 00:40:a6:00:00:01\n"
    + "Local Port ID: ethernet1/1/4\n"
    + "--------------------------------------------------------------------------- \n",
    "OS Version: 10.5.1.4\nSystem Type: S3048-ON\n",
    "sw-spine-003",
    "Address        Hardware address    Interface                     Egress Interface    \n"
    + "------------------------------------------------------------------------------------------\n"
    + "192.168.1.1    aa:bb:cc:dd:ee:ff   vlan2                         port-channel100     \n"
    + "192.168.1.2    11:22:33:44:55:66   vlan7                         port-channel100     \n",
    "VlanId Mac Address      Type      Interface\n"
    + "1   00:40:a6:00:00:00    dynamic    ethernet1/1/3\n",
]


lldp_json_mellanox = {
    "status": "OK",
    "executed_command": "show lldp interfaces ethernet remote",
    "status_message": "",
    "data": [
        {
            "Eth1/1 (Po100)": [
                {
                    "port id subtype": "Interface Name (5)",
                    "Remote chassis id": "aa:bb:cc:dd:ee:ff",
                    "Remote system description": "Test Switch 3",
                    "Remote port-id": "Eth1/11",
                    "Remote port description": "sw-leaf03",
                    "Remote system name": "sw-leaf03",
                },
            ],
        },
        {
            "Eth1/2 (Po100)": [
                {
                    "port id subtype": "Interface Name (5)",
                    "Remote chassis id": "11:22:33:44:55:66",
                    "Remote system description": "Test Switch 4",
                    "Remote port-id": "ethernet1/1/12",
                    "Remote port description": "sw-leaf04",
                    "Remote system name": "sw-leaf04",
                },
            ],
        },
        {
            "Eth1/3 (Po100)": [
                {
                    "port id subtype": "Interface Name (5)",
                    "Remote chassis id": "Not Advertised",
                    "Remote system description": "Not Advertised",
                    "Remote port-id": "Not Advertised",
                    "Remote port description": "Not Advertised",
                    "Remote system name": "Not Advertised",
                },
            ],
        },
        {
            "Eth1/4 (Po100)": [
                {
                    "port id subtype": "Interface Name (5)",
                    "Remote port-id": "Not Advertised",
                },
            ],
        },
    ],
}

arp_neighbors_mellanox = {
    "status": "OK",
    "executed_command": 'show ip arp | exclude "Total number of entries"',
    "status_message": "",
    "data": [
        {"Flags": [{"G": "EVPN Default GW"}]},
        {
            "VRF Name default": [
                {
                    "192.168.1.9": [
                        {
                            "Hardware Address": "aa:bb:cc:dd:ee:ff",
                            "Interface": "vlan 7",
                        },
                    ],
                    "192.168.1.10": [
                        {
                            "Hardware Address": "11:22:33:44:55:66",
                            "Interface": "vlan 4",
                        },
                    ],
                },
            ],
        },
    ],
}

mlag_mellanox = {
    "status": "OK",
    "executed_command": "show interfaces mlag-port-channel summary | include LACP",
    "status_message": "",
    "data": [
        {
            "Lines": [
                "  1 Mpo1(U)          LACP     Eth1/1(P)                 N/A                     ",
                "  2 Mpo2(U)          LACP     Eth1/2(P)                 N/A                     ",
                "  3 Mpo3(U)          LACP     Eth1/3(P)                 N/A                     ",
                "  4 Mpo4(U)          LACP     Eth1/4(P)                 N/A                     ",
            ],
        },
    ],
}

mac_address_table_mellanox = {
    "status": "OK",
    "executed_command": "show mac-address-table",
    "status_message": "",
    "data": {
        "Number of unicast(local)": "45",
        "Number of NVE": "0",
        "2": [
            {
                "Port\\Next Hop": "Mpo2",
                "Type": "Dynamic",
                "Mac Address": "00:40:a6:00:00:33",
            },
            {
                "Port\\Next Hop": "Mpo3",
                "Type": "Dynamic",
                "Mac Address": "00:40:a6:00:00:00",
            },
            {
                "Port\\Next Hop": "Mpo1",
                "Type": "Dynamic",
                "Mac Address": "00:40:a6:00:44:55",
            },
            {
                "Port\\Next Hop": "Mpo4",
                "Type": "Dynamic",
                "Mac Address": "00:40:a6:00:00:02",
            },
        ],
        "4": [
            {
                "Port\\Next Hop": "Mpo1",
                "Type": "Dynamic",
                "Mac Address": "00:40:a6:00:44:55",
            },
            {
                "Port\\Next Hop": "Mpo4",
                "Type": "Dynamic",
                "Mac Address": "00:40:a6:00:00:02",
            },
        ],
        "7": [
            {
                "Port\\Next Hop": "Mpo2",
                "Type": "Dynamic",
                "Mac Address": "00:40:a6:00:00:33",
            },
            {
                "Port\\Next Hop": "Mpo3",
                "Type": "Dynamic",
                "Mac Address": "00:40:a6:00:00:00",
            },
            {
                "Port\\Next Hop": "Mpo1",
                "Type": "Dynamic",
                "Mac Address": "00:40:a6:00:44:55",
            },
            {
                "Port\\Next Hop": "Mpo4",
                "Type": "Dynamic",
                "Mac Address": "00:40:a6:00:00:02",
            },
        ],
    },
}

mac_address_table = (
    "MAC age-time            : 300 seconds\n"
    + "Number of MAC addresses : 90\n"
    + "\n"
    + "MAC Address          VLAN     Type                      Port\n"
    + "--------------------------------------------------------------\n"
    + "00:40:a6:00:00:00    2        dynamic                   1/1/3\n"
)
